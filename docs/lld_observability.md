# LLD — Observability

## Event types

```text
run_started
node_entered
node_completed
tool_call_started
tool_call_completed
tool_call_failed
tool_call_retried
approval_requested
approval_granted
approval_rejected
action_executed
verification_completed
run_completed
run_failed
escalated
```

## Trace fields

| Field | Purpose |
|---|---|
| `run_id` | Identifies the incident run |
| `node` | LangGraph node that produced the event |
| `event` | Event type |
| `message` | Human-readable explanation |
| `data` | Structured event details |
| `created_at` | UTC timestamp |

## Operator visibility

The UI exposes:

- Current workflow step.
- Agent reasoning.
- Evidence IDs and sources.
- Tool-call status and latency.
- Approval request and decision.
- Execution result.
- Verification result.
- Complete chronological event trace.
