from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_logs():
    response = client.get("/logs")
    assert response.status_code == 200
    assert "message" in response.json()
