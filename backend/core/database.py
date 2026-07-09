"""Database configuration and connection"""

from typing import AsyncGenerator
import logging
import asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

from .config import settings, DEFAULT_SQLITE_PATH

logger = logging.getLogger(__name__)


def _resolve_async_database_url(database_url: str) -> str:
    """Normalize database URL to an async-capable driver."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


DATABASE_URL = _resolve_async_database_url(settings.database_url)

# SQLAlchemy
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.debug,
        future=True,
    )
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
except InvalidRequestError:
    fallback_url = f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH}"
    logger.warning("Falling back to SQLite because configured DB URL is not async-compatible")
    engine = create_async_engine(
        fallback_url,
        echo=settings.debug,
        future=True,
    )
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

Base = declarative_base()

# MongoDB
mongo_client: AsyncIOMotorClient = None
mongo_db = None

# Redis
redis_client = None
_schema_initialized = False
_schema_lock = asyncio.Lock()


async def ensure_schema_initialized() -> None:
    """Create tables once per process before DB usage."""
    global _schema_initialized

    if _schema_initialized:
        return

    async with _schema_lock:
        if _schema_initialized:
            return

        from . import models  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        _schema_initialized = True


async def init_db():
    """Initialize database connections"""
    global mongo_client, mongo_db, redis_client

    await ensure_schema_initialized()

    # MongoDB
    mongo_client = AsyncIOMotorClient(settings.mongo_url)
    mongo_db = mongo_client["my_agent"]

    # Redis
    redis_client = await redis.from_url(
        settings.redis_url,
        encoding="utf8",
        decode_responses=True,
    )


async def close_db():
    """Close database connections"""
    global mongo_client, redis_client

    if mongo_client:
        mongo_client.close()

    if redis_client:
        await redis_client.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    await ensure_schema_initialized()

    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
