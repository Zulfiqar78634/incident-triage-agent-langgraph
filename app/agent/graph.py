"""LangGraph workflow with durable SQLite checkpointing."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from app.agent.nodes import approval_gate, diagnose, execute, investigate, plan, triage, verify
from app.agent.state import AgentState
from app.config import DB_PATH


def _route_after_approval(state: dict) -> str:
    if state.get("plan", {}).get("action") == "none":
        return "end"
    return "execute"


def build_graph(checkpointer: SqliteSaver):
    builder = StateGraph(AgentState)

    builder.add_node("triage", triage)
    builder.add_node("investigate", investigate)
    builder.add_node("diagnose", diagnose)
    builder.add_node("plan", plan)
    builder.add_node("approval_gate", approval_gate)
    builder.add_node("execute", execute)
    builder.add_node("verify", verify)

    builder.add_edge(START, "triage")
    builder.add_edge("triage", "investigate")
    builder.add_edge("investigate", "diagnose")
    builder.add_edge("diagnose", "plan")
    builder.add_edge("plan", "approval_gate")
    builder.add_conditional_edges(
        "approval_gate",
        _route_after_approval,
        {"execute": "execute", "end": END},
    )
    builder.add_edge("execute", "verify")
    builder.add_edge("verify", END)

    return builder.compile(checkpointer=checkpointer)


# SQLite checkpointing makes graph state durable across local process restarts.
# For a multi-instance deployment, replace this with a Postgres checkpointer.
_db_path = Path(DB_PATH)
_db_path.parent.mkdir(parents=True, exist_ok=True)
_sqlite_connection = sqlite3.connect(_db_path, check_same_thread=False)
_checkpointer = SqliteSaver(_sqlite_connection)

GRAPH = build_graph(_checkpointer)
