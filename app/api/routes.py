"""FastAPI routes exposing the agent runtime, state, tools, and approvals."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from langgraph.types import Command

from app.agent.graph import GRAPH
from app.models import ApprovalRequest, IncidentCreate
from app.storage import db

router = APIRouter(prefix="/api", tags=["agent-runtime"])


def _config(run_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": run_id}}


def _persist(run_id: str, result: dict[str, Any]) -> dict[str, Any]:
    state = {key: value for key, value in result.items() if not key.startswith("__")}
    db.update_run(run_id, state)
    db.append_events(run_id, state.get("events", []))
    return state


@router.post("/runs")
def create_run(payload: IncidentCreate) -> dict[str, Any]:
    """Start a new incident-triage agent run."""

    run_id = f"run_{uuid.uuid4().hex[:16]}"
    incident = payload.model_dump()

    initial_state = {
        "run_id": run_id,
        "thread_id": run_id,
        "incident": incident,
        "evidence": [],
        "tool_calls": [],
        "events": [],
        "retry_count": 0,
        "status": "created",
    }

    db.create_run(run_id, run_id, incident, initial_state)
    result = GRAPH.invoke(initial_state, config=_config(run_id))
    state = _persist(run_id, result)

    return {
        "run_id": run_id,
        "thread_id": run_id,
        "status": state.get("status"),
        "incident": incident,
        "pending_action": state.get("pending_action"),
        "plan": state.get("plan"),
        "diagnosis": state.get("diagnosis"),
        "events": db.get_events(run_id),
    }


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    run = db.get_run(run_id)
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
        "execution": state.get("execution"),
        "verification": state.get("verification"),
        "context_usage": state.get("context_usage"),
        "events": db.get_events(run_id),
    }


@router.get("/runs/{run_id}/events")
def get_run_events(run_id: str) -> dict[str, Any]:
    if db.get_run(run_id) is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return {"run_id": run_id, "events": db.get_events(run_id)}


@router.post("/runs/{run_id}/approve")
def approve_run(run_id: str, payload: ApprovalRequest) -> dict[str, Any]:
    """Approve or reject a pending human-in-the-loop action."""

    run = db.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if run["status"] != "awaiting_approval":
        raise HTTPException(status_code=409, detail=f"Run is not awaiting approval; status={run['status']}")

    resume_value = {
        "decision": payload.decision,
        "reason": payload.reason,
        "operator_id": payload.operator_id,
    }

    result = GRAPH.invoke(Command(resume=resume_value), config=_config(run_id))
    state = _persist(run_id, result)

    return {
        "run_id": run_id,
        "status": state.get("status"),
        "approval": state.get("approval"),
        "execution": state.get("execution"),
        "verification": state.get("verification"),
        "events": db.get_events(run_id),
    }


@router.get("/tools")
def list_tools() -> dict[str, Any]:
    from app.tools.registry import TOOL_SPECS

    return {"tools": [spec.model_dump() for spec in TOOL_SPECS.values()]}


@router.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "incident-triage-agent"}
