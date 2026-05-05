"""Idempotency helpers that prevent duplicate external system records.

Author: Sarala Biswal
"""

import re

from app.models import EmployeeData


def normalize_key_part(value: str) -> str:
    """Normalize human-entered values into stable idempotency key parts."""
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "unknown"


def idempotency_key(system: str, action: str, employee: EmployeeData) -> str:
    """Build a deterministic key for one external system action."""
    return ":".join(
        [
            normalize_key_part(system),
            normalize_key_part(action),
            normalize_key_part(employee.full_name),
            normalize_key_part(employee.start_date),
        ]
    )
