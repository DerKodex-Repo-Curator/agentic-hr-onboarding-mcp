"""MCP connector tests for mock and real-mode request construction.

Author: Sarala Biswal
"""

import pytest

from app.mcp.jira_mcp import JiraMCPServer
from app.mcp.salesforce_mcp import SalesforceMCPServer
from app.mcp.slack_mcp import SlackMCPServer
from app.mcp.workday_mcp import WorkdayMCPServer, _mapped_payload

API_KEY = "test-key"


@pytest.mark.asyncio
async def test_workday_create_employee():
    mcp = WorkdayMCPServer(api_key=API_KEY)
    response = await mcp.execute(
        "create_employee",
        {
            "full_name": "Jane Smith",
            "role": "Senior Engineer",
            "department": "Platform",
            "start_date": "2026-06-01",
        },
        api_key=API_KEY,
    )
    assert response.success
    assert response.result["employee_id"].startswith("EMP-")
    assert response.result["status"] == "created"


@pytest.mark.asyncio
async def test_invalid_key_returns_error_response():
    mcp = WorkdayMCPServer(api_key=API_KEY)
    response = await mcp.execute("create_employee", {}, api_key="wrong-key")
    assert not response.success
    assert response.error == "Invalid MCP API key"


@pytest.mark.asyncio
async def test_jira_create_ticket():
    mcp = JiraMCPServer(api_key=API_KEY)
    response = await mcp.execute(
        "create_ticket",
        {
            "summary": "Onboarding: Jane Smith",
            "employee_name": "Jane Smith",
            "start_date": "2026-06-01",
            "required_systems": ["laptop", "slack"],
        },
        api_key=API_KEY,
    )
    assert response.success
    assert response.result["ticket_id"].startswith("IT-")


@pytest.mark.asyncio
async def test_slack_send_message_mock():
    mcp = SlackMCPServer(api_key=API_KEY)
    response = await mcp.execute(
        "send_message",
        {"channel": "john.doe", "text": "Test notification"},
        api_key=API_KEY,
    )
    assert response.success
    assert response.result["status"] == "sent"
    assert response.result["mode"] == "mock"


@pytest.mark.asyncio
async def test_salesforce_create_onboarding_record():
    mcp = SalesforceMCPServer(api_key=API_KEY)
    response = await mcp.execute(
        "create_onboarding_record",
        {
            "employee_name": "Jane Smith",
            "role": "Account Executive",
            "department": "Sales",
            "start_date": "2026-06-01",
            "required_systems": ["salesforce", "slack"],
        },
        api_key=API_KEY,
    )
    assert response.success
    assert response.result["record_id"].startswith("SF-")


def test_tool_schemas_valid():
    for mcp_class in [WorkdayMCPServer, JiraMCPServer, SlackMCPServer, SalesforceMCPServer]:
        mcp = mcp_class(api_key=API_KEY)
        schema = mcp.tool_schema()
        assert "name" in schema
        assert "tools" in schema
        assert schema["version"] == "v1"


def test_field_map_json_overrides_vendor_payload_names():
    payload = _mapped_payload(
        {
            "employee_name": "Jane Smith",
            "role": "Senior Engineer",
            "start_date": "2026-06-01",
        },
        '{"employee_name":"Name","role":"Job_Title__c"}',
        {
            "employee_name": "Full_Name__c",
            "role": "Role__c",
            "start_date": "Start_Date__c",
        },
    )

    assert payload == {
        "Name": "Jane Smith",
        "Job_Title__c": "Senior Engineer",
        "Start_Date__c": "2026-06-01",
    }


@pytest.mark.asyncio
async def test_slack_channel_map_resolves_manager_handle():
    class FakeClient:
        async def users_lookupByEmail(self, email):
            raise AssertionError("email lookup should not run when map has the handle")

        async def users_list(self, limit, cursor=None):
            raise AssertionError("users list should not run when map has the handle")

    from app.config import settings

    settings.slack_channel_map_json = '{"john.doe":"U123"}'
    channel = await SlackMCPServer(api_key=API_KEY)._resolve_real_channel(FakeClient(), "john.doe")

    assert channel == "U123"
