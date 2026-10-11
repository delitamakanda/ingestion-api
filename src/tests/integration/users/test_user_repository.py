import pytest
from sqlalchemy.exc import IntegrityError

from ingestion_api.core.security.password import hash_password
from ingestion_api.domain.users.enums import UserRole
from ingestion_api.domain.users.repository import UserRepository


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
