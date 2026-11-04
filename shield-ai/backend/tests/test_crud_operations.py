import pytest

def test_agent_complete_crud(client):
    # 1. CREATE Agent
    create_payload = {
        "agent_code": "agent-test-crud",
        "name": "Audit Agent",
        "agent_type": "Compliance",
        "status": "Active (demo)",
        "description": "Performs compliance verification."
    }
    create_res = client.post("/api/agents", json=create_payload)
    assert create_res.status_code == 201
    agent_data = create_res.json()
    assert agent_data["agent_code"] == "agent-test-crud"
    assert agent_data["agent_name"] == "Audit Agent"
    assert agent_data["is_active"] is True

    # 2. READ ALL Agents
    list_res = client.get("/api/agents")
    assert list_res.status_code == 200
    assert any(a["agent_code"] == "agent-test-crud" for a in list_res.json())

    # 3. READ SINGLE Agent
    get_res = client.get("/api/agents/agent-test-crud")
    assert get_res.status_code == 200
    assert get_res.json()["agent_name"] == "Audit Agent"

    # 4. UPDATE Agent
    update_payload = {"name": "Senior Audit Agent", "status": "Busy"}
    put_res = client.put("/api/agents/agent-test-crud", json=update_payload)
    assert put_res.status_code == 200
    assert put_res.json()["agent_name"] == "Senior Audit Agent"
    assert put_res.json()["demo_status"] == "Busy"

    # 5. DELETE Agent (Soft-delete/Deactivate)
    del_res = client.delete("/api/agents/agent-test-crud")
    assert del_res.status_code == 200
    assert del_res.json()["is_active"] is False
    assert del_res.json()["demo_status"] == "Deactivated"

def test_tool_catalog_complete_crud(client):
    # 1. CREATE Tool
    create_payload = {
        "tool_code": "tool-catalog-test",
        "name": "Cloud Backup Sync",
        "description": "Syncs data to internal cloud backup",
        "risk_level": "Medium"
    }
    create_res = client.post("/api/tool-catalog", json=create_payload)
    assert create_res.status_code == 201
    tool_data = create_res.json()
    assert tool_data["tool_code"] == "tool-catalog-test"
    assert tool_data["risk_level"] == "Medium"
    assert tool_data["is_active"] is True

    # 2. READ ALL Tools
    list_res = client.get("/api/tool-catalog")
    assert list_res.status_code == 200
    assert any(t["tool_code"] == "tool-catalog-test" for t in list_res.json())

    # 3. READ SINGLE Tool
    get_res = client.get("/api/tool-catalog/tool-catalog-test")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Cloud Backup Sync"

    # 4. UPDATE Tool
    update_payload = {"risk_level": "High", "description": "High-impact cloud sync"}
    put_res = client.put("/api/tool-catalog/tool-catalog-test", json=update_payload)
    assert put_res.status_code == 200
    assert put_res.json()["risk_level"] == "High"
    assert put_res.json()["description"] == "High-impact cloud sync"

    # 5. DELETE Tool (Soft-delete/Deactivate)
    del_res = client.delete("/api/tool-catalog/tool-catalog-test")
    assert del_res.status_code == 200
    assert del_res.json()["is_active"] is False

def test_agent_tool_junction_crud(client):
    # 1. Assign tool-6 (File Deletion) to agent-1 (Research Assistant)
    assign_payload = {
        "tool_id": 6,
        "permission_status": "Approval Required"
    }
    post_res = client.post("/api/agents/agent-1/tools", json=assign_payload)
    assert post_res.status_code == 201
    data = post_res.json()
    assert data["permission_status"] == "Approval Required"
    assert data["agent_code"] == "agent-1"

    # 2. Retrieve all tools assigned to agent-1
    get_res = client.get("/api/agents/agent-1/tools")
    assert get_res.status_code == 200
    assert any(at["tool_code"] == "tool-6" for at in get_res.json())

    # 3. Update permission for this agent-tool pair
    put_res = client.put("/api/agents/agent-1/tools/tool-6", json={"permission_status": "Blocked"})
    assert put_res.status_code == 200
    assert put_res.json()["permission_status"] == "Blocked"

    # 4. Remove assignment
    del_res = client.delete("/api/agents/agent-1/tools/tool-6")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "ok"

def test_security_event_crud(client):
    # 1. CREATE Event
    create_payload = {
        "category": "Policy Intercept",
        "source": "Security Gateway",
        "risk_score": 75,
        "risk_level": "High",
        "decision": "Blocked",
        "explanation": "Outbound egress rate limit exceeded.",
        "event_source": "application"
    }
    create_res = client.post("/api/events", json=create_payload)
    assert create_res.status_code == 201
    ev_data = create_res.json()
    assert ev_data["event_code"].startswith("EV-")
    assert ev_data["risk_score"] == 75

    event_code = ev_data["event_code"]

    # 2. READ Event
    get_res = client.get(f"/api/events/{event_code}")
    assert get_res.status_code == 200
    assert get_res.json()["event_code"] == event_code

    # 3. UPDATE administrative metadata
    put_res = client.put(f"/api/events/{event_code}", json={"explanation": "Verified rate limit anomaly."})
    assert put_res.status_code == 200
    assert put_res.json()["explanation"] == "Verified rate limit anomaly."

    # 4. ARCHIVE / Soft-delete Event
    del_res = client.delete(f"/api/events/{event_code}")
    assert del_res.status_code == 200
    assert del_res.json()["is_archived"] is True

def test_approval_request_crud(client):
    # 1. CREATE Approval Request
    create_payload = {
        "operation": "Bulk database export to S3",
        "risk_level": "High",
        "reason": "Quarterly compliance archival",
        "agent_name": "Data Analyst"
    }
    create_res = client.post("/api/approvals", json=create_payload)
    assert create_res.status_code == 201
    appr_data = create_res.json()
    assert appr_data["approval_code"].startswith("AP-")
    assert appr_data["status"] == "Pending"

    appr_code = appr_data["approval_code"]

    # 2. READ Approval Request
    get_res = client.get(f"/api/approvals/{appr_code}")
    assert get_res.status_code == 200
    assert get_res.json()["operation"] == "Bulk database export to S3"

    # 3. UPDATE Approval Request
    put_res = client.put(f"/api/approvals/{appr_code}", json={"reason": "Updated reason: Legal audit"})
    assert put_res.status_code == 200
    assert put_res.json()["reason"] == "Updated reason: Legal audit"

    # 4. CANCEL Approval Request
    del_res = client.delete(f"/api/approvals/{appr_code}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "Cancelled"
