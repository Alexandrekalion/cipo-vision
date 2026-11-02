import os
from concurrent.futures import ThreadPoolExecutor
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import text

os.environ.setdefault("DEV_AUTH_ENABLED", "false")
from app.db import SessionLocal
from app.main import app
from app.models import AuditEvent, Extraction, Request, Signature, User, UserCredential, UserSession, UserSignature, WorkflowEvent
from app.security import hash_password

pytestmark = pytest.mark.skipif(not os.environ.get("DATABASE_URL", "").startswith("postgresql"), reason="requires isolated PostgreSQL")


def seed():
    db = SessionLocal()
    for model in (Extraction, WorkflowEvent, AuditEvent, Signature, Request, UserSession, UserSignature, UserCredential, User):
        db.query(model).delete()
    ids = {}
    roles = {
        "e2e_requester": "Gestor solicitante", "e2e_manager": "Gerente aprovador",
        "e2e_witness": "Testemunha", "e2e_safety": "Segurança do Trabalho",
        "e2e_rh": "RH", "e2e_ti": "TI", "e2e_other": "Gestor solicitante",
    }
    for username, role in roles.items():
        u = User(username=username, display_name=username, role=role); db.add(u); db.flush()
        db.add(UserCredential(user_id=u.id, password_hash=hash_password(username + "-pass"))); ids[username] = u.id
    db.commit(); db.close(); return ids


def auth(username):
    c = TestClient(app)
    r = c.post("/auth/login", json={"username": username, "password": username + "-pass"})
    assert r.status_code == 200, r.text
    return c, r.json()["access_token"]


def create(c, csrf, manager_id):
    r = c.post("/requests", headers={"X-CSRF-Token": csrf}, json={"manager_id": manager_id, "employee": "Fictício", "occurrence_type": "E2E", "occurred_at": "2026-11-02T10:00:00Z", "location": "Teste", "camera_area": "C01", "reason": "Homologação"})
    assert r.status_code == 200, r.text; return r.json()["id"]


def sign(c, csrf, rid, purpose):
    r = c.post(f"/requests/{rid}/sign", headers={"X-CSRF-Token": csrf}, json={"purpose": purpose, "document_hash": f"hash-{rid}", "confirmed": True})
    assert r.status_code == 200, r.text


def approve(c, csrf, rid, witness_id, rh):
    return c.post(f"/requests/{rid}/decision", headers={"X-CSRF-Token": csrf}, json={"decision": "APPROVE", "manager_signature": True, "witness_id": witness_id, "rh_required": rh})


