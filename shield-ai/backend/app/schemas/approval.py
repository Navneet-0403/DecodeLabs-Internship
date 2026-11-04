from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .tool import VALID_RISK_LEVELS

VALID_APPROVAL_STATUSES = {"Pending", "Approved", "Rejected", "Cancelled"}
VALID_APPROVAL_DECISIONS = {"Approved", "Rejected"}

class ApprovalCreate(BaseModel):
    agent_id: Optional[int] = None
    tool_id: Optional[int] = None
    event_id: Optional[int] = None
    operation: str = Field(..., min_length=1, max_length=255)
    risk_level: str = Field(default="High")
    reason: str = Field(..., min_length=1, max_length=255)
    agent_name: Optional[str] = None

    @field_validator("risk_level")
    @classmethod
    def validate_risk(cls, v):
        if v not in VALID_RISK_LEVELS:
            raise ValueError(f"Invalid risk_level '{v}'. Allowed: {', '.join(sorted(VALID_RISK_LEVELS))}")
        return v

class ApprovalUpdate(BaseModel):
    operation: Optional[str] = Field(None, min_length=1, max_length=255)
    reason: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_st(cls, v):
        if v is not None and v not in VALID_APPROVAL_STATUSES:
            raise ValueError(f"Invalid status '{v}'. Allowed: {', '.join(sorted(VALID_APPROVAL_STATUSES))}")
        return v

class ApprovalDecisionRequest(BaseModel):
    decision: str

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v):
        if v not in VALID_APPROVAL_DECISIONS:
            raise ValueError(f"Invalid decision '{v}'. Allowed values: {', '.join(sorted(VALID_APPROVAL_DECISIONS))}")
        return v

class ApprovalResponse(BaseModel):
    id: int
    approval_id: str
    approval_code: str
    agent_id: Optional[int] = None
    tool_id: Optional[int] = None
    event_id: Optional[int] = None
    agent_name: str
    operation: str
    risk_level: str
    reason: str
    status: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

