"""FastAPI application entrypoint."""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.sqlite import SqliteSaver

from incident_agent.agent.graph import build_graph
from incident_agent.api.routes import router
from incident_agent.application.container import build_runtime


@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime = build_runtime()
    connection = sqlite3.connect(runtime.settings.db_path, check_same_thread=False)
    checkpointer = SqliteSaver(connection)
    graph = build_graph(runtime, checkpointer)

    app.state.runtime = runtime
    app.state.graph = graph

    yield

    connection.close()


app = FastAPI(
    title="Incident Triage & Safe Remediation Agent",
    description=(
        "A production-oriented agent runtime that triages incidents, investigates with "
        "tools, proposes remediation, requires human approval for risky actions, and "
        "exposes a resumable decision trace."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

frontend_dist = Path(__file__).resolve().parents[3] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
