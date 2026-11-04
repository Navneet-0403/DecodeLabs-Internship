from typing import Optional, List
from pydantic import BaseModel, Field

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
    event_code: str
