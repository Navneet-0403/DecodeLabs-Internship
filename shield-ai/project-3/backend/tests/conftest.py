import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Create an isolated temporary SQLite database for all automated test runs
# This guarantees that the real demonstration database ('data/shield_ai.db') is never touched
_temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
_test_db_path = Path(_temp_dir.name) / "test_shield_ai.db"
os.environ["SHIELD_AI_DB_PATH"] = str(_test_db_path)

from backend.app.database import init_db, reset_demo_events_and_approvals, reset_tool_permissions, get_session_factory
from backend.app.database.connection import dispose_engine
from backend.app.models import Agent, Tool, ApplicationSettings
from backend.app.main import app

# Initialize test database schema and seeds
init_db()

@pytest.fixture(scope="session", autouse=True)
def session_lifecycle():
    """Manages session teardown and cleanly disposes database connections."""
    yield
    dispose_engine()

@pytest.fixture(scope="session")
def client():
    """Provides a lifespan-aware TestClient connected to the isolated test database."""
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def ensure_clean_test_db():
    """Ensures each test starts with standard demonstration baseline records."""
    reset_demo_events_and_approvals()
    reset_tool_permissions()

    # Clean up any ephemeral agents or tools created by previous CRUD tests and restore default settings
    session_factory = get_session_factory()
    with session_factory() as db:
        initial_agent_codes = {"agent-1", "agent-2", "agent-3", "agent-4"}
        initial_tool_codes = {"tool-1", "tool-2", "tool-3", "tool-4", "tool-5", "tool-6", "tool-7"}
        db.query(Agent).filter(Agent.agent_code.notin_(initial_agent_codes)).delete(synchronize_session=False)
        db.query(Agent).filter(Agent.agent_code.in_(initial_agent_codes)).update({Agent.is_active: True}, synchronize_session=False)
        db.query(Tool).filter(Tool.tool_code.notin_(initial_tool_codes)).delete(synchronize_session=False)
        db.query(Tool).filter(Tool.tool_code.in_(initial_tool_codes)).update({Tool.is_active: True}, synchronize_session=False)
        db.query(ApplicationSettings).filter(ApplicationSettings.id == 1).update({
            ApplicationSettings.risk_sensitivity: 1.0,
            ApplicationSettings.automatic_critical_blocking: True,
            ApplicationSettings.require_high_risk_approval: True,
            ApplicationSettings.mask_sensitive_data: True,
            ApplicationSettings.notifications_enabled: True
        }, synchronize_session=False)
        db.commit()

    yield
