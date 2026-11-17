"""API request and response schemas."""

from __future__ import annotations

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
