"""End-to-End API integration tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["warehouse_connected"] is True


def test_catalog_endpoint(client):
    res = client.get("/api/catalog")
    assert res.status_code == 200
    data = res.json()
    assert "entities" in data
    assert "metrics" in data
    assert "dimensions" in data
    assert len(data["metrics"]) >= 5


def test_chat_turn_kerala_churn(client):
    payload = {"query": "Which products lost the most customers in Kerala during Q2?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert not data["is_refusal"]
    assert "Enterprise Suite Pro" in data["evidence_backed_answer"]
    assert len(data["visualizations"]) > 0
    assert len(data["telemetry_events"]) >= 10


def test_chat_turn_prescriptive_and_hitl(client):
    # Ask prescriptive question triggering HITL review packet
    payload = {"query": "What should we do?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["review_packet"] is not None
    packet_id = data["review_packet"]["packet_id"]

    # Submit HITL Approval
    decision_payload = {
        "packet_id": packet_id,
        "decision": "APPROVED",
        "comments": "Approved via automated API test",
    }
    decision_res = client.post("/api/hitl/decision", json=decision_payload)
    assert decision_res.status_code == 200
    updated_packet = decision_res.json()
    assert updated_packet["status"] == "APPROVED"


def test_benchmark_api_endpoint(client):
    res = client.get("/api/eval/benchmark")
    assert res.status_code == 200
    data = res.json()
    assert data["overall_pass"] is True
    assert data["successful_scenarios"] == 4
