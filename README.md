# Incident Triage & Safe Remediation Agent

An end-to-end incident-response agent that investigates a service incident, identifies the likely root cause, recommends a safe remediation, pauses for operator approval, executes only approved actions, and verifies recovery.

It is designed to demonstrate production-minded agent engineering: controlled autonomy, human-in-the-loop safety, inspectable decision trails, durable workflow state, and replaceable infrastructure.

## What it does

Given an incident such as:

> “Checkout service is returning 5xx errors after the latest deployment.”

The agent:

1. Classifies the incident.
2. Queries metrics, logs, service health, deployment history, and runbooks.
3. Diagnoses the likely root cause.
4. Recommends a remediation action.
5. Requires operator approval before executing a production change.
6. Executes the approved action.
7. Verifies that the service recovered.
8. Produces a complete event trace for auditability.

## Safety model

The agent does not blindly execute LLM output.

```text
LLM assists diagnosis
Deterministic workflow controls execution
Approval policy requires human consent
Tool validation protects arguments
Verification confirms recovery
```

For the default checkout-service scenario, the agent identifies a deployment-related database connection regression and recommends rolling back from `v2.19.0` to `v2.18.3`.

The action is marked as requiring approval. Until an operator approves it, no rollback is executed.

## Local prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- Git
- Optional: Gemini API key

The project runs locally without a database server, Docker, Kubernetes, or cloud credentials.

## Clone and run backend

```bash
git clone https://github.com/Zulfiqar78634/incident-triage-agent-langgraph.git
cd incident-triage-agent-langgraph

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn incident_agent.api.main:app --app-dir src --reload --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

## Optional Gemini setup

Gemini is optional. Without an API key, the agent uses deterministic diagnosis and remains fully functional.

To enable Gemini enrichment:

```bash
export GEMINI_API_KEY="your_api_key"
```

Then restart the backend.

The LLM is used only to improve diagnosis reasoning. It does not directly execute production actions.

## Run frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## End-to-end demo

1. Start the backend and frontend.
2. Open the operator UI.
3. Create an incident for `checkout-service`.
4. Use this example:

```text
Title: Checkout service 5xx spike
Description: Checkout is returning 5xx errors after the latest deployment.
Service: checkout-service
Environment: production
Severity: high
```

5. Start the run.
6. Observe the agent:

```text
Triage
→ Investigate
→ Diagnose
→ Plan
→ Awaiting approval
```

7. Review the evidence, diagnosis, and proposed rollback.
8. Approve the action.
9. Observe:

```text
Rollback executes
→ Metrics recover
→ Service becomes healthy
→ Verification succeeds
→ Run completes
```

10. Open the event trace to inspect every decision and tool result.

## API reference

### Health check

```bash
curl http://localhost:8000/api/health
```

### Create incident run

```bash
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Checkout service 5xx spike",
    "description": "Checkout is returning 5xx errors after the latest deployment.",
    "service": "checkout-service",
    "environment": "production",
    "severity": "high",
    "operator_id": "operator"
  }'
```

### Get run state

```bash
curl http://localhost:8000/api/runs/{run_id}
```

### Get event trace

```bash
curl http://localhost:8000/api/runs/{run_id}/events
```

### Approve remediation

```bash
curl -X POST http://localhost:8000/api/runs/{run_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approved",
    "reason": "Deployment correlation and DB saturation support rollback.",
    "operator_id": "operator"
  }'
```

### Reject remediation

```bash
curl -X POST http://localhost:8000/api/runs/{run_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "rejected",
    "reason": "Do not execute this action.",
    "operator_id": "operator"
  }'
```

## Run tests

```bash
pytest -q
```

Tests cover:

- API health.
- Incident creation.
- Approval interruption.
- Approved rollback execution.
- Post-action verification.
- Rejection safety.

## Architecture

```text
React operator UI
        |
FastAPI interface
        |
LangGraph agent runtime
        |
Application policies, ports, tool registry
        |
Infrastructure adapters
```

Core components:

- **LangGraph workflow:** explicit incident lifecycle and durable state.
- **FastAPI:** runtime API for runs, events, approvals, and health.
- **SQLite:** local persistence for checkpoints, run state, and events.
- **Mock platform:** logs, metrics, deployments, service health, and remediation APIs.
- **Gemini adapter:** optional diagnosis enrichment.
- **Approval policy:** human-in-the-loop safety boundary.
- **Tool registry:** validated tool metadata and execution.
- **React UI:** operator visibility and approval workflow.

## Technology decisions

| Decision | Reason |
|---|---|
| Python | Strong AI/backend ecosystem and readable agent logic |
| FastAPI | Clean, lightweight runtime API |
| LangGraph | Explicit workflow, interrupts, checkpoints, and resumable execution |
| SQLite | Zero-setup local persistence |
| Gemini | Natural-language diagnosis enrichment |
| React | Operator-friendly UI |
| TypeScript | Type-safe frontend integration |
| Vite | Fast local frontend development |
| Pydantic | Strict validation of API and tool inputs |
| Pytest | Reliable workflow and safety tests |

See `docs/technology_decisions.md` for the full decision record.

## Interview explanation

> “I built an incident-remediation agent that investigates an incident, forms a diagnosis, recommends a remediation, and pauses for explicit human approval before executing a production change. I used LangGraph because the workflow needs durable state, controlled branching, interrupts, and resumability. I used FastAPI to expose the agent as a runtime service. I used SQLite locally so the project runs without infrastructure setup, while keeping persistence behind a repository interface so Postgres can replace it later. Gemini enriches diagnosis, but it does not control safety: deterministic policy, validation, approval, and verification remain authoritative.”

## Troubleshooting

### Backend will not start

Ensure you are in the repository root and have activated the virtual environment:

```bash
source .venv/bin/activate
uvicorn incident_agent.api.main:app --app-dir src --reload --port 8000
```

### Frontend cannot reach backend

Confirm the backend is running on port 8000.

### Gemini is unavailable

The system still works with deterministic diagnosis. Gemini is optional.

### Tests fail

Run:

```bash
pip install -r requirements.txt
pytest -q
```

Ensure no other process is using port 8000.
