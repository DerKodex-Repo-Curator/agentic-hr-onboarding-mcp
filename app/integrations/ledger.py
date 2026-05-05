"""External record ledger used to prove what each workflow created.

Author: Sarala Biswal
"""

from datetime import UTC, datetime
from typing import Any

import aiosqlite

from app.config import settings

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS external_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    system TEXT NOT NULL,
    action TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    external_id TEXT NOT NULL,
    external_url TEXT NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(system, action, idempotency_key)
);
"""


async def init_ledger() -> None:
    """Create the external record ledger if it does not exist."""
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def find_external_record(
    system: str,
    action: str,
    key: str,
) -> dict[str, Any] | None:
    """Return an existing external record for an idempotent system action."""
    await init_ledger()
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT *
            FROM external_records
            WHERE system = ? AND action = ? AND idempotency_key = ?
            """,
            (system, action, key),
        )
        row = await cursor.fetchone()
    return dict(row) if row else None


async def record_external_record(
    *,
    workflow_id: str,
    system: str,
    action: str,
    key: str,
    external_id: str,
    external_url: str,
    mode: str,
    status: str = "created",
) -> dict[str, Any]:
    """Persist an external record reference and return the stored row."""
    await init_ledger()
    now = datetime.now(UTC).isoformat()
    # The unique key keeps retry and reload paths from creating duplicate
    # business artifacts for the same employee/system/action combination.
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO external_records
                (workflow_id, system, action, idempotency_key, external_id,
                 external_url, mode, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                system,
                action,
                key,
                external_id,
                external_url,
                mode,
                status,
                now,
            ),
        )
        await db.commit()
    record = await find_external_record(system, action, key)
    if record is None:
        raise RuntimeError("External record ledger write failed")
    return record


async def latest_external_records() -> dict[str, dict[str, Any]]:
    """Return the most recent external record per system for runtime visibility."""
    await init_ledger()
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT er.*
            FROM external_records er
            JOIN (
                SELECT system, MAX(created_at) AS latest_created_at
                FROM external_records
                GROUP BY system
            ) latest
              ON latest.system = er.system
             AND latest.latest_created_at = er.created_at
            ORDER BY er.system
            """
        )
        rows = await cursor.fetchall()
    return {str(row["system"]): dict(row) for row in rows}


async def records_for_workflow(workflow_id: str) -> list[dict[str, Any]]:
    """Return all external record ledger rows for one workflow."""
    await init_ledger()
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT *
            FROM external_records
            WHERE workflow_id = ?
            ORDER BY created_at, system
            """,
            (workflow_id,),
        )
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]
