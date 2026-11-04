from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .tool import VALID_TOOL_PERMISSIONS

class AgentToolAssignRequest(BaseModel):
    tool_id: int = Field(..., description="Database ID or tool code of the tool")
    permission_status: str = Field(default="Allowed")

    @field_validator("permission_status")
    @classmethod
    def validate_perm(cls, v):
        if v not in VALID_TOOL_PERMISSIONS:
            raise ValueError(f"Invalid permission status '{v}'. Allowed: {', '.join(sorted(VALID_TOOL_PERMISSIONS))}")
        return v

class AgentToolUpdateRequest(BaseModel):
    permission_status: str

    @field_validator("permission_status")
    @classmethod
    def validate_perm(cls, v):
        if v not in VALID_TOOL_PERMISSIONS:
            raise ValueError(f"Invalid permission status '{v}'. Allowed: {', '.join(sorted(VALID_TOOL_PERMISSIONS))}")
        return v

class AgentToolResponse(BaseModel):
    id: int
    agent_id: int
    agent_code: str
    agent_name: str
    tool_id: int
    tool_code: str
    tool_name: str
    permission_status: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
