import sqlite3
from typing import Dict, Any, Optional
from .security_engine import analyze_prompt
from .policy_engine import evaluate_worst_decision, map_tool_permission_to_decision

def get_current_settings(conn: sqlite3.Connection) -> Dict[str, Any]:
    cursor = conn.cursor()
    cursor.execute("SELECT risk_sensitivity, automatic_critical_blocking, require_high_risk_approval, mask_sensitive_data, notifications_enabled, updated_at FROM settings WHERE id = 1")
    row = cursor.fetchone()
    if row:
        return {
            "risk_sensitivity": float(row["risk_sensitivity"]),
            "automatic_critical_blocking": bool(row["automatic_critical_blocking"]),
            "require_high_risk_approval": bool(row["require_high_risk_approval"]),
            "mask_sensitive_data": bool(row["mask_sensitive_data"]),
            "notifications_enabled": bool(row["notifications_enabled"]),
            "updated_at": row["updated_at"],
        }
    return {
        "risk_sensitivity": 1.0,
        "automatic_critical_blocking": True,
        "require_high_risk_approval": True,
        "mask_sensitive_data": True,
        "notifications_enabled": True,
        "updated_at": "",
    }

def scan_and_evaluate(conn: sqlite3.Connection, prompt: str) -> Dict[str, Any]:
    settings = get_current_settings(conn)
    result = analyze_prompt(
        text=prompt,
        sensitivity=settings["risk_sensitivity"],
        auto_block=settings["automatic_critical_blocking"],
        high_risk_approval=settings["require_high_risk_approval"],
        mask_pii=settings["mask_sensitive_data"]
    )
    return result

