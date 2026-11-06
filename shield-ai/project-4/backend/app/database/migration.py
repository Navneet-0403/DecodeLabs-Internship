import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from .connection import get_engine, get_database_url
from .base import Base, utc_now_iso
from ..models import Agent, Tool, AgentTool, SecurityEvent, ApprovalRequest, ApplicationSettings

INITIAL_AGENTS = [
    {
        "agent_code": "agent-1",
        "name": "Research Assistant",
        "agent_type": "Retrieval",
        "status": "Active (demo)",
        "description": "Read-only public knowledge base search and document summarization."
    },
    {
        "agent_code": "agent-2",
        "name": "Email Assistant",
        "agent_type": "Messaging",
        "status": "Active (demo)",
        "description": "External communications and message dispatch with human-in-the-loop approvals."
    },
    {
        "agent_code": "agent-3",
        "name": "Data Analyst",
        "agent_type": "Analytics",
        "status": "Active (demo)",
        "description": "Data processing, dataset queries, and restricted customer analytics."
    },
    {
        "agent_code": "agent-4",
        "name": "File Management Agent",
        "agent_type": "Files",
        "status": "Idle (demo)",
        "description": "Protected file system management with deletion prevention safeguards."
    }
]

INITIAL_TOOLS = [
    {
        "tool_code": "tool-1",
        "name": "Public Knowledge Search",
        "description": "Searches approved public sources",
        "risk_level": "Low"
    },
    {
        "tool_code": "tool-2",
        "name": "Approved Database Read",
        "description": "Reads approved datasets",
        "risk_level": "Low"
    },
    {
        "tool_code": "tool-3",
        "name": "Document Reader",
        "description": "Reads shared documents",
        "risk_level": "Low"
    },
    {
        "tool_code": "tool-4",
        "Customer Data Access": "Reads customer records",
        "name": "Customer Data Access",
        "description": "Reads customer records",
        "risk_level": "High"
    },
    {
        "tool_code": "tool-5",
        "name": "External Email Sender",
        "description": "Sends email outside org",
        "risk_level": "High"
    },
    {
        "tool_code": "tool-6",
        "name": "File Deletion",
        "description": "Deletes protected files",
        "risk_level": "Critical"
    },
    {
        "tool_code": "tool-7",
        "name": "Data Export",
        "description": "Exports protected data",
        "risk_level": "Critical"
    }
]

# Baseline agent-tool associations
INITIAL_AGENT_TOOL_MAPPINGS = [
    ("agent-1", "tool-1", "Allowed"),
    ("agent-3", "tool-2", "Allowed"),
    ("agent-1", "tool-3", "Allowed"),
    ("agent-3", "tool-4", "Restricted"),
    ("agent-2", "tool-5", "Approval Required"),
    ("agent-4", "tool-6", "Blocked"),
    ("agent-3", "tool-7", "Blocked"),
]

