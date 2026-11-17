"""Run tracing helpers."""

from __future__ import annotations

from incident_agent.core.events import make_event


def trace_run_started(run_id: str) -> dict:
    return make_event("runtime", "run_started", f"Started incident run {run_id}.", {"run_id": run_id})


def trace_run_completed(run_id: str, status: str) -> dict:
    return make_event(
        "runtime",
        "run_completed",
        f"Run {run_id} completed with status {status}.",
        {"run_id": run_id, "status": status},
    )
