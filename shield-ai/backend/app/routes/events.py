import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, Query
from ..database import get_db
from ..schemas import EventResponse, EventListResponse
from ..exceptions import APIException

router = APIRouter(prefix="/api/events", tags=["Threat Logs"])

@router.get("", response_model=EventListResponse)
def get_events(
    q: Optional[str] = Query(None, description="Search query across category, source, explanation, event_id"),
    risk: Optional[str] = Query(None, description="Filter by risk level"),
    category: Optional[str] = Query(None, description="Filter by category"),
    decision: Optional[str] = Query(None, description="Filter by decision"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    conn: sqlite3.Connection = Depends(get_db)
):
    cursor = conn.cursor()
    conditions = []
    params = []

    if q:
        search_pattern = f"%{q.strip().lower()}%"
        conditions.append("(LOWER(category) LIKE ? OR LOWER(source) LIKE ? OR LOWER(explanation) LIKE ? OR LOWER(event_id) LIKE ?)")
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

    if risk:
        conditions.append("risk_level = ?")
        params.append(risk)

    if category:
        conditions.append("category = ?")
        params.append(category)

    if decision:
        conditions.append("decision = ?")
        params.append(decision)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Count total matching
    count_query = f"SELECT COUNT(*) FROM security_events{where_clause}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Query paginated rows
    query = f"""
        SELECT id, event_id, category, source, risk_level, decision, explanation, created_at, event_source
        FROM security_events
        {where_clause}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [limit, offset])
    rows = cursor.fetchall()

    events = [
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
        for r in rows
    ]

    return EventListResponse(
        events=events,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, event_id, category, source, risk_level, decision, explanation, created_at, event_source
        FROM security_events
        WHERE event_id = ?
    """, (event_id,))
    row = cursor.fetchone()

    if not row:
        raise APIException(
            status_code=404,
            code="EVENT_NOT_FOUND",
            message=f"Security event with ID '{event_id}' was not found."
        )

    return EventResponse(
        id=row["id"],
        event_id=row["event_id"],
        category=row["category"],
        source=row["source"],
        risk_level=row["risk_level"],
        decision=row["decision"],
        explanation=row["explanation"],
        created_at=row["created_at"],
        event_source=row["event_source"]
    )

