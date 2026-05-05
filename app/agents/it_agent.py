"""IT agent that creates or reuses Jira provisioning tickets.

Author: Sarala Biswal
"""

import time

from app.config import settings
from app.governance import audit_logger, metrics
from app.integrations.idempotency import idempotency_key
from app.integrations.ledger import find_external_record, record_external_record
from app.integrations.modes import effective_mode
from app.mcp.jira_mcp import JiraMCPServer
from app.models import EmployeeData, JiraResult


class ITAgent:
    """Coordinate IT provisioning requests through the Jira MCP boundary."""

    def __init__(self) -> None:
        self.mcp = JiraMCPServer(api_key=settings.mcp_api_key, version=settings.mcp_version)

    async def run(
        self,
        workflow_id: str,
        employee: EmployeeData,
        dry_run: bool = False,
    ) -> JiraResult:
        """Create or validate an IT onboarding ticket."""
        summary = f"Onboarding: {employee.full_name} - {employee.role} ({employee.start_date})"
        payload = {
            "summary": summary,
            "employee_name": employee.full_name,
            "start_date": employee.start_date,
            "required_systems": employee.required_systems,
            "priority": "Medium",
        }
        mode = effective_mode(settings.effective_it_mode, dry_run)
        ledger_key = idempotency_key("jira", "create_ticket", employee)

        if mode == "dry_run":
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="it_agent",
                tool="create_ticket",
                input_payload=payload,
                output_payload={"mode": mode, "idempotency_key": ledger_key},
                duration_ms=0,
                status="skipped",
            )
            metrics.record_agent_call("it_agent", "create_ticket", "skipped", mode=mode)
            return JiraResult(ticket_id="DRY-RUN", url="", status="skipped")

        existing = await find_external_record("jira", "create_ticket", ledger_key)
        if existing:
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="it_agent",
                tool="create_ticket",
                input_payload=payload,
                output_payload={
                    "ticket_id": existing["external_id"],
                    "url": existing["external_url"],
                    "mode": existing["mode"],
                    "idempotency_key": ledger_key,
                    "idempotent_replay": True,
                },
                duration_ms=0,
                status="success",
            )
            metrics.record_agent_call("it_agent", "create_ticket", "success", mode=existing["mode"])
            return JiraResult(
                ticket_id=existing["external_id"],
                url=existing["external_url"],
                status="existing",
            )

        start = time.monotonic()
        response = await self.mcp.execute("create_ticket", payload, api_key=settings.mcp_api_key)
        duration_ms = int((time.monotonic() - start) * 1000)
        status = "success" if response.success else "error"
        output_payload = dict(response.result or {"error": response.error})
        if response.success:
            output_payload["mode"] = mode
            output_payload["idempotency_key"] = ledger_key

        await audit_logger.log_action(
            workflow_id=workflow_id,
            agent="it_agent",
            tool="create_ticket",
            input_payload=payload,
            output_payload=output_payload,
            duration_ms=duration_ms,
            status=status,
        )
        metrics.record_agent_call("it_agent", "create_ticket", status, mode=mode)

        if not response.success:
            raise RuntimeError(f"IT Agent failed: {response.error}")

        await record_external_record(
            workflow_id=workflow_id,
            system="jira",
            action="create_ticket",
            key=ledger_key,
            external_id=response.result["ticket_id"],
            external_url=response.result["url"],
            mode=mode,
        )

        return JiraResult(
            ticket_id=response.result["ticket_id"],
            url=response.result["url"],
            status="created",
        )
