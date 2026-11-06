from typing import List

DECISION_HIERARCHY = ["Allowed", "Approval required", "Blocked"]

def normalize_decision(d: str) -> str:
    cleaned = d.strip()
    if cleaned.lower() == "allowed":
        return "Allowed"
    if cleaned.lower() in ("approval required", "approval_required"):
        return "Approval required"
    if cleaned.lower() == "blocked":
        return "Blocked"
    return cleaned

def evaluate_worst_decision(decisions: List[str]) -> str:
    max_idx = 0
    for d in decisions:
        norm = normalize_decision(d)
        if norm in DECISION_HIERARCHY:
            idx = DECISION_HIERARCHY.index(norm)
            if idx > max_idx:
                max_idx = idx
    return DECISION_HIERARCHY[max_idx]

def map_tool_permission_to_decision(permission_status: str) -> str:
    if permission_status == "Allowed":
        return "Allowed"
    elif permission_status == "Approval Required":
        return "Approval required"
    elif permission_status in ("Restricted", "Blocked"):
        return "Blocked"
    return "Blocked"

