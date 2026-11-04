from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..database import reset_demo_events_and_approvals
from ..repositories.settings_repo import SettingsRepository
from ..schemas.settings import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/api/settings", tags=["Settings CRUD"])

@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Retrieve the current persisted gateway application configuration."""
    settings = SettingsRepository.get(db)
    return SettingsResponse(
        risk_sensitivity=settings.risk_sensitivity,
        automatic_critical_blocking=settings.automatic_critical_blocking,
        require_high_risk_approval=settings.require_high_risk_approval,
        mask_sensitive_data=settings.mask_sensitive_data,
        notifications_enabled=settings.notifications_enabled,
        updated_at=settings.updated_at
    )

@router.put("", response_model=SettingsResponse)
def update_settings(request: SettingsUpdateRequest, db: Session = Depends(get_db)):
    """Update gateway configuration and enforce database-level CHECK constraints."""
    updated = SettingsRepository.update(db, request)
    return SettingsResponse(
        risk_sensitivity=updated.risk_sensitivity,
        automatic_critical_blocking=updated.automatic_critical_blocking,
        require_high_risk_approval=updated.require_high_risk_approval,
        mask_sensitive_data=updated.mask_sensitive_data,
        notifications_enabled=updated.notifications_enabled,
        updated_at=updated.updated_at
    )

demo_router = APIRouter(prefix="/api/demo", tags=["Demo Management"])

@demo_router.post("/reset")
def reset_demo(db: Session = Depends(get_db)):
    """Restore initial demonstration events and approvals safely."""
    reset_demo_events_and_approvals()
    return {"status": "ok", "message": "Demonstration security events and approval requests reset to initial state."}
