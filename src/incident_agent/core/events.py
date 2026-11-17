"""Agent event model used for operator-facing observability."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentEvent:
    node: str
    event: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_event(node: str, event: str, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return AgentEvent(node=node, event=event, message=message, data=data or {}).to_dict()
