"""Safety and reliability policies kept separate from workflow logic."""

from __future__ import annotations

from incident_agent.domain.enums import Environment


class ApprovalPolicy:
    """Decides whether an action requires explicit operator approval."""

    def requires_approval(self, *, mutating: bool, default_requires_approval: bool, environment: str) -> bool:
        if not mutating:
            return False
        return default_requires_approval or environment == Environment.PRODUCTION


class RetryPolicy:
    """Bounded retry policy for transient tool failures."""

    max_retries: int = 1
