import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Create an isolated temporary SQLite database for all automated test runs
# This guarantees that the real demonstration database ('data/shield_ai.db') is never touched
_temp_dir = tempfile.TemporaryDirectory()
_test_db_path = Path(_temp_dir.name) / "test_shield_ai.db"
os.environ["SHIELD_AI_DB_PATH"] = str(_test_db_path)

from backend.app.database import init_db, reset_demo_events_and_approvals, reset_tool_permissions
from backend.app.main import app

# Initialize test database schema and seeds
init_db()

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
    yield

