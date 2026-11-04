import os
from pathlib import Path
from typing import Dict, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "shield_ai.db"

# Cached reusable engine instances indexed by database URL
_cached_engines: Dict[str, Engine] = {}

def get_database_url() -> str:
    """Resolve database URL from environment or fallback to project default SQLite path."""
    env_path = os.getenv("SHIELD_AI_DB_PATH")
    if env_path:
        db_path = Path(env_path)
    else:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        db_path = DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce SQLite foreign key constraints and performance pragmas on every connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_engine(db_url: Optional[str] = None) -> Engine:
    """
    Returns a shared, reusable SQLAlchemy Engine instance.
    Reuses existing engine for the same database URL to avoid overhead and connection exhaustion.
    """
    if db_url is None:
        db_url = get_database_url()
    
    if db_url not in _cached_engines:
        _cached_engines[db_url] = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False,
            pool_pre_ping=True
        )
    return _cached_engines[db_url]

def dispose_engine(db_url: Optional[str] = None) -> None:
    """Disposes cached engine connections cleanly."""
    target_url = db_url or get_database_url()
    if target_url in _cached_engines:
        _cached_engines[target_url].dispose()
        del _cached_engines[target_url]

# Shared default engine proxy
engine = get_engine()
