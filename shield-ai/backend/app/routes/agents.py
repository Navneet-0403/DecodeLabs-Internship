import sqlite3
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from ..database import get_db
from ..schemas import AgentResponse, AgentActivityResponse
from ..exceptions import APIException
from ..services.policy_engine import map_tool_permission_to_decision

router = APIRouter(prefix="/api/agents", tags=["Agent Monitor"])

AGENT_CATALOG = [
    {
        "agent_id": "agent-1",
        "index": 0,
        "agent_name": "Research Assistant",
        "agent_type": "Retrieval",
        "demo_status": "Active (demo)",
        "permission_profile": "Read-only public",
        "risk_level": "Low",
        "simulated_requests": 42,
        "proposed_action": "search a public knowledge base",
        "tool_id": "tool-1"
    },
    {
        "agent_id": "agent-2",
        "index": 1,
        "agent_name": "Email Assistant",
        "agent_type": "Messaging",
        "demo_status": "Active (demo)",
        "permission_profile": "Approval for external",
        "risk_level": "Medium",
        "simulated_requests": 17,
        "proposed_action": "send an external email",
        "tool_id": "tool-5"
    },
    {
        "agent_id": "agent-3",
        "index": 2,
        "agent_name": "Data Analyst",
        "agent_type": "Analytics",
        "demo_status": "Active (demo)",
        "permission_profile": "Restricted customer data",
        "risk_level": "High",
        "simulated_requests": 29,
        "proposed_action": "read customer records",
        "tool_id": "tool-4"
    },
    {
        "agent_id": "agent-4",
        "index": 3,
        "agent_name": "File Management Agent",
        "agent_type": "Files",
        "demo_status": "Idle (demo)",
        "permission_profile": "No deletion",
        "risk_level": "Medium",
        "simulated_requests": 8,
        "proposed_action": "delete protected files",
        "tool_id": "tool-6"
    }
]

def find_agent(identifier: str) -> Dict[str, Any]:
    # Match by agent_id, slug, or 0-based index
    for ag in AGENT_CATALOG:
        if ag["agent_id"] == identifier or ag["agent_name"].lower().replace(" ", "-") == identifier.lower():
            return ag
    try:
        idx = int(identifier)
        if 0 <= idx < len(AGENT_CATALOG):
            return AGENT_CATALOG[idx]
    except ValueError:
        pass
    raise APIException(
        status_code=404,
        code="AGENT_NOT_FOUND",
        message=f"Agent with identifier '{identifier}' was not found."
    )

@router.get("", response_model=List[AgentResponse])
def get_agents():
    return [
        AgentResponse(
            agent_id=a["agent_id"],
            agent_name=a["agent_name"],
            agent_type=a["agent_type"],
            demo_status=a["demo_status"],
            permission_profile=a["permission_profile"],
            risk_level=a["risk_level"],
            simulated_requests=a["simulated_requests"]
        )
        for a in AGENT_CATALOG
    ]

@router.get("/{agent_id}/activity", response_model=AgentActivityResponse)
def get_agent_activity(agent_id: str, conn: sqlite3.Connection = Depends(get_db)):
    ag = find_agent(agent_id)
    
    # Retrieve assigned tool's real current permission from SQLite
    cursor = conn.cursor()
    cursor.execute("SELECT tool_name, permission_status FROM tool_permissions WHERE tool_id = ?", (ag["tool_id"],))
    row = cursor.fetchone()
    if not row:
        raise APIException(status_code=500, code="TOOL_CONFIG_ERROR", message=f"Tool {ag['tool_id']} not found in database.")
    
    tool_name = row["tool_name"]
    perm_status = row["permission_status"]
    decision = map_tool_permission_to_decision(perm_status)

    workflow_stages = [
        f"User prompt received by {ag['agent_name']}",
        "Prompt inspected (rule-based heuristic)",
        f"Risk assessed: {ag['risk_level']}",
        f"Policy checked: {ag['permission_profile']}",
        f"Agent proposed: {ag['proposed_action']}",
        f"Tool request intercepted: {tool_name}",
        f"Decision: {decision} (policy “{perm_status}”)",
        "Event recorded in audit log"
    ]

    return AgentActivityResponse(
        agent_id=ag["agent_id"],
        agent_name=ag["agent_name"],
        agent_type=ag["agent_type"],
        permission_profile=ag["permission_profile"],
        risk_level=ag["risk_level"],
        proposed_action=ag["proposed_action"],
        intercepted_tool=tool_name,
        tool_permission=perm_status,
        decision=decision,
        workflow_stages=workflow_stages
    )

