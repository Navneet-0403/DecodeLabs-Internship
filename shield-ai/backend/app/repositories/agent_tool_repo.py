from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.agent_tool import AgentTool
from ..models.agent import Agent
from ..models.tool import Tool
from ..database.base import utc_now_iso

class AgentToolRepository:
    @staticmethod
    def get_all(db: Session) -> List[AgentTool]:
        return db.query(AgentTool).order_by(AgentTool.id.asc()).all()

    @staticmethod
    def get_by_agent_and_tool(db: Session, agent_id: int, tool_id: int) -> Optional[AgentTool]:
        return db.query(AgentTool).filter(
            AgentTool.agent_id == agent_id,
            AgentTool.tool_id == tool_id
        ).first()

    @staticmethod
    def get_all_for_agent(db: Session, agent_id: int) -> List[AgentTool]:
        return db.query(AgentTool).filter(AgentTool.agent_id == agent_id).all()

    @staticmethod
    def assign(db: Session, agent_id: int, tool_id: int, permission_status: str) -> AgentTool:
        now = utc_now_iso()
        existing = AgentToolRepository.get_by_agent_and_tool(db, agent_id, tool_id)
        if existing:
            existing.permission_status = permission_status
            existing.updated_at = now
            db.commit()
            db.refresh(existing)
            return existing

        assignment = AgentTool(
            agent_id=agent_id,
            tool_id=tool_id,
            permission_status=permission_status,
            created_at=now,
            updated_at=now
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def update_permission(db: Session, assignment: AgentTool, new_status: str) -> AgentTool:
        assignment.permission_status = new_status
        assignment.updated_at = utc_now_iso()
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def delete(db: Session, assignment: AgentTool) -> None:
        db.delete(assignment)
        db.commit()
