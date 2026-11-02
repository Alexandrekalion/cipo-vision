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

def test_user_signature_is_private_and_requires_csrf():
    response = client.post("/auth/login", json={"username": "alice", "password": "alice-test"})
    csrf = response.json()["access_token"]
    image = "data:image/png;base64,ZmFrZS1zaWduYXR1cmU="
    assert client.put("/auth/signature", json={"signature_data": image}).status_code == 403
    saved = client.put("/auth/signature", headers={"X-CSRF-Token": csrf}, json={"signature_data": image})
    assert saved.status_code == 200
    assert saved.json()["signature_digest"]
    assert "signature_data" not in saved.json()
    fetched = client.get("/auth/signature")
    assert fetched.status_code == 200
    assert fetched.json()["user_id"] == saved.json()["user_id"]

def test_first_access_profile_requires_corporate_fields_and_signature():
    response = client.post("/auth/login", json={"username": "alice", "password": "alice-test"})
    csrf = response.json()["access_token"]
    assert client.get("/auth/me").json()["profile_complete"] is False
    payload = {"full_name": "Alice Teste", "employee_number": "MAT-001", "department": "TI", "signature_data": "data:image/png;base64,ZmFrZQ=="}
    assert client.put("/auth/profile", json=payload).status_code == 403
    saved = client.put("/auth/profile", headers={"X-CSRF-Token": csrf}, json=payload)
    assert saved.status_code == 200
    assert saved.json()["employee_number"] == "MAT-001"
    assert client.get("/auth/me").json()["profile_complete"] is True

def test_incomplete_profile_cannot_use_operational_endpoint_when_enforced(monkeypatch):
    from app.config import settings
    from app.db import SessionLocal
    from app.models import User
    db = SessionLocal(); user = User(username="incomplete", display_name="Incomplete", role="Gestor solicitante"); db.add(user); db.flush(); db.add(UserCredential(user_id=user.id, password_hash=hash_password("incomplete-test"))); db.commit(); db.close()
    monkeypatch.setattr(settings, "enforce_profile_completion", True)
    response = client.post("/auth/login", json={"username": "incomplete", "password": "incomplete-test"})
    assert response.status_code == 200
    assert client.get("/requests").status_code == 403
    monkeypatch.setattr(settings, "enforce_profile_completion", False)
