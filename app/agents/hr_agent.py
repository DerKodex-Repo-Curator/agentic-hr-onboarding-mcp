"""HR agent that creates or reuses Workday employee records.

Author: Sarala Biswal
"""

import time

from app.config import settings
from app.governance import audit_logger, metrics
from app.integrations.idempotency import idempotency_key
from app.integrations.ledger import find_external_record, record_external_record
from app.integrations.modes import effective_mode
from app.mcp.workday_mcp import WorkdayMCPServer
from app.models import EmployeeData, WorkdayResult


class HRAgent:
    """Coordinate HR-system writes through the Workday MCP boundary."""

    def __init__(self) -> None:
        self.mcp = WorkdayMCPServer(api_key=settings.mcp_api_key, version=settings.mcp_version)

    async def run(
        self,
        workflow_id: str,
        employee: EmployeeData,
        dry_run: bool = False,
    ) -> WorkdayResult:
        """Create or validate a Workday employee record."""
        payload = {
            "full_name": employee.full_name,
            "role": employee.role,
            "department": employee.department,
            "start_date": employee.start_date,
        }
        mode = effective_mode(settings.effective_workday_mode, dry_run)
        ledger_key = idempotency_key("workday", "create_employee", employee)

        if mode == "dry_run":
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="hr_agent",
                tool="create_employee",
                input_payload=payload,
                output_payload={"mode": mode, "idempotency_key": ledger_key},
                duration_ms=0,
                status="skipped",
            )
            metrics.record_agent_call("hr_agent", "create_employee", "skipped", mode=mode)
            return WorkdayResult(employee_id="DRY-RUN", status="skipped")

        existing = await find_external_record("workday", "create_employee", ledger_key)
        if existing:
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="hr_agent",
                tool="create_employee",
                input_payload=payload,
                output_payload={
                    "employee_id": existing["external_id"],
                    "workday_profile_url": existing["external_url"],
                    "mode": existing["mode"],
                    "idempotency_key": ledger_key,
                    "idempotent_replay": True,
                },
                duration_ms=0,
                status="success",
            )
            metrics.record_agent_call(
                "hr_agent",
                "create_employee",
                "success",
                mode=existing["mode"],
            )
            return WorkdayResult(employee_id=existing["external_id"], status="existing")

        start = time.monotonic()
        response = await self.mcp.execute("create_employee", payload, api_key=settings.mcp_api_key)
        duration_ms = int((time.monotonic() - start) * 1000)
        status = "success" if response.success else "error"
        output_payload = dict(response.result or {"error": response.error})
        if response.success:
            output_payload["mode"] = mode
            output_payload["idempotency_key"] = ledger_key

        await audit_logger.log_action(
            workflow_id=workflow_id,
            agent="hr_agent",
            tool="create_employee",
            input_payload=payload,
            output_payload=output_payload,
            duration_ms=duration_ms,
            status=status,
        )
        metrics.record_agent_call("hr_agent", "create_employee", status, mode=mode)

        if not response.success:
            raise RuntimeError(f"HR Agent failed: {response.error}")

        await record_external_record(
            workflow_id=workflow_id,
            system="workday",
            action="create_employee",
            key=ledger_key,
            external_id=response.result["employee_id"],
            external_url=response.result.get("workday_profile_url", ""),
            mode=mode,
        )

        return WorkdayResult(employee_id=response.result["employee_id"], status="created")
