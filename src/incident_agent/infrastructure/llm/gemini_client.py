"""Gemini adapter implementing the LLMClient port."""

from __future__ import annotations

import json
from typing import Any

import httpx

from incident_agent.core.settings import Settings


class GeminiClient:
    """Calls Gemini through its OpenAI-compatible chat completions endpoint."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def diagnose(self, context: dict[str, Any]) -> dict[str, Any] | None:
        if not self._settings.gemini_api_key:
            return None

        url = f"{self._settings.gemini_base_url.rstrip('/')}/chat/completions"

        try:
            response = httpx.post(
                url,
                headers={
                    "Authorization": f"Bearer {self._settings.gemini_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._settings.gemini_model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a production incident diagnosis assistant. Use only "
                                "supplied evidence. Return JSON with root_cause, confidence, "
                                "rationale, and missing_information. Never recommend an action "
                                "not supported by evidence."
                            ),
                        },
                        {"role": "user", "content": json.dumps(context, default=str)},
                    ],
                    "temperature": 0,
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None
