import os
from collections.abc import AsyncGenerator

import pytest
from redis.asyncio import Redis


@pytest.fixture
async def redis_client() -> AsyncGenerator[Redis]:
    url = os.getenv("RATE_LIMIT_TEST_REDIS_URL", "redis://localhost:6379/15")
    redis = Redis.from_url(url, decode_responses=True)
    try:
        await redis.ping()
        yield redis
    finally:
        await redis.aclose()
