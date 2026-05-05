"""Workflow orchestrator for structured extraction and multi-agent execution.

Author: Sarala Biswal
"""

import asyncio
import re
import time
import uuid
from datetime import date, datetime
from typing import Literal, cast

import httpx
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.hr_agent import HRAgent
from app.agents.it_agent import ITAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.salesforce_agent import SalesforceAgent
from app.config import settings
from app.governance import metrics
from app.models import (
    EmployeeData,
    JiraResult,
    OnboardRequest,
    OnboardResponse,
    SalesforceResult,
    SlackResult,
    WorkdayResult,
    WorkflowResults,
)


class OrchestratorAgent:
    """Top-level orchestrator for employee onboarding workflows."""

    employee_parser = JsonOutputParser()
    employee_prompt = PromptTemplate.from_template(
        "Extract employee onboarding data from this instruction as JSON only. "
        "Today's date is {today}. "
        "Use this exact JSON shape: "
        '{{"full_name":"string","role":"string","department":"string",'
        '"start_date":"YYYY-MM-DD","manager_slack_handle":"string",'
        '"required_systems":["laptop","github","gsuite","slack","salesforce"]}}. '
        "Use sensible defaults for missing fields and convert dates to ISO format. "
        "Instruction: {instruction}"
    )

    def __init__(self) -> None:
        self.hr_agent = HRAgent()
        self.it_agent = ITAgent()
        self.notification_agent = NotificationAgent()
        self.salesforce_agent = SalesforceAgent()

    async def extract_employee_data(self, instruction: str) -> EmployeeData:
        """Parse onboarding instruction into structured employee data."""
        provider = settings.llm_provider.lower()
        if provider == "rules":
            return self._extract_with_rules(instruction)

        try:
            if provider == "ollama":
                extracted = await self._extract_with_ollama(instruction)
            elif provider == "openai":
                extracted = await self._extract_with_openai(instruction)
            elif provider == "anthropic":
                extracted = await self._extract_with_anthropic(instruction)
            else:
                extracted = {}
            return EmployeeData.model_validate(extracted)
        except Exception:
            return self._extract_with_rules(instruction)

    async def _extract_with_ollama(self, instruction: str) -> dict:
        """Extract employee data using a local Ollama model."""
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": self._llm_prompt(instruction),
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0},
                },
            )
            response.raise_for_status()
        return self._parse_llm_json(response.json()["response"])

    async def _extract_with_openai(self, instruction: str) -> dict:
        """Extract employee data using OpenAI's Responses API."""
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "input": self._llm_prompt(instruction),
                    "max_output_tokens": settings.llm_max_tokens,
                    "text": {
                        "format": {
                            "type": "json_schema",
                            "name": "employee_data",
                            "strict": True,
                            "schema": self._employee_schema(),
                        }
                    },
                },
            )
            response.raise_for_status()
        return self._parse_llm_json(self._extract_response_text(response.json()))

    async def _extract_with_anthropic(self, instruction: str) -> dict:
        """Extract employee data using Anthropic's Messages API."""
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": settings.llm_max_tokens,
                    "system": "Return only valid JSON matching the requested schema.",
                    "messages": [{"role": "user", "content": self._llm_prompt(instruction)}],
                },
            )
            response.raise_for_status()
        content = response.json()["content"][0]["text"]
        return self._parse_llm_json(content)

    @staticmethod
    def _extract_response_text(payload: dict) -> str:
        if "output_text" in payload:
            return str(payload["output_text"])
        for item in payload.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return str(content.get("text", ""))
        return "{}"

    @staticmethod
    def _employee_schema() -> dict:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "full_name": {"type": "string"},
                "role": {"type": "string"},
                "department": {"type": "string"},
                "start_date": {"type": "string"},
                "manager_slack_handle": {"type": "string"},
                "required_systems": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "full_name",
                "role",
                "department",
                "start_date",
                "manager_slack_handle",
                "required_systems",
            ],
        }

    def _llm_prompt(self, instruction: str) -> str:
        return self.employee_prompt.format(
            today=date.today().isoformat(),
            instruction=instruction,
        )

    def _parse_llm_json(self, text: str) -> dict:
        return cast(dict, self.employee_parser.parse(text))

    def _extract_with_rules(self, instruction: str) -> EmployeeData:
        """Offline parser for demos and tests when no LLM key is configured."""
        text = instruction.strip()
        full_name = self._match(
            r"onboard\s+([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+)+?)\s+as\s+",
            text,
            "Jane Smith",
            flags=re.IGNORECASE,
        )
        role = self._match(
            r"\s+as\s+(?:an|a)?\s*(.+?)\s+on\s+(?:the\s+)?",
            text,
            "Employee",
        )
        department = self._match(
            r"\s+on\s+(?:the\s+)?(.+?)\s+team",
            text,
            "General",
        )
        start_date = self._parse_start_date(
            self._match(
                r"starting\s+([A-Za-z]+\s+\d{1,2}(?:,?\s+\d{4})?|\d{4}-\d{2}-\d{2})",
                text,
                date.today().isoformat(),
            )
        )
        manager = self._match(
            r"(?:manager\s+is|manager:)\s+(@?[A-Za-z0-9._-]+)",
            text,
            "manager",
            flags=re.IGNORECASE,
        )
        return EmployeeData(
            full_name=full_name,
            role=role.strip(),
            department=department.strip(),
            start_date=start_date,
            manager_slack_handle=manager,
            required_systems=self._extract_required_systems(text),
        )

    @staticmethod
    def _match(pattern: str, text: str, default: str, flags: int = 0) -> str:
        match = re.search(pattern, text, flags)
        return match.group(1).strip(" .") if match else default

    @staticmethod
    def _parse_start_date(raw_date: str) -> str:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
            return raw_date

        normalized = raw_date.replace(",", "")
        current_year = date.today().year
        formats = ["%B %d %Y", "%b %d %Y", "%B %d", "%b %d"]
        for fmt in formats:
            try:
                parsed = datetime.strptime(normalized, fmt)
                if "%Y" not in fmt:
                    parsed = parsed.replace(year=current_year)
                return parsed.date().isoformat()
            except ValueError:
                continue
        return date.today().isoformat()

    @staticmethod
    def _extract_required_systems(instruction: str) -> list[str]:
        system_aliases = {
            "laptop": ["laptop", "hardware", "computer"],
            "github": ["github", "git hub", "repository"],
            "gsuite": ["gsuite", "google workspace", "gmail", "google"],
            "slack": ["slack"],
            "salesforce": ["salesforce", "crm"],
        }
        lower_instruction = instruction.lower()
        matched = [
            system
            for system, aliases in system_aliases.items()
            if any(alias in lower_instruction for alias in aliases)
        ]
        return matched or ["laptop", "github", "gsuite", "slack"]

    async def run(self, request: OnboardRequest) -> OnboardResponse:
        """Run the full onboarding workflow and aggregate results."""
        workflow_id = str(uuid.uuid4())
        start = time.monotonic()

        try:
            employee = await self.extract_employee_data(request.instruction)
        except Exception as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            metrics.record_workflow(status="failed", duration_ms=duration_ms)
            return OnboardResponse(
                workflow_id=workflow_id,
                status="failed",
                results=WorkflowResults(errors=[f"Extraction failed: {exc}"]),
                duration_ms=duration_ms,
                audit_log_id=workflow_id,
                dry_run=request.dry_run,
            )

        # Run each system action independently so one blocked connector can return
        # a partial workflow instead of hiding successful downstream evidence.
        outcomes = await asyncio.gather(
            self.hr_agent.run(workflow_id, employee, dry_run=request.dry_run),
            self.it_agent.run(workflow_id, employee, dry_run=request.dry_run),
            self.notification_agent.run(workflow_id, employee, dry_run=request.dry_run),
            self.salesforce_agent.run(workflow_id, employee, dry_run=request.dry_run),
            return_exceptions=True,
        )

        workday_result: WorkdayResult | None = None
        jira_result: JiraResult | None = None
        slack_result: SlackResult | None = None
        salesforce_result: SalesforceResult | None = None
        errors: list[str] = []

        for index, outcome in enumerate(outcomes):
            if isinstance(outcome, Exception):
                errors.append(str(outcome))
            elif index == 0:
                workday_result = cast(WorkdayResult, outcome)
            elif index == 1:
                jira_result = cast(JiraResult, outcome)
            elif index == 2:
                slack_result = cast(SlackResult, outcome)
            else:
                salesforce_result = cast(SalesforceResult, outcome)

        has_success = any([workday_result, jira_result, slack_result, salesforce_result])
        status: Literal["completed", "partial", "failed"] = (
            "completed" if not errors else ("partial" if has_success else "failed")
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        metrics.record_workflow(status=status, duration_ms=duration_ms)

        return OnboardResponse(
            workflow_id=workflow_id,
            status=status,
            results=WorkflowResults(
                workday=workday_result,
                jira=jira_result,
                slack=slack_result,
                salesforce=salesforce_result,
                errors=errors,
            ),
            duration_ms=duration_ms,
            audit_log_id=workflow_id,
            dry_run=request.dry_run,
        )
