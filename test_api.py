import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Forex Chart Analyzer" in response.text

def test_analyze_no_file():
    response = client.post("/api/v1/analyze")
    assert response.status_code == 422  # Unprocessable entity

def test_invalid_file_type():
    # Create a text file
    files = {"image": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/api/v1/analyze", files=files, data={"risk_percent": 1.0})
    assert response.status_code == 400
