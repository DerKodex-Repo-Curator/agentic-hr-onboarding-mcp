"""Notification agent that creates or reuses manager Slack updates.

Author: Sarala Biswal
"""

import time

from app.config import settings
from app.governance import audit_logger, metrics
from app.integrations.idempotency import idempotency_key
from app.integrations.ledger import find_external_record, record_external_record
from app.integrations.modes import effective_mode
from app.mcp.slack_mcp import SlackMCPServer
from app.models import EmployeeData, SlackResult


class NotificationAgent:
    """Coordinate manager notifications through the Slack MCP boundary."""

    def __init__(self) -> None:
        self.mcp = SlackMCPServer(api_key=settings.mcp_api_key, version=settings.mcp_version)

    async def run(
        self,
        workflow_id: str,
        employee: EmployeeData,
        dry_run: bool = False,
    ) -> SlackResult:
        """Send or validate a Slack notification to the hiring manager."""
        channel = employee.manager_slack_handle.lstrip("@")
        text = (
            f"Hi! Your new hire *{employee.full_name}* ({employee.role}) has been onboarded. "
            f"Start date: {employee.start_date}. Workday record created and IT provisioning "
            f"ticket raised. Required systems: {', '.join(employee.required_systems)}."
        )
        payload = {"channel": channel, "text": text}
        mode = effective_mode(settings.effective_slack_mode, dry_run)
        ledger_key = idempotency_key("slack", "send_message", employee)

        if mode == "dry_run":
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="notification_agent",
                tool="send_message",
                input_payload=payload,
                output_payload={"mode": mode, "idempotency_key": ledger_key},
                duration_ms=0,
                status="skipped",
            )
            metrics.record_agent_call("notification_agent", "send_message", "skipped", mode=mode)
            return SlackResult(message_ts="0", channel=channel, status="skipped")

        existing = await find_external_record("slack", "send_message", ledger_key)
        if existing:
            await audit_logger.log_action(
                workflow_id=workflow_id,
                agent="notification_agent",
                tool="send_message",
                input_payload=payload,
                output_payload={
                    "message_ts": existing["external_id"],
                    "channel": channel,
                    "mode": existing["mode"],
                    "idempotency_key": ledger_key,
                    "idempotent_replay": True,
                },
                duration_ms=0,
                status="success",
            )
            metrics.record_agent_call(
                "notification_agent",
                "send_message",
                "success",
                mode=existing["mode"],
            )
            return SlackResult(
                message_ts=existing["external_id"],
                channel=channel,
                status="existing",
            )

        start = time.monotonic()
        response = await self.mcp.execute("send_message", payload, api_key=settings.mcp_api_key)
        duration_ms = int((time.monotonic() - start) * 1000)
        status = "success" if response.success else "error"
        output_payload = dict(response.result or {"error": response.error})
        if response.success:
            output_payload["mode"] = mode
            output_payload["idempotency_key"] = ledger_key

        await audit_logger.log_action(
            workflow_id=workflow_id,
            agent="notification_agent",
            tool="send_message",
            input_payload=payload,
            output_payload=output_payload,
            duration_ms=duration_ms,
            status=status,
        )
        metrics.record_agent_call("notification_agent", "send_message", status, mode=mode)

        if not response.success:
            raise RuntimeError(f"Notification Agent failed: {response.error}")

        message_ts = response.result["message_ts"]
        await record_external_record(
            workflow_id=workflow_id,
            system="slack",
            action="send_message",
            key=ledger_key,
            external_id=message_ts,
            external_url=(
                f"slack://channel/{response.result['channel']}/"
                f"p{message_ts.replace('.', '')}"
            ),
            mode=mode,
        )

        return SlackResult(
            message_ts=message_ts,
            channel=response.result["channel"],
            status="sent",
        )
