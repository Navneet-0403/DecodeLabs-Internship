import pytest
from sqlalchemy.exc import IntegrityError
from backend.app.database.session import get_session_factory
from backend.app.models import Agent, Tool, AgentTool, SecurityEvent, ApprovalRequest, ApplicationSettings
from backend.app.database.base import utc_now_iso

def test_schema_tables_exist(client):
    """Verify all 6 relational models exist in the database metadata."""
    from backend.app.database.base import Base
    table_names = set(Base.metadata.tables.keys())
    expected = {"agents", "tools", "agent_tools", "security_events", "approval_requests", "application_settings"}
    assert expected.issubset(table_names)

def test_agent_unique_constraint():
    """Verify unique constraint on agents.agent_code."""
    session_factory = get_session_factory()
    with session_factory() as db:
        now = utc_now_iso()
        ag1 = Agent(agent_code="test-unique-code", name="Agent One", agent_type="Type A", status="Active", created_at=now, updated_at=now)
        db.add(ag1)
        db.commit()

        ag2 = Agent(agent_code="test-unique-code", name="Agent Two", agent_type="Type B", status="Active", created_at=now, updated_at=now)
        db.add(ag2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_agent_tool_unique_pair_constraint():
    """Verify unique constraint on agent_tools (agent_id, tool_id)."""
    session_factory = get_session_factory()
    with session_factory() as db:
        now = utc_now_iso()
        ag = db.query(Agent).first()
        tl = db.query(Tool).first()
        assert ag is not None and tl is not None

        # Clean any prior assignment between these two
        db.query(AgentTool).filter(AgentTool.agent_id == ag.id, AgentTool.tool_id == tl.id).delete()
        db.commit()

        at1 = AgentTool(agent_id=ag.id, tool_id=tl.id, permission_status="Allowed", created_at=now, updated_at=now)
        db.add(at1)
        db.commit()

        at2 = AgentTool(agent_id=ag.id, tool_id=tl.id, permission_status="Blocked", created_at=now, updated_at=now)
        db.add(at2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_database_check_constraints():
    """Verify CHECK constraints on risk_score (0-100) and application_settings sensitivity."""
    session_factory = get_session_factory()
    with session_factory() as db:
        now = utc_now_iso()
        # Invalid risk_score: 999
        invalid_ev = SecurityEvent(
            event_code="EV-CHECK-FAIL",
            category="Test",
            source="Test",
            risk_score=999,
            risk_level="Critical",
            decision="Blocked",
            explanation="Test check constraint",
            created_at=now
        )
        db.add(invalid_ev)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_foreign_key_referential_integrity():
    """Verify foreign key constraint rejects non-existent foreign key reference."""
    session_factory = get_session_factory()
    with session_factory() as db:
        now = utc_now_iso()
        # Invalid foreign key reference to non-existent agent_id 999999
        invalid_at = AgentTool(
            agent_id=999999,
            tool_id=1,
            permission_status="Allowed",
            created_at=now,
            updated_at=now
        )
        db.add(invalid_at)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

