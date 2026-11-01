import sqlite3
from fastapi import APIRouter, Depends, status
from ..database import get_db
from ..schemas import ScanRequest, ScanResponse
from ..services.risk_engine import scan_and_evaluate
from ..services.audit_service import log_security_event

router = APIRouter(prefix="/api/scans", tags=["Prompt Scanner"])

@router.post("", response_model=ScanResponse, status_code=status.HTTP_200_OK)
def scan_prompt(request: ScanRequest, conn: sqlite3.Connection = Depends(get_db)):
    # 1. Analyze prompt with backend security engine and loaded policy
    result = scan_and_evaluate(conn, request.prompt)

    # 2. Determine security event metadata (without raw prompt or secret leakage)
    hits = result["detected_indicators"]
    pii = result["sensitive_data"]

    if pii and not hits:
        category = "Sensitive data exposure"
    elif hits:
        category = "Prompt injection attempt"
    else:
        category = "Safe prompt allowed"

    indicators_summary = ", ".join(hits + [p[0] for p in pii]) or "No indicators."

    # 3. Store security event in SQLite
    log_security_event(
        conn=conn,
        category=category,
        source="Prompt Scanner",
        risk_level=result["risk_level"],
        decision=result["decision"],
        explanation=indicators_summary,
        event_source="application"
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

