import pytest

from ingestion_api.domain.users.enums import UserRole
from ingestion_api.domain.users.repository import UserRepository
from ingestion_api.domain.users.service import InvalidCredentialsError, UserService


@pytest.mark.integration
async def test_authenticated_user(db_session):
    repository = UserRepository(db_session)
    service = UserService(repository)

    # Create a test user
    email = "test@example.com"
    password = "securepassword"
    user = await service.create_user(email=email, password=password, role=UserRole.USER)

    await db_session.commit()

    # Authenticate the user
    authenticated_user = await service.authenticate_user(email=email, password=password)

    assert authenticated_user.id == user.id
    assert authenticated_user.email == user.email


async def test_authenticated_user_invalid_password(db_session):
    repository = UserRepository(db_session)
    service = UserService(repository)

    # Create a test user
    email = "test_invalid@example.com"
    password = "securepassword"
    await service.create_user(email=email, password=password, role=UserRole.USER)

    await db_session.commit()

    with pytest.raises(InvalidCredentialsError):
        await service.authenticate_user(email=email, password="wrongpassword")
