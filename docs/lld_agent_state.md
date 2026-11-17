# LLD — Agent State

## State fields

```python
class AgentState(TypedDict, total=False):
    run_id: str
    thread_id: str
    incident: dict
    classification: dict
    evidence: list
    tool_calls: list
    diagnosis: dict
    plan: dict
    pending_action: dict | None
    approval: dict | None
    execution: dict | None
    verification: dict | None
    status: str
    events: list
    context_usage: dict
    retry_count: int
```

## Reducers

`tool_calls` and `events` use an append reducer:

```python
def append_list(current, update):
    return (current or []) + (update or [])
```

This prevents later workflow steps from overwriting earlier history.

## Checkpoint behavior

LangGraph persists the graph state at super-step boundaries. When the approval gate interrupts, the state is saved and can be resumed after a process restart.

## Resume rules

| Scenario | Behavior |
|---|---|
| Operator approves | Graph resumes from approval gate |
| Operator rejects | Graph marks run cancelled; no execution occurs |
| Backend restarts | Checkpoint restores workflow state |
| Tool fails | Bounded retry, then visible failure or escalation |
