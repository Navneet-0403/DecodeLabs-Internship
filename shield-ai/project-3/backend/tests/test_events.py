import pytest

def test_get_events_list(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert "total" in data
    assert data["total"] >= 7
    assert len(data["events"]) > 0

def test_get_events_filtering(client):
    # Filter by risk=Critical
    response = client.get("/api/events?risk=Critical")
    assert response.status_code == 200
    data = response.json()
    assert all(e["risk_level"] == "Critical" for e in data["events"])

    # Search keyword
    search_res = client.get("/api/events?q=injection")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] >= 1

def test_get_single_event(client):
    response = client.get("/api/events/EV-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "EV-1001"
    assert data["risk_level"] == "Critical"

def test_get_nonexistent_event(client):
    response = client.get("/api/events/EV-999999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "EVENT_NOT_FOUND"