def migrate_and_init_db():
    """
    Safely initializes all SQLAlchemy ORM models, preserves existing Project 2 records,
    and maps legacy tables into the normalized relational schema.
    """
    engine = get_engine()
    now = utc_now_iso()

    # Step 1: Create all relational tables defined in SQLAlchemy ORM models
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        # Check raw sqlite connection
        raw_conn = conn.connection
        cursor = raw_conn.cursor()

        # Check existing tables in SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}

        # 1. Seed or verify Agents
        cursor.execute("SELECT COUNT(*) FROM agents")
        if cursor.fetchone()[0] == 0:
            for ag in INITIAL_AGENTS:
                cursor.execute("""
                    INSERT INTO agents (agent_code, name, agent_type, status, description, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (ag["agent_code"], ag["name"], ag["agent_type"], ag["status"], ag["description"], now, now))
            raw_conn.commit()

        # Build agent map: name -> id and agent_code -> id
        cursor.execute("SELECT id, agent_code, name FROM agents")
        agent_rows = cursor.fetchall()
        agent_by_name = {row[2]: row[0] for row in agent_rows}
        agent_by_code = {row[1]: row[0] for row in agent_rows}

        # 2. Seed or verify Tools
        cursor.execute("SELECT COUNT(*) FROM tools")
        if cursor.fetchone()[0] == 0:
            for tl in INITIAL_TOOLS:
                cursor.execute("""
                    INSERT INTO tools (tool_code, name, description, risk_level, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                """, (tl["tool_code"], tl["name"], tl["description"], tl["risk_level"], now, now))
            raw_conn.commit()

        # Build tool map: name -> id and tool_code -> id
        cursor.execute("SELECT id, tool_code, name FROM tools")
        tool_rows = cursor.fetchall()
        tool_by_name = {row[2]: row[0] for row in tool_rows}
        tool_by_code = {row[1]: row[0] for row in tool_rows}

        # 3. Seed or verify AgentTools (M:M Junction Table)
        cursor.execute("SELECT COUNT(*) FROM agent_tools")
        if cursor.fetchone()[0] == 0:
            # First check if legacy tool_permissions exists to preserve any user-saved permissions
            if "tool_permissions" in existing_tables:
                cursor.execute("SELECT tool_id, tool_name, assigned_agent, permission_status FROM tool_permissions")
                legacy_tools = cursor.fetchall()
                for t_code, t_name, ag_name, perm in legacy_tools:
                    ag_id = agent_by_name.get(ag_name) or agent_by_code.get("agent-1")
                    t_id = tool_by_code.get(t_code) or tool_by_name.get(t_name)
                    if ag_id and t_id:
                        cursor.execute("""
                            INSERT OR IGNORE INTO agent_tools (agent_id, tool_id, permission_status, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (ag_id, t_id, perm, now, now))
                raw_conn.commit()

            # Ensure all baseline mappings exist
            for ag_code, t_code, perm in INITIAL_AGENT_TOOL_MAPPINGS:
                ag_id = agent_by_code.get(ag_code)
                t_id = tool_by_code.get(t_code)
                if ag_id and t_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO agent_tools (agent_id, tool_id, permission_status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (ag_id, t_id, perm, now, now))
            raw_conn.commit()

        # 4. Seed or verify ApplicationSettings
        cursor.execute("SELECT COUNT(*) FROM application_settings")
        if cursor.fetchone()[0] == 0:
            # Check if legacy settings table has data
            if "settings" in existing_tables:
                cursor.execute("SELECT risk_sensitivity, automatic_critical_blocking, require_high_risk_approval, mask_sensitive_data, notifications_enabled, updated_at FROM settings WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    cursor.execute("""
                        INSERT INTO application_settings (id, risk_sensitivity, automatic_critical_blocking, require_high_risk_approval, mask_sensitive_data, notifications_enabled, updated_at)
                        VALUES (1, ?, ?, ?, ?, ?, ?)
                    """, (float(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4]), row[5]))
            else:
                cursor.execute("""
                    INSERT INTO application_settings (id, risk_sensitivity, automatic_critical_blocking, require_high_risk_approval, mask_sensitive_data, notifications_enabled, updated_at)
                    VALUES (1, 1.0, 1, 1, 1, 1, ?)
                """, (now,))
            raw_conn.commit()

        # 5. Check security_events table schema
        cursor.execute("PRAGMA table_info(security_events)")
        sec_columns = {col[1] for col in cursor.fetchall()}
        if "event_code" not in sec_columns and "event_id" in sec_columns:
            # We have a legacy security_events table. Migrate data safely.
            cursor.execute("ALTER TABLE security_events RENAME TO legacy_security_events")
            raw_conn.commit()
            # Recreate new security_events table from ORM
            Base.metadata.tables["security_events"].create(bind=engine)
            cursor.execute("""
                SELECT id, event_id, category, source, risk_level, decision, explanation, created_at, event_source
                FROM legacy_security_events
            """)
            legacy_events = cursor.fetchall()
            for r in legacy_events:
                # determine score estimate
                score = 85 if r[4] == "Critical" else 70 if r[4] == "High" else 45 if r[4] == "Medium" else 15
                ag_id = agent_by_name.get(r[3])
                # check if explanation or category links to a tool
                t_id = None
                for t_name, tid in tool_by_name.items():
                    if t_name.lower() in r[6].lower() or t_name.lower() in r[2].lower():
                        t_id = tid
                        break
                cursor.execute("""
                    INSERT OR IGNORE INTO security_events (event_code, agent_id, tool_id, category, source, risk_score, risk_level, decision, explanation, event_source, created_at, is_archived)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (r[1], ag_id, t_id, r[2], r[3], score, r[4], r[5], r[6], r[8], r[7]))
            raw_conn.commit()

        # Check approval_requests table schema
        cursor.execute("PRAGMA table_info(approval_requests)")
        appr_columns = {col[1] for col in cursor.fetchall()}
        if "approval_code" not in appr_columns and "approval_id" in appr_columns:
            # We have a legacy approval_requests table. Migrate data safely.
            cursor.execute("ALTER TABLE approval_requests RENAME TO legacy_approval_requests")
            raw_conn.commit()
            # Recreate new approval_requests table from ORM
            Base.metadata.tables["approval_requests"].create(bind=engine)
            cursor.execute("""
                SELECT id, approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at
                FROM legacy_approval_requests
            """)
            legacy_apprs = cursor.fetchall()
            for r in legacy_apprs:
                ag_id = agent_by_name.get(r[2])
                t_id = None
                for t_name, tid in tool_by_name.items():
                    if t_name.lower() in r[3].lower():
                        t_id = tid
                        break
                cursor.execute("""
                    INSERT OR IGNORE INTO approval_requests (approval_code, agent_id, tool_id, event_id, operation, risk_level, reason, status, created_at, updated_at)
                    VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?)
                """, (r[1], ag_id, t_id, r[3], r[4], r[5], r[6], r[7], r[8]))
            raw_conn.commit()

        # Check if security_events is empty; seed 7 demonstration events if empty
        cursor.execute("SELECT COUNT(*) FROM security_events")
        if cursor.fetchone()[0] == 0:
            seed_events = [
                ("EV-1001", agent_by_name.get("Research Assistant"), tool_by_name.get("Public Knowledge Search"), "Prompt injection attempt", "Research Assistant", 85, "Critical", "Blocked", "Instruction override matched.", "seed"),
                ("EV-1002", agent_by_name.get("Data Analyst"), tool_by_name.get("Customer Data Access"), "Sensitive data exposure", "Data Analyst", 70, "High", "Approval required", "API-key-like pattern found in output.", "seed"),
                ("EV-1003", agent_by_name.get("File Management Agent"), tool_by_name.get("File Deletion"), "Unauthorized file access", "File Management Agent", 70, "High", "Blocked", "Tool denied by policy.", "seed"),
                ("EV-1004", agent_by_name.get("Email Assistant"), tool_by_name.get("External Email Sender"), "External email action", "Email Assistant", 70, "High", "Approval required", "External recipient needs review.", "seed"),
                ("EV-1005", agent_by_name.get("Research Assistant"), tool_by_name.get("Public Knowledge Search"), "Approved knowledge-base search", "Research Assistant", 15, "Low", "Allowed", "Public search permitted.", "seed"),
                ("EV-1006", agent_by_name.get("Research Assistant"), tool_by_name.get("Document Reader"), "Safe prompt allowed", "Research Assistant", 10, "Low", "Allowed", "No indicators.", "seed"),
                ("EV-1007", agent_by_name.get("Email Assistant"), tool_by_name.get("External Email Sender"), "Sensitive data exposure", "Email Assistant", 45, "Medium", "Allowed", "Phone number masked.", "seed"),
            ]
            for ev_code, ag_id, t_id, cat, src, score, risk, dec, why, ev_src in seed_events:
                cursor.execute("""
                    INSERT INTO security_events (event_code, agent_id, tool_id, category, source, risk_score, risk_level, decision, explanation, event_source, created_at, is_archived)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (ev_code, ag_id, t_id, cat, src, score, risk, dec, why, ev_src, now))
            raw_conn.commit()

        # Check if approval_requests is empty; seed 4 demonstration approvals if empty
        cursor.execute("SELECT COUNT(*) FROM approval_requests")
        if cursor.fetchone()[0] == 0:
            seed_approvals = [
                ("AP-201", agent_by_name.get("Email Assistant"), tool_by_name.get("External Email Sender"), "Send external email with report", "High", "External recipient", "Pending"),
                ("AP-202", agent_by_name.get("Data Analyst"), tool_by_name.get("Customer Data Access"), "Access protected customer info", "High", "Restricted data", "Pending"),
                ("AP-203", agent_by_name.get("Data Analyst"), tool_by_name.get("Data Export"), "Export sensitive document", "Critical", "Protected export", "Pending"),
                ("AP-204", agent_by_name.get("File Management Agent"), tool_by_name.get("File Deletion"), "High-impact file operation", "High", "Bulk change", "Pending"),
            ]
            for ap_code, ag_id, t_id, op, risk, why, st in seed_approvals:
                cursor.execute("""
                    INSERT INTO approval_requests (approval_code, agent_id, tool_id, event_id, operation, risk_level, reason, status, created_at, updated_at)
                    VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?)
                """, (ap_code, ag_id, t_id, op, risk, why, st, now, now))
            raw_conn.commit()

    print("[MIGRATION] Schema migration & initial seed verification completed successfully.")

