"""Optional LLM enrichment.

The agent remains fully functional without an API key by using deterministic
operational rules. When OPENAI_API_KEY is configured, the LLM is used to
produce a structured diagnosis and remediation rationale.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


def llm_json(system: str, user: str) -> dict[str, Any] | None:
    """Call OpenAI-compatible chat completions and parse a JSON object."""

    if not OPENAI_API_KEY:
        return None

    try:
        response = httpx.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": OPENAI_MODEL,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0,
            },
            timeout=20,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        # The deterministic workflow remains the source of truth for safety.
        return None
