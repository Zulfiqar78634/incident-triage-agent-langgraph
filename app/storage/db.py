"""SQLite persistence for run metadata and the operator-facing event stream."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import DB_PATH

_CONNECTION: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _CONNECTION

    if _CONNECTION is None:
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        _CONNECTION = sqlite3.connect(DB_PATH, check_same_thread=False)
        _CONNECTION.row_factory = sqlite3.Row
        _CONNECTION.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                status TEXT NOT NULL,
                incident_json TEXT NOT NULL,
                state_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                node TEXT NOT NULL,
                event TEXT NOT NULL,
                message TEXT NOT NULL,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
    return _CONNECTION


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_run(run_id: str, thread_id: str, incident: dict[str, Any], state: dict[str, Any]) -> None:
    connection = get_connection()
    connection.execute(
        """
        INSERT INTO runs (run_id, thread_id, status, incident_json, state_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            thread_id,
            state.get("status", "created"),
            json.dumps(incident),
            json.dumps(state, default=str),
            now(),
            now(),
        ),
    )
    connection.commit()


def update_run(run_id: str, state: dict[str, Any]) -> None:
    connection = get_connection()
    connection.execute(
        """
        UPDATE runs
        SET status = ?, state_json = ?, updated_at = ?
        WHERE run_id = ?
        """,
        (state.get("status", "unknown"), json.dumps(state, default=str), now(), run_id),
    )
    connection.commit()


def get_run(run_id: str) -> dict[str, Any] | None:
    connection = get_connection()
    row = connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
    if row is None:
        return None

    return {
        "run_id": row["run_id"],
        "thread_id": row["thread_id"],
        "status": row["status"],
        "incident": json.loads(row["incident_json"]),
        "state": json.loads(row["state_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def append_events(run_id: str, events: list[dict[str, Any]]) -> None:
    connection = get_connection()
    existing = connection.execute(
        "SELECT COALESCE(MAX(sequence), 0) FROM events WHERE run_id = ?", (run_id,)
    ).fetchone()[0]

    for offset, event in enumerate(events, start=1):
        connection.execute(
            """
            INSERT INTO events
            (run_id, sequence, node, event, message, data_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                existing + offset,
                event["node"],
                event["event"],
                event["message"],
                json.dumps(event.get("data", {}), default=str),
                event["created_at"],
            ),
        )
    connection.commit()


def get_events(run_id: str) -> list[dict[str, Any]]:
    connection = get_connection()
    rows = connection.execute(
        "SELECT * FROM events WHERE run_id = ? ORDER BY sequence ASC", (run_id,)
    ).fetchall()

    return [
        {
            "sequence": row["sequence"],
            "run_id": row["run_id"],
            "node": row["node"],
            "event": row["event"],
            "message": row["message"],
            "data": json.loads(row["data_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
