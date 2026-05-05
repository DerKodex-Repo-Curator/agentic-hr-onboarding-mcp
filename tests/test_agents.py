"""Agent behavior tests for workflow idempotency and connector outcomes.

Author: Sarala Biswal
"""

import pytest

from app.agents.hr_agent import HRAgent
from app.agents.it_agent import ITAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.salesforce_agent import SalesforceAgent
from app.config import settings
from app.integrations.idempotency import idempotency_key
from app.integrations.ledger import find_external_record
from app.models import EmployeeData


@pytest.fixture
def employee() -> EmployeeData:
    return EmployeeData(
        full_name="Jane Smith",
        role="Senior Engineer",
        department="Platform",
        start_date="2026-06-01",
        manager_slack_handle="@john.doe",
        required_systems=["laptop", "slack"],
    )


@pytest.mark.asyncio
async def test_hr_agent_dry_run(employee):
    result = await HRAgent().run("workflow-1", employee, dry_run=True)
    assert result.status == "skipped"
    assert result.employee_id == "DRY-RUN"


@pytest.mark.asyncio
async def test_it_agent_creates_ticket(employee):
    result = await ITAgent().run("workflow-1", employee)
    assert result.status == "created"
    assert result.ticket_id.startswith("IT-")


@pytest.mark.asyncio
async def test_it_agent_reuses_existing_ticket(employee):
    first = await ITAgent().run("workflow-1", employee)
    second = await ITAgent().run("workflow-2", employee)
    record = await find_external_record(
        "jira",
        "create_ticket",
        idempotency_key("jira", "create_ticket", employee),
    )

    assert first.status == "created"
    assert second.status == "existing"
    assert second.ticket_id == first.ticket_id
    assert record is not None
    assert record["external_id"] == first.ticket_id


@pytest.mark.asyncio
async def test_connector_dry_run_mode_skips_write(employee):
    settings.it_mode = "dry_run"
    result = await ITAgent().run("workflow-1", employee, dry_run=False)
    record = await find_external_record(
        "jira",
        "create_ticket",
        idempotency_key("jira", "create_ticket", employee),
    )

    assert result.status == "skipped"
    assert result.ticket_id == "DRY-RUN"
    assert record is None


@pytest.mark.asyncio
async def test_notification_agent_normalizes_channel(employee):
    result = await NotificationAgent().run("workflow-1", employee)
    assert result.status == "sent"
    assert result.channel == "john.doe"


@pytest.mark.asyncio
async def test_salesforce_agent_creates_record(employee):
    result = await SalesforceAgent().run("workflow-1", employee)
    assert result.status == "created"
    assert result.record_id.startswith("SF-")


def test_orchestrator_uses_langchain_prompt_and_parser():
    agent = OrchestratorAgent()
    prompt = agent._llm_prompt("Onboard Aisha Morgan as a Sales Manager")
    parsed = agent._parse_llm_json('{"full_name":"Aisha Morgan"}')

    assert "Instruction: Onboard Aisha Morgan" in prompt
    assert parsed["full_name"] == "Aisha Morgan"
