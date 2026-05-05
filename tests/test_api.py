"""API and browser-shell tests for the onboarding command center.

Author: Sarala Biswal
"""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ui_home(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Employee Onboarding Command Center" in response.text
    assert "Onboarding Workspace" in response.text
    assert "Guided intake" in response.text
    assert "Full name" in response.text
    assert "Generated prompt" in response.text
    assert "Generate prompt" in response.text
    assert "Generate form (extract fields)" in response.text
    assert "Load samples" in response.text
    assert "Roster" in response.text
    assert "Salesforce" in response.text
    assert "Settings" in response.text
    assert "Demo mode options" in response.text
    assert "Production mode options" in response.text
    assert "Logical Architecture" in response.text
    assert "LangChain" in response.text
    assert "Agent orchestrator" in response.text
    assert "Physical Architecture" in response.text


@pytest.mark.asyncio
async def test_onboard_dry_run(client):
    response = await client.post(
        "/onboard",
        json={
            "instruction": (
                "Onboard Jane Smith as a Senior Engineer on the Platform team "
                "starting June 1 2026. Manager is @john.doe on Slack."
            ),
            "dry_run": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["dry_run"] is True
    assert data["results"]["workday"]["status"] == "skipped"
    assert data["results"]["jira"]["status"] == "skipped"
    assert data["results"]["slack"]["channel"] == "john.doe"
    assert data["results"]["salesforce"]["status"] == "skipped"


@pytest.mark.asyncio
async def test_extract_prompt_to_employee_fields(client):
    response = await client.post(
        "/extract",
        json={
            "instruction": (
                "Please Onboard Aisha Morgan as an Enablement Manager on the Sales team "
                "starting September 8 2026. Manager is @nora.li on Slack. "
                "Required systems are laptop, Google Workspace, Slack, and Salesforce."
            ),
            "dry_run": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Aisha Morgan"
    assert data["role"] == "Enablement Manager"
    assert data["department"] == "Sales"
    assert data["start_date"] == "2026-09-08"
    assert data["manager_slack_handle"] == "@nora.li"
    assert data["required_systems"] == ["laptop", "gsuite", "slack", "salesforce"]


@pytest.mark.asyncio
async def test_settings_endpoint_masks_runtime_configuration(client):
    response = await client.get("/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["app_mode"] == "demo"
    assert data["llm"]["provider"] == "rules"
    assert data["pilot_readiness"]["status"] == "ready"
    assert data["connectors"]["workday"]["mode"] == "mock"
    assert data["connectors"]["workday"]["latest_record"] is None
    assert data["connectors"]["it"]["provider"] == "jira"
    assert data["connectors"]["salesforce"]["readiness_object"] == "New_Hire__c"
    assert "mcp_api_key" not in data


@pytest.mark.asyncio
async def test_settings_mode_update_changes_effective_connectors(client):
    response = await client.post("/settings/mode", json={"mode": "production"})
    assert response.status_code == 200
    data = response.json()
    assert data["app_mode"] == "real"
    assert data["connectors"]["workday"]["mode"] == "real"
    assert data["pilot_readiness"]["status"] == "blocked"

    response = await client.post("/settings/mode", json={"mode": "demo"})
    assert response.status_code == 200
    data = response.json()
    assert data["app_mode"] == "demo"
    assert data["connectors"]["workday"]["mode"] == "mock"


@pytest.mark.asyncio
async def test_pilot_readiness_endpoint(client):
    response = await client.get("/pilot/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["connectors"]["slack"]["mode"] == "mock"


@pytest.mark.asyncio
async def test_settings_endpoint_shows_latest_external_records(client):
    await client.post(
        "/onboard",
        json={
            "instruction": (
                "Onboard Priya Raman as a Sales Engineer on the Revenue team "
                "starting August 3 2026. Manager is @sam.lee on Slack."
            ),
            "dry_run": False,
        },
    )

    response = await client.get("/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["connectors"]["workday"]["latest_record"]["external_id"].startswith("EMP-")
    assert data["connectors"]["it"]["latest_record"]["external_id"].startswith("IT-")
    assert data["connectors"]["salesforce"]["latest_record"]["external_id"].startswith("SF-")


@pytest.mark.asyncio
async def test_workflow_evidence_returns_ledger_and_audit_rows(client):
    onboard = await client.post(
        "/onboard",
        json={
            "instruction": (
                "Onboard Nia Shah as an Account Executive on the Growth team "
                "starting October 12 2026. Manager is @nora.li on Slack."
            ),
            "dry_run": False,
        },
    )
    workflow_id = onboard.json()["workflow_id"]

    response = await client.get(f"/workflows/{workflow_id}/evidence")
    assert response.status_code == 200
    data = response.json()
    systems = {record["system"] for record in data["records"]}

    assert systems == {"workday", "jira", "slack", "salesforce"}
    assert len(data["audit_entries"]) == 4


@pytest.mark.asyncio
async def test_onboard_status_detects_existing_workflow(client):
    payload = {
        "instruction": (
            "Onboard Mateo Alvarez as a Revenue Operations Analyst on the Growth team "
            "starting July 6 2026. Manager is @samir.patel on Slack."
        ),
        "dry_run": False,
    }
    before = await client.post("/onboard/status", json=payload)
    assert before.status_code == 200
    assert before.json()["processed"] is False

    await client.post("/onboard", json=payload)

    after = await client.post("/onboard/status", json=payload)
    assert after.status_code == 200
    data = after.json()
    assert data["processed"] is True
    assert data["records"]["workday"]["external_id"].startswith("EMP-")
    assert data["records"]["salesforce"]["external_id"].startswith("SF-")


@pytest.mark.asyncio
async def test_audit_log_populated_after_onboard(client):
    await client.post(
        "/onboard",
        json={"instruction": "Onboard Bob Jones as Analyst on Finance team", "dry_run": True},
    )

    response = await client.get("/audit?agent=hr_agent")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    await client.post(
        "/onboard",
        json={"instruction": "Onboard Mira Patel as Engineer on Platform team", "dry_run": True},
    )

    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "onboarding_workflows_total" in response.text
    assert 'agent_calls_total{agent="hr_agent",mode="dry_run"' in response.text
