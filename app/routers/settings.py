"""Settings API routes for demo/production mode and pilot readiness.

Author: Sarala Biswal
"""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.integrations.ledger import latest_external_records
from app.integrations.readiness import overall_readiness

router = APIRouter()


class ModeUpdateRequest(BaseModel):
    """Runtime app mode update from the settings UI."""

    mode: Literal["demo", "production", "real"]


@router.get("/settings")
async def get_settings() -> dict[str, object]:
    """Expose safe, read-only runtime settings for the demo UI."""
    latest_records = await latest_external_records()

    def latest(system: str) -> dict[str, object] | None:
        record = latest_records.get(system)
        if not record:
            return None
        return {
            "workflow_id": record["workflow_id"],
            "external_id": record["external_id"],
            "external_url": record["external_url"],
            "mode": record["mode"],
            "status": record["status"],
            "created_at": record["created_at"],
        }

    return {
        "environment": settings.app_env,
        "app_mode": settings.app_mode,
        "database": settings.db_path,
        "mcp_version": settings.mcp_version,
        "pilot_readiness": overall_readiness(),
        "llm": {
            "provider": settings.llm_provider,
            "ollama_model": settings.ollama_model,
            "openai_model": settings.openai_model,
            "anthropic_model": settings.anthropic_model,
        },
        "connectors": {
            "workday": {
                "mode": settings.effective_workday_mode,
                "configured_mode": settings.workday_mode,
                "configured": bool(settings.workday_base_url and settings.workday_access_token),
                "workers_path": settings.workday_workers_path,
                "latest_record": latest("workday"),
            },
            "it": {
                "mode": settings.effective_it_mode,
                "configured_mode": settings.it_mode,
                "provider": "jira",
                "configured": bool(settings.jira_base_url and settings.jira_api_token),
                "project_key": settings.jira_project_key,
                "issue_type": settings.jira_issue_type,
                "request_type_configured": bool(settings.jira_request_type_id),
                "latest_record": latest("jira"),
            },
            "slack": {
                "mode": settings.effective_slack_mode,
                "configured_mode": settings.slack_mode,
                "configured": bool(settings.slack_bot_token),
                "channel_map_configured": bool(settings.slack_channel_map_json.strip()),
                "latest_record": latest("slack"),
            },
            "salesforce": {
                "mode": settings.effective_salesforce_mode,
                "configured_mode": settings.salesforce_mode,
                "configured": bool(
                    settings.salesforce_instance_url and settings.salesforce_access_token
                ),
                "readiness_object": settings.salesforce_readiness_object,
                "latest_record": latest("salesforce"),
            },
        },
    }


@router.post("/settings/mode")
async def set_app_mode(request: ModeUpdateRequest) -> dict[str, object]:
    """Set the active app mode for this running app process."""
    settings.app_mode = "real" if request.mode in {"production", "real"} else "demo"
    return await get_settings()


@router.get("/pilot/readiness")
async def get_pilot_readiness() -> dict[str, object]:
    """Expose connector readiness checks without returning secrets."""
    return overall_readiness()
