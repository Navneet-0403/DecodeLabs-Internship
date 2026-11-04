from typing import Optional
from sqlalchemy.orm import Session
from ..models.security_event import SecurityEvent
from ..models.approval import ApprovalRequest
from ..repositories.event_repo import SecurityEventRepository
from ..repositories.approval_repo import ApprovalRepository
from ..schemas.security_event import EventCreate
from ..schemas.approval import ApprovalCreate

def log_security_event(
    db: Session,
    category: str,
    source: str,
    risk_level: str,
    decision: str,
    explanation: str,
    event_source: str = "application",
    agent_id: Optional[int] = None,
    tool_id: Optional[int] = None,
    risk_score: Optional[int] = None
) -> str:
    if risk_score is None:
        risk_score = 85 if risk_level == "Critical" else 70 if risk_level == "High" else 45 if risk_level == "Medium" else 15

    event_in = EventCreate(
        category=category,
        source=source,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        explanation=explanation,
        agent_id=agent_id,
        tool_id=tool_id,
        event_source=event_source
    )
    event = SecurityEventRepository.create(db, event_in)
    return event.event_code

def create_approval_request(
    db: Session,
    agent_name: str,
    operation: str,
    risk_level: str,
    reason: str,
    agent_id: Optional[int] = None,
    tool_id: Optional[int] = None,
    event_id: Optional[int] = None
) -> str:
    approval_in = ApprovalCreate(
        agent_id=agent_id,
        tool_id=tool_id,
        event_id=event_id,
        operation=operation,
        risk_level=risk_level,
        reason=reason,
        agent_name=agent_name
    )
    approval = ApprovalRepository.create(db, approval_in)
    return approval.approval_code
