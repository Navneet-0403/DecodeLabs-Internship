import sqlite3
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from ..database import get_db, reset_tool_permissions
from ..schemas import ToolResponse, ToolUpdateRequest, VALID_TOOL_PERMISSIONS
from ..exceptions import APIException

router = APIRouter(prefix="/api/tools", tags=["Tool Permissions"])

def get_tool_by_identifier(cursor: sqlite3.Cursor, identifier: str) -> sqlite3.Row:
    # 1. Match tool_id directly (e.g. 'tool-1')
    cursor.execute("""
        SELECT id, tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at
        FROM tool_permissions WHERE tool_id = ?
    """, (identifier,))
    row = cursor.fetchone()
    if row:
        return row

    # 2. Try match by database id
    try:
        db_id = int(identifier)
        cursor.execute("""
            SELECT id, tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at
            FROM tool_permissions WHERE id = ?
        """, (db_id,))
        row = cursor.fetchone()
        if row:
            return row
    except ValueError:
        pass

    # 3. Try match by 0-based offset or tool name
    cursor.execute("""
        SELECT id, tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at
        FROM tool_permissions ORDER BY id ASC
    """)
    all_rows = cursor.fetchall()
    try:
        idx = int(identifier)
        if 0 <= idx < len(all_rows):
            return all_rows[idx]
    except ValueError:
        pass

    for r in all_rows:
        if r["tool_name"].lower() == identifier.lower():
            return r

    raise APIException(
        status_code=404,
        code="TOOL_NOT_FOUND",
        message=f"Tool with identifier '{identifier}' was not found."
    )

@router.get("", response_model=List[ToolResponse])
def get_tools(conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at
        FROM tool_permissions ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    return [
        ToolResponse(
            id=r["id"],
            tool_id=r["tool_id"],
            tool_name=r["tool_name"],
            description=r["description"],
            assigned_agent=r["assigned_agent"],
            risk_level=r["risk_level"],
            permission_status=r["permission_status"],
            updated_at=r["updated_at"]
        )
        for r in rows
    ]

@router.get("/{tool_id}", response_model=ToolResponse)
def get_tool(tool_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    row = get_tool_by_identifier(cursor, tool_id)
    return ToolResponse(
        id=row["id"],
        tool_id=row["tool_id"],
        tool_name=row["tool_name"],
        description=row["description"],
        assigned_agent=row["assigned_agent"],
        risk_level=row["risk_level"],
        permission_status=row["permission_status"],
        updated_at=row["updated_at"]
    )

@router.put("/{tool_id}", response_model=ToolResponse)
def update_tool_permission(tool_id: str, request: ToolUpdateRequest, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    row = get_tool_by_identifier(cursor, tool_id)

    new_status = request.permission_status
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        UPDATE tool_permissions
        SET permission_status = ?, updated_at = ?
        WHERE id = ?
    """, (new_status, now, row["id"]))
    conn.commit()

    cursor.execute("""
        SELECT id, tool_id, tool_name, description, assigned_agent, risk_level, permission_status, updated_at
        FROM tool_permissions WHERE id = ?
    """, (row["id"],))
    updated_row = cursor.fetchone()

    return ToolResponse(
        id=updated_row["id"],
        tool_id=updated_row["tool_id"],
        tool_name=updated_row["tool_name"],
        description=updated_row["description"],
        assigned_agent=updated_row["assigned_agent"],
        risk_level=updated_row["risk_level"],
        permission_status=updated_row["permission_status"],
        updated_at=updated_row["updated_at"]
    )

@router.post("/reset", response_model=List[ToolResponse])
def reset_tools(conn: sqlite3.Connection = Depends(get_db)):
    reset_tool_permissions()
    return get_tools(conn)

