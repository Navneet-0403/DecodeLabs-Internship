import pytest

def test_simulator_safe_request(client):
    response = client.post("/api/simulations", json={"scenario_index": 0})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_title"] == "Safe request"
    assert data["decision"] == "Allowed"
    assert len(data["stages"]) == 9

def test_simulator_override_blocked(client):
    response = client.post("/api/simulations", json={"scenario_index": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_title"] == "Instruction override"
    assert data["decision"] == "Blocked"
    assert "Instruction override" in data["detected_indicators"]

def test_simulator_external_email_approval(client):
    response = client.post("/api/simulations", json={"scenario_index": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "Approval required"
    assert data["approval_created"] is not None

def test_simulator_invalid_index(client):
    response = client.post("/api/simulations", json={"scenario_index": 99})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_INPUT"
