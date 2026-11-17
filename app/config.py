"""Application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = os.getenv("AGENT_DB_PATH", str(DATA_DIR / "agent.db"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai/",
)

MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "12"))
CONTEXT_TOKEN_BUDGET = int(os.getenv("CONTEXT_TOKEN_BUDGET", "6000"))
