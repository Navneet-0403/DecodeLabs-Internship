import pytest

def test_get_all_tools(client):
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    # Verify initial default permission configuration:
    # tool-1: Allowed, tool-2: Allowed, tool-3: Allowed, tool-4: Restricted, tool-5: Approval Required, tool-6: Blocked, tool-7: Blocked
    tools_by_id = {t["tool_id"]: t["permission_status"] for t in data}
    assert tools_by_id["tool-1"] == "Allowed"
    assert tools_by_id["tool-2"] == "Allowed"
    assert tools_by_id["tool-3"] == "Allowed"
    assert tools_by_id["tool-4"] == "Restricted"
    assert tools_by_id["tool-5"] == "Approval Required"
    assert tools_by_id["tool-6"] == "Blocked"
    assert tools_by_id["tool-7"] == "Blocked"

def test_get_single_tool(client):
    response = client.get("/api/tools/tool-1")
    assert response.status_code == 200
    data = response.json()
    assert data["tool_id"] == "tool-1"
    assert data["tool_name"] == "Public Knowledge Search"

def test_get_nonexistent_tool(client):
    response = client.get("/api/tools/nonexistent-99")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "TOOL_NOT_FOUND"

def test_update_tool_permission_success(client):
    response = client.put("/api/tools/tool-1", json={"permission_status": "Blocked"})
    assert response.status_code == 200
    data = response.json()
    assert data["permission_status"] == "Blocked"

    # Verify persistence via GET
    get_res = client.get("/api/tools/tool-1")
    assert get_res.json()["permission_status"] == "Blocked"

    # Reset back to Allowed
    reset_res = client.put("/api/tools/tool-1", json={"permission_status": "Allowed"})
    assert reset_res.status_code == 200

def test_update_tool_permission_invalid_value(client):
    response = client.put("/api/tools/tool-1", json={"permission_status": "SuperAllowed"})
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_INPUT"

def test_reset_tools_endpoint(client):
    # Change tool-2
    client.put("/api/tools/tool-2", json={"permission_status": "Blocked"})
    # Reset
    reset_res = client.post("/api/tools/reset")
    assert reset_res.status_code == 200
    tools = reset_res.json()
    t2 = next(t for t in tools if t["tool_id"] == "tool-2")
    assert t2["permission_status"] == "Allowed"
