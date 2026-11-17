# LLD — API Contract

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/runs` | Start an incident run |
| `GET` | `/api/runs/{run_id}` | Get run state and trace |
| `GET` | `/api/runs/{run_id}/events` | Get event stream |
| `POST` | `/api/runs/{run_id}/approve` | Approve or reject action |
| `GET` | `/api/tools` | List tool catalog |
| `GET` | `/api/health` | Health check |

## Start run

```http
POST /api/runs
```

```json
{
  "title": "Checkout service 5xx spike",
  "description": "Checkout is returning 5xx errors after the latest deployment.",
  "service": "checkout-service",
  "environment": "production",
  "severity": "high",
  "operator_id": "ops-alice"
}
```

## Approval

```http
POST /api/runs/{run_id}/approve
```

```json
{
  "decision": "approved",
  "reason": "Evidence supports rollback.",
  "operator_id": "ops-alice"
}
```

## Status codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 404 | Run not found |
| 409 | Run is not awaiting approval |
| 422 | Invalid request payload |
