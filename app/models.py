"""Typed API models shared by routers, agents, and MCP connectors.

Author: Sarala Biswal
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class OnboardRequest(BaseModel):
    """Request body for the onboarding workflow."""

    instruction: str = Field(
        ...,
        description="Natural language onboarding instruction",
        examples=[
            "Onboard Jane Smith as Senior Engineer on Platform team starting June 1. "
            "Manager is @john.doe"
        ],
    )
    dry_run: bool = Field(False, description="If true, validates but does not write to systems")


class WorkdayResult(BaseModel):
    employee_id: str
    status: Literal["created", "skipped", "existing"]


class JiraResult(BaseModel):
    ticket_id: str
    url: str
    status: Literal["created", "skipped", "existing"]


class SlackResult(BaseModel):
    message_ts: str
    channel: str
    status: Literal["sent", "skipped", "existing"]


class SalesforceResult(BaseModel):
    record_id: str
    url: str
    status: Literal["created", "skipped", "existing"]


class WorkflowResults(BaseModel):
    workday: WorkdayResult | None = None
    jira: JiraResult | None = None
    slack: SlackResult | None = None
    salesforce: SalesforceResult | None = None
    errors: list[str] = Field(default_factory=list)


class OnboardResponse(BaseModel):
    workflow_id: str
    status: Literal["completed", "partial", "failed"]
    results: WorkflowResults
    duration_ms: int
    audit_log_id: str
    dry_run: bool


class AuditEntry(BaseModel):
    id: str
    workflow_id: str
    agent: str
    tool: str
    input_payload: dict
    output_payload: dict
    duration_ms: int
    status: Literal["success", "error", "skipped"]
    created_at: datetime


class EmployeeData(BaseModel):
    full_name: str
    role: str
    department: str
    start_date: str
    manager_slack_handle: str
    required_systems: list[str] = Field(
        default_factory=lambda: ["laptop", "github", "gsuite", "slack", "salesforce"]
    )
