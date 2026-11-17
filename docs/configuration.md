# Configuration

This project is designed to run locally with minimal configuration.

By default, it uses:

- SQLite for local persistence.
- A mock platform for logs, metrics, deployments, service health, and remediation actions.
- Deterministic diagnosis when Gemini is not configured.

## Setup

```bash
cp .env.example .env
```

You do not need to add any secrets to run the local demo.

## Optional Gemini configuration

To enable Gemini-backed diagnosis enrichment:

```bash
export GEMINI_API_KEY="your_api_key"
```

Or add it to your local `.env` file:

```text
GEMINI_API_KEY=your_api_key
```

Gemini is optional. The workflow, approval gate, rollback execution, verification, and event trace work without it.

## Configuration values

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `GEMINI_API_KEY` | No | Empty | Enables Gemini diagnosis enrichment |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model used by the adapter |
| `APP_ENV` | No | `local` | Runtime environment label |
| `LOG_LEVEL` | No | `INFO` | Application logging level |

## Security practices

- Never commit `.env`.
- Never commit real API keys.
- Use `.env.example` only for non-secret placeholders.
- Rotate any credential that has been exposed.
- In production, load secrets from a managed secret store rather than local files.

## Production direction

For a production deployment, replace local defaults with:

- Postgres for durable persistence.
- A managed secret store for credentials.
- Real observability and cloud platform integrations.
- Authenticated operator access and role-based authorization.
- Centralized logging, metrics, and tracing.
