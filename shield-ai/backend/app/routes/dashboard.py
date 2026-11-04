from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from ..database.session import get_db
from ..models.security_event import SecurityEvent
from ..models.approval import ApprovalRequest
from ..schemas.dashboard import DashboardResponse
from .events import format_event_response

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

PROTECTION_MODULES = [
    "Prompt inspection",
    "Permission policies",
    "Tool interception",
    "Data protection",
    "Audit monitoring"
]

@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    """Retrieve aggregated dashboard metrics derived directly from SQLAlchemy ORM records."""
    # Total events (unarchived)
    total_events = db.query(SecurityEvent).filter(SecurityEvent.is_archived == False).count()

    # Threats detected (Medium, High, Critical)
    threats_detected = db.query(SecurityEvent).filter(
        SecurityEvent.is_archived == False,
        SecurityEvent.risk_level != "Low"
    ).count()

    # Actions blocked
    actions_blocked = db.query(SecurityEvent).filter(
        SecurityEvent.is_archived == False,
        SecurityEvent.decision == "Blocked"
    ).count()

    # Pending approvals
    pending_approvals = db.query(ApprovalRequest).filter(ApprovalRequest.status == "Pending").count()

    # Risk distribution
    risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    dist_rows = db.query(
        SecurityEvent.risk_level,
        func.count(SecurityEvent.id)
    ).filter(SecurityEvent.is_archived == False).group_by(SecurityEvent.risk_level).all()
    for level, count in dist_rows:
        if level in risk_counts:
            risk_counts[level] = count

    # Recent events (up to 6)
    recent_events = db.query(SecurityEvent).filter(
        SecurityEvent.is_archived == False
    ).order_by(desc(SecurityEvent.id)).limit(6).all()

    # Real activity timeline calculated from actual events partitioned across 7 chronological intervals
    all_event_ids = [e.id for e in db.query(SecurityEvent.id).filter(SecurityEvent.is_archived == False).order_by(SecurityEvent.id.asc()).all()]
    timeline = [0] * 7
    if all_event_ids:
        bin_size = max(1.0, len(all_event_ids) / 7.0)
        for idx in range(len(all_event_ids)):
            bin_idx = min(6, int(idx / bin_size))
            timeline[bin_idx] += 1

    return DashboardResponse(
        total_events=total_events,
        threats_detected=threats_detected,
        actions_blocked=actions_blocked,
        pending_approvals=pending_approvals,
        risk_distribution=risk_counts,
        recent_events=[format_event_response(e) for e in recent_events],
        activity_timeline=timeline,
        protection_modules=PROTECTION_MODULES
    )
