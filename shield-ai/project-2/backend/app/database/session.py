from typing import Generator, Dict, Optional
from sqlalchemy.orm import sessionmaker, Session
from .connection import get_engine, get_database_url

# Cached reusable sessionmaker instances indexed by database URL
_cached_session_factories: Dict[str, sessionmaker] = {}

def get_session_factory(db_url: Optional[str] = None) -> sessionmaker:
    """
    Returns a reusable singleton sessionmaker factory bound to the shared engine.
    Avoids re-instantiating sessionmaker factories on every incoming API request.
    """
    target_url = db_url or get_database_url()
    if target_url not in _cached_session_factories:
        eng = get_engine(target_url)
        _cached_session_factories[target_url] = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=eng,
            expire_on_commit=False
        )
    return _cached_session_factories[target_url]

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy Session from the shared factory
    and guarantees reliable session closure upon request completion.
    """
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()
