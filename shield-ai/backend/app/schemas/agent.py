from typing import Optional, List
from pydantic import BaseModel, Field

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    agent_type: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="Active (demo)", max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = True

class AgentCreate(AgentBase):
    agent_code: Optional[str] = Field(None, min_length=1, max_length=50)

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    agent_type: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class AgentResponse(BaseModel):
    id: int
    agent_id: str
    agent_code: str
    agent_name: str
    agent_type: str
    demo_status: str
    status: str
    description: Optional[str] = None
    permission_profile: str
    risk_level: str
    simulated_requests: int
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

class AgentActivityResponse(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str
    permission_profile: str
    risk_level: str
    proposed_action: str
    intercepted_tool: str
    tool_permission: str
    decision: str
    workflow_stages: List[str]
