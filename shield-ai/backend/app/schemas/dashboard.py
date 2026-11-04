from typing import List, Dict
from pydantic import BaseModel
from .security_event import EventResponse

class DashboardResponse(BaseModel):
    total_events: int
    threats_detected: int
    actions_blocked: int
    pending_approvals: int
    risk_distribution: Dict[str, int]
    recent_events: List[EventResponse]
    activity_timeline: List[int]
    protection_modules: List[str]
