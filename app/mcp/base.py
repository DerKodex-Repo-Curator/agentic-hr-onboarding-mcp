"""Base MCP abstractions for authenticated tool execution.

Author: Sarala Biswal
"""

from abc import ABC, abstractmethod
from typing import Any


class MCPResponse:
    """Response envelope returned by all MCP server stubs."""

    def __init__(
        self,
        tool: str,
        version: str,
        result: dict[str, Any],
        error: str | None = None,
    ) -> None:
        self.tool = tool
        self.version = version
        self.result = result
        self.error = error
        self.success = error is None


class BaseMCPServer(ABC):
    """Base class for MCP-like tools with auth, versioning, and error wrapping."""

    def __init__(self, api_key: str, version: str = "v1") -> None:
        self.api_key = api_key
        self.version = version

    def _authenticate(self, provided_key: str) -> None:
        if provided_key != self.api_key:
            raise PermissionError("Invalid MCP API key")

    @abstractmethod
    def tool_schema(self) -> dict[str, Any]:
        """Return JSON Schema describing available tools."""

    @abstractmethod
    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute the named tool with params."""

    async def execute(
        self,
        tool_name: str,
        params: dict[str, Any],
        api_key: str,
    ) -> MCPResponse:
        """Execute a tool and return an MCPResponse instead of raising expected errors."""
        try:
            self._authenticate(api_key)
            result = await self._execute_tool(tool_name, params)
            return MCPResponse(tool=tool_name, version=self.version, result=result)
        except Exception as exc:
            return MCPResponse(tool=tool_name, version=self.version, result={}, error=str(exc))
