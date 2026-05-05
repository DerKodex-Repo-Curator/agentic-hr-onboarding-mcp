"""Slack MCP connector with mock and real Slack API support.

Author: Sarala Biswal
"""

import json
import time
from typing import Any

from app.config import settings
from app.mcp.base import BaseMCPServer


class SlackMCPServer(BaseMCPServer):
    """Slack MCP server with mock mode and optional real Slack API support."""

    def tool_schema(self) -> dict[str, Any]:
        return {
            "name": "slack_mcp",
            "version": self.version,
            "tools": {
                "send_message": {
                    "description": "Send a Slack DM or channel message",
                    "parameters": {
                        "type": "object",
                        "required": ["channel", "text"],
                        "properties": {
                            "channel": {
                                "type": "string",
                                "description": "Slack handle or channel ID",
                            },
                            "text": {"type": "string"},
                            "blocks": {
                                "type": "array",
                                "description": "Optional Slack block kit JSON",
                            },
                        },
                    },
                }
            },
        }

    async def _execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        if tool_name != "send_message":
            raise ValueError(f"Unknown tool: {tool_name}")

        if settings.effective_slack_mode == "real" and not settings.slack_bot_token:
            raise RuntimeError("SLACK_BOT_TOKEN is required when SLACK_MODE=real")

        if settings.effective_slack_mode != "real":
            return {
                "message_ts": f"{int(time.time())}.000",
                "channel": params["channel"],
                "status": "sent",
                "mode": "mock",
            }

        from slack_sdk.web.async_client import AsyncWebClient

        client = AsyncWebClient(token=settings.slack_bot_token)
        channel = await self._resolve_real_channel(client, str(params["channel"]))
        response = await client.chat_postMessage(
            channel=channel,
            text=params["text"],
            blocks=params.get("blocks"),
        )
        return {
            "message_ts": response["ts"],
            "channel": response["channel"],
            "status": "sent",
            "mode": "real",
        }

    async def _resolve_real_channel(self, client: Any, channel: str) -> str:
        """Resolve pilot-friendly handles/emails to Slack IDs before sending."""
        configured = self._channel_map()
        lookup_keys = [channel, channel.lstrip("@"), f"@{channel.lstrip('@')}"]
        for key in lookup_keys:
            if key in configured:
                return str(configured[key])

        if channel.startswith(("C", "D", "G", "U")):
            return channel

        if "@" in channel and "." in channel:
            response = await client.users_lookupByEmail(email=channel)
            user = response.get("user", {})
            if user.get("id"):
                return str(user["id"])

        handle = channel.lstrip("@").lower()
        cursor = None
        while True:
            response = await client.users_list(limit=200, cursor=cursor)
            for user in response.get("members", []):
                profile = user.get("profile", {})
                candidates = {
                    str(user.get("name", "")).lower(),
                    str(profile.get("display_name", "")).lower(),
                    str(profile.get("real_name", "")).lower().replace(" ", "."),
                }
                if handle in candidates and user.get("id"):
                    return str(user["id"])
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return channel

    @staticmethod
    def _channel_map() -> dict[str, str]:
        if not settings.slack_channel_map_json.strip():
            return {}
        parsed = json.loads(settings.slack_channel_map_json)
        if not isinstance(parsed, dict):
            raise ValueError("SLACK_CHANNEL_MAP_JSON must be a JSON object")
        return {str(key): str(value) for key, value in parsed.items()}
