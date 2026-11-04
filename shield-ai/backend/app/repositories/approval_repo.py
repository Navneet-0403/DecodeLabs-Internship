from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.approval import ApprovalRequest
from ..schemas.approval import ApprovalCreate, ApprovalUpdate
from ..database.base import utc_now_iso

class ApprovalRepository:
    @staticmethod
    def get_all(db: Session, status_filter: Optional[str] = None) -> List[ApprovalRequest]:
        query = db.query(ApprovalRequest)
        if status_filter:
            query = query.filter(ApprovalRequest.status == status_filter)
        return query.order_by(desc(ApprovalRequest.id)).all()

    @staticmethod
    def get_by_code(db: Session, approval_code: str) -> Optional[ApprovalRequest]:
        return db.query(ApprovalRequest).filter(ApprovalRequest.approval_code == approval_code).first()

    @staticmethod
    def get_by_id(db: Session, approval_id: int) -> Optional[ApprovalRequest]:
        return db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()

    @staticmethod
    def get_by_identifier(db: Session, identifier: str) -> Optional[ApprovalRequest]:
        appr = db.query(ApprovalRequest).filter(ApprovalRequest.approval_code == identifier).first()
        if appr:
            return appr
        try:
            aid = int(identifier)
            return db.query(ApprovalRequest).filter(ApprovalRequest.id == aid).first()
        except ValueError:
            pass
        return None

    @staticmethod
    def generate_next_code(db: Session) -> str:
        last = db.query(ApprovalRequest).order_by(desc(ApprovalRequest.id)).first()
        if last and last.approval_code and last.approval_code.startswith("AP-"):
            try:
                num = int(last.approval_code.split("-")[1])
                return f"AP-{num + 1}"
            except ValueError:
                pass
        count = db.query(ApprovalRequest).count()
        return f"AP-{200 + count + 1}"

    @staticmethod
    def create(db: Session, obj_in: ApprovalCreate) -> ApprovalRequest:
        code = ApprovalRepository.generate_next_code(db)
        now = utc_now_iso()
        approval = ApprovalRequest(
            approval_code=code,
            agent_id=obj_in.agent_id,
            tool_id=obj_in.tool_id,
            event_id=obj_in.event_id,
            operation=obj_in.operation,
            risk_level=obj_in.risk_level,
            reason=obj_in.reason,
            status="Pending",
            created_at=now,
            updated_at=now
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def update(db: Session, approval: ApprovalRequest, obj_in: ApprovalUpdate) -> ApprovalRequest:
        now = utc_now_iso()
        if obj_in.operation is not None:
            approval.operation = obj_in.operation
        if obj_in.reason is not None:
            approval.reason = obj_in.reason
        if obj_in.status is not None:
            approval.status = obj_in.status
        approval.updated_at = now
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def cancel(db: Session, approval: ApprovalRequest) -> ApprovalRequest:
        now = utc_now_iso()
        approval.status = "Cancelled"
        approval.updated_at = now
        db.commit()
        db.refresh(approval)
        return approval
