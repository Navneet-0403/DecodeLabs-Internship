from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..repositories.approval_repo import ApprovalRepository
from ..repositories.agent_repo import AgentRepository
from ..repositories.tool_repo import ToolRepository
from ..schemas.approval import ApprovalResponse, ApprovalCreate, ApprovalUpdate, ApprovalDecisionRequest
from ..exceptions import APIException
from ..services.audit_service import log_security_event

router = APIRouter(prefix="/api/approvals", tags=["Approval Center & CRUD"])

def format_approval_response(appr, db: Session) -> ApprovalResponse:
    agent_name = appr.agent.name if appr.agent else "Simulator"
    return ApprovalResponse(
        id=appr.id,
        approval_id=appr.approval_code,
        approval_code=appr.approval_code,
        agent_id=appr.agent_id,
        tool_id=appr.tool_id,
        event_id=appr.event_id,
        agent_name=agent_name,
        operation=appr.operation,
        risk_level=appr.risk_level,
        reason=appr.reason,
        status=appr.status,
        created_at=appr.created_at,
        updated_at=appr.updated_at
    )

@router.get("", response_model=List[ApprovalResponse])
def get_approvals(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Pending, Approved, Rejected, Cancelled)"),
    db: Session = Depends(get_db)
):
    """Retrieve all approval requests with optional status filtering."""
    approvals = ApprovalRepository.get_all(db, status_filter=status_filter)
    return [format_approval_response(a, db) for a in approvals]

@router.post("", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
def create_approval(approval_in: ApprovalCreate, db: Session = Depends(get_db)):
    """Create a new human approval request."""
    if approval_in.agent_name and not approval_in.agent_id:
        ag = AgentRepository.get_by_identifier(db, approval_in.agent_name)
        if ag:
            approval_in.agent_id = ag.id
    approval = ApprovalRepository.create(db, approval_in)
    return format_approval_response(approval, db)

@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(approval_id: str, db: Session = Depends(get_db)):
    """Retrieve an individual approval request."""
    appr = ApprovalRepository.get_by_identifier(db, approval_id)
    if not appr:
        raise APIException(status_code=404, code="APPROVAL_NOT_FOUND", message=f"Approval request '{approval_id}' was not found.")
    return format_approval_response(appr, db)

@router.put("/{approval_id}", response_model=ApprovalResponse)
def update_approval(approval_id: str, update_in: ApprovalUpdate, db: Session = Depends(get_db)):
    """Update an allowed pending approval state."""
    appr = ApprovalRepository.get_by_identifier(db, approval_id)
    if not appr:
        raise APIException(status_code=404, code="APPROVAL_NOT_FOUND", message=f"Approval request '{approval_id}' was not found.")
    if appr.status != "Pending" and update_in.status != appr.status:
        raise APIException(status_code=409, code="APPROVAL_ALREADY_RESOLVED", message=f"Approval request '{approval_id}' is already {appr.status} and cannot be modified.")
    
    updated = ApprovalRepository.update(db, appr, update_in)
    return format_approval_response(updated, db)

@router.delete("/{approval_id}", response_model=ApprovalResponse)
def cancel_approval(approval_id: str, db: Session = Depends(get_db)):
    """Cancel an eligible pending approval request safely."""
    appr = ApprovalRepository.get_by_identifier(db, approval_id)
    if not appr:
        raise APIException(status_code=404, code="APPROVAL_NOT_FOUND", message=f"Approval request '{approval_id}' was not found.")
    if appr.status != "Pending":
        raise APIException(status_code=409, code="APPROVAL_ALREADY_RESOLVED", message=f"Approval request '{approval_id}' is already resolved with status '{appr.status}'.")
    cancelled = ApprovalRepository.cancel(db, appr)
    return format_approval_response(cancelled, db)

@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
def decide_approval(approval_id: str, request: ApprovalDecisionRequest, db: Session = Depends(get_db)):
    """Resolve an approval request (Approve or Reject), updating audit logs and preventing duplicate decisions."""
    appr = ApprovalRepository.get_by_identifier(db, approval_id)
    if not appr:
        raise APIException(status_code=404, code="APPROVAL_NOT_FOUND", message=f"Approval request with ID '{approval_id}' was not found.")
    if appr.status != "Pending":
        raise APIException(status_code=409, code="APPROVAL_ALREADY_RESOLVED", message=f"Approval request '{approval_id}' has already been resolved with status '{appr.status}'.")

    new_status = request.decision
    appr = ApprovalRepository.update(db, appr, ApprovalUpdate(status=new_status))

    # Log security event
    event_category = "Approval granted" if new_status == "Approved" else "Approval rejected"
    event_decision = "Allowed" if new_status == "Approved" else "Blocked"
    agent_name = appr.agent.name if appr.agent else "Simulator"
    event_explanation = f"Demo {new_status.lower()} for {appr.operation}. No external operation executed."

    log_security_event(
        db=db,
        category=event_category,
        source=agent_name,
        risk_level=appr.risk_level,
        decision=event_decision,
        explanation=event_explanation,
        event_source="application",
        agent_id=appr.agent_id,
        tool_id=appr.tool_id
    )

    return format_approval_response(appr, db)
