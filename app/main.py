"""FastAPI application entrypoint."""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router

load_dotenv()

app = FastAPI(
    title="Incident Triage & Safe Remediation Agent",
    description=(
        "A production-oriented AI agent runtime that triages incidents, investigates with "
        "tools, proposes remediation, requires human approval for risky actions, and exposes "
        "a resumable decision trace."
    ),
    version="1.0.0",
)

app.include_router(router)

static_dir = Path(__file__).resolve().parents[1] / "static"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
