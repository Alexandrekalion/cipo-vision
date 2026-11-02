"""Deployment-only database configuration for Alembic.

The application may use SQLite for isolated development tests. Alembic must
never silently migrate that database during PostgreSQL deployment.
"""

import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL, make_url


EXPECTED_DRIVER = "postgresql+psycopg"
EXPECTED_HOST = "127.0.0.1"
EXPECTED_PORT = 5432
EXPECTED_DATABASE = "cipo_vision"
EXPECTED_USERNAME = "cipo_vision_app"


def get_migration_database_url() -> URL:
    # Alembic runs outside the Pydantic settings object; load the same local
    # .env file used by the application, without logging its contents.
    load_dotenv()
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL migrations")

    url = make_url(raw_url)
    if url.drivername != EXPECTED_DRIVER:
        raise RuntimeError("DATABASE_URL must use the approved PostgreSQL psycopg driver")
    test_mode = os.getenv("CIPO_MIGRATION_TEST") == "1"
    port = 55432 if test_mode else EXPECTED_PORT
    database = "cipo_test" if test_mode else EXPECTED_DATABASE
    username = "cipo_test" if test_mode else EXPECTED_USERNAME
    if url.host != EXPECTED_HOST or url.port != port:
        raise RuntimeError("DATABASE_URL must target the approved local PostgreSQL endpoint")
    if url.database != database or url.username != username:
        raise RuntimeError("DATABASE_URL must target the approved CIPO VISION database")
    return url
