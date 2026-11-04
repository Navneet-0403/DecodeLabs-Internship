from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..repositories.event_repo import SecurityEventRepository
from ..schemas.security_event import EventCreate, EventUpdate, EventResponse, EventListResponse
from ..exceptions import APIException

router = APIRouter(prefix="/api/events", tags=["Threat Logs & Security Event CRUD"])

def format_event_response(ev) -> EventResponse:
    return EventResponse(
        id=ev.id,
        event_id=ev.event_code,
        event_code=ev.event_code,
        agent_id=ev.agent_id,
        tool_id=ev.tool_id,
        category=ev.category,
        source=ev.source,
        risk_score=ev.risk_score,
        risk_level=ev.risk_level,
        decision=ev.decision,
        explanation=ev.explanation,
        event_source=ev.event_source,
        created_at=ev.created_at,
        is_archived=ev.is_archived
    )

@router.get("", response_model=EventListResponse)
def get_events(
    q: Optional[str] = Query(None, description="Search query across category, source, explanation, event_code"),
    risk: Optional[str] = Query(None, description="Filter by risk level"),
    category: Optional[str] = Query(None, description="Filter by category"),
    decision: Optional[str] = Query(None, description="Filter by decision"),
    include_archived: bool = Query(False, description="Include archived security events"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """Retrieve security audit events with search, filtering, and pagination."""
    events, total = SecurityEventRepository.get_all(
        db, q=q, risk=risk, category=category, decision=decision,
        include_archived=include_archived, limit=limit, offset=offset
    )
    return EventListResponse(
        events=[format_event_response(e) for e in events],
        total=total,
        limit=limit,
        offset=offset
    )

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    """Create a security event through a validated internal event-creation operation."""
    event = SecurityEventRepository.create(db, event_in)
    return format_event_response(event)

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Retrieve complete information about an individual security event."""
    event = SecurityEventRepository.get_by_identifier(db, event_id)
    if not event:
        raise APIException(status_code=404, code="EVENT_NOT_FOUND", message=f"Security event with ID '{event_id}' was not found.")
    return format_event_response(event)

@router.put("/{event_id}", response_model=EventResponse)
def update_event_metadata(event_id: str, update_in: EventUpdate, db: Session = Depends(get_db)):
    """Update permitted administrative metadata (category, explanation, archived status), not the immutable audit decision."""
    event = SecurityEventRepository.get_by_identifier(db, event_id)
    if not event:
        raise APIException(status_code=404, code="EVENT_NOT_FOUND", message=f"Security event with ID '{event_id}' was not found.")
    updated = SecurityEventRepository.update(db, event, update_in)
    return format_event_response(updated)

@router.delete("/{event_id}", response_model=EventResponse)
def archive_event(event_id: str, db: Session = Depends(get_db)):
    """Safely archive / soft-delete a security event without destroying historical audit trails."""
    event = SecurityEventRepository.get_by_identifier(db, event_id)
    if not event:
        raise APIException(status_code=404, code="EVENT_NOT_FOUND", message=f"Security event with ID '{event_id}' was not found.")
    archived = SecurityEventRepository.soft_delete(db, event)
    return format_event_response(archived)

@router.delete("/{event_id}/purge", status_code=status.HTTP_204_NO_CONTENT)
def purge_event(event_id: str, db: Session = Depends(get_db)):
    """Permanently delete an event, returning HTTP 204 No Content with an empty body."""
    event = SecurityEventRepository.get_by_identifier(db, event_id)
    if not event:
        raise APIException(status_code=404, code="EVENT_NOT_FOUND", message=f"Security event with ID '{event_id}' was not found.")
    SecurityEventRepository.delete(db, event)
    return None
