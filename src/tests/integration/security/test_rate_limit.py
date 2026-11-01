import uuid

import pytest
from redis.asyncio import Redis

from ingestion_api.core.security.rate_limit import RedisRateLimiter


@pytest.mark.integration
async def test_limit_is_enforced():
    redis = Redis.from_url("redis://localhost:6379/0", decode_responses=True)

    key = f"test:rate_limit:{uuid.uuid4()}"

    try:
        limiter = RedisRateLimiter(redis)

        for remaining in range(2, -1, -1):
            result = await limiter.is_allowed(key=key, limit=3, window_seconds=60)
            assert result.allowed is True
            assert result.remaining == remaining
        result = await limiter.is_allowed(key=key, limit=3, window_seconds=60)
        assert result.allowed is False
        assert result.retry_after > 0
    finally:
        await redis.delete(key)
        await redis.aclose()
