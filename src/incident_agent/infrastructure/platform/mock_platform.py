"""Mock platform adapter implementing the PlatformClient port."""

from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any

from incident_agent.infrastructure.platform.fixtures import (
    DEPLOYMENTS,
    LOGS,
    METRICS,
    RUNBOOKS,
    SERVICE_STATUS,
)


class MockPlatform:
    """In-memory stand-in for logs, metrics, deployments, and remediation APIs."""

    def __init__(self) -> None:
        self._metrics = deepcopy(METRICS)
        self._status = deepcopy(SERVICE_STATUS)

    def search_logs(self, service: str, query: str = "", limit: int = 10) -> dict[str, Any]:
        matches = [
            log
            for log in LOGS
            if log["service"] == service
            and (not query or query.lower() in log["message"].lower())
        ][:limit]
        return {"logs": matches, "matched_count": len(matches)}

    def query_metrics(self, service: str, window_minutes: int = 15) -> dict[str, Any]:
        return {
            "service": service,
            "window_minutes": window_minutes,
            **self._metrics.get(service, {}),
        }

    def get_service_status(self, service: str) -> dict[str, Any]:
        return self._status.get(service, {"status": "unknown", "dependencies": {}})

    def get_deployment_history(self, service: str, limit: int = 5) -> dict[str, Any]:
        return {
            "service": service,
            "deployments": DEPLOYMENTS.get(service, [])[:limit],
        }

    def search_runbooks(self, query: str) -> dict[str, Any]:
        terms = query.lower().split()
        scored = []
        for runbook in RUNBOOKS:
            text = f"{runbook['title']} {runbook['content']}".lower()
            score = sum(term in text for term in terms)
            if score:
                scored.append((score, runbook))
        scored.sort(reverse=True, key=lambda item: item[0])
        return {"runbooks": [item[1] for item in scored[:3]]}

    def rollback_deployment(self, service: str, to_version: str, idempotency_key: str) -> dict[str, Any]:
        if not idempotency_key:
            return {
                "success": False,
                "error": "idempotency_key is required",
                "retryable": False,
            }

        if service == "checkout-service":
            self._metrics[service].update(
                {
                    "error_rate_percent": 0.3,
                    "p99_latency_ms": 420,
                    "database_connections": 42,
                }
            )
            self._status[service].update(
                {
                    "status": "healthy",
                    "healthy_replicas": 4,
                }
            )
            self._status[service]["dependencies"]["postgres-primary"] = "healthy"

        return {
            "success": True,
            "service": service,
            "rolled_back_to": to_version,
            "idempotency_key": idempotency_key,
            "message": "Rollback completed; service recovered.",
        }

    def restart_service(self, service: str, idempotency_key: str) -> dict[str, Any]:
        if not idempotency_key:
            return {
                "success": False,
                "error": "idempotency_key is required",
                "retryable": False,
            }

        if service in self._metrics:
            self._metrics[service]["error_rate_percent"] = 0.8
        if service in self._status:
            self._status[service]["status"] = "healthy"

        return {
            "success": True,
            "service": service,
            "idempotency_key": idempotency_key,
            "message": "Service restart completed.",
        }

    def new_idempotency_key(self, prefix: str = "action") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:16]}"
