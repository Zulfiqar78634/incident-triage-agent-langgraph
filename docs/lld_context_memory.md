# LLD — Context and Memory

## Context layers

```text
System policy
Incident objective
Current diagnosis and plan
Selected evidence
Recent tool calls
Long-term memory
```

## Budgeting

The context budget is configurable through:

```env
CONTEXT_TOKEN_BUDGET=6000
```

Evidence receives 45% of the total budget.

## Compaction rules

| Data | Rule |
|---|---|
| System policy | Always retained |
| Current objective | Always retained |
| Diagnosis and plan | Always retained |
| Evidence | Selected within budget |
| Tool output | Summarized or truncated |
| Conversation | Recent turns retained |
| Long-term memory | Relevant facts only |

## Memory promotion

Facts are promoted to long-term memory only when they are durable and useful, such as:

- Confirmed root cause.
- Approved remediation.
- Service ownership.
- Recurring failure pattern.

Raw chat messages, sensitive data, and transient tool output are not promoted.
