# Incident Triage & Safe Remediation Agent

A production-oriented AI agent that triages platform incidents, investigates root causes with tools, proposes remediation, requires human approval for risky actions, and preserves a resumable decision trace.

It is built with **Python, FastAPI, LangGraph, SQLite checkpointing, Google Gemini, and a lightweight operator UI**. The project runs locally without an API key: deterministic operational logic handles the core workflow. If `GEMINI_API_KEY` is configured, Gemini enriches diagnosis while the deterministic safety and approval boundaries remain in control.

## Why this use case

Platform teams need agents that reduce investigation time without taking unsafe autonomous actions. This project deliberately separates:

- **Autonomy:** investigating, forming hypotheses, selecting tools, and proposing remediation.
- **Control:** requiring operator approval before any production mutation.
- **Trust:** exposing evidence, tool calls, decisions, retries, and verification results.

The demo scenario is a `checkout-service` 5xx incident that begins after a deployment. The agent correlates metrics, logs, service health, deployment history, and runbooks, then recommends a rollback only after evidence supports it.

## What it demonstrates

| Capability | Implementation |
|---|---|
| Multi-step agent workflow | LangGraph state graph with triage, investigation, diagnosis, planning, approval, execution, and verification nodes |
| Tool use | Structured mock tools for logs, metrics, health, deployments, runbooks, rollback, and restart |
| Durable execution | LangGraph SQLite checkpointer persists graph state across process restarts |
| Human-in-the-loop | `interrupt()` pauses execution before rollback/restart; the operator approves or rejects it |
| Context engineering | Evidence selection, tool-output truncation, token estimation, and a context budget |
| Observability | Persistent event stream for every agent node, tool action, approval, and verification result |
| Safe remediation | Mutating tools require approval and use idempotency keys |
| Error recovery | Failed retryable tool calls are retried once, then the run escalates or fails visibly |
| Operator UX | Web UI shows live status, timeline, evidence, proposed action, and approval controls |

## Architecture

```text
Operator UI
      |
      v
FastAPI Agent Runtime API
      |
      v
LangGraph Orchestrator
  |-- triage
  |-- investigate
  |-- diagnose
  |-- plan
  |-- approval_gate  --> human approval interrupt
  |-- execute
  |-- verify
      |
      +--> SQLite checkpoint store
      +--> SQLite run/event store
      +--> Mock platform tools
      +--> Gemini diagnosis enrichment
```

## Agent workflow

```text
Incident
  -> Triage and classify
  -> Investigate with read-only tools
  -> Diagnose from evidence
  -> Create remediation plan
  -> Approval gate for risky action
  -> Execute approved action
  -> Verify recovery
  -> Complete or escalate
```

The approval gate is a hard runtime boundary, not a prompt-level request. A rollback or restart cannot execute until the operator explicitly approves it.

## Quickstart

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Gemini

```bash
cp .env.example .env
```

Open `.env` and add your Google AI Studio API key:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

The application works without an API key. When `GEMINI_API_KEY` is present, Gemini is used for LLM-assisted diagnosis through Gemini’s OpenAI-compatible endpoint.

### 3. Run the application

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000
```

### 4. Run tests

```bash
pytest -q
```

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/runs` | Start an incident run |
| `GET` | `/api/runs/{run_id}` | Get run state, evidence, plan, and trace |
| `GET` | `/api/runs/{run_id}/events` | Get the event stream |
| `POST` | `/api/runs/{run_id}/approve` | Approve or reject a pending action |
| `GET` | `/api/tools` | List tools, risk levels, and approval requirements |
| `GET` | `/api/health` | Health check |

### Start a run

```bash
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Checkout service 5xx spike",
    "description": "Checkout is returning 5xx errors after the latest deployment.",
    "service": "checkout-service",
    "environment": "production",
    "severity": "high",
    "operator_id": "ops-alice"
  }'
```

The response will contain a `run_id` and, for a rollback recommendation, `status: "awaiting_approval"`.

### Approve remediation

```bash
curl -X POST http://localhost:8000/api/runs/{run_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approved",
    "reason": "Deployment correlation and DB saturation support rollback.",
    "operator_id": "ops-alice"
  }'
```

## Design decisions

### Why LangGraph

LangGraph provides explicit control flow, state, checkpoints, interrupts, and resumable execution. Those primitives matter more than a generic chat loop when an agent may recommend or perform operational actions.

### Why SQLite checkpointing

SQLite keeps the local developer experience simple while demonstrating the important production behavior: graph state survives a process restart and an approval can resume from the saved point. In a multi-instance deployment, the same interface can be replaced with a Postgres-backed checkpointer.

### Why approval gates

An agent should be allowed to investigate autonomously, but it should not silently mutate production. Rollback and restart are modeled as high-risk, approval-required tools.

### Why context is budgeted

Adding every log line, tool response, and historical event to the model context does not improve reasoning; it can degrade it. The agent selects evidence, truncates verbose tool output, and retains only operationally relevant context.

### Why deterministic fallback

The core workflow is deterministic so the repository is runnable, testable, and safe to demonstrate without external credentials. Gemini is an enhancement layer, not the authority for whether a production mutation occurs.

## Security boundaries

- Retrieved runbooks and tool output are treated as untrusted context.
- Tool arguments are validated through Pydantic schemas.
- Mutating tools require explicit operator approval.
- Mutating tool calls use idempotency keys.
- Tool-call count is bounded by `MAX_TOOL_CALLS`.
- The event stream records decisions, approvals, executions, and verification results.

## What I would build next

- Replace mock tools with real cloud, Kubernetes, observability, and deployment APIs.
- Add Postgres-backed checkpointing and distributed run execution.
- Add role-based access control and per-tool authorization policies.
- Add LangSmith/Langfuse/OpenTelemetry GenAI tracing.
- Add a golden-set evaluation suite and CI quality gates.
- Add multi-agent supervisor/worker execution for parallel investigation.
- Add memory lifecycle policies, redaction, TTLs, and operator-editable long-term memory.

## Repository structure

```text
app/
  agent/       LangGraph state, nodes, context, graph, and Gemini enrichment
  api/         FastAPI runtime endpoints
  tools/       Tool registry, schemas, policies, and mock platform data
  storage/     Run and event persistence
static/        Operator UI
tests/         Workflow, approval, resume, and safety tests
docs/          Architecture and design documentation
ai_usage/      AI-assisted development log
```
