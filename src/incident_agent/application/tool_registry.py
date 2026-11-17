"""Tool registry implementing the Registry and Facade patterns."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from incident_agent.core.results import ToolResult
from incident_agent.domain.enums import Risk
from incident_agent.domain.exceptions import UnknownToolError


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    risk: Risk
    mutating: bool
    requires_approval: bool
    input_model: type[BaseModel]
    handler: Callable[..., dict[str, Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise UnknownToolError(f"Unknown tool: {name}")
        return self._tools[name]

    def list(self) -> list[dict[str, Any]]:
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "risk": spec.risk.value,
                "mutating": spec.mutating,
                "requires_approval": spec.requires_approval,
                "parameters": spec.input_model.model_json_schema(),
            }
            for spec in self._tools.values()
        ]

    def execute(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        try:
            spec = self.get(name)
        except UnknownToolError as exc:
            return ToolResult(success=False, error=str(exc))

        try:
            params = spec.input_model.model_validate(arguments)
        except ValidationError as exc:
            return ToolResult(success=False, error=f"Invalid arguments: {exc}")

        try:
            data = spec.handler(**params.model_dump())
            success = bool(data.get("success", True))
            return ToolResult(
                success=success,
                data=data,
                error=data.get("error"),
                retryable=bool(data.get("retryable", False)),
            )
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), retryable=True)


def new_idempotency_key(prefix: str = "action") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"
