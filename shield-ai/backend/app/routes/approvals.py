import sqlite3
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from ..database import get_db
from ..schemas import ApprovalResponse, ApprovalDecisionRequest
from ..exceptions import APIException
from ..services.audit_service import log_security_event

router = APIRouter(prefix="/api/approvals", tags=["Approval Center"])

@router.get("", response_model=List[ApprovalResponse])
def get_approvals(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Pending, Approved, Rejected)"),
    conn: sqlite3.Connection = Depends(get_db)
):
    cursor = conn.cursor()
    if status_filter:
        cursor.execute("""
            SELECT id, approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at
            FROM approval_requests
            WHERE status = ?
            ORDER BY id DESC
        """, (status_filter,))
    else:
        cursor.execute("""
            SELECT id, approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at
            FROM approval_requests
            ORDER BY id DESC
        """)
    rows = cursor.fetchall()
    return [
        ApprovalResponse(
            id=r["id"],
            approval_id=r["approval_id"],
            agent_name=r["agent_name"],
            operation=r["operation"],
            risk_level=r["risk_level"],
            reason=r["reason"],
            status=r["status"],
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        )
        for r in rows
    ]

@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
def decide_approval(
    approval_id: str,
    request: ApprovalDecisionRequest,
    conn: sqlite3.Connection = Depends(get_db)
):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at
        FROM approval_requests
        WHERE approval_id = ?
    """, (approval_id,))
    row = cursor.fetchone()

    if not row:
        raise APIException(
            status_code=404,
            code="APPROVAL_NOT_FOUND",
            message=f"Approval request with ID '{approval_id}' was not found."
        )

    # Check if already resolved
    current_status = row["status"]
    if current_status != "Pending":
        raise APIException(
            status_code=409,
            code="APPROVAL_ALREADY_RESOLVED",
            message=f"Approval request '{approval_id}' has already been resolved with status '{current_status}'."
        )

    new_status = request.decision
    now = datetime.now(timezone.utc).isoformat()

    # Update approval
    cursor.execute("""
        UPDATE approval_requests
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (new_status, now, row["id"]))
    conn.commit()

    # Record security event
    event_category = "Approval granted" if new_status == "Approved" else "Approval rejected"
    event_decision = "Allowed" if new_status == "Approved" else "Blocked"
    event_explanation = f"Demo {new_status.lower()} for {row['operation']}. No external operation executed."

    log_security_event(
        conn=conn,
        category=event_category,
        source=row["agent_name"],
        risk_level=row["risk_level"],
        decision=event_decision,
        explanation=event_explanation,
        event_source="application"
    )

    cursor.execute("""
        SELECT id, approval_id, agent_name, operation, risk_level, reason, status, created_at, updated_at
        FROM approval_requests
        WHERE id = ?
    """, (row["id"],))
    updated_row = cursor.fetchone()

    return ApprovalResponse(
        id=updated_row["id"],
        approval_id=updated_row["approval_id"],
        agent_name=updated_row["agent_name"],
        operation=updated_row["operation"],
        risk_level=updated_row["risk_level"],
        reason=updated_row["reason"],
        status=updated_row["status"],
        created_at=updated_row["created_at"],
        updated_at=updated_row["updated_at"]
    )

