import pytest
from fastapi.testclient import TestClient

from incident_agent.api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agent_pauses_for_approval(client):
    response = client.post(
        "/api/runs",
        json={
            "title": "Checkout service 5xx spike",
            "description": "Checkout is returning 5xx errors after the latest deployment.",
            "service": "checkout-service",
            "environment": "production",
            "severity": "high",
            "operator_id": "test-operator",
        },
    )

    assert response.status_code == 200
    run = response.json()

    assert run["status"] == "awaiting_approval"
    assert run["pending_action"]["action"] == "rollback_deployment"
    assert run["plan"]["requires_approval"] is True


def test_approval_completes_and_verifies_recovery(client):
    created = client.post(
        "/api/runs",
        json={
            "title": "Checkout service 5xx spike",
            "description": "Checkout is returning 5xx errors after the latest deployment.",
            "service": "checkout-service",
            "environment": "production",
            "severity": "high",
            "operator_id": "test-operator",
        },
    ).json()

    response = client.post(
        f"/api/runs/{created['run_id']}/approve",
        json={
            "decision": "approved",
            "reason": "Deployment correlation and DB saturation support rollback.",
            "operator_id": "test-operator",
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "completed"
    assert result["approval"]["decision"] == "approved"
    assert result["execution"]["success"] is True
    assert result["verification"]["recovered"] is True


def test_rejection_does_not_execute(client):
    created = client.post(
        "/api/runs",
        json={
            "title": "Checkout service 5xx spike",
            "description": "Checkout is returning 5xx errors after the latest deployment.",
            "service": "checkout-service",
            "environment": "production",
            "severity": "high",
            "operator_id": "test-operator",
        },
    ).json()

    response = client.post(
        f"/api/runs/{created['run_id']}/approve",
        json={
            "decision": "rejected",
            "reason": "Do not execute this action.",
            "operator_id": "test-operator",
        },
    )

    assert response.status_code == 200
    result = response.json()

    assert result["status"] == "cancelled"
    assert result["approval"]["decision"] == "rejected"
    assert result["execution"] is None
