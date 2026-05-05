"""Integration helper tests for modes, readiness, and ledger behavior.

Author: Sarala Biswal
"""

from app.config import settings
from app.integrations.idempotency import idempotency_key
from app.integrations.ledger import (
    find_external_record,
    latest_external_records,
    record_external_record,
)
from app.integrations.modes import effective_mode
from app.integrations.readiness import connector_readiness, overall_readiness
from app.models import EmployeeData


def test_effective_mode_respects_request_dry_run():
    assert effective_mode("real", request_dry_run=True) == "dry_run"
    assert effective_mode("mock", request_dry_run=False) == "mock"


def test_idempotency_key_normalizes_employee_identity():
    employee = EmployeeData(
        full_name="Jane A. Smith",
        role="Senior Engineer",
        department="Platform",
        start_date="2026-06-01",
        manager_slack_handle="@john.doe",
    )

    assert (
        idempotency_key("Salesforce", "Create Onboarding Record", employee)
        == "salesforce:create-onboarding-record:jane-a-smith:2026-06-01"
    )


async def test_ledger_records_and_returns_latest_external_record():
    await record_external_record(
        workflow_id="workflow-1",
        system="jira",
        action="create_ticket",
        key="jira:create-ticket:jane-smith:2026-06-01",
        external_id="IT-123",
        external_url="https://example.atlassian.net/browse/IT-123",
        mode="mock",
    )

    found = await find_external_record(
        "jira",
        "create_ticket",
        "jira:create-ticket:jane-smith:2026-06-01",
    )
    latest = await latest_external_records()

    assert found is not None
    assert found["external_id"] == "IT-123"
    assert latest["jira"]["external_url"].endswith("/IT-123")


def test_readiness_blocks_real_connectors_without_credentials():
    settings.workday_mode = "real"

    readiness = connector_readiness()

    assert readiness["workday"]["status"] == "blocked"
    assert "WORKDAY_BASE_URL is required for real mode" in readiness["workday"]["issues"]
    assert overall_readiness()["status"] == "blocked"


def test_readiness_accepts_configured_sandbox_connector():
    settings.slack_mode = "real"
    settings.slack_bot_token = "xoxb-test"
    settings.slack_channel_map_json = '{"john.doe":"U123"}'

    readiness = connector_readiness()

    assert readiness["slack"]["status"] == "ready"
    assert readiness["slack"]["warnings"] == []
    assert overall_readiness()["status"] == "ready"


def test_readiness_warns_on_invalid_mapping_json():
    settings.salesforce_field_map_json = '["not", "an", "object"]'

    readiness = connector_readiness()

    assert readiness["salesforce"]["status"] == "ready"
    assert "SALESFORCE_FIELD_MAP_JSON must be a JSON object" in readiness["salesforce"]["warnings"]
