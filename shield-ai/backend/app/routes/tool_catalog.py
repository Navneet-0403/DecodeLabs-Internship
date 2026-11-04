from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..repositories.tool_repo import ToolRepository
from ..schemas.tool import ToolCreate, ToolUpdate, ToolCatalogResponse
from ..exceptions import APIException

router = APIRouter(prefix="/api/tool-catalog", tags=["Tool Catalog CRUD"])

@router.get("", response_model=List[ToolCatalogResponse])
def get_all_tools(active_only: bool = False, db: Session = Depends(get_db)):
    """Retrieve all tools in the system catalog."""
    tools = ToolRepository.get_all(db, active_only=active_only)
    return tools

@router.post("", response_model=ToolCatalogResponse, status_code=status.HTTP_201_CREATED)
def create_tool(tool_in: ToolCreate, db: Session = Depends(get_db)):
    """Create a new external tool in the catalog."""
    if tool_in.tool_code:
        existing = ToolRepository.get_by_code(db, tool_in.tool_code)
        if existing:
            raise APIException(status_code=400, code="TOOL_CODE_EXISTS", message=f"Tool code '{tool_in.tool_code}' already exists.")
    tool = ToolRepository.create(db, tool_in)
    return tool

@router.get("/{tool_id}", response_model=ToolCatalogResponse)
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    """Retrieve an individual tool from the catalog."""
    tool = ToolRepository.get_by_identifier(db, tool_id)
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool '{tool_id}' was not found.")
    return tool

@router.put("/{tool_id}", response_model=ToolCatalogResponse)
def update_tool(tool_id: str, tool_in: ToolUpdate, db: Session = Depends(get_db)):
    """Update tool information."""
    tool = ToolRepository.get_by_identifier(db, tool_id)
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool '{tool_id}' was not found.")
    updated = ToolRepository.update(db, tool, tool_in)
    return updated

@router.delete("/{tool_id}", response_model=ToolCatalogResponse)
def delete_tool(tool_id: str, db: Session = Depends(get_db)):
    """Safely deactivate a tool without deleting historical audit event records."""
    tool = ToolRepository.get_by_identifier(db, tool_id)
    if not tool:
        raise APIException(status_code=404, code="TOOL_NOT_FOUND", message=f"Tool '{tool_id}' was not found.")
    deactivated = ToolRepository.soft_delete(db, tool)
    return deactivated

