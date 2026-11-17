"""Strategy pattern for evidence-based incident diagnosis."""

from __future__ import annotations

from typing import Any, Protocol


class DiagnosisStrategy(Protocol):
    def diagnose(self, context: dict[str, Any]) -> dict[str, Any] | None: ...


class DeterministicDiagnosisStrategy:
    """Evidence-rule diagnosis used as the safe default and fallback."""

    def diagnose(self, context: dict[str, Any]) -> dict[str, Any]:
        evidence_text = str(context.get("evidence", [])).lower()
        tool_text = str(context.get("recent_tool_calls", [])).lower()
        combined_evidence = f"{evidence_text} {tool_text}"

        if "database connection timeout" in combined_evidence and "deploy-184" in combined_evidence:
            return {
                "root_cause": "deployment_database_pool_regression",
                "confidence": 0.86,
                "rationale": (
                    "Recent deployment and database connection saturation correlate "
                    "with the 5xx spike."
                ),
            }

        if "database connection timeout" in combined_evidence:
            return {
                "root_cause": "database_connection_saturation",
                "confidence": 0.72,
                "rationale": "Database connection saturation is present, but deployment correlation is unclear.",
            }

        if "error_rate_percent" in combined_evidence:
            return {
                "root_cause": "service_degradation",
                "confidence": 0.58,
                "rationale": "Service degradation detected, but root cause requires more evidence.",
            }

        return {
            "root_cause": "insufficient_evidence",
            "confidence": 0.45,
            "rationale": "Evidence is insufficient for a high-confidence diagnosis.",
        }


class GeminiDiagnosisStrategy:
    """LLM-enriched diagnosis; returns None when Gemini is unavailable or invalid."""

    def __init__(self, llm: Any) -> None:
        self._llm = llm

    def diagnose(self, context: dict[str, Any]) -> dict[str, Any] | None:
        result = self._llm.diagnose(context)

        if not result or not result.get("root_cause"):
            return None

        try:
            confidence = float(result.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5

        return {
            "root_cause": str(result["root_cause"]),
            "confidence": confidence,
            "rationale": str(result.get("rationale", "")),
        }


class DiagnosisSupervisor:
    """Chooses the first valid diagnosis strategy result."""

    def __init__(self, strategies: list[Any]) -> None:
        self._strategies = strategies

    def diagnose(self, context: dict[str, Any]) -> dict[str, Any]:
        for strategy in self._strategies:
            result = strategy.diagnose(context)
            if result:
                return result

        return {
            "root_cause": "insufficient_evidence",
            "confidence": 0.45,
            "rationale": "No diagnosis strategy produced a valid result.",
        }
