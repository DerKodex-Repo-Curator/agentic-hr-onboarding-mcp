"""Salesforce MCP connector with mock and real-mode execution paths.

Author: Sarala Biswal
"""

from typing import Any

import httpx

from app.config import settings
from app.mcp.base import BaseMCPServer
from app.mcp.workday_mcp import _mapped_payload, _stable_number


class SalesforceMCPServer(BaseMCPServer):
    """Mock MCP server simulating Salesforce CRM enablement records."""

    def tool_schema(self) -> dict[str, Any]:
        return {
            "name": "salesforce_mcp",
            "version": self.version,
            "tools": {
                "create_onboarding_record": {
                    "description": "Create a Salesforce onboarding/readiness record",
                    "parameters": {
                        "type": "object",
                        "required": ["employee_name", "role", "department", "start_date"],
                        "properties": {
                            "employee_name": {"type": "string"},
                            "role": {"type": "string"},
                            "department": {"type": "string"},
                            "start_date": {"type": "string"},
                            "enablement_stage": {"type": "string"},
                            "required_systems": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                }
            },
        }

    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        if tool_name != "create_onboarding_record":
            raise ValueError(f"Unknown tool: {tool_name}")

        if settings.effective_salesforce_mode == "real":
            if not all([settings.salesforce_instance_url, settings.salesforce_access_token]):
                raise RuntimeError(
                    "SALESFORCE_INSTANCE_URL and SALESFORCE_ACCESS_TOKEN are required when "
                    "SALESFORCE_MODE=real"
                )

            normalized_params = {
                **params,
                "required_systems": ", ".join(params.get("required_systems", [])),
            }
            record_payload = _mapped_payload(
                normalized_params,
                settings.salesforce_field_map_json,
                {
                    "employee_name": "Name",
                    "role": "Role__c",
                    "department": "Department__c",
                    "start_date": "Start_Date__c",
                    "enablement_stage": "Enablement_Stage__c",
                    "required_systems": "Required_Systems__c",
                },
            )
            base_url = settings.salesforce_instance_url.rstrip("/")
            object_name = settings.salesforce_readiness_object
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    (
                        f"{base_url}/services/data/{settings.salesforce_api_version}"
                        f"/sobjects/{object_name}/"
                    ),
                    headers={"Authorization": f"Bearer {settings.salesforce_access_token}"},
                    json=record_payload,
                )
                response.raise_for_status()
            payload = response.json()
            record_id = str(payload["id"])
            return {
                "record_id": record_id,
                "url": f"{base_url}/lightning/r/{object_name}/{record_id}/view",
                "status": "created",
                "enablement_stage": params.get("enablement_stage", "Pre-Start"),
            }

        record_id = f"SF-{_stable_number(str(params['employee_name']))}"
        return {
            "record_id": record_id,
            "url": f"https://mock.salesforce.com/lightning/r/New_Hire__c/{record_id}/view",
            "status": "created",
            "enablement_stage": params.get("enablement_stage", "Pre-Start"),
        }
