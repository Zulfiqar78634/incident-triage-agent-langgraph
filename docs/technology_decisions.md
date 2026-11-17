# Technology Decisions

This document explains why each technology, architectural pattern, and design decision was selected for the Incident Triage & Safe Remediation Agent.

## Decision principles

The project optimizes for:

1. A working, locally runnable end-to-end agent.
2. Clear separation between agent autonomy and production safety.
3. Inspectable decisions for operators.
4. Replaceable infrastructure through interfaces.
5. Simple local setup without cloud credentials.
6. Honest separation between implemented features and future enterprise architecture.

## Technology choices

| Technology | Why chosen | What it solves | Trade-off |
|---|---|---|---|
| Python | Strong AI/backend ecosystem and readable agent workflows | Fast development, rich AI libraries, clear domain logic | Not the fastest choice for CPU-heavy workloads |
| FastAPI | Lightweight, modern async API framework | Clean REST APIs, request validation, easy local development | Less batteries-included than Django |
| LangGraph | Explicit agent workflow and state management | Checkpoints, interrupts, resumable execution, controlled branching | More structure than a basic LLM loop |
| SQLite | Zero-setup durable local persistence | Checkpoints, run metadata, and event history work immediately | Not suitable for multi-instance production |
| Gemini | Accessible LLM with OpenAI-compatible API | Natural-language diagnosis enrichment | Output is probabilistic and must not control safety |
| React | Component-based UI framework | Clear operator workflow and reusable UI components | More setup than plain HTML |
| TypeScript | Typed frontend | Safer API integration and fewer runtime errors | Adds build configuration |
| Vite | Fast frontend development server | Quick local iteration and simple build | Separate dev server during development |
| Pydantic | Strict validation | Prevents invalid tool arguments and unsafe actions | Requires schema maintenance |
| Pytest | Simple Python testing framework | Tests workflow, approval, resume, and failure paths | Requires disciplined test maintenance |
| httpx | Simple HTTP client | Gemini API integration | Additional dependency |

## Why LangGraph?

An incident-remediation agent needs more than a single LLM call.

It needs:

- Explicit workflow steps.
- Shared state across steps.
- Tool calls.
- Error recovery.
- Human approval.
- Durable checkpoints.
- Resumable execution.

LangGraph provides these primitives directly.

```text
Triage -> Investigate -> Diagnose -> Plan -> Approval -> Execute -> Verify
```

A basic LLM loop could generate a response, but it would not naturally provide durable state, controlled branching, or a safe human-in-the-loop boundary.

## Why FastAPI?

FastAPI exposes the agent as a runtime service rather than a script.

The API supports:

- Starting a run.
- Reading run state.
- Reading the event trace.
- Approving or rejecting an action.
- Listing tools.
- Health checks.

This makes the agent consumable by an operator UI, another service, or a future automation system.

## Why SQLite locally?

SQLite keeps the assessment reproducible:

```bash
pip install -r requirements.txt
uvicorn incident_agent.api.main:app --app-dir src --reload --port 8000
```

No Postgres, Redis, Docker, or cloud account is required.

The repository uses a `RunRepository` interface, so SQLite can be replaced with Postgres without changing the agent workflow.

## Why Gemini?

Gemini enriches diagnosis with natural-language reasoning.

However, it is intentionally not the authority for production actions.

```text
Gemini proposes reasoning
Deterministic policy validates safety
Approval gate requires operator consent
Only approved actions execute
```

This separation keeps the system safe when the model fails, returns poor output, or is unavailable.

## Why React and TypeScript?

The operator needs to understand the agent while it runs.

The UI shows:

- Current workflow step.
- Agent reasoning.
- Evidence and sources.
- Tool calls.
- Approval request.
- Execution result.
- Verification result.
- Complete event trace.

TypeScript keeps the frontend API contract explicit and reduces integration mistakes.

## Architecture pattern

The project uses a simplified hexagonal/layered architecture.

```text
Presentation
  React operator UI
  FastAPI interface

Application
  policies, tool registry, ports, dependency container

Agent runtime
  LangGraph state machine, nodes, context, diagnosis strategies

Domain
  incidents, evidence, diagnosis, plans, approvals

Infrastructure
  Gemini adapter, mock platform, SQLite persistence
```

The dependency rule is:

```text
agent -> application ports -> infrastructure adapters
```

This prevents the agent from being tightly coupled to Gemini, SQLite, or mock tools.

## SOLID principles

| Principle | Implementation |
|---|---|
| Single Responsibility | Each LangGraph node has one clear responsibility |
| Open/Closed | New tools or LLM providers can be added without rewriting the workflow |
| Liskov Substitution | Gemini and null LLM clients implement the same interface |
| Interface Segregation | Separate ports for platform, LLM, and persistence |
| Dependency Inversion | Agent and API depend on abstractions, not concrete infrastructure |

## Design patterns

| Pattern | Where used | Why |
|---|---|---|
| Strategy | Diagnosis strategies | Separates deterministic and Gemini diagnosis |
| Registry | Tool registry | Central tool metadata and execution |
| Repository | SQLite run repository | Isolates persistence behind an interface |
| Dependency Injection | Application container | Wires settings, clients, repositories, and policies |
| Policy | Approval and retry policies | Separates safety rules from workflow logic |
| Facade | Tool executor | Hides validation, execution, and error mapping |
| Observer | Event stream | Makes agent decisions observable |
| State Machine | LangGraph graph | Models the incident workflow explicitly |
| Adapter | Gemini, mock platform, SQLite | Connects the core to external systems |

## Current implementation versus enterprise target

| Area | Current implementation | Enterprise target |
|---|---|---|
| Persistence | SQLite | Postgres |
| Tools | Mock platform tools | Real cloud, Kubernetes, observability APIs |
| LLM | Gemini | Provider-agnostic LLM gateway |
| Workflow | Single LangGraph process | Durable orchestration and workers |
| Security | Approval gate and validation | Auth, RBAC, sandboxing, audit export |
| Observability | SQLite event stream | OpenTelemetry, LangSmith, or Langfuse |
| Deployment | Local process | Kubernetes |

## What was intentionally not built

The following were intentionally not implemented in this assessment because they would add infrastructure complexity without improving the core demonstration:

- Kubernetes deployment.
- Kafka or external message queue.
- Real cloud credentials.
- Postgres migration.
- Multi-agent supervisor/worker execution.
- Full production observability stack.

They are documented as the enterprise roadmap, not claimed as implemented features.

## Interview-ready explanation

> “I chose LangGraph because an incident-remediation agent needs explicit control flow, durable checkpoints, human interrupts, and inspectable state. I chose FastAPI because it gives me a clean runtime API without unnecessary framework complexity. I used SQLite locally so the project runs with zero infrastructure setup, but the repository interface allows Postgres later. I used Gemini for diagnosis enrichment, but I deliberately did not let it control safety. The deterministic workflow and approval policy remain authoritative.”
