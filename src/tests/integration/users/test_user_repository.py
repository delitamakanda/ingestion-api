from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from ingestion_api.core.security.password import hash_password
from ingestion_api.core.security.tokens import create_access_token
from ingestion_api.domain.users.enums import UserRole
from ingestion_api.domain.users.repository import UserRepository
from ingestion_api.domain.users.service import UserService


@pytest.mark.integration
async def test_create_and_find_user(db_session):
    repository = UserRepository(db_session)
    user = await repository.create_user(
        email="test@example.com", password=hash_password("password"), role=UserRole.USER
    )

    await db_session.commit()  # Commit the transaction to save the user in the database
    found_user = await repository.get_user_by_email(email="test@example.com")
    assert found_user is not None
    assert found_user.email == "test@example.com"
    assert found_user.id == user.id


@pytest.mark.integration
async def test_get_user_by_id(db_session):
    repository = UserRepository(db_session)
    user = await repository.create_user(
        email="test@example.com", password=hash_password("password"), role=UserRole.USER
    )

    await db_session.commit()  # Commit the transaction to save the user in the database
    found_user = await repository.get_user_by_id(user_id=user.id)
    assert found_user is not None
    assert found_user.email == "test@example.com"
    assert found_user.id == user.id


@pytest.mark.integration
async def test_me_returns_current_user(async_client, db_session):
    repository = UserRepository(db_session)
    service = UserService(repository)
    user = await service.create_user(
        email="test@example.com", password="SuperSecretPassword", role=UserRole.USER
    )
    await db_session.commit()  # Commit the transaction to save the user in the database
    token = create_access_token(sub=str(user.id), role=user.role.value)

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["id"] == str(user.id)


@pytest.mark.integration
async def test_me_without_token_returns_401(async_client):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.integration
async def test_me_with_unknown_user_returns_401(async_client, db_session):
    # Create a token with a random UUID that does not correspond to any user
    unknown_user_id = str(uuid4())
    token = create_access_token(sub=unknown_user_id, role=UserRole.USER.value)

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"


@pytest.mark.integration
async def test_inactive_user_returns_401(async_client, db_session):
    repository = UserRepository(db_session)
    service = UserService(repository)
    user = await service.create_user(
        email="test@example.com", password="SuperSecretPassword", role=UserRole.USER
    )
    user.is_active = False
    await db_session.commit()  # Commit the transaction to save the user in the database
    token = create_access_token(sub=str(user.id), role=user.role.value)
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"


@pytest.mark.integration
async def test_me_with_invalid_token_returns_401(async_client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"


@pytest.mark.integration
async def test_email_must_be_unique(db_session):
    repository = UserRepository(db_session)
    password_hash = hash_password("password")
    await repository.create_user(
        email="test@example.com", password=password_hash, role=UserRole.USER
    )

    await (
        db_session.commit()
    )  # Commit the transaction to save the first user in the database

    with pytest.raises(IntegrityError):
        await repository.create_user(
            email="test@example.com", password=password_hash, role=UserRole.USER
        )
        await (
            db_session.commit()
        )  # This should raise an IntegrityError due to unique constraint violation
