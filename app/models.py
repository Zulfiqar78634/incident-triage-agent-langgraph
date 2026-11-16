"""API and agent domain models."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=4000)
    service: str = ""
    environment: Literal["production", "staging", "development"] = "production"
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    operator_id: str = "operator"


class ApprovalRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = ""
    operator_id: str = "operator"


class ToolCallRecord(BaseModel):
    call_id: str
    tool: str
    arguments: dict[str, Any]
    status: Literal["success", "failed", "retried"]
    latency_ms: int
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class AgentEvent(BaseModel):
    sequence: int
    run_id: str
    node: str
    event: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: str
