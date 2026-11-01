from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

# Standard Error Models
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

# Health Model
class HealthResponse(BaseModel):
    status: str
    application: str
    api_version: str
    database: str

# Settings Models
class SettingsResponse(BaseModel):
    risk_sensitivity: float
    automatic_critical_blocking: bool
    require_high_risk_approval: bool
    mask_sensitive_data: bool
    notifications_enabled: bool
    updated_at: str

class SettingsUpdateRequest(BaseModel):
    risk_sensitivity: Optional[float] = None
    automatic_critical_blocking: Optional[bool] = None
    require_high_risk_approval: Optional[bool] = None
    mask_sensitive_data: Optional[bool] = None
    notifications_enabled: Optional[bool] = None

    @field_validator("risk_sensitivity")
    @classmethod
    def validate_sensitivity(cls, v):
        if v is not None and (v < 0.1 or v > 5.0):
            raise ValueError("risk_sensitivity must be between 0.1 and 5.0")
        return v

# Tool Permission Models
VALID_TOOL_PERMISSIONS = {"Allowed", "Approval Required", "Restricted", "Blocked"}

class ToolResponse(BaseModel):
    id: int
    tool_id: str
    tool_name: str
    description: str
    assigned_agent: str
    risk_level: str
    permission_status: str
    updated_at: str

class ToolUpdateRequest(BaseModel):
    permission_status: str

    @field_validator("permission_status")
    @classmethod
    def validate_permission_status(cls, v):
        if v not in VALID_TOOL_PERMISSIONS:
            raise ValueError(f"Invalid permission status '{v}'. Allowed: {', '.join(sorted(VALID_TOOL_PERMISSIONS))}")
        return v

# Approval Models
VALID_APPROVAL_DECISIONS = {"Approved", "Rejected"}

class ApprovalResponse(BaseModel):
    id: int
    approval_id: str
    agent_name: str
    operation: str
    risk_level: str
    reason: str
    status: str
    created_at: str
    updated_at: str

class ApprovalDecisionRequest(BaseModel):
    decision: str

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v):
        if v not in VALID_APPROVAL_DECISIONS:
            raise ValueError(f"Invalid decision '{v}'. Allowed values: {', '.join(sorted(VALID_APPROVAL_DECISIONS))}")
        return v

# Event Models
class EventResponse(BaseModel):
    id: int
    event_id: str
    category: str
    source: str
    risk_level: str
    decision: str
    explanation: str
    created_at: str
    event_source: str

class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    limit: int
    offset: int

# Scanner Models
class ScanRequest(BaseModel):
    prompt: str = Field(..., max_length=1000)

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("The submitted prompt cannot be empty.")
        if len(cleaned) > 1000:
            raise ValueError("Prompt exceeds the maximum allowed length of 1000 characters.")
        return cleaned

class ScanResponse(BaseModel):
    classification: str
    risk_score: int
    risk_level: str
    detected_indicators: List[str]
    sensitive_data: List[List[str]]
    decision: str
    explanation: str
    remediation: str

# Agent Models
class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str
    demo_status: str
    permission_profile: str
    risk_level: str
    simulated_requests: int

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

# Simulation Models
class SimulationRequest(BaseModel):
    scenario_index: Optional[int] = Field(None, ge=0, le=4)
    scenario_id: Optional[str] = None

class SimulationResponse(BaseModel):
    scenario_title: str
    prompt: str
    classification: str
    risk_score: int
    risk_level: str
    detected_indicators: List[str]
    tool_name: str
    tool_permission: str
    decision: str
    explanation: str
    stages: List[str]
    approval_created: Optional[str] = None
    event_id: str

# Dashboard Models
class DashboardResponse(BaseModel):
    total_events: int
    threats_detected: int
    actions_blocked: int
    pending_approvals: int
    risk_distribution: Dict[str, int]
    recent_events: List[EventResponse]
    activity_timeline: List[int]
    protection_modules: List[str]

