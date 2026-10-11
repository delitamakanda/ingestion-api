import pytest

from ingestion_api.core.security.tokens import decode_access_token
from ingestion_api.domain.users.enums import UserRole
from ingestion_api.domain.users.repository import UserRepository
from ingestion_api.domain.users.service import UserService


@pytest.mark.integration
async def test_login_returns_access_token(async_client, db_session):
    repository = UserRepository(db_session)
    service = UserService(repository)

    user = await service.create_user(
        email="test@example.com", password="password", role=UserRole.USER
    )

    await db_session.commit()

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == str(user.id)


async def test_login_with_invalid_credentials_returns_401(async_client):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong_password"},
    )
    assert response.status_code == 401
