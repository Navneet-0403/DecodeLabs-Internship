from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..database.base import Base, utc_now_iso

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    approval_code = Column(String(50), unique=True, nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(Integer, ForeignKey("security_events.id", ondelete="SET NULL"), nullable=True)
    operation = Column(String(255), nullable=False)
    risk_level = Column(String(20), nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, default="Pending")
    created_at = Column(String(50), nullable=False, default=utc_now_iso)
    updated_at = Column(String(50), nullable=False, default=utc_now_iso)

    __table_args__ = (
        CheckConstraint("risk_level IN ('Low', 'Medium', 'High', 'Critical')", name="ck_approval_risk_level"),
        CheckConstraint("status IN ('Pending', 'Approved', 'Rejected', 'Cancelled')", name="ck_approval_status"),
    )

    # Relationships
    agent = relationship("Agent", back_populates="approval_requests")
    tool = relationship("Tool", back_populates="approval_requests")
    security_event = relationship("SecurityEvent", back_populates="approval_requests")

