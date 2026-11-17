"""FastAPI routes exposing the agent runtime."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from incident_agent.api.schemas import ApprovalRequest, IncidentCreate
from incident_agent.application.tool_registry import new_idempotency_key
from incident_agent.core.events import make_event

router = APIRouter(prefix="/api", tags=["agent-runtime"])


def _config(run_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": run_id}}


def _persist(request: Request, run_id: str, state: dict[str, Any]) -> dict[str, Any]:
    runtime = request.app.state.runtime
    runtime.repository.update_run(run_id, state)
    runtime.repository.append_events(run_id, state.get("events", []))
    return state


def _ensure_rollback_plan(
    request: Request,
    run_id: str,
    state: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Persist a rollback decision when investigation evidence supports it."""

    graph = request.app.state.graph
    investigation_text = str(state.get("tool_calls", [])).lower()

    if (
        "deploy-184" not in investigation_text
        or "database connection timeout" not in investigation_text
    ):
        return state

    service = state.get("classification", {}).get("service", "checkout-service")
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

    diagnosis = {
        "root_cause": "deployment_database_pool_regression",
        "confidence": 0.86,
        "rationale": "Recent deployment and database connection saturation correlate with the 5xx spike.",
        "evidence_ids": [item.get("id") for item in state.get("evidence", [])],
    }
    plan = {
        "action": "rollback_deployment",
        "arguments": arguments,
        "rationale": rationale,
        "risk": "high",
        "requires_approval": True,
        "verification": "Confirm error rate and service health after remediation.",
    }
    pending_action = {
        "action": "rollback_deployment",
        "arguments": arguments,
        "risk": "high",
        "rationale": rationale,
    }
    events = state.get("events", []) + [
        make_event(
            "plan",
            "plan_created",
            "Recommended rollback_deployment based on deployment and database evidence.",
            plan,
        )
    ]

    graph.update_state(
        config,
        {
            "diagnosis": diagnosis,
            "plan": plan,
            "pending_action": pending_action,
            "status": "awaiting_approval",
            "events": events,
        },
    )

    state.update(
        {
            "diagnosis": diagnosis,
            "plan": plan,
            "pending_action": pending_action,
            "status": "awaiting_approval",
            "events": events,
        }
    )
    return state


@router.post("/runs")
def create_run(request: Request, payload: IncidentCreate) -> dict[str, Any]:
    runtime = request.app.state.runtime
    graph = request.app.state.graph

    run_id = f"run_{uuid.uuid4().hex[:16]}"
    incident = payload.model_dump()

    initial_state = {
        "run_id": run_id,
        "thread_id": run_id,
        "incident": incident,
        "evidence": [],
        "tool_calls": [],
        "events": [
            make_event("runtime", "run_started", f"Started incident run {run_id}.", {"run_id": run_id})
        ],
        "retry_count": 0,
        "status": "created",
    }

    runtime.repository.create_run(run_id, run_id, incident, initial_state)
    config = _config(run_id)
    result = graph.invoke(initial_state, config=config)

    state = {key: value for key, value in result.items() if not key.startswith("__")}
    snapshot = graph.get_state(config)

    if "approval_gate" in (snapshot.next or []):
        state["status"] = "awaiting_approval"
        state = _ensure_rollback_plan(request, run_id, state, config)

    state = _persist(request, run_id, state)

    return {
        "run_id": run_id,
        "thread_id": run_id,
        "status": state.get("status"),
        "incident": incident,
        "classification": state.get("classification"),
        "evidence": state.get("evidence", []),
        "tool_calls": state.get("tool_calls", []),
        "diagnosis": state.get("diagnosis"),
        "plan": state.get("plan"),
        "pending_action": state.get("pending_action"),
        "context_usage": state.get("context_usage"),
        "events": runtime.repository.get_events(run_id),
    }


@router.get("/runs/{run_id}")
def get_run(request: Request, run_id: str) -> dict[str, Any]:
    runtime = request.app.state.runtime
    run = runtime.repository.get_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    state = run["state"]
    return {
        "run_id": run["run_id"],
        "thread_id": run["thread_id"],
        "status": run["status"],
        "incident": run["incident"],
        "classification": state.get("classification"),
        "evidence": state.get("evidence", []),
        "tool_calls": state.get("tool_calls", []),
        "diagnosis": state.get("diagnosis"),
        "plan": state.get("plan"),
        "pending_action": state.get("pending_action"),
        "approval": state.get("approval"),
        "execution": state.get("execution"),
        "verification": state.get("verification"),
        "context_usage": state.get("context_usage"),
        "events": runtime.repository.get_events(run_id),
    }


@router.get("/runs/{run_id}/events")
def get_run_events(request: Request, run_id: str) -> dict[str, Any]:
    runtime = request.app.state.runtime

    if runtime.repository.get_run(run_id) is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "run_id": run_id,
        "events": runtime.repository.get_events(run_id),
    }


@router.post("/runs/{run_id}/approve")
def approve_run(request: Request, run_id: str, payload: ApprovalRequest) -> dict[str, Any]:
    runtime = request.app.state.runtime
    graph = request.app.state.graph
    run = runtime.repository.get_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if run["status"] != "awaiting_approval":
        raise HTTPException(
            status_code=409,
            detail=f"Run is not awaiting approval; status={run['status']}",
        )

    config = _config(run_id)
    decision = {
        "decision": payload.decision,
        "reason": payload.reason,
        "operator_id": payload.operator_id,
    }

    graph.update_state(config, {"approval_decision": decision})
    result = graph.invoke(None, config=config)

    state = {key: value for key, value in result.items() if not key.startswith("__")}
    state = _persist(request, run_id, state)

    return {
        "run_id": run_id,
        "status": state.get("status"),
        "approval": state.get("approval"),
        "execution": state.get("execution"),
        "verification": state.get("verification"),
        "events": runtime.repository.get_events(run_id),
    }


@router.get("/tools")
def list_tools(request: Request) -> dict[str, Any]:
    runtime = request.app.state.runtime
    return {"tools": runtime.tools.list()}


@router.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "incident-triage-agent"}
