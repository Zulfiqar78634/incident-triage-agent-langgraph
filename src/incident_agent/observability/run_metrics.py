"""Lightweight run metrics helpers."""

from __future__ import annotations

from typing import Any


def estimate_tokens(value: Any) -> int:
    return max(1, len(str(value)) // 4)


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return round((input_tokens * 0.0000015) + (output_tokens * 0.000006), 6)
