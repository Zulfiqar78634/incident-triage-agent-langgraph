# Architecture

## Layers

```text
Presentation
  static operator UI
  FastAPI interface

Application
  use cases, policies, tool registry, dependency container

Agent runtime
  LangGraph state machine, nodes, context, diagnosis strategies

Domain
  incidents, evidence, diagnosis, plans, approvals, results

Infrastructure
  mock platform, Gemini LLM adapter, SQLite persistence
```

## Dependency rule

Inner layers depend on abstractions, not concrete infrastructure.

```text
agent --> application ports --> infrastructure adapters
```

This allows replacing:

- Mock platform with real cloud APIs.
- Gemini with another LLM provider.
- SQLite with Postgres.
- Local UI with an enterprise console.

## Runtime components

| Component | Location | Responsibility |
|---|---|---|
| Settings | `core/settings.py` | Environment configuration |
| Domain models | `domain/` | Pure business objects |
| Ports | `application/ports.py` | Interfaces for tools, LLM, persistence |
| Policies | `application/policies.py` | Approval and retry rules |
| Tool registry | `application/tool_registry.py` | Tool metadata and execution |
| Agent graph | `agent/graph.py` | LangGraph workflow |
| Diagnosis | `agent/diagnosis/` | Deterministic and Gemini strategies |
| Gemini adapter | `infrastructure/llm/` | LLM integration |
| Mock platform | `infrastructure/platform/` | Simulated operational systems |
| Persistence | `infrastructure/persistence/` | Run and event storage |
| API | `api/` | HTTP interface |
