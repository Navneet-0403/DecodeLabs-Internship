import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "shield_ai.db"

def get_database_url() -> str:
    env_path = os.getenv("SHIELD_AI_DB_PATH")
    if env_path:
        db_path = Path(env_path)
    else:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        db_path = DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"

def get_engine():
    db_url = get_database_url()
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
    return engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce SQLite foreign key constraints and WAL mode for high performance and integrity."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Shared engine instance
engine = get_engine()
