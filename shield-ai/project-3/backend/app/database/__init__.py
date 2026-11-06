from .connection import get_database_url, get_engine, engine
from .base import Base, utc_now_iso
from .session import get_db, get_session_factory
from .migration import migrate_and_init_db, INITIAL_AGENT_TOOL_MAPPINGS
from ..models import Agent, Tool, AgentTool, SecurityEvent, ApprovalRequest, ApplicationSettings
from sqlalchemy import text

def init_db():
    migrate_and_init_db()

def check_db_health() -> bool:
    try:
        eng = get_engine()
        with eng.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            return result is not None and result[0] == 1
    except Exception:
        return False

def reset_demo_events_and_approvals():
    session_factory = get_session_factory()
    with session_factory() as db:
        db.query(ApprovalRequest).delete()
        db.query(SecurityEvent).delete()
        db.commit()

        now = utc_now_iso()
        agents = {a.name: a.id for a in db.query(Agent).all()}
        tools = {t.name: t.id for t in db.query(Tool).all()}

        seed_events = [
            ("EV-1001", agents.get("Research Assistant"), tools.get("Public Knowledge Search"), "Prompt injection attempt", "Research Assistant", 85, "Critical", "Blocked", "Instruction override matched.", "seed"),
            ("EV-1002", agents.get("Data Analyst"), tools.get("Customer Data Access"), "Sensitive data exposure", "Data Analyst", 70, "High", "Approval required", "API-key-like pattern found in output.", "seed"),
            ("EV-1003", agents.get("File Management Agent"), tools.get("File Deletion"), "Unauthorized file access", "File Management Agent", 70, "High", "Blocked", "Tool denied by policy.", "seed"),
            ("EV-1004", agents.get("Email Assistant"), tools.get("External Email Sender"), "External email action", "Email Assistant", 70, "High", "Approval required", "External recipient needs review.", "seed"),
            ("EV-1005", agents.get("Research Assistant"), tools.get("Public Knowledge Search"), "Approved knowledge-base search", "Research Assistant", 15, "Low", "Allowed", "Public search permitted.", "seed"),
            ("EV-1006", agents.get("Research Assistant"), tools.get("Document Reader"), "Safe prompt allowed", "Research Assistant", 10, "Low", "Allowed", "No indicators.", "seed"),
            ("EV-1007", agents.get("Email Assistant"), tools.get("External Email Sender"), "Sensitive data exposure", "Email Assistant", 45, "Medium", "Allowed", "Phone number masked.", "seed"),
        ]

        for ev_code, ag_id, t_id, cat, src, score, risk, dec, why, ev_src in seed_events:
            ev = SecurityEvent(
                event_code=ev_code,
                agent_id=ag_id,
                tool_id=t_id,
                category=cat,
                source=src,
                risk_score=score,
                risk_level=risk,
                decision=dec,
                explanation=why,
                event_source=ev_src,
                created_at=now,
                is_archived=False
            )
            db.add(ev)

        seed_approvals = [
            ("AP-201", agents.get("Email Assistant"), tools.get("External Email Sender"), "Send external email with report", "High", "External recipient", "Pending"),
            ("AP-202", agents.get("Data Analyst"), tools.get("Customer Data Access"), "Access protected customer info", "High", "Restricted data", "Pending"),
            ("AP-203", agents.get("Data Analyst"), tools.get("Data Export"), "Export sensitive document", "Critical", "Protected export", "Pending"),
            ("AP-204", agents.get("File Management Agent"), tools.get("File Deletion"), "High-impact file operation", "High", "Bulk change", "Pending"),
        ]

        for ap_code, ag_id, t_id, op, risk, why, st in seed_approvals:
            appr = ApprovalRequest(
                approval_code=ap_code,
                agent_id=ag_id,
                tool_id=t_id,
                event_id=None,
                operation=op,
                risk_level=risk,
                reason=why,
                status=st,
                created_at=now,
                updated_at=now
            )
            db.add(appr)

        db.commit()

def reset_tool_permissions():
    session_factory = get_session_factory()
    with session_factory() as db:
        agents = {a.agent_code: a.id for a in db.query(Agent).all()}
        tools = {t.tool_code: t.id for t in db.query(Tool).all()}
        now = utc_now_iso()

        for ag_code, t_code, perm in INITIAL_AGENT_TOOL_MAPPINGS:
            ag_id = agents.get(ag_code)
            t_id = tools.get(t_code)
            if ag_id and t_id:
                at = db.query(AgentTool).filter(AgentTool.agent_id == ag_id, AgentTool.tool_id == t_id).first()
                if at:
                    at.permission_status = perm
                    at.updated_at = now
                else:
                    at = AgentTool(
                        agent_id=ag_id,
                        tool_id=t_id,
                        permission_status=perm,
                        created_at=now,
                        updated_at=now
                    )
                    db.add(at)
        db.commit()

__all__ = [
    "get_database_url",
    "get_engine",
    "engine",
    "Base",
    "utc_now_iso",
    "get_db",
    "get_session_factory",
    "init_db",
    "check_db_health",
    "reset_demo_events_and_approvals",
    "reset_tool_permissions",
]
