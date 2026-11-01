import pytest

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["application"] == "Shield AI"
    assert data["api_version"] == "1.0.0"
    assert data["database"] == "connected"

def test_root_index_serving(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Shield AI" in response.text
