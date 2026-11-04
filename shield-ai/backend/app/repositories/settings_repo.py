from sqlalchemy.orm import Session
from ..models.settings import ApplicationSettings
from ..schemas.settings import SettingsUpdateRequest
from ..database.base import utc_now_iso

class SettingsRepository:
    @staticmethod
    def get(db: Session) -> ApplicationSettings:
        settings = db.query(ApplicationSettings).filter(ApplicationSettings.id == 1).first()
        if not settings:
            settings = ApplicationSettings(
                id=1,
                risk_sensitivity=1.0,
                automatic_critical_blocking=True,
                require_high_risk_approval=True,
                mask_sensitive_data=True,
                notifications_enabled=True,
                updated_at=utc_now_iso()
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings

    @staticmethod
    def update(db: Session, obj_in: SettingsUpdateRequest) -> ApplicationSettings:
        settings = SettingsRepository.get(db)
        if obj_in.risk_sensitivity is not None:
            settings.risk_sensitivity = obj_in.risk_sensitivity
        if obj_in.automatic_critical_blocking is not None:
            settings.automatic_critical_blocking = obj_in.automatic_critical_blocking
        if obj_in.require_high_risk_approval is not None:
            settings.require_high_risk_approval = obj_in.require_high_risk_approval
        if obj_in.mask_sensitive_data is not None:
            settings.mask_sensitive_data = obj_in.mask_sensitive_data
        if obj_in.notifications_enabled is not None:
            settings.notifications_enabled = obj_in.notifications_enabled
        settings.updated_at = utc_now_iso()
        db.commit()
        db.refresh(settings)
        return settings
