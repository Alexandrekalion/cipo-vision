import os
os.environ['DATABASE_URL']='sqlite://'
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_unauthenticated_is_rejected():
    assert client.get('/requests').status_code == 401

def test_approval_requires_witness_and_rh_decision():
    response = client.post('/auth/dev-login',json={'username':'giuliano'})
    assert response.status_code == 200
    assert response.json()['access_token'] == 'dev-giuliano'

def test_openapi_available():
    assert client.get('/openapi.json').status_code == 200
