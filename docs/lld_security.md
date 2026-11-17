# LLD — Security and Guardrails

## Trust boundaries

```text
Untrusted inputs
├── Operator incident description
├── Retrieved runbooks
└── Tool outputs
```

These are treated as data, not instructions that can override system policy.

## Guardrails

| Guardrail | Implementation |
|---|---|
| Tool argument validation | Pydantic schemas |
| Approval for mutations | LangGraph interrupt |
| Production protection | Approval policy |
| Idempotency | Required for mutating tools |
| Bounded tool calls | `MAX_TOOL_CALLS` |
| Bounded retries | `RetryPolicy` |
| Auditability | Persistent event stream |

## Prompt-injection defense

Retrieved documents and tool outputs are included as context, but they cannot:

- Change system policy.
- Approve an action.
- Bypass the approval gate.
- Execute a tool directly.

## Future production controls

- Authentication and RBAC.
- Per-tool authorization policies.
- Sandboxed tool execution.
- Secret redaction.
- Immutable audit export.
- Rate limiting.
