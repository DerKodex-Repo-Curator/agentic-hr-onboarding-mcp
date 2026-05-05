"""Jira MCP connector with mock and real-mode execution paths.

Author: Sarala Biswal
"""

from typing import Any

import httpx

from app.config import settings
from app.mcp.base import BaseMCPServer
from app.mcp.workday_mcp import _stable_number


class JiraMCPServer(BaseMCPServer):
    """Mock MCP server simulating Jira Service Management."""

    def tool_schema(self) -> dict[str, Any]:
        return {
            "name": "jira_mcp",
            "version": self.version,
            "tools": {
                "create_ticket": {
                    "description": "Create an IT onboarding ticket in Jira",
                    "parameters": {
                        "type": "object",
                        "required": ["summary", "employee_name", "start_date", "required_systems"],
                        "properties": {
                            "summary": {"type": "string"},
                            "employee_name": {"type": "string"},
                            "start_date": {"type": "string"},
                            "required_systems": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "priority": {"type": "string", "default": "Medium"},
                        },
                    },
                }
            },
        }

    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        if tool_name != "create_ticket":
            raise ValueError(f"Unknown tool: {tool_name}")

        if settings.effective_it_mode == "real":
            if not all([settings.jira_base_url, settings.jira_email, settings.jira_api_token]):
                raise RuntimeError(
                    "JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN are required when "
                    "IT_MODE=real"
                )

            issue_payload = {
                "fields": {
                    "project": {"key": settings.jira_project_key},
                    "summary": params["summary"],
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": (
                                            f"Provision access for {params['employee_name']} "
                                            f"starting {params['start_date']}. Systems: "
                                            f"{', '.join(params['required_systems'])}."
                                        ),
                                    }
                                ],
                            }
                        ],
                    },
                    "issuetype": {"name": settings.jira_issue_type},
                    "priority": {"name": params.get("priority", "Medium")},
                    "labels": [settings.jira_onboarding_label],
                }
            }
            if settings.jira_request_type_id:
                issue_payload["fields"]["customfield_request_type"] = settings.jira_request_type_id
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{settings.jira_base_url.rstrip('/')}/rest/api/3/issue",
                    auth=(settings.jira_email, settings.jira_api_token),
                    json=issue_payload,
                )
                response.raise_for_status()
            payload = response.json()
            ticket_id = str(payload["key"])
            return {
                "ticket_id": ticket_id,
                "url": f"{settings.jira_base_url.rstrip('/')}/browse/{ticket_id}",
                "status": "created",
                "assignee_queue": "IT-Onboarding",
            }

        ticket_id = f"IT-{_stable_number(str(params['employee_name']))}"
        return {
            "ticket_id": ticket_id,
            "url": f"https://mock.jira.com/browse/{ticket_id}",
            "status": "created",
            "assignee_queue": "IT-Onboarding",
        }
