from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database.base import Base, utc_now_iso

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(String(50), nullable=False, default=utc_now_iso)
    updated_at = Column(String(50), nullable=False, default=utc_now_iso)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    agent_tools = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")
    tools = relationship("Tool", secondary="agent_tools", back_populates="agents", viewonly=True)
    security_events = relationship("SecurityEvent", back_populates="agent")
    approval_requests = relationship("ApprovalRequest", back_populates="agent")
