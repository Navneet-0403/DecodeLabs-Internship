from typing import List
from pydantic import BaseModel, Field, field_validator

class ScanRequest(BaseModel):
    prompt: str = Field(..., max_length=1000)

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("The submitted prompt cannot be empty.")
        if len(cleaned) > 1000:
            raise ValueError("Prompt exceeds the maximum allowed length of 1000 characters.")
        return cleaned

class ScanResponse(BaseModel):
    classification: str
    risk_score: int
    risk_level: str
    detected_indicators: List[str]
    sensitive_data: List[List[str]]
    decision: str
    explanation: str
    remediation: str
