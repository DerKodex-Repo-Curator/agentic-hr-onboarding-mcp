"""Connector mode resolution for demo, dry-run, and real execution.

Author: Sarala Biswal
"""

from typing import Literal

ConnectorMode = Literal["mock", "dry_run", "real"]


def effective_mode(configured_mode: ConnectorMode, request_dry_run: bool) -> ConnectorMode:
    """Resolve request and connector settings into the mode used for a call."""
    if request_dry_run:
        return "dry_run"
    return configured_mode
