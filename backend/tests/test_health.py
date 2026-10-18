from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns application identity and status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "LexExtract"
    assert data["status"] == "running"
    assert "health_check" in data
    assert "api_v1" in data


def test_health_endpoint():
    """Verify operational health probe."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "LexExtract"


def test_api_v1_info_endpoint():
    """Verify API v1 root returns version and architecture info."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["api_version"] == "v1"
    assert data["application"] == "LexExtract"
    assert "Three-Tier" in data["architecture"]
