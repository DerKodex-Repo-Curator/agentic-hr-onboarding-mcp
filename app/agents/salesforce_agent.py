"""Salesforce agent that creates or reuses new-hire readiness records.

Author: Sarala Biswal
"""

import time

from app.config import settings
from app.governance import audit_logger, metrics
from app.integrations.idempotency import idempotency_key
from app.integrations.ledger import find_external_record, record_external_record
from app.integrations.modes import effective_mode
from app.mcp.salesforce_mcp import SalesforceMCPServer
from app.models import EmployeeData, SalesforceResult


class SalesforceAgent:
    """Coordinate CRM enablement records through the Salesforce MCP boundary."""

    def __init__(self) -> None:
        self.mcp = SalesforceMCPServer(api_key=settings.mcp_api_key, version=settings.mcp_version)

    async def run(
        self,
        workflow_id: str,
        employee: EmployeeData,
        dry_run: bool = False,
    ) -> SalesforceResult:
        """Create or validate a Salesforce onboarding/readiness record."""
        payload = {
            "employee_name": employee.full_name,
            "role": employee.role,
            "department": employee.department,
            "start_date": employee.start_date,
            "enablement_stage": "Pre-Start",
            "required_systems": employee.required_systems,
        }
        mode = effective_mode(settings.effective_salesforce_mode, dry_run)
        ledger_key = idempotency_key("salesforce", "create_onboarding_record", employee)

        if mode == "dry_run":
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="salesforce_agent",
                tool="create_onboarding_record",
                input_payload=payload,
                output_payload={"mode": mode, "idempotency_key": ledger_key},
                duration_ms=0,
                status="skipped",
            )
            metrics.record_agent_call(
                "salesforce_agent",
                "create_onboarding_record",
                "skipped",
                mode=mode,
            )
            return SalesforceResult(record_id="DRY-RUN", url="", status="skipped")

        existing = await find_external_record(
            "salesforce",
            "create_onboarding_record",
            ledger_key,
        )
        if existing:
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="salesforce_agent",
                tool="create_onboarding_record",
                input_payload=payload,
                output_payload={
                    "record_id": existing["external_id"],
                    "url": existing["external_url"],
                    "mode": existing["mode"],
                    "idempotency_key": ledger_key,
                    "idempotent_replay": True,
                },
                duration_ms=0,
                status="success",
            )
            metrics.record_agent_call(
                "salesforce_agent",
                "create_onboarding_record",
                "success",
                mode=existing["mode"],
            )
            return SalesforceResult(
                record_id=existing["external_id"],
                url=existing["external_url"],
                status="existing",
            )

        start = time.monotonic()
        response = await self.mcp.execute(
            "create_onboarding_record",
            payload,
            api_key=settings.mcp_api_key,
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        status = "success" if response.success else "error"
        output_payload = dict(response.result or {"error": response.error})
        if response.success:
            output_payload["mode"] = mode
            output_payload["idempotency_key"] = ledger_key

        await audit_logger.log_action(
            workflow_id=workflow_id,
            agent="salesforce_agent",
            tool="create_onboarding_record",
            input_payload=payload,
            output_payload=output_payload,
            duration_ms=duration_ms,
            status=status,
        )
        metrics.record_agent_call(
            "salesforce_agent",
            "create_onboarding_record",
            status,
            mode=mode,
        )

        if not response.success:
            raise RuntimeError(f"Salesforce Agent failed: {response.error}")

        await record_external_record(
            workflow_id=workflow_id,
            system="salesforce",
            action="create_onboarding_record",
            key=ledger_key,
            external_id=response.result["record_id"],
            external_url=response.result["url"],
            mode=mode,
        )

        return SalesforceResult(
            record_id=response.result["record_id"],
            url=response.result["url"],
            status="created",
        )
