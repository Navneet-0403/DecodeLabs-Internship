from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from ..database.base import Base, utc_now_iso

class AgentTool(Base):
    __tablename__ = "agent_tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    permission_status = Column(String(30), nullable=False)
    created_at = Column(String(50), nullable=False, default=utc_now_iso)
    updated_at = Column(String(50), nullable=False, default=utc_now_iso)

    __table_args__ = (
        UniqueConstraint("agent_id", "tool_id", name="uq_agent_tool_pair"),
        CheckConstraint("permission_status IN ('Allowed', 'Approval Required', 'Restricted', 'Blocked')", name="ck_agent_tool_permission"),
    )

    # Relationships
    agent = relationship("Agent", back_populates="agent_tools")
    tool = relationship("Tool", back_populates="agent_tools")
