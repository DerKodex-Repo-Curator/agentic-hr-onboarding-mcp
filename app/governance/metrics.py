"""Prometheus-compatible metrics emitted by onboarding workflows.

Author: Sarala Biswal
"""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

workflows_total = Counter(
    "onboarding_workflows_total",
    "Total onboarding workflows triggered",
    ["status"],
)

agent_calls_total = Counter(
    "agent_calls_total",
    "Total agent MCP calls",
    ["agent", "tool", "status", "mode"],
)

workflow_duration_ms = Histogram(
    "onboarding_workflow_duration_ms",
    "End-to-end workflow duration in milliseconds",
    buckets=[500, 1000, 2000, 5000, 10000, 30000],
)


def record_workflow(status: str, duration_ms: int) -> None:
    """Record workflow-level metrics."""
    workflows_total.labels(status=status).inc()
    workflow_duration_ms.observe(duration_ms)


def record_agent_call(agent: str, tool: str, status: str, mode: str = "unknown") -> None:
    """Record one agent MCP call metric."""
    agent_calls_total.labels(agent=agent, tool=tool, status=status, mode=mode).inc()


def get_metrics_output() -> tuple[bytes, str]:
    """Return Prometheus-compatible metrics output and content type."""
    return generate_latest(), CONTENT_TYPE_LATEST
