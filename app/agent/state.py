"""Typed state shared across the LangGraph workflow."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict


def append_list(current: list[Any] | None, update: list[Any] | None) -> list[Any]:
    """Reducer that safely appends workflow events and records."""

    return (current or []) + (update or [])


class AgentState(TypedDict, total=False):
    run_id: str
    thread_id: str
    incident: dict[str, Any]
    classification: dict[str, Any]
    evidence: list[dict[str, Any]]
    tool_calls: Annotated[list[dict[str, Any]], append_list]
    diagnosis: dict[str, Any]
    plan: dict[str, Any]
    pending_action: dict[str, Any] | None
    approval: dict[str, Any] | None
    execution: dict[str, Any] | None
    verification: dict[str, Any] | None
    status: str
    events: Annotated[list[dict[str, Any]], append_list]
    context_usage: dict[str, Any]
    retry_count: int
    error: str | None
