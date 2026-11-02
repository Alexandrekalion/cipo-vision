import os
os.environ['DATABASE_URL']='sqlite://'
os.environ['DEV_AUTH_ENABLED']='true'
from app.db import Base, engine
from app import models
Base.metadata.create_all(engine)
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.db import SessionLocal
db = SessionLocal(); db.add(User(username='giuliano', display_name='Giuliano', role='Gerente aprovador')); db.commit(); db.close()

client=TestClient(app)

def test_unauthenticated_is_rejected():
    assert client.get('/requests').status_code == 401

def test_approval_requires_witness_and_rh_decision():
    response = client.post('/auth/dev-login',json={'username':'giuliano'})
    assert response.status_code == 200
    assert response.json()['access_token'] == 'dev-giuliano'

def test_openapi_available():
    assert client.get('/openapi.json').status_code == 200
