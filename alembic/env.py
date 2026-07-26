"""Alembic environment configuration for async SQLAlchemy.

Reads the database URL from src.config.settings, registers all ORM models
on Base.metadata via importing src.db.models, and runs migrations online
using an async engine.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import settings and Base so Alembic can read the URL and metadata.
from src.config import settings
from src.db.database import Base

# Import all models so they are registered on Base.metadata before autogenerate.
from src.db.models import Conversation, Message, Document  # noqa: F401


# this is the Alembic Config object.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from settings (overrides alembic.ini).
# Normalise postgresql:// to postgresql+asyncpg:// for the async engine.
# asyncpg doesn't accept sslmode param, needs ssl=require instead.
_db_url = settings.database_url
if _db_url.startswith("postgresql://"):
    _db_url = "postgresql+asyncpg://" + _db_url[len("postgresql://"):]
    _db_url = _db_url.replace("sslmode=require", "ssl=require")
config.set_main_option("sqlalchemy.url", _db_url)

# Target metadata for autogenerate.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL to a script)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())