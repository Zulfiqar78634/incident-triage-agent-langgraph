import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from incident_agent.api.main import app
from incident_agent.api.middleware import RateLimitMiddleware


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_returns_security_headers_and_request_id(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"].startswith("req_")


def test_request_id_is_preserved(client):
    response = client.get("/api/health", headers={"x-request-id": "test-request-id"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request-id"


def test_oversized_payload_is_rejected(client):
    response = client.post(
        "/api/runs",
        json={
            "title": "x" * 200_000,
            "description": "Checkout is returning 5xx errors after the latest deployment.",
            "service": "checkout-service",
            "environment": "production",
            "severity": "high",
            "operator_id": "test-operator",
        },
    )

    assert response.status_code == 413
    assert "payload" in response.json()["detail"].lower()


def test_rate_limit_returns_429():
    limited_app = FastAPI()
    limited_app.add_middleware(RateLimitMiddleware, max_requests=3, window_seconds=60)

    @limited_app.get("/ping")
    async def ping():
        return {"status": "ok"}

    with TestClient(limited_app) as limited_client:
        for _ in range(3):
            assert limited_client.get("/ping").status_code == 200

        response = limited_client.get("/ping")

    assert response.status_code == 429
    assert "too many requests" in response.json()["detail"].lower()
