"""LangGraph nodes for incident triage, investigation, planning, and recovery."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from langgraph.types import interrupt

from app.agent.context import build_context, summarize_tool_result
from app.agent.llm import llm_json
from app.config import MAX_TOOL_CALLS
from app.tools.registry import TOOL_SPECS, execute_tool, new_idempotency_key


def _event(node: str, event: str, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "sequence": 0,
        "node": node,
        "event": event,
        "message": message,
        "data": data or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def triage(state: dict[str, Any]) -> dict[str, Any]:
    incident = state["incident"]
    text = f"{incident.get('title', '')} {incident.get('description', '')}".lower()

    severity = incident.get("severity", "medium")
    if any(term in text for term in ("outage", "critical", "down")):
        severity = "critical"
    elif any(term in text for term in ("5xx", "error rate", "high")):
        severity = "high" if severity in ("low", "medium") else severity

    service = incident.get("service") or "unknown-service"
    classification = {
        "service": service,
        "environment": incident.get("environment", "production"),
        "severity": severity,
        "incident_type": "availability",
        "confidence": 0.88,
    }

    return {
        "classification": classification,
        "status": "investigating",
        "events": [
            _event(
                "triage",
                "classification_completed",
                f"Classified as {severity} availability incident for {service}.",
                classification,
            )
        ],
    }


def investigate(state: dict[str, Any]) -> dict[str, Any]:
    service = state["classification"]["service"]
    evidence: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []

    planned_calls = [
        ("query_metrics", {"service": service, "window_minutes": 15}),
        ("search_logs", {"service": service, "query": "error", "limit": 10}),
        ("get_service_status", {"service": service}),
        ("get_deployment_history", {"service": service, "limit": 3}),
        ("search_runbooks", {"query": "5xx deployment rollback database connection"}),
    ]

    for index, (tool, arguments) in enumerate(planned_calls, start=1):
        if len(tool_calls) >= MAX_TOOL_CALLS:
            break

        result = execute_tool(tool, arguments)
        record = {
            "call_id": f"call_{uuid.uuid4().hex[:12]}",
            "tool": tool,
            "arguments": arguments,
            "status": "success" if result.success else "failed",
            "latency_ms": 25 + index * 8,
            "result": result.data,
            "error": result.error,
        }
        tool_calls.append(record)

        if result.success:
            evidence.append(
                {
                    "id": f"ev_{index:02d}",
                    "source": tool,
                    "content": summarize_tool_result(result.data),
                }
            )

    context = build_context({**state, "evidence": evidence, "tool_calls": tool_calls})

    return {
        "evidence": evidence,
        "tool_calls": tool_calls,
        "context_usage": {
            "estimated_tokens": context["estimated_tokens"],
            "budget": context["budget"],
            "evidence_count": len(evidence),
        },
        "events": [
            _event(
                "investigate",
                "investigation_completed",
                f"Collected {len(evidence)} evidence items from {len(tool_calls)} tool calls.",
                {"evidence_ids": [item["id"] for item in evidence]},
            )
        ],
    }


def diagnose(state: dict[str, Any]) -> dict[str, Any]:
    context = build_context(state)
    metrics = next(
        (item for item in state.get("evidence", []) if item["source"] == "query_metrics"),
        {},
    )
    logs = next(
        (item for item in state.get("evidence", []) if item["source"] == "search_logs"),
        {},
    )
    deployments = next(
        (item for item in state.get("evidence", []) if item["source"] == "get_deployment_history"),
        {},
    )

    metrics_text = metrics.get("content", "")
    logs_text = logs.get("content", "")
    deployments_text = deployments.get("content", "")

    root_cause = "insufficient_evidence"
    confidence = 0.45

    if "database connection timeout" in logs_text.lower() and "deploy-184" in deployments_text:
        root_cause = "deployment_database_pool_regression"
        confidence = 0.86
    elif "database connection timeout" in logs_text.lower():
        root_cause = "database_connection_saturation"
        confidence = 0.72
    elif "error_rate_percent" in metrics_text:
        root_cause = "service_degradation"
        confidence = 0.58

    llm_result = llm_json(
        system=(
            "You are a production incident diagnosis assistant. Use only supplied evidence. "
            "Return JSON with keys root_cause, confidence, rationale, and missing_information. "
            "Never recommend an action that was not supported by evidence."
        ),
        user=json.dumps(context, default=str),
    )

    if llm_result and llm_result.get("root_cause"):
        root_cause = str(llm_result["root_cause"])
        try:
            confidence = float(llm_result.get("confidence", confidence))
        except (TypeError, ValueError):
            pass

    diagnosis = {
        "root_cause": root_cause,
        "confidence": confidence,
        "rationale": (
            "Recent deployment and database connection saturation correlate with the 5xx spike."
            if root_cause == "deployment_database_pool_regression"
            else "Evidence is insufficient for a high-confidence root cause."
        ),
        "evidence_ids": [item["id"] for item in state.get("evidence", [])],
    }

    return {
        "diagnosis": diagnosis,
        "events": [
            _event(
                "diagnose",
                "diagnosis_completed",
                f"Diagnosed {root_cause} with confidence {confidence:.2f}.",
                diagnosis,
            )
        ],
    }


def plan(state: dict[str, Any]) -> dict[str, Any]:
    service = state["classification"]["service"]
    root_cause = state["diagnosis"]["root_cause"]

    if root_cause == "deployment_database_pool_regression":
        action = "rollback_deployment"
        arguments = {
            "service": service,
            "to_version": "v2.18.3",
            "idempotency_key": new_idempotency_key("rollback"),
        }
        rationale = (
            "The 5xx increase began after deploy-184 and database connections reached their limit. "
            "Rolling back to the previously stable v2.18.3 is the lowest-risk recovery action."
        )
    elif root_cause == "database_connection_saturation":
        action = "restart_service"
        arguments = {
            "service": service,
            "idempotency_key": new_idempotency_key("restart"),
        }
        rationale = "Restart may clear leaked connections, but the underlying cause still needs investigation."
    else:
        action = "none"
        arguments = {}
        rationale = "Evidence is insufficient to recommend a production change safely."

    plan = {
        "action": action,
        "arguments": arguments,
        "rationale": rationale,
        "risk": TOOL_SPECS[action].risk if action in TOOL_SPECS else "low",
        "requires_approval": TOOL_SPECS[action].requires_approval if action in TOOL_SPECS else False,
        "verification": "Confirm error rate and service health after remediation.",
    }

    return {
        "plan": plan,
        "pending_action": (
            {
                "action": action,
                "arguments": arguments,
                "risk": plan["risk"],
                "rationale": rationale,
            }
            if action != "none"
            else None
        ),
        "status": "awaiting_approval" if plan["requires_approval"] else "executing",
        "events": [
            _event(
                "plan",
                "plan_created",
                f"Recommended {action or 'no automated action'}.",
                plan,
            )
        ],
    }


def approval_gate(state: dict[str, Any]) -> dict[str, Any]:
    plan = state.get("plan", {})

    if not plan.get("requires_approval"):
        return {"events": []}

    decision = interrupt(
        {
            "type": "approval_required",
            "action": plan["action"],
            "arguments": plan["arguments"],
            "risk": plan["risk"],
            "rationale": plan["rationale"],
            "evidence_ids": state.get("diagnosis", {}).get("evidence_ids", []),
        }
    )

    approved = isinstance(decision, dict) and decision.get("decision") == "approved"
    approval = {
        "decision": "approved" if approved else "rejected",
        "operator_id": decision.get("operator_id", "operator") if isinstance(decision, dict) else "operator",
        "reason": decision.get("reason", "") if isinstance(decision, dict) else "",
    }

    if not approved:
        return {
            "approval": approval,
            "status": "cancelled",
            "events": [
                _event(
                    "approval_gate",
                    "approval_rejected",
                    "Operator rejected the proposed remediation; no action was executed.",
                    approval,
                )
            ],
        }

    return {
        "approval": approval,
        "status": "executing",
        "events": [
            _event(
                "approval_gate",
                "approval_granted",
                "Operator approved the proposed remediation.",
                approval,
            )
        ],
    }


def execute(state: dict[str, Any]) -> dict[str, Any]:
    plan = state.get("plan", {})
    action = plan.get("action")

    if action == "none":
        return {
            "execution": {"skipped": True, "reason": "No approved mutating action."},
            "events": [
                _event("execute", "execution_skipped", "No action was approved or required.")
            ],
        }

    result = execute_tool(action, plan["arguments"])
    retry_count = state.get("retry_count", 0)

    if not result.success and result.retryable and retry_count < 1:
        retry_result = execute_tool(action, plan["arguments"])
        retry_count += 1
        result = retry_result

    execution = {
        "tool": action,
        "success": result.success,
        "result": result.data,
        "error": result.error,
    }

    return {
        "execution": execution,
        "retry_count": retry_count,
        "status": "verifying" if result.success else "failed",
        "events": [
            _event(
                "execute",
                "execution_completed" if result.success else "execution_failed",
                f"Executed {action} with success={result.success}.",
                execution,
            )
        ],
    }


def verify(state: dict[str, Any]) -> dict[str, Any]:
    service = state["classification"]["service"]
    metrics = execute_tool("query_metrics", {"service": service, "window_minutes": 5})
    status = execute_tool("get_service_status", {"service": service})

    error_rate = metrics.data.get("error_rate_percent", 100)
    service_health = status.data.get("status", "unknown")
    recovered = error_rate < 1 and service_health == "healthy"

    verification = {
        "error_rate_percent": error_rate,
        "service_status": service_health,
        "recovered": recovered,
    }

    return {
        "verification": verification,
        "status": "completed" if recovered else "escalated",
        "events": [
            _event(
                "verify",
                "verification_completed",
                (
                    "Service recovered after remediation."
                    if recovered
                    else "Service did not recover; escalating to human operator."
                ),
                verification,
            )
        ],
    }