def finish_flow(require_rh):
    ids = seed(); requester, rc = auth("e2e_requester"); rid = create(requester, rc, ids["e2e_manager"]); sign(requester, rc, rid, "SOLICITANTE")
    manager, mc = auth("e2e_manager"); assert approve(manager, mc, rid, ids["e2e_witness"], require_rh).status_code == 200
    safety, sc = auth("e2e_safety")
    def witness_sign():
        c, csrf = auth("e2e_witness"); return c.post(f"/requests/{rid}/sign", headers={"X-CSRF-Token":csrf}, json={"purpose":"TESTEMUNHA", "document_hash":f"hash-{rid}", "confirmed":True}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool: witness_results=list(pool.map(lambda _: witness_sign(), [1, 2]))
    assert sorted(witness_results) == [200, 409]
    sign(safety, sc, rid, "SEGURANCA")
    ti, tc = auth("e2e_ti")
    if require_rh:
        assert ti.post(f"/requests/{rid}/extraction/start", headers={"X-CSRF-Token": tc}, json={"storage_reference": "e2e://video"}).status_code == 409
        rh, hc = auth("e2e_rh"); sign(rh, hc, rid, "RH")
    start = ti.post(f"/requests/{rid}/extraction/start", headers={"X-CSRF-Token": tc}, json={"storage_reference": "e2e://video"}); assert start.status_code == 200
    assert ti.post(f"/requests/{rid}/extraction/finish", headers={"X-CSRF-Token": tc}).status_code == 200
    db = SessionLocal(); item = db.get(Request, rid); sigs = db.query(Signature).filter_by(request_id=rid).count(); exts = db.query(Extraction).filter_by(request_id=rid).count(); events = db.query(AuditEvent).filter_by(request_id=rid).count(); db.close()
    assert item.status == "FINALIZADA" and sigs == (5 if require_rh else 4) and exts == 1 and events >= 6


def test_postgres_e2e_without_rh(): finish_flow(False)
def test_postgres_e2e_with_rh(): finish_flow(True)


def test_postgres_negative_authorization_and_rejection():
    ids = seed(); requester, rc = auth("e2e_requester"); rid = create(requester, rc, ids["e2e_manager"]); other, oc = auth("e2e_other")
    assert other.post(f"/requests/{rid}/sign", headers={"X-CSRF-Token": oc}, json={"purpose":"SOLICITANTE", "document_hash":"x", "confirmed":True}).status_code == 403
    manager, mc = auth("e2e_manager"); assert manager.post(f"/requests/{rid}/decision", headers={"X-CSRF-Token":mc}, json={"decision":"REJECT"}).status_code == 422
    assert manager.post(f"/requests/{rid}/decision", headers={"X-CSRF-Token":mc}, json={"decision":"REJECT", "reason":"Sem autorização"}).status_code == 200


def test_postgres_duplicate_decision_and_extraction_are_serialized():
    ids = seed(); requester, rc = auth("e2e_requester"); rid = create(requester, rc, ids["e2e_manager"]); sign(requester, rc, rid, "SOLICITANTE")
    manager, mc = auth("e2e_manager")
    def decision():
        c, csrf = auth("e2e_manager")
        return approve(c, csrf, rid, ids["e2e_witness"], False).status_code
    with ThreadPoolExecutor(max_workers=2) as pool: results = list(pool.map(lambda _: decision(), [1, 2]))
    assert sorted(results) == [200, 409]
    witness, wc = auth("e2e_witness"); safety, sc = auth("e2e_safety"); sign(witness, wc, rid, "TESTEMUNHA"); sign(safety, sc, rid, "SEGURANCA")
    # Requester signature plus manager, witness and safety now unlock TI.
    ti_results=[]
    def start():
        c, csrf = auth("e2e_ti"); return c.post(f"/requests/{rid}/extraction/start", headers={"X-CSRF-Token":csrf}, json={"storage_reference":"e2e://concurrent"}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool: ti_results=list(pool.map(lambda _: start(), [1, 2]))
    assert sorted(ti_results) == [200, 409]

def ready_extraction():
    ids = seed(); requester, rc = auth("e2e_requester"); rid = create(requester, rc, ids["e2e_manager"]); sign(requester, rc, rid, "SOLICITANTE")
    manager, mc = auth("e2e_manager"); assert approve(manager, mc, rid, ids["e2e_witness"], False).status_code == 200
    witness, wc = auth("e2e_witness"); safety, sc = auth("e2e_safety"); sign(witness, wc, rid, "TESTEMUNHA"); sign(safety, sc, rid, "SEGURANCA")
    ti, tc = auth("e2e_ti"); assert ti.post(f"/requests/{rid}/extraction/start", headers={"X-CSRF-Token":tc}, json={"storage_reference":"e2e://finish"}).status_code == 200
    return rid

def test_postgres_concurrent_finish_has_one_success_and_one_conflict():
    rid = ready_extraction()
    def finish():
        c, csrf = auth("e2e_ti"); return c.post(f"/requests/{rid}/extraction/finish", headers={"X-CSRF-Token":csrf}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool: results = list(pool.map(lambda _: finish(), [1, 2]))
    assert sorted(results) == [200, 409]
    db = SessionLocal(); assert db.query(Extraction).filter_by(request_id=rid).count() == 1; assert db.get(Request, rid).status == "FINALIZADA"; db.close()

def test_postgres_concurrent_resubmit_has_one_success_and_one_conflict():
    ids = seed(); requester, rc = auth("e2e_requester"); rid = create(requester, rc, ids["e2e_manager"])
    manager, mc = auth("e2e_manager"); assert manager.post(f"/requests/{rid}/decision", headers={"X-CSRF-Token":mc}, json={"decision":"RETURN", "reason":"Corrigir dados"}).status_code == 200
    def resubmit():
        c, csrf = auth("e2e_requester"); return c.post(f"/requests/{rid}/resubmit", headers={"X-CSRF-Token":csrf}, json={"employee":"Corrigido", "occurrence_type":"E2E", "occurred_at":"2026-11-02T10:00:00Z", "location":"Teste", "camera_area":"C02", "reason":"Corrigido"}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool: results = list(pool.map(lambda _: resubmit(), [1, 2]))
    assert sorted(results) == [200, 409]
    db = SessionLocal(); assert db.get(Request, rid).status == "RASCUNHO"; events = db.query(WorkflowEvent).filter_by(request_id=rid).all(); assert len(events) == 3; assert sum(event.from_status == "DEVOLVIDA_PARA_CORRECAO" and event.to_status == "RASCUNHO" for event in events) == 1; db.close()
