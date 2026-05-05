"""Runtime configuration for the onboarding agent service.

Author: Sarala Biswal
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ConnectorMode = Literal["auto", "mock", "dry_run", "real"]
ResolvedConnectorMode = Literal["mock", "dry_run", "real"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: Literal["ollama", "openai", "anthropic", "rules"] = "ollama"
    llm_max_tokens: int = 2048

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    openai_api_key: str = ""
    openai_model: str = "gpt-5.5"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    mcp_api_key: str = "dev-secret-key"
    mcp_version: str = "v1"

    app_mode: Literal["demo", "real"] = "demo"
    workday_mode: ConnectorMode = "auto"
    it_mode: ConnectorMode = "auto"
    slack_mode: ConnectorMode = "auto"
    salesforce_mode: ConnectorMode = "auto"

    workday_base_url: str = ""
    workday_tenant: str = ""
    workday_access_token: str = ""
    workday_workers_path: str = "/ccx/api/v1/{tenant}/workers"
    workday_field_map_json: str = ""

    jira_base_url: str = ""
    jira_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = "IT"
    jira_issue_type: str = "Task"
    jira_request_type_id: str = ""
    jira_onboarding_label: str = "onboarding"

    slack_bot_token: str = ""
    slack_mock_mode: bool = True
    slack_channel_map_json: str = ""

    salesforce_instance_url: str = ""
    salesforce_access_token: str = ""
    salesforce_api_version: str = "v60.0"
    salesforce_readiness_object: str = "New_Hire__c"
    salesforce_field_map_json: str = ""

    db_path: str = "audit.db"

    app_env: Literal["development", "production"] = "development"
    log_level: str = "INFO"

    def resolve_connector_mode(self, configured_mode: ConnectorMode) -> ResolvedConnectorMode:
        """Resolve connector mode from app mode plus optional per-connector override."""
        if configured_mode != "auto":
            return configured_mode
        return "real" if self.app_mode == "real" else "mock"

    @property
    def effective_workday_mode(self) -> ResolvedConnectorMode:
        return self.resolve_connector_mode(self.workday_mode)

    @property
    def effective_it_mode(self) -> ResolvedConnectorMode:
        return self.resolve_connector_mode(self.it_mode)

    @property
    def effective_slack_mode(self) -> ResolvedConnectorMode:
        return self.resolve_connector_mode(self.slack_mode)

    @property
    def effective_salesforce_mode(self) -> ResolvedConnectorMode:
        return self.resolve_connector_mode(self.salesforce_mode)


settings = Settings()
