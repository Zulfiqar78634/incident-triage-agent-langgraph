"""LLM adapter used when no API key is configured."""

from __future__ import annotations

from typing import Any


class NullLLMClient:
    def diagnose(self, context: dict[str, Any]) -> dict[str, Any] | None:
        return None
