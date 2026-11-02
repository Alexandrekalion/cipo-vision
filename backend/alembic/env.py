from alembic import context
from sqlalchemy import create_engine, pool
from app.db import Base
from app import models
from app.migration_config import get_migration_database_url

config = context.config
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=get_migration_database_url(), target_metadata=target_metadata, literal_binds=True, dialect_opts={'paramstyle':'named'})
    with context.begin_transaction(): context.run_migrations()

def run_migrations_online():
    connectable = create_engine(get_migration_database_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()

if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
