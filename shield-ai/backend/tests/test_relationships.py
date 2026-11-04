import pytest
from backend.app.database.session import get_session_factory
from backend.app.models import Agent, Tool, AgentTool, SecurityEvent, ApprovalRequest
from backend.app.database.base import utc_now_iso

def test_agent_to_events_one_to_many():
    """Verify 1:M relationship where an Agent has multiple SecurityEvent instances."""
    session_factory = get_session_factory()
    with session_factory() as db:
        agent = db.query(Agent).filter(Agent.agent_code == "agent-1").first()
        assert agent is not None
        # Add 2 events for agent-1
        now = utc_now_iso()
        ev1 = SecurityEvent(event_code="EV-REL-1", agent_id=agent.id, category="Test Rel", source=agent.name, risk_score=20, risk_level="Low", decision="Allowed", explanation="Rel test 1", created_at=now)
        ev2 = SecurityEvent(event_code="EV-REL-2", agent_id=agent.id, category="Test Rel", source=agent.name, risk_score=30, risk_level="Medium", decision="Approval required", explanation="Rel test 2", created_at=now)
        db.add_all([ev1, ev2])
        db.commit()

        # Query agent and check relationship
        db.refresh(agent)
        event_codes = [e.event_code for e in agent.security_events]
        assert "EV-REL-1" in event_codes
        assert "EV-REL-2" in event_codes

def test_agent_to_approvals_one_to_many():
    """Verify 1:M relationship where an Agent has multiple ApprovalRequest instances."""
    session_factory = get_session_factory()
    with session_factory() as db:
        agent = db.query(Agent).filter(Agent.agent_code == "agent-2").first()
        assert agent is not None
        now = utc_now_iso()
        ap1 = ApprovalRequest(approval_code="AP-REL-1", agent_id=agent.id, operation="Op 1", risk_level="High", reason="Test", status="Pending", created_at=now, updated_at=now)
        ap2 = ApprovalRequest(approval_code="AP-REL-2", agent_id=agent.id, operation="Op 2", risk_level="Medium", reason="Test", status="Pending", created_at=now, updated_at=now)
        db.add_all([ap1, ap2])
        db.commit()

        db.refresh(agent)
        approval_codes = [a.approval_code for a in agent.approval_requests]
        assert "AP-REL-1" in approval_codes
        assert "AP-REL-2" in approval_codes

def test_agents_tools_many_to_many():
    """Verify M:M relationship between Agents and Tools via agent_tools junction table."""
    session_factory = get_session_factory()
    with session_factory() as db:
        now = utc_now_iso()
        ag1 = db.query(Agent).filter(Agent.agent_code == "agent-1").first()
        ag2 = db.query(Agent).filter(Agent.agent_code == "agent-2").first()
        tool = db.query(Tool).filter(Tool.tool_code == "tool-1").first()

        assert ag1 is not None and ag2 is not None and tool is not None

        # Clean assignments for tool-1
        db.query(AgentTool).filter(AgentTool.tool_id == tool.id).delete()
        db.commit()

        # Assign tool-1 to both agent-1 and agent-2 (M:M)
        at1 = AgentTool(agent_id=ag1.id, tool_id=tool.id, permission_status="Allowed", created_at=now, updated_at=now)
        at2 = AgentTool(agent_id=ag2.id, tool_id=tool.id, permission_status="Approval Required", created_at=now, updated_at=now)
        db.add_all([at1, at2])
        db.commit()

        # Query tool and verify it is mapped to multiple agents
        db.refresh(tool)
        associated_agent_codes = [at.agent.agent_code for at in tool.agent_tools]
        assert "agent-1" in associated_agent_codes
        assert "agent-2" in associated_agent_codes

        # Query agent-1 and check its tool permissions
        db.refresh(ag1)
        ag1_tools = [at.tool.tool_code for at in ag1.agent_tools]
        assert "tool-1" in ag1_tools

