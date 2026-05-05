"""Audit logger tests for masking and query behavior.

Author: Sarala Biswal
"""

import pytest

from app.governance.audit_logger import log_action, query_audit_log


@pytest.mark.asyncio
async def test_audit_log_masks_sensitive_fields():
    entry_id = await log_action(
        workflow_id="workflow-1",
        agent="hr_agent",
        tool="create_employee",
        input_payload={"full_name": "Jane Smith", "ssn": "123-45-6789"},
        output_payload={"token": "secret-token", "status": "ok"},
        duration_ms=12,
        status="success",
    )

    rows = await query_audit_log(workflow_id="workflow-1")
    assert rows[0]["id"] == entry_id
    assert rows[0]["input_payload"]["ssn"] == "***"
    assert rows[0]["output_payload"]["token"] == "***"


@pytest.mark.asyncio
async def test_audit_query_filters_by_agent_and_status():
    await log_action(
        workflow_id="workflow-1",
        agent="it_agent",
        tool="create_ticket",
        input_payload={},
        output_payload={},
        duration_ms=1,
        status="success",
    )
    await log_action(
        workflow_id="workflow-1",
        agent="hr_agent",
        tool="create_employee",
        input_payload={},
        output_payload={},
        duration_ms=1,
        status="error",
    )

    rows = await query_audit_log(agent="it_agent", status="success")
    assert len(rows) == 1
    assert rows[0]["tool"] == "create_ticket"
