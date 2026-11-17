"""Core domain models for the incident workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Incident:
    title: str
    description: str
    service: str
    environment: str
    severity: str
    operator_id: str


@dataclass
class Classification:
    service: str
    environment: str
    severity: str
    incident_type: str
    confidence: float


@dataclass
class Evidence:
    evidence_id: str
    source: str
    content: str


@dataclass
class Diagnosis:
    root_cause: str
    confidence: float
    rationale: str
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class RemediationPlan:
    action: str
    arguments: dict[str, Any]
    rationale: str
    risk: str
    requires_approval: bool
    verification: str


@dataclass
class Approval:
    decision: str
    operator_id: str
    reason: str


@dataclass
class ExecutionResult:
    tool: str
    success: bool
    result: dict[str, Any]
    error: str | None = None


@dataclass
class Verification:
    error_rate_percent: float
    service_status: str
    recovered: bool
