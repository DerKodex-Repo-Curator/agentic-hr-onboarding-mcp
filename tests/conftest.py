"""Shared pytest fixtures for isolated onboarding-agent tests.

Author: Sarala Biswal
"""

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app

os.environ.setdefault("SLACK_MOCK_MODE", "true")


@pytest.fixture(autouse=True)
def test_settings(tmp_path):
    """Use isolated settings for each test."""
    original_db_path = settings.db_path
    original_slack_mock_mode = settings.slack_mock_mode
    original_mcp_api_key = settings.mcp_api_key
    original_llm_provider = settings.llm_provider
    original_app_mode = settings.app_mode
    original_workday_mode = settings.workday_mode
    original_it_mode = settings.it_mode
    original_slack_mode = settings.slack_mode
    original_salesforce_mode = settings.salesforce_mode
    original_workday_base_url = settings.workday_base_url
    original_workday_tenant = settings.workday_tenant
    original_workday_access_token = settings.workday_access_token
    original_workday_workers_path = settings.workday_workers_path
    original_workday_field_map_json = settings.workday_field_map_json
    original_jira_base_url = settings.jira_base_url
    original_jira_email = settings.jira_email
    original_jira_api_token = settings.jira_api_token
    original_jira_issue_type = settings.jira_issue_type
    original_jira_request_type_id = settings.jira_request_type_id
    original_jira_onboarding_label = settings.jira_onboarding_label
    original_slack_bot_token = settings.slack_bot_token
    original_slack_channel_map_json = settings.slack_channel_map_json
    original_salesforce_instance_url = settings.salesforce_instance_url
    original_salesforce_access_token = settings.salesforce_access_token
    original_salesforce_readiness_object = settings.salesforce_readiness_object
    original_salesforce_field_map_json = settings.salesforce_field_map_json

    settings.db_path = str(tmp_path / "audit.db")
    settings.slack_mock_mode = True
    settings.mcp_api_key = "test-key"
    settings.llm_provider = "rules"
    settings.app_mode = "demo"
    settings.workday_mode = "auto"
    settings.it_mode = "auto"
    settings.slack_mode = "auto"
    settings.salesforce_mode = "auto"
    settings.workday_base_url = ""
    settings.workday_tenant = ""
    settings.workday_access_token = ""
    settings.workday_workers_path = "/ccx/api/v1/{tenant}/workers"
    settings.workday_field_map_json = ""
    settings.jira_base_url = ""
    settings.jira_email = ""
    settings.jira_api_token = ""
    settings.jira_issue_type = "Task"
    settings.jira_request_type_id = ""
    settings.jira_onboarding_label = "onboarding"
    settings.slack_bot_token = ""
    settings.slack_channel_map_json = ""
    settings.salesforce_instance_url = ""
    settings.salesforce_access_token = ""
    settings.salesforce_readiness_object = "New_Hire__c"
    settings.salesforce_field_map_json = ""
    yield

    settings.db_path = original_db_path
    settings.slack_mock_mode = original_slack_mock_mode
    settings.mcp_api_key = original_mcp_api_key
    settings.llm_provider = original_llm_provider
    settings.app_mode = original_app_mode
    settings.workday_mode = original_workday_mode
    settings.it_mode = original_it_mode
    settings.slack_mode = original_slack_mode
    settings.salesforce_mode = original_salesforce_mode
    settings.workday_base_url = original_workday_base_url
    settings.workday_tenant = original_workday_tenant
    settings.workday_access_token = original_workday_access_token
    settings.workday_workers_path = original_workday_workers_path
    settings.workday_field_map_json = original_workday_field_map_json
    settings.jira_base_url = original_jira_base_url
    settings.jira_email = original_jira_email
    settings.jira_api_token = original_jira_api_token
    settings.jira_issue_type = original_jira_issue_type
    settings.jira_request_type_id = original_jira_request_type_id
    settings.jira_onboarding_label = original_jira_onboarding_label
    settings.slack_bot_token = original_slack_bot_token
    settings.slack_channel_map_json = original_slack_channel_map_json
    settings.salesforce_instance_url = original_salesforce_instance_url
    settings.salesforce_access_token = original_salesforce_access_token
    settings.salesforce_readiness_object = original_salesforce_readiness_object
    settings.salesforce_field_map_json = original_salesforce_field_map_json


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
