# Guardrails

Guardrails are the controls that keep the agent useful without giving it unchecked authority.

This project implements guardrails at multiple layers: HTTP middleware, agent workflow policy, tool execution, and verification.

## Guardrail philosophy

The agent is designed for controlled autonomy:

```text
LLM assists reasoning
Deterministic workflow controls execution
Approval policy requires human consent
Tool validation protects arguments
Verification confirms recovery
```

A guardrail is not only a middleware filter. It is any control that prevents unsafe, invalid, excessive, or unapproved behavior.

## API middleware guardrails

These guardrails run at the FastAPI boundary before or around application handlers.

| Middleware | Guardrail | Behavior |
|---|---|---|
| `RequestIDMiddleware` | Traceability | Assigns or preserves `x-request-id` |
| `SecurityHeadersMiddleware` | Browser and transport safety | Adds baseline security headers |
| `PayloadSizeLimitMiddleware` | Abuse prevention | Rejects oversized request bodies with HTTP 413 |
| `RateLimitMiddleware` | Abuse prevention | Limits each client to 30 requests per 60 seconds; returns HTTP 429 |
| `ErrorHandlingMiddleware` | Failure containment | Converts unexpected errors into a structured HTTP 500 response |

These middleware components are registered by `add_guardrails(app)` in `src/incident_agent/api/main.py`.

## Agent workflow guardrails

The LangGraph workflow itself is a guardrail because it prevents free-form LLM execution.

```text
Triage
→ Investigate
→ Diagnose
→ Plan
→ Approval gate
→ Execute
→ Verify
```

Key controls:

- The workflow has explicit nodes and transitions.
- The LLM cannot directly execute a production action.
- Mutating actions require approval.
- Rejection cancels the run and prevents execution.
- Execution is followed by verification.
- Failed verification escalates rather than silently declaring success.

## Human approval guardrail

The approval gate is the most important production-safety boundary.

```text
Agent proposes rollback
→ Workflow interrupts
→ Operator reviews evidence and action
→ Operator approves or rejects
→ Only approval allows execution
```

The approval decision is recorded in the event trace, including the operator identity and reason.

## Tool execution guardrails

Tools are not arbitrary functions exposed directly to the LLM.

They are controlled through:

- A tool registry with metadata.
- Argument validation.
- Risk classification.
- Approval requirements.
- Idempotency keys for mutating actions.
- Retry policy for transient failures.
- Structured execution results.

This prevents the agent from invoking an unknown or unsafe operation.

## Data and prompt guardrails

The agent limits what enters the model context:

- Evidence is summarized rather than sending raw logs.
- Context has a token budget.
- Tool results are structured.
- The diagnosis strategy separates deterministic reasoning from LLM enrichment.

This reduces prompt-injection exposure and keeps the agent explainable.

## Verification guardrail

Execution success alone is not treated as incident resolution.

After an approved rollback, the agent checks:

- Post-action error rate.
- Service health.
- Recovery threshold.

Only when both conditions pass does the run become `completed`. Otherwise, it becomes `escalated`.

## Production guardrails

For production, extend these controls with:

- Authentication and operator identity.
- Role-based access control.
- Action-specific permissions.
- Centralized rate limiting.
- Request and audit logging.
- Secret management.
- Tool sandboxing.
- Policy-as-code approval rules.
- OpenTelemetry tracing.
- Alerting for escalation and failed verification.

## Interview-ready explanation

> “I implemented guardrails at multiple layers. At the API boundary, middleware provides request IDs, security headers, payload limits, rate limiting, and structured error handling. At the agent layer, LangGraph provides an explicit workflow, approval policy, human-in-the-loop approval, and post-action verification. At the tool layer, the registry validates arguments, classifies risk, requires approval for mutating actions, and uses idempotency keys. The key principle is that the LLM can assist reasoning, but it cannot bypass the deterministic safety controls.”
