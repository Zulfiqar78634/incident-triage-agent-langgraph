"""LangGraph workflow definition."""

from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from incident_agent.agent.nodes import build_nodes
from incident_agent.agent.state import AgentState
from incident_agent.application.container import Runtime


def _route_after_approval(state: dict) -> str:
    if state.get("plan", {}).get("action") == "none":
        return "end"
    return "execute"


def build_graph(runtime: Runtime, checkpointer: BaseCheckpointSaver):
    nodes = build_nodes(runtime)
    builder = StateGraph(AgentState)

    builder.add_node("triage", nodes["triage"])
    builder.add_node("investigate", nodes["investigate"])
    builder.add_node("diagnose", nodes["diagnose"])
    builder.add_node("plan", nodes["plan"])
    builder.add_node("approval_gate", nodes["approval_gate"])
    builder.add_node("execute", nodes["execute"])
    builder.add_node("verify", nodes["verify"])

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

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["approval_gate"],
    )
