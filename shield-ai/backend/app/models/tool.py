from sqlalchemy import Column, Integer, String, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from ..database.base import Base, utc_now_iso

class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tool_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    risk_level = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String(50), nullable=False, default=utc_now_iso)
    updated_at = Column(String(50), nullable=False, default=utc_now_iso)

    __table_args__ = (
        CheckConstraint("risk_level IN ('Low', 'Medium', 'High', 'Critical')", name="ck_tool_risk_level"),
    )

    # Relationships
    agent_tools = relationship("AgentTool", back_populates="tool", cascade="all, delete-orphan")
    agents = relationship("Agent", secondary="agent_tools", back_populates="tools", viewonly=True)
    security_events = relationship("SecurityEvent", back_populates="tool")
    approval_requests = relationship("ApprovalRequest", back_populates="tool")
