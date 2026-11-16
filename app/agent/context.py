"""Context selection, token budgeting, and compaction."""

from __future__ import annotations

from typing import Any

from app.config import CONTEXT_TOKEN_BUDGET


def estimate_tokens(value: Any) -> int:
    """Estimate tokens without requiring a tokenizer dependency."""

    return max(1, len(str(value)) // 4)


def summarize_tool_result(result: dict[str, Any], max_chars: int = 700) -> str:
    """Compress tool output while retaining operationally useful fields."""

    text = str(result)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + " ... [truncated for context budget]"


def select_evidence(evidence: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    """Keep the most useful recent evidence within a token budget."""

    selected: list[dict[str, Any]] = []
    used = 0

    for item in reversed(evidence):
        content = item.get("content", "")
        tokens = estimate_tokens(content)
        if used + tokens > budget:
            break
        selected.insert(0, item)
        used += tokens

    return selected


def build_context(state: dict[str, Any]) -> dict[str, Any]:
    """Build a layered, budgeted context for diagnosis and planning."""

    evidence_budget = int(CONTEXT_TOKEN_BUDGET * 0.45)
    selected_evidence = select_evidence(state.get("evidence", []), evidence_budget)

    context = {
        "incident": state.get("incident", {}),
        "classification": state.get("classification", {}),
        "evidence": selected_evidence,
        "recent_tool_calls": state.get("tool_calls", [])[-5:],
        "long_term_memory": [
            "Checkout deployments require a canary period before full rollout.",
            "Rollback is the preferred recovery action when a new deployment causes a regression.",
        ],
    }

    context["estimated_tokens"] = estimate_tokens(context)
    context["budget"] = CONTEXT_TOKEN_BUDGET
    return context
