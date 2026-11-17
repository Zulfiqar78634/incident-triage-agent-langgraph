"""Context selection, token budgeting, and compaction."""

from __future__ import annotations

from typing import Any


def estimate_tokens(value: Any) -> int:
    return max(1, len(str(value)) // 4)


def summarize_tool_result(result: dict[str, Any], max_chars: int = 700) -> str:
    text = str(result)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + " ... [truncated for context budget]"


def select_evidence(evidence: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    used = 0

    for item in evidence:
        tokens = estimate_tokens(item.get("content", ""))

        if used + tokens > budget:
            break

        selected.append(item)
        used += tokens

    return selected


def build_context(state: dict[str, Any], budget: int) -> dict[str, Any]:
    evidence_budget = int(budget * 0.45)
    selected_evidence = select_evidence(state.get("evidence", []), evidence_budget)

    context = {
        "incident": state.get("incident", {}),
        "classification": state.get("classification", {}),
        "evidence": selected_evidence,
        "recent_tool_calls": state.get("tool_calls", [])[-5:],
        "long_term_memory": [
            "Checkout deployments require a canary period before full rollout.",
            "Rollback is preferred when a new deployment causes a regression.",
        ],
    }

    context["estimated_tokens"] = estimate_tokens(context)
    context["budget"] = budget
    return context
