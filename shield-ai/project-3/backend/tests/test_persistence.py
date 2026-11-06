import pytest

def test_settings_persistence(client):
    # Update settings
    update_res = client.put("/api/settings", json={"risk_sensitivity": 1.25, "automatic_critical_blocking": False})
    assert update_res.status_code == 200
    assert update_res.json()["risk_sensitivity"] == 1.25
    assert update_res.json()["automatic_critical_blocking"] is False

    # Get settings
    get_res = client.get("/api/settings")
    assert get_res.status_code == 200
    assert get_res.json()["risk_sensitivity"] == 1.25
    assert get_res.json()["automatic_critical_blocking"] is False

    # Revert settings
    client.put("/api/settings", json={"risk_sensitivity": 1.0, "automatic_critical_blocking": True})

def test_settings_validation(client):
    # Invalid sensitivity (> 5.0)
    response = client.put("/api/settings", json={"risk_sensitivity": 10.0})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_INPUT"

def test_dashboard_metrics(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "threats_detected" in data
    assert "actions_blocked" in data
    assert "pending_approvals" in data
    assert "risk_distribution" in data
    assert "recent_events" in data
    assert "activity_timeline" in data
    assert len(data["activity_timeline"]) == 7
    # Verify no fabricated counts: sum of timeline matches total events or is real
    assert sum(data["activity_timeline"]) == data["total_events"]
    assert len(data["protection_modules"]) == 5

def test_agent_monitor_and_activity(client):
    agents_res = client.get("/api/agents")
    assert agents_res.status_code == 200
    agents = agents_res.json()
    assert len(agents) == 4

    # Activity for agent-1
    act_res = client.get("/api/agents/agent-1/activity")
    assert act_res.status_code == 200
    act_data = act_res.json()
    assert act_data["agent_name"] == "Research Assistant"
    assert len(act_data["workflow_stages"]) == 8

def test_demo_reset(client):
    response = client.post("/api/demo/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify event count reset
    events_res = client.get("/api/events")
    assert events_res.status_code == 200
    assert events_res.json()["total"] == 7
