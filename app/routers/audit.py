"""Audit API routes for workflow governance review.

Author: Sarala Biswal
"""

from fastapi import APIRouter, Query

from app.governance.audit_logger import query_audit_log

router = APIRouter()


@router.get("/audit")
async def get_audit_log(
    workflow_id: str | None = Query(None),
    agent: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, le=500),
):
    """Query audit log entries."""
    return await query_audit_log(
        workflow_id=workflow_id,
        agent=agent,
        status=status,
        limit=limit,
    )
