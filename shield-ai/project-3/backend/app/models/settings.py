from sqlalchemy import Column, Integer, Float, Boolean, String, CheckConstraint
from ..database.base import Base, utc_now_iso

class ApplicationSettings(Base):
    __tablename__ = "application_settings"

    id = Column(Integer, primary_key=True, default=1)
    risk_sensitivity = Column(Float, nullable=False, default=1.0)
    automatic_critical_blocking = Column(Boolean, nullable=False, default=True)
    require_high_risk_approval = Column(Boolean, nullable=False, default=True)
    mask_sensitive_data = Column(Boolean, nullable=False, default=True)
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(String(50), nullable=False, default=utc_now_iso)

    __table_args__ = (
        CheckConstraint("risk_sensitivity >= 0.1 AND risk_sensitivity <= 5.0", name="ck_settings_sensitivity"),
    )

