from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
