from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200