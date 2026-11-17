# Interview Preparation

This document helps you explain the Incident Triage & Safe Remediation Agent clearly and confidently in an interview.

## 30-second pitch

> “I built an incident-remediation agent that investigates a service incident, identifies the likely root cause, recommends a safe remediation, and pauses for explicit human approval before executing a production change. It uses LangGraph for a controlled, resumable workflow, FastAPI for the runtime API, React for operator visibility, and SQLite locally for persistence. The key design principle is that the LLM assists diagnosis, but deterministic policy, validation, approval, and verification control execution.”

## Detailed explanation

> “The agent starts with an incident description. It triages the incident, queries metrics, logs, service health, deployment history, and runbooks, then forms a diagnosis. For the checkout-service scenario, it identifies a deployment-related database connection regression and recommends rolling back to the last stable version.
>
> Before executing, the workflow interrupts and asks the operator for approval. If the operator approves, the rollback runs through a validated tool. The agent then queries post-action metrics and service health to verify recovery. If recovery is confirmed, the run completes; otherwise, it escalates.
>
> Every step is recorded in an event trace, so an operator can inspect what the agent observed, which tools it used, why it chose an action, who approved it, what was executed, and whether recovery was verified.”

## Why LangGraph?

> “I chose LangGraph because an incident-remediation agent needs more than a single LLM call. It needs explicit workflow steps, shared state, tool calls, error handling, durable checkpoints, interrupts, and resumability. LangGraph gives me those primitives directly.
>
> A basic LLM loop could generate a response, but it would not naturally provide controlled branching, durable state, or a safe human-in-the-loop boundary. LangGraph lets me model the workflow explicitly: triage, investigate, diagnose, plan, approval, execute, and verify.”

## Why FastAPI?

> “I chose FastAPI because it exposes the agent as a runtime service rather than a script. It provides clean REST endpoints for starting runs, reading state, inspecting events, approving actions, and checking health. It is lightweight, supports async operations, and integrates well with Pydantic validation.”

## Why SQLite locally?

> “I used SQLite so the project runs locally with zero infrastructure setup. There is no need for Postgres, Redis, Docker, or cloud credentials. The repository uses a repository interface, so SQLite can be replaced with Postgres later without changing the agent workflow.”

## Why Gemini?

> “I used Gemini to enrich diagnosis with natural-language reasoning. However, I deliberately did not let it control safety. Gemini can help explain the likely root cause, but the deterministic workflow, approval policy, tool validation, and verification remain authoritative.”

## Why React and TypeScript?

> “The operator needs visibility into what the agent is doing. React provides a component-based UI for incident creation, run monitoring, evidence inspection, approval, and event tracing. TypeScript keeps the frontend API contract explicit and reduces runtime integration errors.”

## Why Pydantic?

> “Pydantic validates API requests and tool arguments. This is especially important for a remediation agent because invalid or unsafe arguments should be rejected before execution.”

## Why Pytest?

> “Pytest lets me test the safety-critical workflow. The tests verify that the agent pauses for approval, executes only approved actions, verifies recovery, and does not execute rejected actions.”

## Architecture explanation

> “The system follows a simplified hexagonal or layered architecture. The React UI and FastAPI form the presentation layer. LangGraph coordinates the agent workflow. The application layer contains policies, ports, and the tool registry. Infrastructure adapters isolate Gemini, SQLite, and the mock platform.
>
> The dependency direction is important: the agent depends on application abstractions, not directly on Gemini, SQLite, or mock tools. That makes the system replaceable and testable.”

## Safety explanation

> “The central safety boundary is that the LLM cannot directly execute a production action. The workflow determines the action, the approval policy decides whether human approval is required, and the approval gate interrupts execution until an operator decides.
>
> If the operator rejects, the run is cancelled and nothing executes. If the operator approves, the action runs through validated tools. After execution, the agent verifies recovery using post-action metrics and service health.”

## Testing explanation

> “I test the safety-critical workflow, not just the LLM output. Integration tests verify that the run reaches approval, approval resumes execution, rollback updates the mock platform, verification detects recovery, and the run completes. I also test rejection: a rejected action must not execute.”

## Trade-offs

| Trade-off | Decision | Why |
|---|---|---|
| Local simplicity versus production scale | SQLite and mock tools | Enables zero-setup local demo |
| LLM usefulness versus safety | Gemini assists, does not execute | Keeps production authority deterministic |
| Autonomy versus control | Human approval gate | Prevents unapproved production changes |
| Speed versus structure | LangGraph | Adds structure but provides checkpoints and interrupts |
| Mock tools versus real integrations | Mock platform | Avoids cloud credentials in assessment |

## Common follow-ups

### What happens if Gemini fails?

> “The workflow falls back to deterministic diagnosis. Gemini is optional and is not a dependency for the approval, execution, or verification path.”

### What happens if the operator rejects?

> “The approval gate records the rejection, cancels the run, and prevents execution. No rollback or other mutating action occurs.”

### What happens if verification fails?

> “The run is marked as escalated rather than completed. In production, this would trigger alerting and human follow-up.”

### How would you scale this?

> “I would move persistence to Postgres, deploy the API and workflow with Kubernetes, use durable workers for long-running workflows, add centralized observability, and integrate real cloud and observability APIs.”

### How would you secure it?

> “I would add authentication, role-based access control, action-specific permissions, secret management, audit logs, and sandboxing for tool execution.”

### Why not fully automate remediation?

> “Because production changes carry risk. The system should recommend and prepare the action, but a human should approve high-risk changes. The approval gate provides controlled autonomy rather than blind automation.”

### What would you improve next?

> “I would add real platform integrations, Postgres persistence, authentication and RBAC, centralized observability, Kubernetes deployment, and more extensive failure-path testing.”
