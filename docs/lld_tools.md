# LLD — Tools and Registry

## Tool contract

Every tool has:

- Name.
- Description.
- Risk level.
- Mutating flag.
- Approval requirement.
- Pydantic input schema.
- Handler function.

## Registered tools

| Tool | Risk | Mutating | Approval | Purpose |
|---|---|---:|---:|---|
| `search_logs` | Low | No | No | Search service logs |
| `query_metrics` | Low | No | No | Query health metrics |
| `get_service_status` | Low | No | No | Check service health |
| `get_deployment_history` | Low | No | No | Correlate recent changes |
| `search_runbooks` | Low | No | No | Retrieve operational guidance |
| `rollback_deployment` | High | Yes | Yes | Roll back a deployment |
| `restart_service` | High | Yes | Yes | Restart a service |

## Execution flow

```text
Agent selects tool
      |
Registry validates arguments
      |
Handler executes
      |
ToolResult returned
```

## Error handling

| Failure | Result |
|---|---|
| Unknown tool | `success=false`, structured error |
| Invalid arguments | `success=false`, validation error |
| Handler exception | `success=false`, retryable where appropriate |
| Missing idempotency key | Mutation rejected |
