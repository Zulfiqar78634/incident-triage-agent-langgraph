"""LangGraph node implementations."""

from __future__ import annotations

import uuid
from typing import Any

from incident_agent.agent.context import build_context, summarize_tool_result
from incident_agent.application.container import Runtime
from incident_agent.application.tool_registry import new_idempotency_key
from incident_agent.core.events import make_event


def build_nodes(runtime: Runtime) -> dict[str, Any]:
    settings = runtime.settings
    tools = runtime.tools
    approval_policy = runtime.approval_policy
    retry_policy = runtime.retry_policy
    diagnosis = runtime.diagnosis

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
                make_event(
                    "triage",
                    "classification_completed",
                    f"Classified as {severity} availability incident for {service}.",
                    classification,
                )
            ],
        }

    def investigate(state: dict[str, Any]) -> dict[str, Any]:
        service = state["classification"]["service"]
        evidence = []
        tool_calls = []

        planned_calls = [
            ("query_metrics", {"service": service, "window_minutes": 15}),
            ("search_logs", {"service": service, "query": "error", "limit": 10}),
            ("get_service_status", {"service": service}),
            ("get_deployment_history", {"service": service, "limit": 3}),
            ("search_runbooks", {"query": "5xx deployment rollback database connection"}),
        ]

        for index, (name, arguments) in enumerate(planned_calls, start=1):
            if len(tool_calls) >= settings.max_tool_calls:
                break

            result = tools.execute(name, arguments)
            tool_calls.append(
                {
                    "call_id": f"call_{uuid.uuid4().hex[:12]}",
                    "tool": name,
                    "arguments": arguments,
                    "status": "success" if result.success else "failed",
                    "latency_ms": 25 + index * 8,
                    "result": result.data,
                    "error": result.error,
                }
            )

            if result.success:
                evidence.append(
                    {
                        "id": f"ev_{index:02d}",
                        "source": name,
                        "content": summarize_tool_result(result.data),
                    }
                )

        context = build_context(
            {**state, "evidence": evidence, "tool_calls": tool_calls},
            settings.context_token_budget,
        )

        return {
            "evidence": evidence,
            "tool_calls": tool_calls,
            "context_usage": {
                "estimated_tokens": context["estimated_tokens"],
                "budget": context["budget"],
                "evidence_count": len(evidence),
            },
            "events": [
                make_event(
                    "investigate",
                    "investigation_completed",
                    f"Collected {len(evidence)} evidence items from {len(tool_calls)} tool calls.",
                    {"evidence_ids": [item["id"] for item in evidence]},
                )
            ],
        }

    def diagnose(state: dict[str, Any]) -> dict[str, Any]:
        context = build_context(state, settings.context_token_budget)
        result = diagnosis.diagnose(context)
        evidence_ids = [item["id"] for item in state.get("evidence", [])]

        diagnosis_result = {
            "root_cause": result["root_cause"],
            "confidence": result["confidence"],
            "rationale": result["rationale"],
            "evidence_ids": evidence_ids,
        }

        return {
            "diagnosis": diagnosis_result,
            "events": [
                make_event(
                    "diagnose",
                    "diagnosis_completed",
                    f"Diagnosed {result['root_cause']} with confidence {result['confidence']:.2f}.",
                    diagnosis_result,
                )
            ],
        }

    def plan(state: dict[str, Any]) -> dict[str, Any]:
        service = state["classification"]["service"]
        environment = state["classification"]["environment"]
        root_cause = state["diagnosis"]["root_cause"]

        if root_cause == "deployment_database_pool_regression":
            action = "rollback_deployment"
            arguments = {
                "service": service,
                "to_version": "v2.18.3",
                "idempotency_key": new_idempotency_key("rollback"),
            }
            rationale = (
                "The 5xx increase began after deploy-184 and database connections reached "
                "their limit. Rolling back to the previously stable v2.18.3 is the lowest-risk "
                "recovery action."
            )
        elif root_cause == "database_connection_saturation":
            action = "restart_service"
            arguments = {
                "service": service,
                "idempotency_key": new_idempotency_key("restart"),
            }
            rationale = "Restart may clear leaked connections, but the underlying cause needs investigation."
        else:
            action = "none"
            arguments = {}
            rationale = "Evidence is insufficient to recommend a production change safely."

        spec = tools.get(action) if action != "none" else None
        requires_approval = (
            approval_policy.requires_approval(
                mutating=spec.mutating,
                default_requires_approval=spec.requires_approval,
                environment=environment,
            )
            if spec
            else False
        )

        plan = {
            "action": action,
            "arguments": arguments,
            "rationale": rationale,
            "risk": spec.risk.value if spec else "low",
            "requires_approval": requires_approval,
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
            "status": "awaiting_approval" if requires_approval else "executing",
            "events": [
                make_event(
                    "plan",
                    "plan_created",
                    f"Recommended {action or 'no automated action'}.",
                    plan,
                )
            ],
        }

    def approval_gate(state: dict[str, Any]) -> dict[str, Any]:
        decision = state.get("approval_decision") or {}
        approved = decision.get("decision") == "approved"

        approval = {
            "decision": "approved" if approved else "rejected",
            "operator_id": decision.get("operator_id", "operator"),
            "reason": decision.get("reason", ""),
        }

        if not approved:
            return {
                "approval": approval,
                "status": "cancelled",
                "events": [
                    make_event(
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
                make_event(
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
                    make_event("execute", "execution_skipped", "No action was approved or required.")
                ],
            }

        result = tools.execute(action, plan["arguments"])
        retry_count = state.get("retry_count", 0)

        if not result.success and result.retryable and retry_count < retry_policy.max_retries:
            result = tools.execute(action, plan["arguments"])
            retry_count += 1

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
                make_event(
                    "execute",
                    "execution_completed" if result.success else "execution_failed",
                    f"Executed {action} with success={result.success}.",
                    execution,
                )
            ],
        }

    def verify(state: dict[str, Any]) -> dict[str, Any]:
        service = state["classification"]["service"]
        metrics = tools.execute("query_metrics", {"service": service, "window_minutes": 5})
        status = tools.execute("get_service_status", {"service": service})

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
                make_event(
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

    return {
        "triage": triage,
        "investigate": investigate,
        "diagnose": diagnose,
        "plan": plan,
        "approval_gate": approval_gate,
        "execute": execute,
        "verify": verify,
    }
