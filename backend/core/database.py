"""Database configuration and connection"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

from .config import settings

# SQLAlchemy
engine = create_async_engine(
    settings.database_url,
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


async def init_db():
    """Initialize database connections"""
    global mongo_client, mongo_db, redis_client

    # PostgreSQL (Tables created via Alembic)
    # await engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

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
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
