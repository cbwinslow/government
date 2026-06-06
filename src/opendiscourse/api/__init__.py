"""OpenDiscourse FastAPI application serving the dashboard and agent endpoints."""

from opendiscourse.api.agents_endpoints import router as agents_router

__all__ = ["agents_router"]