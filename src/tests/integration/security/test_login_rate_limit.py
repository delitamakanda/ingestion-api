from uuid import uuid4

import pytest

from ingestion_api.core.config import settings


@pytest.mark.integration
async def test_login_email_rate_limit(client, monkeypatch):
    monkeypatch.setattr(settings, "login_email_limit", 2)
    monkeypatch.setattr(settings, "login_ip_limit", 100)

    email = f"unknown-{uuid4()}@example.com"

    payload = {"email": email, "password": "wrongpassword"}

    first = client.post("/api/v1/auth/login", json=payload)
    second = client.post("/api/v1/auth/login", json=payload)
    third = client.post("/api/v1/auth/login", json=payload)

    assert first.status_code == 401
    assert second.status_code == 401
    assert third.status_code == 429

    assert int(third.headers["Retry-After"]) > 0
