import os

import pytest

from app.migration_config import get_migration_database_url


def test_migration_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        get_migration_database_url()


def test_migration_rejects_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./cipo_vision_dev.sqlite3")
    with pytest.raises(RuntimeError, match="approved PostgreSQL psycopg driver"):
        get_migration_database_url()


def test_migration_rejects_other_destination(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://cipo_vision_app:secret@10.0.0.5:5432/cipo_vision",
    )
    with pytest.raises(RuntimeError, match="approved local PostgreSQL endpoint"):
        get_migration_database_url()


def test_migration_accepts_only_approved_target(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://cipo_vision_app:secret@127.0.0.1:5432/cipo_vision",
    )
    url = get_migration_database_url()
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "127.0.0.1"
    assert url.database == "cipo_vision"
    assert url.username == "cipo_vision_app"
