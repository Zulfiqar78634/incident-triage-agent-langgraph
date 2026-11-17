# LLD — Scaling and Enterprise Roadmap

## Current implementation

```text
Single FastAPI service
Single LangGraph workflow
SQLite checkpointing
Mock platform tools
Local operator UI
```

## Enterprise target

```mermaid
flowchart TD
    UI[Operator Console] --> GW[API Gateway]
    GW --> ORCH[Agent Orchestration Service]
    ORCH --> SUP[Supervisor Agent]
    SUP --> W1[Investigation Worker]
    SUP --> W2[Diagnosis Worker]
    SUP --> W3[Remediation Worker]
    W1 --> TG[Tool Gateway]
    W2 --> MEM[Memory Store]
    W3 --> OBS[Observability Stack]
    TG --> CLOUD[Cloud / Kubernetes / CI-CD]
```

## Scaling decisions

| Concern | Current | Enterprise target |
|---|---|---|
| Persistence | SQLite | Postgres |
| Workflow execution | Single process | Durable workers and queues |
| Tool execution | In-process mock tools | Sandboxed tool gateway |
| Retrieval | Simple runbook search | Vector database with reranking |
| Observability | SQLite event stream | OpenTelemetry, LangSmith, or Langfuse |
| Security | Approval gate | Auth, RBAC, policy engine, audit export |
| Deployment | Local process | Kubernetes with horizontal scaling |

## Rollout plan

1. Replace mock tools with real read-only integrations.
2. Move checkpointing to Postgres.
3. Add authentication, RBAC, and audit logging.
4. Add tool gateway with sandboxing and policy enforcement.
5. Add vector retrieval and evaluation harness.
6. Add supervisor/worker execution for parallel investigation.
7. Deploy to Kubernetes with observability and alerting.
