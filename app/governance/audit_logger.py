"""SQLite-backed audit logging for every agent and connector action.

Author: Sarala Biswal
"""

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import aiosqlite

from app.config import settings

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    tool TEXT NOT NULL,
    input_payload TEXT NOT NULL,
    output_payload TEXT NOT NULL,
    duration_ms INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _mask_sensitive(payload: dict[str, Any]) -> dict[str, Any]:
    """Mask known sensitive fields before logging."""
    sensitive_keys = {"ssn", "salary", "password", "token", "secret"}
    masked: dict[str, Any] = {}
    for key, value in payload.items():
        if key.lower() in sensitive_keys:
            masked[key] = "***"
        elif isinstance(value, dict):
            masked[key] = _mask_sensitive(value)
        else:
            masked[key] = value
    return masked


async def init_db() -> None:
    """Create the audit_log table if it does not exist."""
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def log_action(
    workflow_id: str,
    agent: str,
    tool: str,
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    duration_ms: int,
    status: str,
) -> str:
    """Persist one agent action to the audit log and return its ID."""
    await init_db()
    entry_id = str(uuid.uuid4())
    now = datetime.now(UTC).isoformat()

    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            INSERT INTO audit_log
                (id, workflow_id, agent, tool, input_payload, output_payload,
                 duration_ms, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                workflow_id,
                agent,
                tool,
                json.dumps(_mask_sensitive(input_payload)),
                json.dumps(_mask_sensitive(output_payload)),
                duration_ms,
                status,
                now,
            ),
        )
        await db.commit()
    return entry_id


async def query_audit_log(
    workflow_id: str | None = None,
    agent: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Query audit entries with optional filters."""
    await init_db()
    conditions: list[str] = []
    args: list[Any] = []

    if workflow_id:
        conditions.append("workflow_id = ?")
        args.append(workflow_id)
    if agent:
        conditions.append("agent = ?")
        args.append(agent)
    if status:
        conditions.append("status = ?")
        args.append(status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM audit_log {where} ORDER BY created_at DESC LIMIT ?"
    args.append(limit)

    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(sql, args)
        rows = await cursor.fetchall()

    entries = []
    for row in rows:
        entry = dict(row)
        entry["input_payload"] = json.loads(entry["input_payload"])
        entry["output_payload"] = json.loads(entry["output_payload"])
        entries.append(entry)
    return entries
