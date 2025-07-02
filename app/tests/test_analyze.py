from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@patch("app.services.gpt_service.analyze_logs")
def test_analyze_success(mock_analyze):
    mock_analyze.return_value = "TA database connection failure can occur due to various reasons. Here are some potential causes and solutions..."

    response = client.post("/analyze", json={"log": "Database connection failed at 10:23"})
    
    assert response.status_code == 200
    assert "analysis" in response.json()
    assert "database" in response.json()["analysis"]

def test_analyze_empty_log():
    response = client.post("/analyze", json={"log": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Log cannot be empty."
