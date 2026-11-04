from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..schemas.scanner import ScanRequest, ScanResponse
from ..services.risk_engine import scan_and_evaluate
from ..services.audit_service import log_security_event

router = APIRouter(prefix="/api/scans", tags=["Prompt Scanner"])

@router.post("", response_model=ScanResponse, status_code=status.HTTP_200_OK)
def scan_prompt(request: ScanRequest, db: Session = Depends(get_db)):
    """Analyze incoming prompt, detect malicious patterns & PII, and record event in SQLite via ORM."""
    result = scan_and_evaluate(db, request.prompt)

    hits = result["detected_indicators"]
    pii = result["sensitive_data"]

    if pii and not hits:
        category = "Sensitive data exposure"
    elif hits:
        category = "Prompt injection attempt"
    else:
        category = "Safe prompt allowed"

    indicators_summary = ", ".join(hits + [p[0] for p in pii]) or "No indicators."

    # Store event using ORM audit service
    log_security_event(
        db=db,
        category=category,
        source="Prompt Scanner",
        risk_level=result["risk_level"],
        decision=result["decision"],
        explanation=indicators_summary,
        event_source="application",
        risk_score=result["risk_score"]
    )

    return ScanResponse(
        classification=result["classification"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        detected_indicators=result["detected_indicators"],
        sensitive_data=result["sensitive_data"],
        decision=result["decision"],
        explanation=result["explanation"],
        remediation=result["remediation"]
    )
