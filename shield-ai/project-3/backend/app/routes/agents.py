from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..repositories.agent_repo import AgentRepository
from ..repositories.agent_tool_repo import AgentToolRepository
from ..repositories.tool_repo import ToolRepository
from ..schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentActivityResponse
from ..schemas.agent_tool import AgentToolAssignRequest, AgentToolUpdateRequest, AgentToolResponse
from ..exceptions import APIException
from ..services.policy_engine import map_tool_permission_to_decision

router = APIRouter(prefix="/api/agents", tags=["Agent Monitor & CRUD"])

def agent_to_response(agent, db: Session) -> AgentResponse:
    # Calculate simulated requests and permission profile
    events_count = len(agent.security_events)
    tools_count = len(agent.agent_tools)
    simulated_reqs = 40 + events_count * 2
    
    # Permission profile description
    perm_profile = agent.description or f"{agent.agent_type} agent with {tools_count} tool(s)"
    if "Research" in agent.name:
        perm_profile = "Read-only public"
        simulated_reqs = max(42, simulated_reqs)
        risk = "Low"
    elif "Email" in agent.name:
        perm_profile = "Approval for external"
        simulated_reqs = max(17, simulated_reqs)
        risk = "Medium"
    elif "Data" in agent.name:
        perm_profile = "Restricted customer data"
        simulated_reqs = max(29, simulated_reqs)
        risk = "High"
    elif "File" in agent.name:
        perm_profile = "No deletion"
        simulated_reqs = max(8, simulated_reqs)
        risk = "Medium"
    else:
        risk = "Low"

    return AgentResponse(
        id=agent.id,
        agent_id=agent.agent_code,
        agent_code=agent.agent_code,
        agent_name=agent.name,
        agent_type=agent.agent_type,
        demo_status=agent.status,
        status=agent.status,
        description=agent.description,
        permission_profile=perm_profile,
        risk_level=risk,
        simulated_requests=simulated_reqs,
        is_active=agent.is_active,
        created_at=agent.created_at,
        updated_at=agent.updated_at
    )

@router.get("", response_model=List[AgentResponse])
def get_agents(active_only: bool = False, db: Session = Depends(get_db)):
    """Retrieve all agents."""
    agents = AgentRepository.get_all(db, active_only=active_only)
    return [agent_to_response(a, db) for a in agents]

@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    """Create a new AI agent."""
    if agent_in.agent_code:
        existing = AgentRepository.get_by_code(db, agent_in.agent_code)
        if existing:
            raise APIException(status_code=400, code="AGENT_CODE_EXISTS", message=f"Agent code '{agent_in.agent_code}' already exists.")
    agent = AgentRepository.create(db, agent_in)
    return agent_to_response(agent, db)

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Retrieve an individual agent by code, ID, or index."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")
    return agent_to_response(agent, db)

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    """Update agent details."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")
    updated = AgentRepository.update(db, agent, agent_in)
    return agent_to_response(updated, db)

@router.patch("/{agent_id}", response_model=AgentResponse)
def patch_agent(agent_id: str, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    """Partially update agent fields via HTTP PATCH."""
    return update_agent(agent_id, agent_in, db)

@router.delete("/{agent_id}", response_model=AgentResponse)
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Soft-deletes / deactivates an agent safely, preserving audit history."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")
    deactivated = AgentRepository.soft_delete(db, agent)
    return agent_to_response(deactivated, db)

@router.get("/{agent_id}/activity", response_model=AgentActivityResponse)
def get_agent_activity(agent_id: str, db: Session = Depends(get_db)):
    """Retrieve real-time telemetry workflow and policy evaluation for an agent."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")

    # Determine proposed action and primary tool
    if "Research" in agent.name:
        action = "search a public knowledge base"
        tool_code = "tool-1"
        risk = "Low"
        profile = "Read-only public"
    elif "Email" in agent.name:
        action = "send an external email"
        tool_code = "tool-5"
        risk = "Medium"
        profile = "Approval for external"
    elif "Data" in agent.name:
        action = "read customer records"
        tool_code = "tool-4"
        risk = "High"
        profile = "Restricted customer data"
    else:
        action = "delete protected files"
        tool_code = "tool-6"
        risk = "Medium"
        profile = "No deletion"

    tool = ToolRepository.get_by_code(db, tool_code)
    if not tool:
        tool = ToolRepository.get_all(db)[0]

    # Look up agent-specific tool permission from agent_tools
    at = AgentToolRepository.get_by_agent_and_tool(db, agent.id, tool.id)
    perm_status = at.permission_status if at else "Allowed"
    decision = map_tool_permission_to_decision(perm_status)

    workflow_stages = [
        f"User prompt received by {agent.name}",
        "Prompt inspected (rule-based heuristic)",
        f"Risk assessed: {risk}",
        f"Policy checked: {profile}",
        f"Agent proposed: {action}",
        f"Tool request intercepted: {tool.name}",
        f"Decision: {decision} (policy “{perm_status}”)",
        "Event recorded in audit log"
    ]

    return AgentActivityResponse(
        agent_id=agent.agent_code,
        agent_name=agent.name,
        agent_type=agent.agent_type,
        permission_profile=profile,
        risk_level=risk,
        proposed_action=action,
        intercepted_tool=tool.name,
        tool_permission=perm_status,
        decision=decision,
        workflow_stages=workflow_stages
    )

