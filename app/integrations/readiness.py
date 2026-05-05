"""Production-mode readiness checks for cloud connector configuration.

Author: Sarala Biswal
"""

import json
from typing import Any

from app.config import settings


def _json_object_status(raw_value: str, name: str) -> list[str]:
    if not raw_value.strip():
        return []
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        return [f"{name} is not valid JSON: {exc.msg}"]
    if not isinstance(parsed, dict):
        return [f"{name} must be a JSON object"]
    return []


def _connector_status(
    *,
    mode: str,
    required_when_real: dict[str, str],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    issues: list[str] = []
    if mode == "real":
        issues.extend(
            f"{env_name} is required for real mode"
            for env_name, value in required_when_real.items()
            if not value
        )
    status = "ready" if not issues else "blocked"
    return {
        "mode": mode,
        "status": status,
        "issues": issues,
        "warnings": warnings or [],
    }


def connector_readiness() -> dict[str, dict[str, Any]]:
    """Return pilot readiness checks without exposing secrets."""
    workday_warnings = _json_object_status(
        settings.workday_field_map_json,
        "WORKDAY_FIELD_MAP_JSON",
    )
    jira_warnings = []
    if settings.effective_it_mode == "real" and not settings.jira_request_type_id:
        jira_warnings.append("JIRA_REQUEST_TYPE_ID is optional but recommended for JSM pilots")
    slack_warnings = _json_object_status(
        settings.slack_channel_map_json,
        "SLACK_CHANNEL_MAP_JSON",
    )
    if settings.effective_slack_mode == "real" and not settings.slack_channel_map_json.strip():
        slack_warnings.append("SLACK_CHANNEL_MAP_JSON is recommended for initial sandbox pilots")
    salesforce_warnings = _json_object_status(
        settings.salesforce_field_map_json,
        "SALESFORCE_FIELD_MAP_JSON",
    )

    return {
        "workday": _connector_status(
            mode=settings.effective_workday_mode,
            required_when_real={
                "WORKDAY_BASE_URL": settings.workday_base_url,
                "WORKDAY_TENANT": settings.workday_tenant,
                "WORKDAY_ACCESS_TOKEN": settings.workday_access_token,
            },
            warnings=workday_warnings,
        ),
        "it": _connector_status(
            mode=settings.effective_it_mode,
            required_when_real={
                "JIRA_BASE_URL": settings.jira_base_url,
                "JIRA_EMAIL": settings.jira_email,
                "JIRA_API_TOKEN": settings.jira_api_token,
            },
            warnings=jira_warnings,
        ),
        "slack": _connector_status(
            mode=settings.effective_slack_mode,
            required_when_real={"SLACK_BOT_TOKEN": settings.slack_bot_token},
            warnings=slack_warnings,
        ),
        "salesforce": _connector_status(
            mode=settings.effective_salesforce_mode,
            required_when_real={
                "SALESFORCE_INSTANCE_URL": settings.salesforce_instance_url,
                "SALESFORCE_ACCESS_TOKEN": settings.salesforce_access_token,
            },
            warnings=salesforce_warnings,
        ),
    }


def overall_readiness() -> dict[str, Any]:
    """Summarize whether configured real connector pilots can run."""
    connectors = connector_readiness()
    blocked = [
        name
        for name, details in connectors.items()
        if details["mode"] == "real" and details["status"] != "ready"
    ]
    warning_count = sum(len(details["warnings"]) for details in connectors.values())
    return {
        "status": "blocked" if blocked else "ready",
        "blocked_connectors": blocked,
        "warning_count": warning_count,
        "connectors": connectors,
    }
