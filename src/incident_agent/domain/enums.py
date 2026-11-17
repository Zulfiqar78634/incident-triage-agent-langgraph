"""Domain enumerations."""

from __future__ import annotations

from enum import StrEnum


class RunStatus(StrEnum):
    CREATED = "created"
    INVESTIGATING = "investigating"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Risk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Environment(StrEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
