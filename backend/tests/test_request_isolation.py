from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models import Request, User, UserCredential
from app.security import hash_password


def test_request_creation_and_requester_isolation():
    db = SessionLocal()
    db.query(Request).delete()
    db.query(UserCredential).delete()
    db.query(User).delete()
    requester = User(username="test_requester", display_name="Requester", role="Gestor solicitante")
    other = User(username="test_other", display_name="Other", role="Gestor solicitante")
    manager = User(username="test_manager", display_name="Manager", role="Gerente aprovador")
    db.add_all([requester, other, manager]); db.flush()
    db.add_all([
        UserCredential(user_id=requester.id, password_hash=hash_password("requester-pass")),
        UserCredential(user_id=other.id, password_hash=hash_password("other-pass")),
        UserCredential(user_id=manager.id, password_hash=hash_password("manager-pass")),
    ])
    db.commit(); db.close()
    client = TestClient(app)
    login = client.post("/auth/login", json={"username": "test_requester", "password": "requester-pass"})
    assert login.status_code == 200
    csrf = login.json()["access_token"]
    created = client.post("/requests", headers={"X-CSRF-Token": csrf}, json={
        "manager_id": manager.id, "employee": "Colaborador teste", "occurrence_type": "Incidente",
        "occurred_at": "2026-11-02T10:00:00Z", "location": "Local de teste", "camera_area": "C01", "reason": "Teste isolado",
    })
    assert created.status_code == 200
    client.cookies.clear()
    login_other = client.post("/auth/login", json={"username": "test_other", "password": "other-pass"})
    assert login_other.status_code == 200
    assert client.get("/requests").json() == []
