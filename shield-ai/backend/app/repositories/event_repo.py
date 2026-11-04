from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from ..models.security_event import SecurityEvent
from ..schemas.security_event import EventCreate, EventUpdate
from ..database.base import utc_now_iso

class SecurityEventRepository:
    @staticmethod
    def get_all(
        db: Session,
        q: Optional[str] = None,
        risk: Optional[str] = None,
        category: Optional[str] = None,
        decision: Optional[str] = None,
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[SecurityEvent], int]:
        query = db.query(SecurityEvent)
        if not include_archived:
            query = query.filter(SecurityEvent.is_archived == False)
        if risk:
            query = query.filter(SecurityEvent.risk_level == risk)
        if category:
            query = query.filter(SecurityEvent.category == category)
        if decision:
            query = query.filter(SecurityEvent.decision == decision)
        if q:
            pattern = f"%{q.strip().lower()}%"
            query = query.filter(
                or_(
                    SecurityEvent.category.ilike(pattern),
                    SecurityEvent.source.ilike(pattern),
                    SecurityEvent.explanation.ilike(pattern),
                    SecurityEvent.event_code.ilike(pattern)
                )
            )

        total = query.count()
        events = query.order_by(desc(SecurityEvent.id)).offset(offset).limit(limit).all()
        return events, total

    @staticmethod
    def get_by_code(db: Session, event_code: str) -> Optional[SecurityEvent]:
        return db.query(SecurityEvent).filter(SecurityEvent.event_code == event_code).first()

    @staticmethod
    def get_by_id(db: Session, event_id: int) -> Optional[SecurityEvent]:
        return db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()

    @staticmethod
    def get_by_identifier(db: Session, identifier: str) -> Optional[SecurityEvent]:
        event = db.query(SecurityEvent).filter(SecurityEvent.event_code == identifier).first()
        if event:
            return event
        try:
            eid = int(identifier)
            return db.query(SecurityEvent).filter(SecurityEvent.id == eid).first()
        except ValueError:
            pass
        return None

    @staticmethod
    def generate_next_code(db: Session) -> str:
        last = db.query(SecurityEvent).order_by(desc(SecurityEvent.id)).first()
        if last and last.event_code and last.event_code.startswith("EV-"):
            try:
                num = int(last.event_code.split("-")[1])
                return f"EV-{num + 1}"
            except ValueError:
                pass
        count = db.query(SecurityEvent).count()
        return f"EV-{1000 + count + 1}"

    @staticmethod
    def create(db: Session, obj_in: EventCreate) -> SecurityEvent:
        code = SecurityEventRepository.generate_next_code(db)
        now = utc_now_iso()
        event = SecurityEvent(
            event_code=code,
            agent_id=obj_in.agent_id,
            tool_id=obj_in.tool_id,
            category=obj_in.category,
            source=obj_in.source,
            risk_score=obj_in.risk_score,
            risk_level=obj_in.risk_level,
            decision=obj_in.decision,
            explanation=obj_in.explanation,
            event_source=obj_in.event_source,
            created_at=now,
            is_archived=False
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update(db: Session, event: SecurityEvent, obj_in: EventUpdate) -> SecurityEvent:
        if obj_in.category is not None:
            event.category = obj_in.category
        if obj_in.explanation is not None:
            event.explanation = obj_in.explanation
        if obj_in.is_archived is not None:
            event.is_archived = obj_in.is_archived
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def soft_delete(db: Session, event: SecurityEvent) -> SecurityEvent:
        event.is_archived = True
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete(db: Session, event: SecurityEvent) -> None:
        db.delete(event)
        db.commit()

