from typing import Dict, Any
from sqlalchemy.orm import Session
from .security_engine import analyze_prompt
from ..repositories.settings_repo import SettingsRepository

def get_current_settings_dict(db: Session) -> Dict[str, Any]:
    s = SettingsRepository.get(db)
    return {
        "risk_sensitivity": s.risk_sensitivity,
        "automatic_critical_blocking": s.automatic_critical_blocking,
        "require_high_risk_approval": s.require_high_risk_approval,
        "mask_sensitive_data": s.mask_sensitive_data,
        "notifications_enabled": s.notifications_enabled,
        "updated_at": s.updated_at,
    }

def scan_and_evaluate(db: Session, prompt: str) -> Dict[str, Any]:
    s = SettingsRepository.get(db)
    result = analyze_prompt(
        text=prompt,
        sensitivity=s.risk_sensitivity,
        auto_block=s.automatic_critical_blocking,
        high_risk_approval=s.require_high_risk_approval,
        mask_pii=s.mask_sensitive_data
    )
    return result
