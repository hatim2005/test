"""Alembic Environment Configuration.

This module configures the Alembic migration environment for the Color Correction System.
It handles database connection, logging, and migration execution for both online and offline modes.

The configuration supports:
- SQLite (development)
- PostgreSQL (production)
- Both online and offline migration modes
- Automatic model metadata detection
"""

from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all models to ensure they are registered with Base.metadata
from models.database import Base
from models.user import User
from models.image import Image, ImageMetadata
from models.job import Job, JobStatus

# This is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# Get database URL from environment variable or use default
# Priority: DATABASE_URL > SQLALCHEMY_DATABASE_URL > default SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "SQLALCHEMY_DATABASE_URL",
        "sqlite:///./color_correction.db"
    )
)

# Set the sqlalchemy.url in the alembic config
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    # Get configuration from alembic.ini
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL

    # Create engine with appropriate settings
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't use connection pooling for migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detect column type changes
            compare_server_default=True,  # Detect default value changes
            render_as_batch=True,  # Enable batch mode for SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run migrations in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
