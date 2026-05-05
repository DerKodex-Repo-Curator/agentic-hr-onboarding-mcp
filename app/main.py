"""FastAPI application entry point for the onboarding command center.

Author: Sarala Biswal
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.governance.audit_logger import init_db
from app.integrations.ledger import init_ledger
from app.routers import audit, onboard, settings
from app.routers import metrics as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize durable stores required by workflow execution and evidence views."""
    await init_db()
    await init_ledger()
    yield


app = FastAPI(
    title="Enterprise AI Agent POC",
    description="Multi-agent employee onboarding powered by LLMs and MCP servers",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(onboard.router)
app.include_router(audit.router)
app.include_router(metrics_router.router)
app.include_router(settings.router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/", include_in_schema=False)
async def ui() -> FileResponse:
    """Serve the browser demo UI."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}
