"""
OpenDiscourse FastAPI Application
==================================
Main application entry point serving both the dashboard frontend
and the agent API endpoints.

Run with:
    uv run fastapi dev src/opendiscourse/api/main.py
    # or
    uvicorn opendiscourse.api.main:app --reload
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from opendiscourse.api.agents_endpoints import router as agents_router
from opendiscourse.core.config import settings

logger = logging.getLogger(__name__)

# ── Detect ZeroTier / SSH setup ──────────────────────────────────────────────

def _get_zerotier_ip() -> str:
    """Try to find the ZeroTier IP for client/server access."""
    try:
        import subprocess
        result = subprocess.run(
            ["ip", "addr", "show"],
            capture_output=True, text=True, timeout=3,
        )
        for line in result.stdout.split("\n"):
            if "inet 172." in line and "zt" in line.split(":")[0] if ":" in line[:10] else False:
                # More robust: find any 172.x.x.x on a zt interface
                for line2 in result.stdout.split("\n"):
                    if "inet 172." in line2 and "zt" in result.stdout.split(line2.split("inet ")[0])[0].strip():
                        pass
        # Simpler approach: grep for zt interface lines
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if "zt" in line and "mtu" in line:
                # The next line should have the inet address
                for j in range(i, min(i+3, len(lines))):
                    if "inet 172." in lines[j]:
                        return lines[j].split("inet ")[1].split("/")[0].strip()
    except Exception:
        pass
    return None


ZT_IP = _get_zerotier_ip()
if ZT_IP:
    logger.info(f"ZeroTier IP detected: {ZT_IP}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info(f"Starting OpenDiscourse API (v{settings.VERSION})...")
    logger.info(f"Server reaching at: http://{ZT_IP or settings.HOST}:{settings.PORT}")
    if ZT_IP:
        logger.info(f"  → From local machine: http://{ZT_IP}:{settings.PORT}")
        logger.info(f"  → Architecture viz:   http://{ZT_IP}:{settings.PORT}/viz")
    logger.info(f"  → API docs:            http://{ZT_IP or 'localhost'}:{settings.PORT}/docs")
    
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set. Agent LLM features will be unavailable.")
    else:
        logger.info("OpenRouter API key configured.")
    
    yield
    
    logger.info("Shutting down OpenDiscourse API...")


app = FastAPI(
    title="OpenDiscourse API",
    description="Political intelligence and honesty scoring engine API. "
                "Provides agent tools for multi-source research, consistency scoring, "
                "and LLM-powered analysis via OpenRouter.",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS - allow the dashboard frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(agents_router)


# ── Static endpoints ─────────────────────────────────────────────────────


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
        "zerotier_ip": ZT_IP,
        "host": settings.HOST,
        "port": settings.PORT,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "architecture_viz": "/viz",
            "agents": {
                "tools": "/api/agents/tools",
                "research": "/api/agents/research",
                "score": "/api/agents/score-consistency",
                "chat": "/api/agents/chat",
                "models": "/api/agents/discover-models",
                "alerts": "/api/agents/alerts",
            },
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": bool(settings.database_url),
    }


@app.get("/viz", response_class=HTMLResponse)
async def architecture_viz():
    """
    Interactive architecture visualization.
    
    Access from your local browser at:
        http://172.25.10.64:8000/viz
    Or via SSH tunnel:
        ssh -L 8000:localhost:8000 user@server
        then open http://localhost:8000/viz
    """
    html_path = Path(__file__).parent.parent.parent.parent / "scripts" / "agent_architecture.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(
        content="<h2>Visualization not generated yet</h2><p>Run: <code>uv run python scripts/visualize_agents.py</code></p>",
        status_code=200,
    )
