import pytest
from fastapi.testclient import TestClient

from ingestion_api.main import app

PROTECTED_ENDPOINTS = [
    ("POST", "/api/v1/search"),
    ("GET", "/api/v1/documents/00000000-0000-0000-0000-000000000001/chunks"),
    ("POST", "/api/v1/ingestion/documents"),
    ("POST", "/api/v1/documents/00000000-0000-0000-0000-000000000001/reindex"),
    ("GET", "/api/v1/jobs/"),
    ("GET", "/api/v1/jobs/00000000-0000-0000-0000-000000000001"),
    ("POST", "/api/v1/jobs/00000000-0000-0000-0000-000000000001/retry"),
]


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.mark.parametrize("method, path", PROTECTED_ENDPOINTS)
def test_protected_endpoints(client, method, path):
    response = client.request(method, path)
    assert response.status_code == 401
