# Roadmap

This document separates what is implemented today from what would be required for a production deployment.

It is important for interview clarity: the project demonstrates a complete, locally runnable agent workflow, while honestly identifying the enterprise components that would be added in a real deployment.

## Implemented today

The repository includes:

- A LangGraph incident workflow.
- Triage, investigation, diagnosis, planning, approval, execution, and verification nodes.
- FastAPI runtime endpoints.
- React operator UI.
- SQLite-backed run state, events, and checkpoints.
- Mock platform tools for logs, metrics, deployments, service health, and remediation.
- Optional Gemini diagnosis enrichment.
- Approval policy and human-in-the-loop gate.
- Tool registry and validated tool execution.
- Retry policy.
- Event trace for auditability.
- Integration tests for approval, rejection, execution, and recovery verification.

## Intentionally local or mocked

These components are intentionally simplified so the assessment can run locally without cloud credentials or infrastructure:

| Component | Current implementation | Why |
|---|---|---|
| Platform tools | Mock platform | Demonstrates workflow without requiring cloud access |
| Persistence | SQLite | Zero-setup local persistence |
| LLM | Gemini adapter | Accessible diagnosis enrichment |
| Deployment | Local FastAPI process | Simple local demonstration |
| Observability | SQLite event stream | Basic inspectability without extra infrastructure |
| Authentication | Not implemented | Assessment focuses on agent workflow and safety model |

## Production roadmap

### Real platform integration

Replace mock tools with real integrations:

- Cloud monitoring APIs.
- Log search platforms.
- Kubernetes or cloud deployment APIs.
- Incident-management systems.
- Runbook and knowledge-base systems.

### Durable persistence

Replace SQLite with Postgres.

Add:

- Database migrations.
- Connection pooling.
- Backup and recovery procedures.
- Retention policies for events and audit data.

### Security and authorization

Add:

- Operator authentication.
- Role-based access control.
- Action-specific permissions.
- Approval audit records.
- Secret management.
- Sandbox boundaries for tool execution.

### Observability

Add:

- Structured logs.
- Metrics.
- Distributed tracing.
- OpenTelemetry instrumentation.
- LangSmith or Langfuse integration.
- Alerting for failed runs and escalated incidents.

### Deployment

Add:

- Docker images.
- Kubernetes manifests.
- Health and readiness probes.
- Horizontal scaling.
- Configuration management.
- CI/CD pipeline.

### Durable workflow operations

Add:

- Separate workflow workers.
- Durable execution infrastructure.
- Retry and dead-letter handling.
- Run recovery across process restarts.
- Multi-instance-safe persistence.

### Multi-agent orchestration

For larger incidents, extend the system with specialized agents:

- Investigation agent.
- Diagnosis agent.
- Remediation planner.
- Safety reviewer.
- Verification agent.

A supervisor would coordinate these agents while preserving the approval and verification boundaries.

## What not to claim

This project does not claim to include:

- Kubernetes deployment.
- Real cloud credentials.
- Kafka or external message queues.
- Postgres migrations.
- Full production observability.
- Multi-agent supervisor/worker execution.
- Complete enterprise RBAC.

These are roadmap items, not implemented features.

## Interview-ready explanation

> “The current implementation demonstrates the complete agent workflow locally: investigation, diagnosis, planning, approval, execution, and verification. I intentionally used SQLite and mock platform tools so the project runs without cloud infrastructure. For production, I would replace the mock tools with real cloud and observability integrations, move persistence to Postgres, add authentication and RBAC, deploy with Kubernetes, and add centralized observability. The core safety architecture—approval, validation, execution, and verification—would remain the same.”
