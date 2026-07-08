"""FastAPI application factory"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db, close_db
from .logging_config import setup_logging

# Import routers
from .routers import analysis, projects, health, auth

setup_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    print("✅ Application started")
    yield
    # Shutdown
    await close_db()
    print("👋 Application stopped")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered Software Engineering Agent",
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.myagent.dev"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(analysis.router, prefix="/api/v1")
    app.include_router(projects.router, prefix="/api/v1")

    return app

# Create the app instance
app = create_app()
