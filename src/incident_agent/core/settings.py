"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    db_path: str
    gemini_api_key: str
    gemini_model: str
    gemini_base_url: str
    max_tool_calls: int
    context_token_budget: int


def load_settings() -> Settings:
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(exist_ok=True)

    return Settings(
        db_path=os.getenv("AGENT_DB_PATH", str(data_dir / "agent.db")),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        gemini_base_url=os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        ),
        max_tool_calls=int(os.getenv("MAX_TOOL_CALLS", "12")),
        context_token_budget=int(os.getenv("CONTEXT_TOKEN_BUDGET", "6000")),
    )
