import os
import tempfile
import sqlite3
from pathlib import Path
import pytest
from alembic.config import Config
from alembic import command
import sqlalchemy as sa
from sqlalchemy import create_engine, text

def test_alembic_fresh_database_creation_and_upgrade():
    """Verify that 'alembic upgrade head' creates all 6 tables and initial records on an empty database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "fresh_alembic.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", db_url)
        
        # Run upgrade head
        command.upgrade(cfg, "head")
        
        # Verify tables created
        engine = create_engine(db_url)
        inspector = sa.inspect(engine)
        table_names = inspector.get_table_names()
        
        expected_tables = {
            "agents",
            "tools",
            "agent_tools",
            "security_events",
            "approval_requests",
            "application_settings",
            "alembic_version"
        }
        for table in expected_tables:
            assert table in table_names, f"Expected table '{table}' was not created by Alembic"
            
        with engine.connect() as conn:
            # Check agents count
            res = conn.execute(text("SELECT COUNT(*) FROM agents")).scalar()
            assert res == 4
            
            # Check tools count
            res = conn.execute(text("SELECT COUNT(*) FROM tools")).scalar()
            assert res == 7
            
            # Check agent_tools count
            res = conn.execute(text("SELECT COUNT(*) FROM agent_tools")).scalar()
            assert res == 7
            
            # Check application_settings default
            res = conn.execute(text("SELECT risk_sensitivity FROM application_settings WHERE id = 1")).scalar()
            assert res == 1.0
            
        engine.dispose()


def test_alembic_downgrade_and_reupgrade():
    """Verify rollback (downgrade base) and subsequent re-upgrade."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "rollback_test.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", db_url)
        
        # 1. Upgrade
        command.upgrade(cfg, "head")
        
        # 2. Downgrade to base
        command.downgrade(cfg, "base")
        
        engine = create_engine(db_url)
        inspector = sa.inspect(engine)
        tables_after_downgrade = inspector.get_table_names()
        
        assert "agents" not in tables_after_downgrade
        assert "tools" not in tables_after_downgrade
        assert "agent_tools" not in tables_after_downgrade
        assert "security_events" not in tables_after_downgrade
        assert "approval_requests" not in tables_after_downgrade
        assert "application_settings" not in tables_after_downgrade
        
        engine.dispose()
        
        # 3. Re-upgrade
        command.upgrade(cfg, "head")
        engine2 = create_engine(db_url)
        inspector_re = sa.inspect(engine2)
        assert "agents" in inspector_re.get_table_names()
        engine2.dispose()


def test_alembic_preserves_legacy_project2_data():
    """Verify that running Alembic upgrade on a legacy Project 2 SQLite DB preserves and migrates data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "legacy_test.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        
        # Pre-populate legacy Project 2 tables
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE tool_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT UNIQUE,
                tool_name TEXT,
                description TEXT,
                assigned_agent TEXT,
                risk_level TEXT,
                permission_status TEXT,
                updated_at TEXT
            )
        """)
        # Custom user setting in tool_permissions: tool-4 is Restricted
        cur.execute("""
            INSERT INTO tool_permissions (tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at)
            VALUES ('tool-4', 'Customer Data Access', 'Custom Desc', 'Data Analyst', 'High', 'Restricted', '2026-11-01T12:00:00Z')
        """)
        
        cur.execute("""
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY,
                risk_sensitivity REAL DEFAULT 1.0,
                automatic_critical_blocking INTEGER DEFAULT 1,
                require_high_risk_approval INTEGER DEFAULT 1,
                mask_sensitive_data INTEGER DEFAULT 1,
                notifications_enabled INTEGER DEFAULT 1,
                updated_at TEXT
            )
        """)
        # Custom sensitivity 2.5
        cur.execute("""
            INSERT INTO settings (id, risk_sensitivity, automatic_critical_blocking, require_high_risk_approval, mask_sensitive_data, notifications_enabled, updated_at)
            VALUES (1, 2.5, 0, 1, 1, 0, '2026-11-01T12:00:00Z')
        """)
        conn.commit()
        conn.close()
        
        # Now run Alembic upgrade
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(cfg, "head")
        
        # Check that legacy data was preserved and migrated
        engine = create_engine(db_url)
        with engine.connect() as check_conn:
            # Check application_settings has the preserved 2.5 sensitivity
            sens = check_conn.execute(text("SELECT risk_sensitivity FROM application_settings WHERE id = 1")).scalar()
            assert sens == 2.5
            
            # Check legacy table itself is preserved and not dropped
            inspector = sa.inspect(engine)
            assert "tool_permissions" in inspector.get_table_names()
            assert "settings" in inspector.get_table_names()
            
        engine.dispose()


def test_database_foreign_keys_and_constraints():
    """Verify foreign keys and CHECK constraints on Alembic-created schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "constraint_test.db"
        db_url = f"sqlite:///{db_path.as_posix()}"
        
        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(cfg, "head")
        
        engine = create_engine(db_url)
        
        # Enable foreign keys for raw connection
        with engine.connect() as conn:
            conn.execute(text("PRAGMA foreign_keys = ON;"))
            
            # 1. Invalid foreign key should fail
            with pytest.raises(Exception):
                conn.execute(text("""
                    INSERT INTO agent_tools (agent_id, tool_id, permission_status, created_at, updated_at)
                    VALUES (9999, 9999, 'Allowed', '2026-11-04T00:00:00Z', '2026-11-04T00:00:00Z')
                """))
                conn.commit()
                
            # 2. CHECK constraint violation on risk_level
            with pytest.raises(Exception):
                conn.execute(text("""
                    INSERT INTO tools (tool_code, name, risk_level, is_active, created_at, updated_at)
                    VALUES ('tool-invalid', 'Invalid Tool', 'SUPER_HIGH', 1, '2026-11-04T00:00:00Z', '2026-11-04T00:00:00Z')
                """))
                conn.commit()
                
            # 3. CHECK constraint violation on sensitivity
            with pytest.raises(Exception):
                conn.execute(text("""
                    UPDATE application_settings SET risk_sensitivity = 10.0 WHERE id = 1
                """))
                conn.commit()
                
        engine.dispose()
