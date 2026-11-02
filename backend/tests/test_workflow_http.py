import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["DEV_AUTH_ENABLED"] = "false"

from fastapi.testclient import TestClient
from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import AuditEvent, Extraction, Request, Signature, User, UserCredential, UserSession, WorkflowEvent
from app.security import hash_password

Base.metadata.create_all(engine)


def seed_users():
    db = SessionLocal()
    for model in (Extraction, WorkflowEvent, AuditEvent, Signature, Request, UserSession, UserCredential, User):
        db.query(model).delete()
    users = {}
    for username, role in {
        "requester": "Gestor solicitante", "manager": "Gerente aprovador",
        "witness": "Testemunha", "safety": "Segurança do Trabalho", "rh": "RH", "ti": "TI",
    }.items():
        user = User(username=username, display_name=username.title(), role=role)
        db.add(user); db.flush()
        db.add(UserCredential(user_id=user.id, password_hash=hash_password(f"{username}-password")))
        users[username] = user.id
    db.commit(); db.close()
    return users


def login(username):
    client = TestClient(app)
    response = client.post("/auth/login", json={"username": username, "password": f"{username}-password"})
    assert response.status_code == 200
    return client, response.json()["access_token"]


def create_request(client, csrf, manager_id):
    response = client.post("/requests", headers={"X-CSRF-Token": csrf}, json={
        "manager_id": manager_id, "employee": "Colaborador fictício", "occurrence_type": "Teste",
        "occurred_at": "2026-11-02T10:00:00Z", "location": "Homologação", "camera_area": "C01",
        "reason": "Registro de teste isolado",
    })
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_full_workflow_without_rh_and_extraction_rbac():
    ids = seed_users()
    requester, requester_csrf = login("requester")
    request_id = create_request(requester, requester_csrf, ids["manager"])
    assert requester.post(f"/requests/{request_id}/sign", headers={"X-CSRF-Token": requester_csrf}, json={"purpose":"SOLICITANTE", "document_hash":"hash-v1", "confirmed":True}).status_code == 200

    manager, manager_csrf = login("manager")
    decision = manager.post(f"/requests/{request_id}/decision", headers={"X-CSRF-Token": manager_csrf}, json={"decision":"APPROVE", "manager_signature":True, "witness_id":ids["witness"], "rh_required":False})
    assert decision.status_code == 200
    assert manager.post(f"/requests/{request_id}/decision", headers={"X-CSRF-Token": manager_csrf}, json={"decision":"APPROVE", "manager_signature":True, "witness_id":ids["witness"], "rh_required":False}).status_code == 409

    ti, ti_csrf = login("ti")
    assert ti.post(f"/requests/{request_id}/extraction/start", headers={"X-CSRF-Token":ti_csrf}, json={"storage_reference":"test-only://video"}).status_code == 409
    witness, witness_csrf = login("witness")
    assert witness.post(f"/requests/{request_id}/sign", headers={"X-CSRF-Token":witness_csrf}, json={"purpose":"TESTEMUNHA", "document_hash":"hash-v1", "confirmed":True}).status_code == 200
    safety, safety_csrf = login("safety")
    assert safety.post(f"/requests/{request_id}/sign", headers={"X-CSRF-Token":safety_csrf}, json={"purpose":"SEGURANCA", "document_hash":"hash-v1", "confirmed":True}).status_code == 200
    started = ti.post(f"/requests/{request_id}/extraction/start", headers={"X-CSRF-Token":ti_csrf}, json={"storage_reference":"test-only://video"})
    assert started.status_code == 200
    assert ti.post(f"/requests/{request_id}/extraction/finish", headers={"X-CSRF-Token":ti_csrf}).status_code == 200


def test_required_csrf_and_rh_conditional_rule():
    ids = seed_users()
    requester, csrf = login("requester")
    request_id = create_request(requester, csrf, ids["manager"])
    assert requester.post(f"/requests/{request_id}/sign", json={"purpose":"SOLICITANTE", "document_hash":"h", "confirmed":True}).status_code == 403
    manager, manager_csrf = login("manager")
    assert manager.post(f"/requests/{request_id}/decision", headers={"X-CSRF-Token":manager_csrf}, json={"decision":"APPROVE", "manager_signature":True, "witness_id":ids["witness"], "rh_required":True}).status_code == 200
    rh, rh_csrf = login("rh")
    assert rh.post(f"/requests/{request_id}/sign", headers={"X-CSRF-Token":rh_csrf}, json={"purpose":"RH", "document_hash":"h", "confirmed":True}).status_code == 200

