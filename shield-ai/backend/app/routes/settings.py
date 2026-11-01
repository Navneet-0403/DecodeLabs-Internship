import sqlite3
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from ..database import get_db, reset_demo_events_and_approvals
from ..schemas import SettingsResponse, SettingsUpdateRequest
from ..services.risk_engine import get_current_settings

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("", response_model=SettingsResponse)
def get_settings(conn: sqlite3.Connection = Depends(get_db)):
    settings = get_current_settings(conn)
    return SettingsResponse(**settings)

@router.put("", response_model=SettingsResponse)
def update_settings(request: SettingsUpdateRequest, conn: sqlite3.Connection = Depends(get_db)):
    current = get_current_settings(conn)
    
    sens = request.risk_sensitivity if request.risk_sensitivity is not None else current["risk_sensitivity"]
    ab = request.automatic_critical_blocking if request.automatic_critical_blocking is not None else current["automatic_critical_blocking"]
    ha = request.require_high_risk_approval if request.require_high_risk_approval is not None else current["require_high_risk_approval"]
    mk = request.mask_sensitive_data if request.mask_sensitive_data is not None else current["mask_sensitive_data"]
    nt = request.notifications_enabled if request.notifications_enabled is not None else current["notifications_enabled"]
    now = datetime.now(timezone.utc).isoformat()

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE settings
        SET risk_sensitivity = ?,
            automatic_critical_blocking = ?,
            require_high_risk_approval = ?,
            mask_sensitive_data = ?,
            notifications_enabled = ?,
            updated_at = ?
        WHERE id = 1
    """, (sens, 1 if ab else 0, 1 if ha else 0, 1 if mk else 0, 1 if nt else 0, now))
    conn.commit()

    return SettingsResponse(
        risk_sensitivity=sens,
        automatic_critical_blocking=ab,
        require_high_risk_approval=ha,
        mask_sensitive_data=mk,
        notifications_enabled=nt,
        updated_at=now
    )

demo_router = APIRouter(prefix="/api/demo", tags=["Demo Management"])

@demo_router.post("/reset")
def reset_demo(conn: sqlite3.Connection = Depends(get_db)):
    reset_demo_events_and_approvals()
    return {"status": "ok", "message": "Demonstration security events and approval requests reset to initial state."}

