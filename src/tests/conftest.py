import logging

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from ingestion_api.api.v1.search import get_search_router
from ingestion_api.core.config import settings
from ingestion_api.core.database import engine


def pytest_configure():
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)
    engine.echo = False


# @pytest_asyncio.fixture
# async def db_session():
# async with AsyncSessionFactory() as session:
# yield session


@pytest_asyncio.fixture
async def search_router(db_session):
    return get_search_router(session=db_session)


@pytest_asyncio.fixture
async def client():
    from fastapi.testclient import TestClient

    from ingestion_api.main import app

    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session):
    from httpx import ASGITransport, AsyncClient

    from ingestion_api.core.database import get_db
    from ingestion_api.main import app

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.pop(get_db, None)
