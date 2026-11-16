# Architecture

## Runtime components

```text
Operator UI
   |
   v
FastAPI
   |
   +--> Run Store (SQLite)
   +--> Event Store (SQLite)
   |
   v
LangGraph Agent Runtime
   |
   +--> SQLite Checkpointer
   +--> Tool Registry
   +--> Mock Platform Services
   +--> Optional LLM Enrichment
```

## State ownership

The LangGraph state contains the current incident, classification, evidence, tool-call history, diagnosis, plan, approval, execution, verification, and event stream.

The SQLite checkpointer persists the graph state, allowing an interrupted run to resume after a process restart. The application-level SQLite store persists run metadata and the operator-facing event stream.

## Execution boundary

Read-only tools can run during investigation. Mutating tools require an approval interrupt.

The agent can recommend an action, but it cannot execute a rollback or restart until an operator approves the exact proposed action and arguments.

## Context model

Context is layered and budgeted:

1. Incident task and current objective
2. Current classification and diagnosis
3. Selected evidence with source IDs
4. Recent tool calls
5. Relevant long-term operational conventions

Verbose tool output is truncated. Evidence is selected within a token budget rather than being appended without limit.
