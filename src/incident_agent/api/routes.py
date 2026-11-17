"""FastAPI routes exposing the agent runtime."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from langgraph.types import Command

from incident_agent.api.schemas import ApprovalRequest, IncidentCreate
from incident_agent.core.events import make_event

router = APIRouter(prefix="/api", tags=["agent-runtime"])


def _config(run_id: str) -> dict[str, Any]:
    return {"configurable": {"thread_id": run_id}}


def _persist(request: Request, run_id: str, result: dict[str, Any]) -> dict[str, Any]:
    runtime = request.app.state.runtime
    state = {key: value for key, value in result.items() if not key.startswith("__")}
    runtime.repository.update_run(run_id, state)
    runtime.repository.append_events(run_id, state.get("events", []))
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
    result = graph.invoke(initial_state, config=_config(run_id))
    state = _persist(request, run_id, result)

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

    resume_value = {
        "decision": payload.decision,
        "reason": payload.reason,
        "operator_id": payload.operator_id,
    }

    result = graph.invoke(Command(resume=resume_value), config=_config(run_id))
    state = _persist(request, run_id, result)

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
