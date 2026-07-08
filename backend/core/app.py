"""FastAPI application factory"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db, close_db
from .logging_config import setup_logging

# Import routers
from .routers import health, auth, users, projects, analyses, sessions, fixes

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
        title="My Agent API",
        version="1.0.0-alpha",
        description="AI-powered Software Engineering Agent",
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
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
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(projects.router, prefix="/api/v1")
    app.include_router(analyses.router, prefix="/api/v1")
    app.include_router(sessions.router, prefix="/api/v1")
    app.include_router(fixes.router, prefix="/api/v1")

    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="My Agent API",
            version="1.0.0-alpha",
            description="AI-powered Software Engineering Agent with advanced analysis and auto-fix",
            routes=app.routes,
        )
        
        openapi_schema["info"]["contact"] = {
            "name": "Savaş Aldemir",
            "url": "https://github.com/savasaldemir",
        }
        
        openapi_schema["info"]["license"] = {
            "name": "MIT",
        }
        
        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8000",
                "description": "Development"
            },
            {
                "url": "https://api.myagent.dev",
                "description": "Production"
            }
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app

# Create the app instance
app = create_app()
