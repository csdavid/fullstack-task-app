import os
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import your models
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from app.database import Base
from app.models import User, Task  # Import all models

# This is the Alembic Config object
config = context.config

# Set the database URL from environment
database_url = os.getenv("DATABASE_URL_SYNC")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode."""
    # For async migrations, we need to use the async database URL
    async_database_url = os.getenv("DATABASE_URL")
    if async_database_url:
        # Create a copy of the configuration section and update the URL
        configuration = dict(config.get_section(config.config_ini_section, {}))
        configuration["sqlalchemy.url"] = async_database_url
    else:
        configuration = config.get_section(config.config_ini_section, {})
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
