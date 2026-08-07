"""SQLAlchemy 2.0 async engine, session, and Base class."""
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# Engine and sessionmaker are created lazily so that importing this module
# does not require a configured DATABASE_URL (useful for Alembic, tests, and
# tooling that only needs the metadata/models).
_engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def _ensure_engine() -> AsyncEngine:
    """Create the async engine and sessionmaker on first use."""
    global _engine, AsyncSessionLocal
    if _engine is None:
        # Normalise postgresql:// to postgresql+asyncpg:// for asyncpg driver
        # asyncpg doesn't accept sslmode param, needs ssl=require instead
        db_url = settings.database_url
        if db_url.startswith("postgresql://"):
            db_url = "postgresql+asyncpg://" + db_url[len("postgresql://"):]
            db_url = db_url.replace("sslmode=require", "ssl=require")
        _engine = create_async_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine
