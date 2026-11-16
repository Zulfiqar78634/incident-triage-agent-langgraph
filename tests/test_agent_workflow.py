import os
import tempfile

# Configure an isolated database before the application modules are imported.
_tmp_dir = tempfile.mkdtemp(prefix="incident-agent-test-")
os.environ["AGENT_DB_PATH"] = os.path.join(_tmp_dir, "test_agent.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def incident_run(client):
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
    return response.json()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_tools_are_listed_with_risk_metadata(client):
    response = client.get("/api/tools")
    assert response.status_code == 200

    tools = response.json()["tools"]
    assert {tool["name"] for tool in tools} >= {
        "search_logs",
        "query_metrics",
        "rollback_deployment",
    }

    rollback = next(tool for tool in tools if tool["name"] == "rollback_deployment")
    assert rollback["risk"] == "high"
    assert rollback["requires_approval"] is True


def test_agent_pauses_for_approval_before_rollback(client, incident_run):
    assert incident_run["status"] == "awaiting_approval"
    assert incident_run["pending_action"]["action"] == "rollback_deployment"
    assert incident_run["plan"]["requires_approval"] is True

    events = incident_run["events"]
    assert any(event["event"] == "classification_completed" for event in events)
    assert any(event["event"] == "investigation_completed" for event in events)
    assert any(event["event"] == "plan_created" for event in events)


def test_approval_resumes_and_verifies_recovery(client, incident_run):
    run_id = incident_run["run_id"]

    response = client.post(
        f"/api/runs/{run_id}/approve",
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


def test_rejection_does_not_execute_action(client):
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
    run = response.json()

    response = client.post(
        f"/api/runs/{run['run_id']}/approve",
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
