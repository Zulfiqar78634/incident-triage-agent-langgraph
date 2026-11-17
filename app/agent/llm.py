"""Optional Gemini LLM enrichment.

The agent remains fully functional without an API key by using deterministic
operational rules. When GEMINI_API_KEY is configured, Gemini enriches the
diagnosis while deterministic safety and approval boundaries remain in control.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL


def llm_json(system: str, user: str) -> dict[str, Any] | None:
    """Call Gemini through its OpenAI-compatible chat completions endpoint."""

    if not GEMINI_API_KEY:
        return None

    url = f"{GEMINI_BASE_URL.rstrip('/')}/chat/completions"

    try:
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {GEMINI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GEMINI_MODEL,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
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
        # The deterministic workflow remains the source of truth for safety.
        return None
