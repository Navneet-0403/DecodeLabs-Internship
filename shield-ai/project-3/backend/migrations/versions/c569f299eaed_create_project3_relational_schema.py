"""create_project3_relational_schema

Revision ID: c569f299eaed
Revises: 
Create Date: 2026-11-04 15:38:17.321135

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision: str = 'c569f299eaed'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INITIAL_AGENTS = [
    ("agent-1", "Research Assistant", "Retrieval", "Active (demo)", "Read-only public knowledge base search and document summarization."),
    ("agent-2", "Email Assistant", "Messaging", "Active (demo)", "External communications and message dispatch with human-in-the-loop approvals."),
    ("agent-3", "Data Analyst", "Analytics", "Active (demo)", "Data processing, dataset queries, and restricted customer analytics."),
    ("agent-4", "File Management Agent", "Files", "Idle (demo)", "Protected file system management with deletion prevention safeguards.")
]

INITIAL_TOOLS = [
    ("tool-1", "Public Knowledge Search", "Searches approved public sources", "Low"),
    ("tool-2", "Approved Database Read", "Reads approved datasets", "Low"),
    ("tool-3", "Document Reader", "Reads shared documents", "Low"),
    ("tool-4", "Customer Data Access", "Reads customer records", "High"),
    ("tool-5", "External Email Sender", "Sends email outside org", "High"),
    ("tool-6", "File Deletion", "Deletes protected files", "Critical"),
    ("tool-7", "Data Export", "Exports protected data", "Critical")
]

INITIAL_MAPPINGS = [
    ("agent-1", "tool-1", "Allowed"),
    ("agent-3", "tool-2", "Allowed"),
    ("agent-1", "tool-3", "Allowed"),
    ("agent-3", "tool-4", "Restricted"),
    ("agent-2", "tool-5", "Approval Required"),
    ("agent-4", "tool-6", "Blocked"),
    ("agent-3", "tool-7", "Blocked"),
]

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def upgrade() -> None:
    """Upgrade schema to Project 3 relational models while preserving existing Project 2 data."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
    now = utc_now_iso()

    # 1. Create 'agents' table if not exists
    if "agents" not in existing_tables:
        op.create_table(
            "agents",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("agent_code", sa.String(length=50), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("agent_type", sa.String(length=50), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.String(length=50), nullable=False),
            sa.Column("updated_at", sa.String(length=50), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("agent_code", name="uq_agent_code")
        )
        op.create_index("ix_agents_agent_code", "agents", ["agent_code"], unique=True)

    # 2. Create 'tools' table if not exists
    if "tools" not in existing_tables:
        op.create_table(
            "tools",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("tool_code", sa.String(length=50), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("risk_level", sa.String(length=20), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.String(length=50), nullable=False),
            sa.Column("updated_at", sa.String(length=50), nullable=False),
            sa.CheckConstraint("risk_level IN ('Low', 'Medium', 'High', 'Critical')", name="ck_tool_risk_level"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tool_code", name="uq_tool_code")
        )
        op.create_index("ix_tools_tool_code", "tools", ["tool_code"], unique=True)

    # 3. Create 'agent_tools' M:M junction table if not exists
    if "agent_tools" not in existing_tables:
        op.create_table(
            "agent_tools",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("agent_id", sa.Integer(), nullable=False),
            sa.Column("tool_id", sa.Integer(), nullable=False),
            sa.Column("permission_status", sa.String(length=30), nullable=False),
            sa.Column("created_at", sa.String(length=50), nullable=False),
            sa.Column("updated_at", sa.String(length=50), nullable=False),
            sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], name="fk_agent_tools_agent_id", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["tool_id"], ["tools.id"], name="fk_agent_tools_tool_id", ondelete="CASCADE"),
            sa.CheckConstraint("permission_status IN ('Allowed', 'Approval Required', 'Restricted', 'Blocked')", name="ck_agent_tool_permission"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("agent_id", "tool_id", name="uq_agent_tool_pair")
        )

    # 4. Create 'security_events' table if not exists
    if "security_events" not in existing_tables:
        op.create_table(
            "security_events",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("event_code", sa.String(length=50), nullable=False),
            sa.Column("agent_id", sa.Integer(), nullable=True),
            sa.Column("tool_id", sa.Integer(), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=False),
            sa.Column("source", sa.String(length=100), nullable=False),
            sa.Column("risk_score", sa.Integer(), nullable=False),
            sa.Column("risk_level", sa.String(length=20), nullable=False),
            sa.Column("decision", sa.String(length=30), nullable=False),
            sa.Column("explanation", sa.Text(), nullable=False),
            sa.Column("event_source", sa.String(length=50), nullable=False, server_default=sa.text("'application'")),
            sa.Column("created_at", sa.String(length=50), nullable=False),
            sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], name="fk_security_events_agent_id", ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["tool_id"], ["tools.id"], name="fk_security_events_tool_id", ondelete="SET NULL"),
            sa.CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_security_event_score"),
            sa.CheckConstraint("risk_level IN ('Low', 'Medium', 'High', 'Critical')", name="ck_security_event_level"),
            sa.CheckConstraint("decision IN ('Allowed', 'Approval required', 'Approval Required', 'Blocked')", name="ck_security_event_decision"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("event_code", name="uq_event_code")
        )
        op.create_index("ix_security_events_event_code", "security_events", ["event_code"], unique=True)
        op.create_index("ix_security_events_created_at", "security_events", ["created_at"], unique=False)

    # 5. Create 'approval_requests' table if not exists
    if "approval_requests" not in existing_tables:
        op.create_table(
            "approval_requests",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("approval_code", sa.String(length=50), nullable=False),
            sa.Column("agent_id", sa.Integer(), nullable=True),
            sa.Column("tool_id", sa.Integer(), nullable=True),
            sa.Column("event_id", sa.Integer(), nullable=True),
            sa.Column("operation", sa.String(length=255), nullable=False),
            sa.Column("risk_level", sa.String(length=20), nullable=False),
            sa.Column("reason", sa.String(length=255), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'Pending'")),
            sa.Column("created_at", sa.String(length=50), nullable=False),
            sa.Column("updated_at", sa.String(length=50), nullable=False),
            sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], name="fk_approval_requests_agent_id", ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["tool_id"], ["tools.id"], name="fk_approval_requests_tool_id", ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["event_id"], ["security_events.id"], name="fk_approval_requests_event_id", ondelete="SET NULL"),
            sa.CheckConstraint("risk_level IN ('Low', 'Medium', 'High', 'Critical')", name="ck_approval_risk_level"),
            sa.CheckConstraint("status IN ('Pending', 'Approved', 'Rejected', 'Cancelled')", name="ck_approval_status"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("approval_code", name="uq_approval_code")
        )
        op.create_index("ix_approval_requests_approval_code", "approval_requests", ["approval_code"], unique=True)

    # 6. Create 'application_settings' table if not exists
    if "application_settings" not in existing_tables:
        op.create_table(
            "application_settings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("risk_sensitivity", sa.Float(), nullable=False, server_default=sa.text("1.0")),
            sa.Column("automatic_critical_blocking", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("require_high_risk_approval", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("mask_sensitive_data", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("notifications_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("updated_at", sa.String(length=50), nullable=False),
            sa.CheckConstraint("risk_sensitivity >= 0.1 AND risk_sensitivity <= 5.0", name="ck_settings_sensitivity"),
            sa.PrimaryKeyConstraint("id")
        )

    # 7. Seed Initial Agents if table is empty
    conn = bind.connection
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agents")
    if cursor.fetchone()[0] == 0:
        for code, name, a_type, status, desc in INITIAL_AGENTS:
            cursor.execute("""
                INSERT INTO agents (agent_code, name, agent_type, status, description, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (code, name, a_type, status, desc, now, now))

    # 8. Seed Initial Tools if table is empty
    cursor.execute("SELECT COUNT(*) FROM tools")
    if cursor.fetchone()[0] == 0:
        for code, name, desc, risk in INITIAL_TOOLS:
            cursor.execute("""
                INSERT INTO tools (tool_code, name, description, risk_level, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (code, name, desc, risk, now, now))

    # Build lookup dictionaries
    cursor.execute("SELECT id, agent_code, name FROM agents")
    agent_map_code = {row[1]: row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT id, tool_code, name FROM tools")
    tool_map_code = {row[1]: row[0] for row in cursor.fetchall()}

    # 9. Seed / Migrate AgentTools if table is empty
    cursor.execute("SELECT COUNT(*) FROM agent_tools")
    if cursor.fetchone()[0] == 0:
        # Check if legacy tool_permissions exists
        if "tool_permissions" in existing_tables:
            cursor.execute("SELECT tool_id, permission_status FROM tool_permissions")
            legacy_perms = {row[0]: row[1] for row in cursor.fetchall()}
        else:
            legacy_perms = {}

        for ag_code, t_code, default_perm in INITIAL_MAPPINGS:
            ag_id = agent_map_code.get(ag_code)
            t_id = tool_map_code.get(t_code)
            perm = legacy_perms.get(t_code, default_perm)
            if ag_id and t_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO agent_tools (agent_id, tool_id, permission_status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (ag_id, t_id, perm, now, now))

    # 10. Seed / Migrate ApplicationSettings if table is empty
    cursor.execute("SELECT COUNT(*) FROM application_settings")
    if cursor.fetchone()[0] == 0:
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
        else:
            cursor.execute("""
                INSERT INTO application_settings (id, risk_sensitivity, automatic_critical_blocking, require_high_risk_approval, mask_sensitive_data, notifications_enabled, updated_at)
                VALUES (1, 1.0, 1, 1, 1, 1, ?)
            """, (now,))

    conn.commit()


def downgrade() -> None:
    """Downgrade schema safely by dropping Project 3 tables in foreign-key safe order."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # Drop in reverse dependency order
    if "approval_requests" in existing_tables:
        op.drop_table("approval_requests")
    if "security_events" in existing_tables:
        op.drop_table("security_events")
    if "agent_tools" in existing_tables:
        op.drop_table("agent_tools")
    if "application_settings" in existing_tables:
        op.drop_table("application_settings")
    if "tools" in existing_tables:
        op.drop_table("tools")
    if "agents" in existing_tables:
        op.drop_table("agents")
