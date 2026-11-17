"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from incident_agent.api.middleware import add_guardrails
from incident_agent.api.routes import router
from incident_agent.application.container import build_runtime


def create_app() -> FastAPI:
    runtime = build_runtime()
    app = FastAPI(
        title="Incident Triage & Safe Remediation Agent",
        version="1.0.0",
        description="Controlled incident-response agent with human-in-the-loop remediation.",
    )

    app.state.runtime = runtime
    add_guardrails(app)
    app.include_router(router)

    return app


app = create_app()