# --- Agent-Tool Junction CRUD Endpoints (Part 7.C) ---

@router.get("/{agent_id}/tools", response_model=List[AgentToolResponse])
def get_agent_tools(agent_id: str, db: Session = Depends(get_db)):
    """Retrieve all tools and permissions assigned to a particular agent."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")
    
    assignments = AgentToolRepository.get_all_for_agent(db, agent.id)
    return [
        AgentToolResponse(
            id=a.id,
            agent_id=agent.id,
            agent_code=agent.agent_code,
            agent_name=agent.name,
            tool_id=a.tool.id,
            tool_code=a.tool.tool_code,
            tool_name=a.tool.name,
            permission_status=a.permission_status,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in assignments
    ]

@router.post("/{agent_id}/tools", response_model=AgentToolResponse, status_code=status.HTTP_201_CREATED)
def assign_tool_to_agent(agent_id: str, assign_in: AgentToolAssignRequest, db: Session = Depends(get_db)):
    """Assign a tool to an agent with a specific permission policy."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")

    tool = ToolRepository.get_by_identifier(db, str(assign_in.tool_id))
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool '{assign_in.tool_id}' was not found.")

    assignment = AgentToolRepository.assign(db, agent.id, tool.id, assign_in.permission_status)
    return AgentToolResponse(
        id=assignment.id,
        agent_id=agent.id,
        agent_code=agent.agent_code,
        agent_name=agent.name,
        tool_id=tool.id,
        tool_code=tool.tool_code,
        tool_name=tool.name,
        permission_status=assignment.permission_status,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at
    )

@router.put("/{agent_id}/tools/{tool_id}", response_model=AgentToolResponse)
def update_agent_tool_permission(agent_id: str, tool_id: str, update_in: AgentToolUpdateRequest, db: Session = Depends(get_db)):
    """Update permission for an agent-tool pair."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")
    tool = ToolRepository.get_by_identifier(db, tool_id)
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool '{tool_id}' was not found.")

    assignment = AgentToolRepository.get_by_agent_and_tool(db, agent.id, tool.id)
    if not assignment:
        raise APIException(status_code=404, code="ASSIGNMENT_NOT_FOUND", message=f"Tool '{tool.name}' is not assigned to agent '{agent.name}'.")

    updated = AgentToolRepository.update_permission(db, assignment, update_in.permission_status)
    return AgentToolResponse(
        id=updated.id,
        agent_id=agent.id,
        agent_code=agent.agent_code,
        agent_name=agent.name,
        tool_id=tool.id,
        tool_code=tool.tool_code,
        tool_name=tool.name,
        permission_status=updated.permission_status,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )

@router.delete("/{agent_id}/tools/{tool_id}", status_code=status.HTTP_200_OK)
def remove_agent_tool_assignment(agent_id: str, tool_id: str, db: Session = Depends(get_db)):
    """Remove tool assignment from an agent."""
    agent = AgentRepository.get_by_identifier(db, agent_id)
    if not agent:
        raise APIException(status_code=404, code="AGENT_NOT_FOUND", message=f"Agent '{agent_id}' was not found.")
    tool = ToolRepository.get_by_identifier(db, tool_id)
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool '{tool_id}' was not found.")

    assignment = AgentToolRepository.get_by_agent_and_tool(db, agent.id, tool.id)
    if not assignment:
        raise APIException(status_code=404, code="ASSIGNMENT_NOT_FOUND", message=f"Tool '{tool.name}' is not assigned to agent '{agent.name}'.")

    AgentToolRepository.delete(db, assignment)
    return {"status": "ok", "message": f"Tool '{tool.name}' unassigned from agent '{agent.name}'."}
