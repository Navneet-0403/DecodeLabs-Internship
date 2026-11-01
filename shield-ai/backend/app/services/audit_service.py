import sqlite3
from datetime import datetime, timezone

def generate_next_event_id(conn: sqlite3.Connection) -> str:
    cursor = conn.cursor()
    cursor.execute("SELECT event_id FROM security_events ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row and row[0].startswith("EV-"):
        try:
            num = int(row[0].split("-")[1])
            return f"EV-{num + 1}"
        except ValueError:
            pass
    cursor.execute("SELECT COUNT(*) FROM security_events")
    count = cursor.fetchone()[0]
    return f"EV-{1000 + count + 1}"

def generate_next_approval_id(conn: sqlite3.Connection) -> str:
    cursor = conn.cursor()
    cursor.execute("SELECT approval_id FROM approval_requests ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row and row[0].startswith("AP-"):
        try:
            num = int(row[0].split("-")[1])
            return f"AP-{num + 1}"
        except ValueError:
            pass
    cursor.execute("SELECT COUNT(*) FROM approval_requests")
    count = cursor.fetchone()[0]
    return f"AP-{200 + count + 1}"

def log_security_event(
    conn: sqlite3.Connection,
    category: str,
    source: str,
    risk_level: str,
    decision: str,
    explanation: str,
    event_source: str = "application"
) -> str:
    event_id = generate_next_event_id(conn)
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO security_events (event_id, category, source, risk_level, decision, explanation, created_at, event_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (event_id, category, source, risk_level, decision, explanation, now, event_source))
    conn.commit()
    return event_id

def create_approval_request(
    conn: sqlite3.Connection,
    agent_name: str,
    operation: str,
    risk_level: str,
    reason: str
) -> str:
    approval_id = generate_next_approval_id(conn)
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO approval_requests (approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (approval_id, agent_name, operation, risk_level, reason, "Pending", now, now))
    conn.commit()
    return approval_id

