"""Workday MCP connector with deterministic mock and real-mode support.

Author: Sarala Biswal
"""

import json
from typing import Any

import httpx

from app.config import settings
from app.mcp.base import BaseMCPServer


def _stable_number(value: str, modulo: int = 9000, offset: int = 1000) -> int:
    return sum((idx + 1) * ord(char) for idx, char in enumerate(value)) % modulo + offset


def _mapped_payload(
    params: dict[str, Any],
    mapping_json: str,
    defaults: dict[str, str],
) -> dict[str, Any]:
    mapping = defaults
    if mapping_json.strip():
        configured = json.loads(mapping_json)
        if not isinstance(configured, dict):
            raise ValueError("Field map JSON must be an object")
        mapping = {**defaults, **{str(key): str(value) for key, value in configured.items()}}
    return {target: params[source] for source, target in mapping.items() if source in params}


class WorkdayMCPServer(BaseMCPServer):
    """Mock MCP server simulating Workday HRIS."""

    def tool_schema(self) -> dict[str, Any]:
        return {
            "name": "workday_mcp",
            "version": self.version,
            "tools": {
                "create_employee": {
                    "description": "Create a new employee record in Workday",
                    "parameters": {
                        "type": "object",
                        "required": ["full_name", "role", "department", "start_date"],
                        "properties": {
                            "full_name": {"type": "string"},
                            "role": {"type": "string"},
                            "department": {"type": "string"},
                            "start_date": {"type": "string", "format": "date"},
                        },
                    },
                }
            },
        }

    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        if tool_name != "create_employee":
            raise ValueError(f"Unknown tool: {tool_name}")

        if settings.effective_workday_mode == "real":
            if not all(
                [
                    settings.workday_base_url,
                    settings.workday_tenant,
                    settings.workday_access_token,
                ]
            ):
                raise RuntimeError(
                    "WORKDAY_BASE_URL, WORKDAY_TENANT, and WORKDAY_ACCESS_TOKEN are "
                    "required when WORKDAY_MODE=real"
                )

            async with httpx.AsyncClient(timeout=30) as client:
                path = settings.workday_workers_path.format(tenant=settings.workday_tenant)
                response = await client.post(
                    f"{settings.workday_base_url.rstrip('/')}/{path.lstrip('/')}",
                    headers={"Authorization": f"Bearer {settings.workday_access_token}"},
                    json=_mapped_payload(
                        params,
                        settings.workday_field_map_json,
                        {
                            "full_name": "full_name",
                            "role": "role",
                            "department": "department",
                            "start_date": "start_date",
                        },
                    ),
                )
                response.raise_for_status()
            payload = response.json()
            employee_id = str(payload.get("employee_id") or payload.get("id") or "")
            return {
                "employee_id": employee_id,
                "status": "created",
                "workday_profile_url": str(payload.get("url") or ""),
            }

        full_name = str(params["full_name"])
        emp_id = f"EMP-{_stable_number(full_name)}"
        return {
            "employee_id": emp_id,
            "status": "created",
            "workday_profile_url": f"https://mock.workday.com/employees/{emp_id}",
        }
