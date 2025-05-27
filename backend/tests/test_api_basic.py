import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_tools_health_check(client: TestClient):
    """Test tools health check"""
    response = client.get("/domain/tools/health")
    assert response.status_code in [200, 500]
    assert "error" in response.json() or "status" in response.json()

def test_scan_list_empty(client: TestClient):
    """Test getting empty scan list"""
    response = client.get("/domain/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

def test_scan_stats_empty(client: TestClient):
    """Test getting scan stats when no scans exist"""
    response = client.get("/domain/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)