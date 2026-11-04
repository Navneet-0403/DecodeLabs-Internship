from typing import Optional
from pydantic import BaseModel, Field, field_validator

VALID_TOOL_PERMISSIONS = {"Allowed", "Approval Required", "Restricted", "Blocked"}
VALID_RISK_LEVELS = {"Low", "Medium", "High", "Critical"}

class ToolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    risk_level: str = Field(default="Medium")
    is_active: bool = True

    @field_validator("risk_level")
    @classmethod
    def validate_risk(cls, v):
        if v not in VALID_RISK_LEVELS:
            raise ValueError(f"Invalid risk_level '{v}'. Allowed: {', '.join(sorted(VALID_RISK_LEVELS))}")
        return v

class ToolCreate(ToolBase):
    tool_code: Optional[str] = Field(None, min_length=1, max_length=50)

class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    risk_level: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("risk_level")
    @classmethod
    def validate_risk(cls, v):
        if v is not None and v not in VALID_RISK_LEVELS:
            raise ValueError(f"Invalid risk_level '{v}'. Allowed: {', '.join(sorted(VALID_RISK_LEVELS))}")
        return v

# Tool Catalog Response for Project 3 CRUD
class ToolCatalogResponse(BaseModel):
    id: int
    tool_code: str
    name: str
    description: Optional[str] = None
    risk_level: str
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

# Tool Permission Response for Project 2 and Project 3 /api/tools
class ToolResponse(BaseModel):
    id: int
    tool_id: str
    tool_code: str
    tool_name: str
    description: str
    assigned_agent: str
    risk_level: str
    permission_status: str
    updated_at: str

    model_config = {"from_attributes": True}

class ToolUpdateRequest(BaseModel):
    permission_status: str

    @field_validator("permission_status")
    @classmethod
    def validate_permission_status(cls, v):
        if v not in VALID_TOOL_PERMISSIONS:
            raise ValueError(f"Invalid permission status '{v}'. Allowed: {', '.join(sorted(VALID_TOOL_PERMISSIONS))}")
        return v

