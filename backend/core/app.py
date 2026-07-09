"""FastAPI application factory"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import init_db, close_db
from .logging_config import setup_logging

# Import routers
from .routers import analysis, projects, health, auth, workspaces

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    logger.info("Application started")
    yield
    # Shutdown
    await close_db()
    logger.info("Application stopped")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered Software Engineering Agent",
        debug=settings.debug,
        lifespan=lifespan,
    )

    cors_origins = _parse_csv(settings.cors_origins)
    allow_credentials = "*" not in cors_origins

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["http://localhost:5173"],
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    allowed_hosts = _parse_csv(settings.allowed_hosts)

    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts or ["localhost", "127.0.0.1", "testserver"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(analysis.router, prefix="/api/v1")
    app.include_router(projects.router, prefix="/api/v1")
    app.include_router(workspaces.router, prefix="/api/v1")

    return app

# Create the app instance
app = create_app()