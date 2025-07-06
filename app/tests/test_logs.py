from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_logs():
    response = client.get("/logs")
    data = response.json()
    assert "files" in data
    assert "total_count" in data
    assert "total_size" in data
