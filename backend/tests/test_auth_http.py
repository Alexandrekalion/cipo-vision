import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["DEV_AUTH_ENABLED"] = "true"

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import User, UserCredential
from app.security import hash_password

Base.metadata.create_all(engine)
db = SessionLocal()
db.query(UserCredential).delete()
db.query(User).delete()
alice = User(username="alice", display_name="Alice", role="Gestor solicitante")
db.add(alice)
db.flush()
db.add(UserCredential(user_id=alice.id, password_hash=hash_password("alice-test")))
db.commit()
db.close()

client = TestClient(app)


def test_login_sets_http_only_cookie_and_returns_csrf_token():
    response = client.post("/auth/login", json={"username": "alice", "password": "alice-test"})
    assert response.status_code == 200
    assert response.json()["access_token"]
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie


def test_invalid_login_and_unauthenticated_me_are_rejected():
    assert client.post("/auth/login", json={"username": "alice", "password": "wrong"}).status_code == 401
    client.cookies.clear()
    assert client.get("/auth/me").status_code == 401


def test_logout_requires_csrf_and_revokes_session():
    response = client.post("/auth/login", json={"username": "alice", "password": "alice-test"})
    csrf = response.json()["access_token"]
    assert client.post("/auth/logout").status_code == 403
    assert client.post("/auth/logout", headers={"X-CSRF-Token": csrf}).status_code == 200
    assert client.get("/auth/me").status_code == 401


def test_dev_login_is_disabled_when_homologation_flag_is_false(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "dev_auth_enabled", False)
    assert client.post("/auth/dev-login", json={"username": "alice"}).status_code == 404
