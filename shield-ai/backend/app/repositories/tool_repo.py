from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.tool import Tool
from ..schemas.tool import ToolCreate, ToolUpdate
from ..database.base import utc_now_iso

class ToolRepository:
    @staticmethod
    def get_all(db: Session, active_only: bool = False) -> List[Tool]:
        query = db.query(Tool)
        if active_only:
            query = query.filter(Tool.is_active == True)
        return query.order_by(Tool.id.asc()).all()

    @staticmethod
    def get_by_id(db: Session, tool_id: int) -> Optional[Tool]:
        return db.query(Tool).filter(Tool.id == tool_id).first()

    @staticmethod
    def get_by_code(db: Session, tool_code: str) -> Optional[Tool]:
        return db.query(Tool).filter(Tool.tool_code == tool_code).first()

    @staticmethod
    def get_by_identifier(db: Session, identifier: str) -> Optional[Tool]:
        # 1. Match tool_code directly
        tool = db.query(Tool).filter(Tool.tool_code == identifier).first()
        if tool:
            return tool
        # 2. Match numeric ID
        try:
            tid = int(identifier)
            tool = db.query(Tool).filter(Tool.id == tid).first()
            if tool:
                return tool
        except ValueError:
            pass
        # 3. Match by name or slug
        slug = identifier.lower().replace("-", " ")
        all_tools = db.query(Tool).order_by(Tool.id.asc()).all()
        for t in all_tools:
            if t.name.lower() == slug or t.name.lower() == identifier.lower():
                return t
        # 4. Match 0-based offset
        try:
            idx = int(identifier)
            if 0 <= idx < len(all_tools):
                return all_tools[idx]
        except ValueError:
            pass
        return None

    @staticmethod
    def create(db: Session, obj_in: ToolCreate) -> Tool:
        now = utc_now_iso()
        code = obj_in.tool_code
        if not code:
            count = db.query(Tool).count()
            code = f"tool-{count + 1}"
        tool = Tool(
            tool_code=code,
            name=obj_in.name,
            description=obj_in.description,
            risk_level=obj_in.risk_level,
            is_active=obj_in.is_active,
            created_at=now,
            updated_at=now
        )
        db.add(tool)
        db.commit()
        db.refresh(tool)
        return tool

    @staticmethod
    def update(db: Session, tool: Tool, obj_in: ToolUpdate) -> Tool:
        now = utc_now_iso()
        if obj_in.name is not None:
            tool.name = obj_in.name
        if obj_in.description is not None:
            tool.description = obj_in.description
        if obj_in.risk_level is not None:
            tool.risk_level = obj_in.risk_level
        if obj_in.is_active is not None:
            tool.is_active = obj_in.is_active
        tool.updated_at = now
        db.commit()
        db.refresh(tool)
        return tool

    @staticmethod
    def soft_delete(db: Session, tool: Tool) -> Tool:
        now = utc_now_iso()
        tool.is_active = False
        tool.updated_at = now
        db.commit()
        db.refresh(tool)
        return tool
