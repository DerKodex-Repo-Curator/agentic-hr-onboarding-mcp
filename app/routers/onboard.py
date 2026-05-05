"""Workflow API routes for onboarding, extraction, status, and evidence.

Author: Sarala Biswal
"""

from fastapi import APIRouter

from app.agents.orchestrator import OrchestratorAgent
from app.governance.audit_logger import query_audit_log
from app.integrations.idempotency import idempotency_key
from app.integrations.ledger import find_external_record, records_for_workflow
from app.models import EmployeeData, OnboardRequest, OnboardResponse

router = APIRouter()


@router.post("/onboard", response_model=OnboardResponse)
async def onboard(request: OnboardRequest) -> OnboardResponse:
    """Trigger the multi-agent onboarding workflow."""
    agent = OrchestratorAgent()
    return await agent.run(request)


@router.post("/onboard/status")
async def onboard_status(request: OnboardRequest) -> dict[str, object]:
    """Check whether this employee onboarding has already been processed."""
    agent = OrchestratorAgent()
    employee = await agent.extract_employee_data(request.instruction)
    record_specs = {
        "workday": ("workday", "create_employee"),
        "jira": ("jira", "create_ticket"),
        "slack": ("slack", "send_message"),
        "salesforce": ("salesforce", "create_onboarding_record"),
    }
    records = {}

    for key, (system, action) in record_specs.items():
        record = await find_external_record(
            system,
            action,
            idempotency_key(system, action, employee),
        )
        if record:
            records[key] = {
                "external_id": record["external_id"],
                "external_url": record["external_url"],
                "mode": record["mode"],
                "status": record["status"],
            }

    return {
        "processed": "workday" in records,
        "employee": employee.model_dump(),
        "records": records,
    }


@router.post("/extract", response_model=EmployeeData)
async def extract(request: OnboardRequest) -> EmployeeData:
    """Extract structured employee data from a natural language instruction."""
    agent = OrchestratorAgent()
    return await agent.extract_employee_data(request.instruction)


@router.get("/workflows/{workflow_id}/evidence")
async def workflow_evidence(workflow_id: str) -> dict[str, object]:
    """Return ledger and audit evidence for one onboarding workflow."""
    records = await records_for_workflow(workflow_id)
    audit_entries = await query_audit_log(workflow_id=workflow_id, limit=50)
    return {
        "workflow_id": workflow_id,
        "records": records,
        "audit_entries": audit_entries,
    }
