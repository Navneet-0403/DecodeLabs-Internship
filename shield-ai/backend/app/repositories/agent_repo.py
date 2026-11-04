from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.agent import Agent
from ..schemas.agent import AgentCreate, AgentUpdate
from ..database.base import utc_now_iso

class AgentRepository:
    @staticmethod
    def get_all(db: Session, active_only: bool = False) -> List[Agent]:
        query = db.query(Agent)
        if active_only:
            query = query.filter(Agent.is_active == True)
        return query.order_by(Agent.id.asc()).all()

    @staticmethod
    def get_by_id(db: Session, agent_id: int) -> Optional[Agent]:
        return db.query(Agent).filter(Agent.id == agent_id).first()

    @staticmethod
    def get_by_code(db: Session, agent_code: str) -> Optional[Agent]:
        return db.query(Agent).filter(Agent.agent_code == agent_code).first()

    @staticmethod
    def get_by_identifier(db: Session, identifier: str) -> Optional[Agent]:
        # 1. Match code directly
        agent = db.query(Agent).filter(Agent.agent_code == identifier).first()
        if agent:
            return agent
        # 2. Match numeric ID
        try:
            aid = int(identifier)
            agent = db.query(Agent).filter(Agent.id == aid).first()
            if agent:
                return agent
        except ValueError:
            pass
        # 3. Match by name or slug
        slug = identifier.lower().replace("-", " ")
        all_agents = db.query(Agent).order_by(Agent.id.asc()).all()
        for a in all_agents:
            if a.name.lower() == slug or a.name.lower() == identifier.lower():
                return a
        # 4. Match 0-based index
        try:
            idx = int(identifier)
            if 0 <= idx < len(all_agents):
                return all_agents[idx]
        except ValueError:
            pass
        return None

    @staticmethod
    def create(db: Session, obj_in: AgentCreate) -> Agent:
        now = utc_now_iso()
        code = obj_in.agent_code
        if not code:
            count = db.query(Agent).count()
            code = f"agent-{count + 1}"
        agent = Agent(
            agent_code=code,
            name=obj_in.name,
            agent_type=obj_in.agent_type,
            status=obj_in.status,
            description=obj_in.description,
            created_at=now,
            updated_at=now,
            is_active=obj_in.is_active
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def update(db: Session, agent: Agent, obj_in: AgentUpdate) -> Agent:
        now = utc_now_iso()
        if obj_in.name is not None:
            agent.name = obj_in.name
        if obj_in.agent_type is not None:
            agent.agent_type = obj_in.agent_type
        if obj_in.status is not None:
            agent.status = obj_in.status
        if obj_in.description is not None:
            agent.description = obj_in.description
        if obj_in.is_active is not None:
            agent.is_active = obj_in.is_active
        agent.updated_at = now
        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def soft_delete(db: Session, agent: Agent) -> Agent:
        now = utc_now_iso()
        agent.is_active = False
        agent.status = "Deactivated"
        agent.updated_at = now
        db.commit()
        db.refresh(agent)
        return agent
