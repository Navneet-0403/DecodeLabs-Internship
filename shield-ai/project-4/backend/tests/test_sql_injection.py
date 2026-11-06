import pytest

def test_sql_injection_in_event_search(client):
    """Verify SQL injection strings in search filters are safely parameterized."""
    malicious_queries = [
        "' OR '1'='1",
        "'; DROP TABLE security_events; --",
        "1 UNION SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 --",
        "admin'--",
    ]
    for q in malicious_queries:
        response = client.get(f"/api/events?q={q}")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data

    # Verify security_events table was NOT dropped
    verify_res = client.get("/api/events")
    assert verify_res.status_code == 200
    assert verify_res.json()["total"] >= 7

def test_sql_injection_in_data_creation(client):
    """Verify that injection vectors stored in text columns remain passive literal data."""
    injection_name = "Agent'); DROP TABLE agents; --"
    payload = {
        "agent_code": "agent-sqli-test",
        "name": injection_name,
        "agent_type": "Security",
        "status": "Active"
    }
    create_res = client.post("/api/agents", json=payload)
    assert create_res.status_code == 201
    assert create_res.json()["agent_name"] == injection_name

    # Verify agents table is still intact and queryable
    get_res = client.get("/api/agents/agent-sqli-test")
    assert get_res.status_code == 200
    assert get_res.json()["agent_name"] == injection_name

