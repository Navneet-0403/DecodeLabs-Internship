import pytest

def test_get_approvals(client):
    response = client.get("/api/approvals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    assert any(a["approval_id"] == "AP-201" for a in data)

def test_get_approvals_with_filter(client):
    response = client.get("/api/approvals?status=Pending")
    assert response.status_code == 200
    data = response.json()
    assert all(a["status"] == "Pending" for a in data)

def test_approval_decision_workflow(client):
    # Make decision on AP-201
    response = client.post("/api/approvals/AP-201/decision", json={"decision": "Approved"})
    assert response.status_code == 200
    data = response.json()
    assert data["approval_id"] == "AP-201"
    assert data["status"] == "Approved"

    # Repeated decision must return 409 Conflict
    conflict_res = client.post("/api/approvals/AP-201/decision", json={"decision": "Approved"})
    assert conflict_res.status_code == 409
    assert conflict_res.json()["error"]["code"] == "APPROVAL_ALREADY_RESOLVED"

def test_approval_not_found(client):
    response = client.post("/api/approvals/AP-9999/decision", json={"decision": "Approved"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "APPROVAL_NOT_FOUND"

def test_approval_invalid_decision(client):
    response = client.post("/api/approvals/AP-202/decision", json={"decision": "Maybe"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_INPUT"
