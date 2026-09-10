import pytest_asyncio
import logging

from ingestion_api.api.v1.search import get_search_router
from ingestion_api.core.database import AsyncSessionFactory, engine


def pytest_configure():
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)
    engine.echo = False


@pytest_asyncio.fixture
async def db_session():
    async with AsyncSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def search_router(db_session):
    return get_search_router(session=db_session)
