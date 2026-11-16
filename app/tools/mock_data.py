"""Mock enterprise platform data used by the agent tools.

This keeps the assessment project self-contained: no cloud credentials or
external systems are required to demonstrate the agent workflow.
"""

from __future__ import annotations

LOGS = [
    {
        "timestamp": "2026-11-17T00:52:10Z",
        "service": "checkout-service",
        "level": "ERROR",
        "message": "Database connection timeout after 5000ms; active_connections=98/100",
        "correlation_id": "req_8842",
    },
    {
        "timestamp": "2026-11-17T00:52:18Z",
        "service": "checkout-service",
        "level": "ERROR",
        "message": "HTTP 503 while calling payment-provider; retry_count=3",
        "correlation_id": "req_8843",
    },
    {
        "timestamp": "2026-11-17T00:52:31Z",
        "service": "checkout-service",
        "level": "ERROR",
        "message": "Database connection timeout after 5000ms; active_connections=100/100",
        "correlation_id": "req_8844",
    },
    {
        "timestamp": "2026-11-17T00:41:02Z",
        "service": "checkout-service",
        "level": "INFO",
        "message": "Deployment deploy-184 completed; version v2.18.4",
        "correlation_id": "deploy_184",
    },
]

METRICS = {
    "checkout-service": {
        "error_rate_percent": 18.4,
        "p99_latency_ms": 2740,
        "cpu_utilization_percent": 61,
        "memory_utilization_percent": 72,
        "database_connections": 100,
        "database_connection_limit": 100,
    }
}

SERVICE_STATUS = {
    "checkout-service": {
        "status": "degraded",
        "healthy_replicas": 2,
        "total_replicas": 4,
        "dependencies": {
            "payment-provider": "healthy",
            "inventory-service": "healthy",
            "postgres-primary": "degraded",
        },
    }
}

DEPLOYMENTS = {
    "checkout-service": [
        {
            "deployment_id": "deploy-184",
            "version": "v2.18.4",
            "deployed_at": "2026-11-17T00:41:02Z",
            "status": "active",
            "change_summary": "Increased database pool size and changed retry policy",
        },
        {
            "deployment_id": "deploy-183",
            "version": "v2.18.3",
            "deployed_at": "2026-11-16T18:12:44Z",
            "status": "previous",
            "change_summary": "Stable release; no known database connection issues",
        },
    ]
}

RUNBOOKS = [
    {
        "id": "rb_checkout_5xx",
        "title": "Checkout service 5xx response runbook",
        "service": "checkout-service",
        "content": (
            "If 5xx errors begin immediately after a deployment and database connection "
            "saturation is observed, correlate the release with the incident. If the previous "
            "version was stable, rollback is the preferred low-risk recovery action. "
            "Rollback requires operator approval in production."
        ),
    },
    {
        "id": "rb_db_pool",
        "title": "Database connection pool saturation",
        "service": "checkout-service",
        "content": (
            "Database connection saturation can be caused by a connection leak, increased "
            "traffic, or a deployment changing pool configuration. Confirm metrics and recent "
            "changes before restarting or scaling the service."
        ),
    },
]

INCIDENT_HISTORY = [
    {
        "incident_id": "INC-2291",
        "service": "checkout-service",
        "summary": "5xx spike after database pool configuration change",
        "resolution": "Rolled back to previous stable version; error rate recovered within 4 minutes.",
    }
]
