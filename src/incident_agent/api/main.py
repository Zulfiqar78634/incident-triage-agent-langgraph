"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from incident_agent.api.middleware import add_guardrails
from incident_agent.api.routes import create_router
from incident_agent.application.container import build_runtime


def create_app() -> FastAPI:
    runtime = build_runtime()
    app = FastAPI(
        title="Incident Triage & Safe Remediation Agent",
        version="1.0.0",
        description="Controlled incident-response agent with human-in-the-loop remediation.",
    )

    add_guardrails(app)
    app.include_router(create_router(runtime))

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
