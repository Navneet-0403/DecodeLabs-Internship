import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

# Database file location
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "shield_ai.db"

def get_db_path() -> Path:
    env_path = os.getenv("SHIELD_AI_DB_PATH")
    if env_path:
        p = Path(env_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# Initial Demonstration Seed Data according to Project 2 Specification
SEED_TOOLS = [
    ("tool-1", "Public Knowledge Search", "Searches approved public sources", "Research Assistant", "Low", "Allowed"),
    ("tool-2", "Approved Database Read", "Reads approved datasets", "Data Analyst", "Low", "Allowed"),
    ("tool-3", "Document Reader", "Reads shared documents", "Research Assistant", "Low", "Allowed"),
    ("tool-4", "Customer Data Access", "Reads customer records", "Data Analyst", "High", "Restricted"),
    ("tool-5", "External Email Sender", "Sends email outside org", "Email Assistant", "High", "Approval Required"),
    ("tool-6", "File Deletion", "Deletes protected files", "File Management Agent", "Critical", "Blocked"),
    ("tool-7", "Data Export", "Exports protected data", "Data Analyst", "Critical", "Blocked"),
]

SEED_EVENTS = [
    ("EV-1001", "Prompt injection attempt", "Research Assistant", "Critical", "Blocked", "Instruction override matched.", "seed"),
    ("EV-1002", "Sensitive data exposure", "Data Analyst", "High", "Approval required", "API-key-like pattern found in output.", "seed"),
    ("EV-1003", "Unauthorized file access", "File Management Agent", "High", "Blocked", "Tool denied by policy.", "seed"),
    ("EV-1004", "External email action", "Email Assistant", "High", "Approval required", "External recipient needs review.", "seed"),
    ("EV-1005", "Approved knowledge-base search", "Research Assistant", "Low", "Allowed", "Public search permitted.", "seed"),
    ("EV-1006", "Safe prompt allowed", "Research Assistant", "Low", "Allowed", "No indicators.", "seed"),
    ("EV-1007", "Sensitive data exposure", "Email Assistant", "Medium", "Allowed", "Phone number masked.", "seed"),
]

SEED_APPROVALS = [
    ("AP-201", "Email Assistant", "Send external email with report", "High", "External recipient", "Pending"),
    ("AP-202", "Data Analyst", "Access protected customer info", "High", "Restricted data", "Pending"),
    ("AP-203", "Data Analyst", "Export sensitive document", "Critical", "Protected export", "Pending"),
    ("AP-204", "File Management Agent", "High-impact file operation", "High", "Bulk change", "Pending"),
]

def init_db():
    """Initializes tables and seeds baseline demonstration data only if tables are empty."""
    get_db_path()
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. security_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                decision TEXT NOT NULL,
                explanation TEXT NOT NULL,
                created_at TEXT NOT NULL,
                event_source TEXT NOT NULL DEFAULT 'application'
            )
        """)

        # 2. tool_permissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT UNIQUE NOT NULL,
                tool_name TEXT NOT NULL,
                description TEXT NOT NULL,
                assigned_agent TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                permission_status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 3. approval_requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approval_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                approval_id TEXT UNIQUE NOT NULL,
                agent_name TEXT NOT NULL,
                operation TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 4. settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                risk_sensitivity REAL NOT NULL DEFAULT 1.0,
                automatic_critical_blocking INTEGER NOT NULL DEFAULT 1,
                require_high_risk_approval INTEGER NOT NULL DEFAULT 1,
                mask_sensitive_data INTEGER NOT NULL DEFAULT 1,
                notifications_enabled INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL
            )
        """)

        # Seed initial data ONLY if tables are completely empty (preserves existing user changes)
        cursor.execute("SELECT COUNT(*) FROM settings")
        if cursor.fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO settings (id, risk_sensitivity, automatic_critical_blocking, require_high_risk_approval, mask_sensitive_data, notifications_enabled, updated_at)
                VALUES (1, 1.0, 1, 1, 1, 1, ?)
            """, (now,))

        cursor.execute("SELECT COUNT(*) FROM tool_permissions")
        if cursor.fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            for tool_id, name, desc, agent, risk, perm in SEED_TOOLS:
                cursor.execute("""
                    INSERT INTO tool_permissions (tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (tool_id, name, desc, agent, risk, perm, now))

        cursor.execute("SELECT COUNT(*) FROM security_events")
        if cursor.fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            for ev_id, cat, src, risk, dec, why, ev_src in SEED_EVENTS:
                cursor.execute("""
                    INSERT INTO security_events (event_id, category, source, risk_level, decision, explanation, created_at, event_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ev_id, cat, src, risk, dec, why, now, ev_src))

        cursor.execute("SELECT COUNT(*) FROM approval_requests")
        if cursor.fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            for ap_id, ag, op, risk, why, st in SEED_APPROVALS:
                cursor.execute("""
                    INSERT INTO approval_requests (approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ap_id, ag, op, risk, why, st, now, now))

        conn.commit()

def reset_demo_events_and_approvals():
    """Restores initial demonstration security events and approval records."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM security_events")
        cursor.execute("DELETE FROM approval_requests")
        
        now = datetime.now(timezone.utc).isoformat()
        for ev_id, cat, src, risk, dec, why, ev_src in SEED_EVENTS:
            cursor.execute("""
                INSERT INTO security_events (event_id, category, source, risk_level, decision, explanation, created_at, event_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ev_id, cat, src, risk, dec, why, now, ev_src))

        for ap_id, ag, op, risk, why, st in SEED_APPROVALS:
            cursor.execute("""
                INSERT INTO approval_requests (approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ap_id, ag, op, risk, why, st, now, now))
            
        conn.commit()

def reset_tool_permissions():
    """Restores initial default tool permissions according to the specification."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tool_permissions")
        now = datetime.now(timezone.utc).isoformat()
        for tool_id, name, desc, agent, risk, perm in SEED_TOOLS:
            cursor.execute("""
                INSERT INTO tool_permissions (tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tool_id, name, desc, agent, risk, perm, now))
        conn.commit()

def check_db_health() -> bool:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            return row is not None and row[0] == 1
    except Exception:
        return False
