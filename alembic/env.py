import asyncio
import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from apps.models.auth import Base

load_dotenv()

config = context.config


def get_env_variable(var_name):
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Set the {var_name} environment variable")
    return value


config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+asyncpg://{get_env_variable('DB_USER')}:{get_env_variable('DB_PASS')}"
    f"@{get_env_variable('DB_HOST')}:{get_env_variable('DB_PORT')}/{get_env_variable('DB_NAME')}"
)

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

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
    """Run migrations."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
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
