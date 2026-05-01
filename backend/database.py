"""
Database configuration and session management for Verity.
Uses async SQLAlchemy with asyncpg driver for PostgreSQL.
"""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Load environment variables from root .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Convert postgresql:// to postgresql+asyncpg:// for async driver
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Also keep a sync URL for Alembic migrations
SYNC_DATABASE_URL = DATABASE_URL

# Create async engine with SSL support for Neon
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    connect_args={"ssl": True} if "sslmode=require" in DATABASE_URL else {},
)

# Remove sslmode from the URL since asyncpg handles it via connect_args
if "?sslmode=require" in ASYNC_DATABASE_URL:
    engine = create_async_engine(
        ASYNC_DATABASE_URL.replace("?sslmode=require", ""),
        echo=False,
        pool_size=5,
        max_overflow=10,
        connect_args={"ssl": True},
    )

# Async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db():
    """FastAPI dependency that provides an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables in the database (used for initial setup)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
