"""Tool schemas, registry, policy, and execution."""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field

from app.tools import mock_data


class ToolSpec(BaseModel):
    name: str
    description: str
    risk: Literal["low", "medium", "high"]
    mutating: bool
    requires_approval: bool
    parameters: dict[str, Any]


class ToolResult(BaseModel):
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    retryable: bool = False


def search_logs(service: str, query: str = "", limit: int = 10) -> dict[str, Any]:
    """Search recent service logs. Read-only."""

    matches = [
        log
        for log in mock_data.LOGS
        if log["service"] == service
        and (not query or query.lower() in log["message"].lower())
    ][:limit]
    return {"logs": matches, "matched_count": len(matches)}


def query_metrics(service: str, window_minutes: int = 15) -> dict[str, Any]:
    """Return recent service health metrics. Read-only."""

    return {
        "service": service,
        "window_minutes": window_minutes,
        **mock_data.METRICS.get(service, {}),
    }


def get_service_status(service: str) -> dict[str, Any]:
    """Return service and dependency health. Read-only."""

    return mock_data.SERVICE_STATUS.get(service, {"status": "unknown", "dependencies": {}})


def get_deployment_history(service: str, limit: int = 5) -> dict[str, Any]:
    """Return recent deployments for change correlation. Read-only."""

    return {
        "service": service,
        "deployments": mock_data.DEPLOYMENTS.get(service, [])[:limit],
    }


def search_runbooks(query: str) -> dict[str, Any]:
    """Retrieve relevant operational runbooks. Read-only."""

    terms = query.lower().split()
    scored = []
    for runbook in mock_data.RUNBOOKS:
        text = f"{runbook['title']} {runbook['content']}".lower()
        score = sum(term in text for term in terms)
        if score:
            scored.append((score, runbook))
    scored.sort(reverse=True, key=lambda item: item[0])
    return {"runbooks": [item[1] for item in scored[:3]]}


def rollback_deployment(service: str, to_version: str, idempotency_key: str) -> dict[str, Any]:
    """Roll a service back to a prior version. Mutating and approval-gated."""

    if not idempotency_key:
        return {"success": False, "error": "idempotency_key is required", "retryable": False}

    return {
        "success": True,
        "service": service,
        "rolled_back_to": to_version,
        "idempotency_key": idempotency_key,
        "message": "Rollback completed; new rollout is healthy.",
    }


def restart_service(service: str, idempotency_key: str) -> dict[str, Any]:
    """Restart a service. Mutating and approval-gated."""

    if not idempotency_key:
        return {"success": False, "error": "idempotency_key is required", "retryable": False}

    return {
        "success": True,
        "service": service,
        "idempotency_key": idempotency_key,
        "message": "Service restart completed.",
    }


TOOL_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "search_logs": search_logs,
    "query_metrics": query_metrics,
    "get_service_status": get_service_status,
    "get_deployment_history": get_deployment_history,
    "search_runbooks": search_runbooks,
    "rollback_deployment": rollback_deployment,
    "restart_service": restart_service,
}

TOOL_SPECS: dict[str, ToolSpec] = {
    "search_logs": ToolSpec(
        name="search_logs",
        description="Search recent application logs for a service.",
        risk="low",
        mutating=False,
        requires_approval=False,
        parameters={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["service"],
        },
    ),
    "query_metrics": ToolSpec(
        name="query_metrics",
        description="Query service health metrics.",
        risk="low",
        mutating=False,
        requires_approval=False,
        parameters={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "window_minutes": {"type": "integer", "default": 15},
            },
            "required": ["service"],
        },
    ),
    "get_service_status": ToolSpec(
        name="get_service_status",
        description="Get current service and dependency health.",
        risk="low",
        mutating=False,
        requires_approval=False,
        parameters={
            "type": "object",
            "properties": {"service": {"type": "string"}},
            "required": ["service"],
        },
    ),
    "get_deployment_history": ToolSpec(
        name="get_deployment_history",
        description="Get recent deployments for change correlation.",
        risk="low",
        mutating=False,
        requires_approval=False,
        parameters={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["service"],
        },
    ),
    "search_runbooks": ToolSpec(
        name="search_runbooks",
        description="Search approved operational runbooks.",
        risk="low",
        mutating=False,
        requires_approval=False,
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    ),
    "rollback_deployment": ToolSpec(
        name="rollback_deployment",
        description="Roll a service back to a previous version.",
        risk="high",
        mutating=True,
        requires_approval=True,
        parameters={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "to_version": {"type": "string"},
                "idempotency_key": {"type": "string"},
            },
            "required": ["service", "to_version", "idempotency_key"],
        },
    ),
    "restart_service": ToolSpec(
        name="restart_service",
        description="Restart a degraded service.",
        risk="high",
        mutating=True,
        requires_approval=True,
        parameters={
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "idempotency_key": {"type": "string"},
            },
            "required": ["service", "idempotency_key"],
        },
    ),
}


def execute_tool(name: str, arguments: dict[str, Any]) -> ToolResult:
    """Execute a registered tool with validation and bounded error handling."""

    spec = TOOL_SPECS.get(name)
    if spec is None:
        return ToolResult(success=False, error=f"Unknown tool: {name}")

    function = TOOL_FUNCTIONS[name]
    started = time.perf_counter()
    try:
        data = function(**arguments)
        success = bool(data.get("success", True))
        return ToolResult(
            success=success,
            data=data,
            error=data.get("error"),
            retryable=bool(data.get("retryable", False)),
        )
    except TypeError as exc:
        return ToolResult(success=False, error=f"Invalid arguments: {exc}")
    except Exception as exc:  # pragma: no cover - defensive boundary
        return ToolResult(success=False, error=str(exc), retryable=True)
    finally:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        TOOL_CALL_AUDIT.append(
            {
                "call_id": f"call_{uuid.uuid4().hex[:12]}",
                "tool": name,
                "arguments": arguments,
                "latency_ms": elapsed_ms,
            }
        )


TOOL_CALL_AUDIT: list[dict[str, Any]] = []


def new_idempotency_key(prefix: str = "action") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"
