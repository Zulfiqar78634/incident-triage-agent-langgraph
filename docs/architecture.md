# Architecture

The Incident Triage & Safe Remediation Agent is a controlled, observable, human-in-the-loop agent system.

It investigates incidents, forms a diagnosis, recommends remediation, waits for approval, executes approved actions, and verifies recovery.

## High-level architecture

```text
+-------------------+
| React Operator UI |
+---------+---------+
          |
          v
+-------------------+
|    FastAPI API    |
+---------+---------+
          |
          v
+---------------------------+
|   LangGraph Agent Runtime |
+---------+-----------------+
          |
          v
+-----------------------------------+
| Application policies and ports    |
+---------+-------------------------+
          |
          v
+-----------------------------------+
| Infrastructure adapters           |
| Mock platform | Gemini | SQLite   |
+-----------------------------------+
```

## End-to-end flow

```text
Operator creates incident
        |
        v
FastAPI creates run
        |
        v
LangGraph starts workflow
        |
        v
Triage classifies incident
        |
        v
Investigate collects evidence
        |
        v
Diagnose identifies likely root cause
        |
        v
Plan recommends remediation
        |
        v
Approval gate interrupts workflow
        |
        +--> Operator rejects --> Run cancelled
        |
        +--> Operator approves
                    |
                    v
              Execute approved action
                    |
                    v
              Verify recovery
                    |
          +---------+---------+
          |                   |
          v                   v
      Completed           Escalated
```

## LangGraph workflow

```text
START
  |
  v
triage
  |
  v
investigate
  |
  v
diagnose
  |
  v
plan
  |
  v
approval_gate
  |
  +--> rejected --> END
  |
  +--> approved
          |
          v
       execute
          |
          v
       verify
          |
          v
        END
```

## Component responsibilities

| Component | Responsibility |
|---|---|
| React UI | Incident creation, run monitoring, approval, and trace inspection |
| FastAPI | HTTP interface, request validation, run lifecycle, and approval endpoints |
| LangGraph | Explicit workflow, shared state, interrupts, checkpoints, and resumability |
| Triage node | Classifies service, severity, environment, and incident type |
| Investigate node | Calls read-only tools and collects evidence |
| Diagnose node | Produces root-cause reasoning using deterministic or Gemini strategy |
| Plan node | Selects remediation and determines approval requirements |
| Approval gate | Stops execution until an operator makes an explicit decision |
| Execute node | Runs only the approved action through validated tools |
| Verify node | Checks post-action metrics and service health |
| Tool registry | Central tool metadata, validation, and execution |
| Approval policy | Decides when human approval is required |
| Retry policy | Controls safe retry behavior |
| SQLite repository | Persists run state, events, and checkpoints locally |
| Mock platform | Simulates logs, metrics, deployments, health, and remediation APIs |
| Gemini adapter | Optional LLM diagnosis enrichment |

## Data and event flow

Every meaningful agent decision is recorded as an event.

```text
Incident input
  -> classification
  -> tool calls
  -> evidence
  -> diagnosis
  -> plan
  -> approval decision
  -> execution result
  -> verification result
  -> final run status
```

The event trace gives an operator a complete audit trail:

- What the agent observed.
- Which tools it called.
- What evidence it used.
- Why it chose an action.
- Who approved it.
- What was executed.
- Whether recovery was verified.

## Safety boundaries

The system separates model reasoning from production authority.

```text
Gemini proposes reasoning
Deterministic workflow controls execution
Approval policy requires human consent
Tool validation protects arguments
Verification confirms recovery
```

Key safety rules:

- The LLM cannot directly execute a production action.
- Mutating actions require explicit operator approval.
- Tool arguments are validated before execution.
- Rejection prevents execution.
- Execution is followed by verification.
- Failed verification escalates rather than silently declaring success.

## Local implementation

The local implementation is intentionally simple to run:

```bash
pip install -r requirements.txt
uvicorn incident_agent.api.main:app --app-dir src --reload --port 8000
```

It uses:

- SQLite for persistence.
- Mock platform tools for safe demonstration.
- Optional Gemini for diagnosis enrichment.
- React for operator visibility.

## Production target

| Area | Local implementation | Production target |
|---|---|---|
| Persistence | SQLite | Postgres |
| Tools | Mock platform | Real cloud, Kubernetes, and observability APIs |
| LLM | Gemini adapter | Provider-agnostic LLM gateway |
| Workflow | Single LangGraph process | Durable orchestration and workers |
| Security | Approval gate and validation | Authentication, RBAC, sandboxing, audit export |
| Observability | SQLite event stream | OpenTelemetry, LangSmith, or Langfuse |
| Deployment | Local process | Kubernetes |

## Interview-ready explanation

> “The system follows a controlled agent architecture. The React UI and FastAPI expose the workflow to operators. LangGraph coordinates triage, investigation, diagnosis, planning, approval, execution, and verification. The application layer contains policies, ports, and the tool registry. Infrastructure adapters isolate Gemini, SQLite, and the mock platform. The key safety boundary is that the LLM can assist diagnosis, but it cannot execute a production action. A deterministic approval policy and human approval gate control execution, and verification determines whether the incident is resolved.”
