from typing import Optional
from pydantic import BaseModel, field_validator

class SettingsResponse(BaseModel):
    risk_sensitivity: float
    automatic_critical_blocking: bool
    require_high_risk_approval: bool
    mask_sensitive_data: bool
    notifications_enabled: bool
    updated_at: str

    model_config = {"from_attributes": True}

class SettingsUpdateRequest(BaseModel):
    risk_sensitivity: Optional[float] = None
    automatic_critical_blocking: Optional[bool] = None
    require_high_risk_approval: Optional[bool] = None
    mask_sensitive_data: Optional[bool] = None
    notifications_enabled: Optional[bool] = None

    @field_validator("risk_sensitivity")
    @classmethod
    def validate_sensitivity(cls, v):
        if v is not None and (v < 0.1 or v > 5.0):
            raise ValueError("risk_sensitivity must be between 0.1 and 5.0")
        return v
