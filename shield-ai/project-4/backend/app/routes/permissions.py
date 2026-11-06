from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..database import reset_tool_permissions
from ..repositories.tool_repo import ToolRepository
from ..repositories.agent_tool_repo import AgentToolRepository
from ..repositories.agent_repo import AgentRepository
from ..schemas.tool import ToolResponse, ToolUpdateRequest
from ..exceptions import APIException

router = APIRouter(prefix="/api/tools", tags=["Tool Permissions"])

DEFAULT_AGENT_ASSIGNMENTS = {
    "tool-1": "Research Assistant",
    "tool-2": "Data Analyst",
    "tool-3": "Research Assistant",
    "tool-4": "Data Analyst",
    "tool-5": "Email Assistant",
    "tool-6": "File Management Agent",
    "tool-7": "Data Analyst",
}

def format_tool_response(tool, db: Session) -> ToolResponse:
    # Find assignment in agent_tools
    assigned_name = DEFAULT_AGENT_ASSIGNMENTS.get(tool.tool_code, "Research Assistant")
    agent = db.query(AgentRepository.get_all(db)[0].__class__).filter_by(name=assigned_name).first()
    
    perm = "Allowed"
    if agent:
        at = AgentToolRepository.get_by_agent_and_tool(db, agent.id, tool.id)
        if at:
            perm = at.permission_status
    else:
        # Check any assignment
        assignments = db.query(AgentToolRepository.get_all(db)[0].__class__).filter_by(tool_id=tool.id).all() if AgentToolRepository.get_all(db) else []
        if assignments:
            perm = assignments[0].permission_status
            assigned_name = assignments[0].agent.name

    return ToolResponse(
        id=tool.id,
        tool_id=tool.tool_code,
        tool_code=tool.tool_code,
        tool_name=tool.name,
        description=tool.description or "",
        assigned_agent=assigned_name,
        risk_level=tool.risk_level,
        permission_status=perm,
        updated_at=tool.updated_at
    )

@router.get("", response_model=List[ToolResponse])
def get_tools(db: Session = Depends(get_db)):
    """Retrieve all tool permissions using SQLAlchemy ORM models."""
    tools = ToolRepository.get_all(db)
    return [format_tool_response(t, db) for t in tools]

@router.get("/{tool_id}", response_model=ToolResponse)
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    """Retrieve a particular tool's permission configuration."""
    tool = ToolRepository.get_by_identifier(db, tool_id)
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool with identifier '{tool_id}' was not found.")
    return format_tool_response(tool, db)

@router.put("/{tool_id}", response_model=ToolResponse)
def update_tool_permission(tool_id: str, request: ToolUpdateRequest, db: Session = Depends(get_db)):
    """Update tool permission status in the relational agent_tools junction table."""
    tool = ToolRepository.get_by_identifier(db, tool_id)
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool with identifier '{tool_id}' was not found.")

    assigned_agent_name = DEFAULT_AGENT_ASSIGNMENTS.get(tool.tool_code, "Research Assistant")
    agent = AgentRepository.get_by_identifier(db, assigned_agent_name)
    if not agent:
        agents = AgentRepository.get_all(db)
        agent = agents[0] if agents else None

    if agent:
        AgentToolRepository.assign(db, agent.id, tool.id, request.permission_status)

    tool = ToolRepository.get_by_id(db, tool.id)
    return format_tool_response(tool, db)

@router.patch("/{tool_id}", response_model=ToolResponse)
def patch_tool_permission(tool_id: str, request: ToolUpdateRequest, db: Session = Depends(get_db)):
    """Partially update tool permission status via HTTP PATCH."""
    return update_tool_permission(tool_id, request, db)

@router.post("/reset", response_model=List[ToolResponse])
def reset_tools(db: Session = Depends(get_db)):
    """Restore default tool permissions."""
    reset_tool_permissions()
    return get_tools(db)
