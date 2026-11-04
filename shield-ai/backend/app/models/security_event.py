from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..database.base import Base, utc_now_iso

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_code = Column(String(50), unique=True, nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(100), nullable=False)
    source = Column(String(100), nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    decision = Column(String(30), nullable=False)
    explanation = Column(Text, nullable=False)
    event_source = Column(String(50), nullable=False, default="application")
    created_at = Column(String(50), nullable=False, index=True, default=utc_now_iso)
    is_archived = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_security_event_score"),
        CheckConstraint("risk_level IN ('Low', 'Medium', 'High', 'Critical')", name="ck_security_event_level"),
        CheckConstraint("decision IN ('Allowed', 'Approval required', 'Approval Required', 'Blocked')", name="ck_security_event_decision"),
    )

    # Relationships
    agent = relationship("Agent", back_populates="security_events")
    tool = relationship("Tool", back_populates="security_events")
    approval_requests = relationship("ApprovalRequest", back_populates="security_event")

