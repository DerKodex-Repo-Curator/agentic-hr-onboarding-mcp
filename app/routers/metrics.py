"""Metrics API route for Prometheus-compatible observability.

Author: Sarala Biswal
"""

from fastapi import APIRouter
from fastapi.responses import Response

from app.governance.metrics import get_metrics_output

router = APIRouter()


@router.get("/metrics")
async def metrics() -> Response:
    """Return Prometheus-compatible metrics."""
    data, content_type = get_metrics_output()
    return Response(content=data, media_type=content_type)
