from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from .tool import VALID_RISK_LEVELS

VALID_EVENT_DECISIONS = {"Allowed", "Approval required", "Approval Required", "Blocked"}

class EventCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    source: str = Field(..., min_length=1, max_length=100)
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(..., max_length=20)
    decision: str = Field(..., max_length=30)
    explanation: str = Field(..., min_length=1)
    agent_id: Optional[int] = None
    tool_id: Optional[int] = None
    event_source: str = Field(default="application")

    @field_validator("risk_level")
    @classmethod
    def validate_risk(cls, v):
        if v not in VALID_RISK_LEVELS:
            raise ValueError(f"Invalid risk_level '{v}'. Allowed: {', '.join(sorted(VALID_RISK_LEVELS))}")
        return v

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v):
        if v not in VALID_EVENT_DECISIONS:
            raise ValueError(f"Invalid decision '{v}'. Allowed: {', '.join(sorted(VALID_EVENT_DECISIONS))}")
        return v

class EventUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    explanation: Optional[str] = Field(None, min_length=1)
    is_archived: Optional[bool] = None

class EventResponse(BaseModel):
    id: int
    event_id: str
    event_code: str
    agent_id: Optional[int] = None
    tool_id: Optional[int] = None
    category: str
    source: str
    risk_score: int
    risk_level: str
    decision: str
    explanation: str
    event_source: str
    created_at: str
    is_archived: bool = False

    model_config = {"from_attributes": True}

class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    limit: int
    offset: int

