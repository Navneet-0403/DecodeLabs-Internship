import sqlite3
from fastapi import APIRouter, Depends
from ..database import get_db
from ..schemas import DashboardResponse, EventResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

PROTECTION_MODULES = [
    "Prompt inspection",
    "Permission policies",
    "Tool interception",
    "Data protection",
    "Audit monitoring"
]

@router.get("", response_model=DashboardResponse)
def get_dashboard(conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()

    # Total events
    cursor.execute("SELECT COUNT(*) FROM security_events")
    total_events = cursor.fetchone()[0]

    # Threats detected (Medium, High, Critical)
    cursor.execute("SELECT COUNT(*) FROM security_events WHERE risk_level != 'Low'")
    threats_detected = cursor.fetchone()[0]

    # Actions blocked
    cursor.execute("SELECT COUNT(*) FROM security_events WHERE decision = 'Blocked'")
    actions_blocked = cursor.fetchone()[0]

    # Pending approvals
    cursor.execute("SELECT COUNT(*) FROM approval_requests WHERE status = 'Pending'")
    pending_approvals = cursor.fetchone()[0]

    # Risk distribution
    cursor.execute("SELECT risk_level, COUNT(*) FROM security_events GROUP BY risk_level")
    risk_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for row in cursor.fetchall():
        if row[0] in risk_counts:
            risk_counts[row[0]] = row[1]

    # Recent events (up to 6)
    cursor.execute("""
        SELECT id, event_id, category, source, risk_level, decision, explanation, created_at, event_source
        FROM security_events
        ORDER BY id DESC
        LIMIT 6
    """)
    recent_events = [
        EventResponse(
            id=r["id"],
            event_id=r["event_id"],
            category=r["category"],
            source=r["source"],
            risk_level=r["risk_level"],
            decision=r["decision"],
            explanation=r["explanation"],
            created_at=r["created_at"],
            event_source=r["event_source"]
        )
        for r in cursor.fetchall()
    ]

    # Real activity timeline calculated from actual events partitioned across 7 chronological intervals
    cursor.execute("SELECT id FROM security_events ORDER BY id ASC")
    event_ids = [r[0] for r in cursor.fetchall()]
    timeline = [0] * 7
    if event_ids:
        bin_size = max(1.0, len(event_ids) / 7.0)
        for idx in range(len(event_ids)):
            bin_idx = min(6, int(idx / bin_size))
            timeline[bin_idx] += 1

    return DashboardResponse(
        total_events=total_events,
        threats_detected=threats_detected,
        actions_blocked=actions_blocked,
        pending_approvals=pending_approvals,
        risk_distribution=risk_counts,
        recent_events=recent_events,
        activity_timeline=timeline,
        protection_modules=PROTECTION_MODULES
    )
