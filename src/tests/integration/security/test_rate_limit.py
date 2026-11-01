import asyncio
import uuid

import pytest
from redis.asyncio import Redis

from ingestion_api.core.security.rate_limit import RedisRateLimiter


@pytest.mark.parametrize(
    ("limit", "window_seconds"),
    [
        (0, 60),  # No requests allowed
        (-1, 60),  # Negative limit, should be treated as no limit
        (5, 0),
        (5, -1),  # Negative window, should be treated as no limit
    ],
)
@pytest.mark.integration
async def test_invalid_rate_limit_policy(redis_client, limit, window_seconds):
    limiter = RedisRateLimiter(redis_client)

    with pytest.raises(ValueError):
        await limiter.is_allowed(
            key="test:invalid_policy", limit=limit, window_seconds=window_seconds
        )


@pytest.mark.integration
async def test_concurrent_requests_respect_limit(redis_client):
    key = f"test:rate_limit:concurrent:{uuid.uuid4()}"
    limiter = RedisRateLimiter(redis_client)

    try:
        results = await asyncio.gather(
            *[
                limiter.is_allowed(key=key, limit=5, window_seconds=60)
                for _ in range(20)
            ]
        )
        allowed = sum(result.allowed for result in results)
        rejected = sum(not result.allowed for result in results)
        assert allowed == 5
        assert rejected == 15
        assert all(result.retry_after > 0 for result in results if not result.allowed)

    finally:
        await redis_client.delete(key)


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


@pytest.mark.integration
async def test_rate_limit_resets_after_expiration(redis_client):
    key = f"test:rate_limit:expiration:{uuid.uuid4()}"
    limiter = RedisRateLimiter(redis_client)

    try:
        first = await limiter.is_allowed(key=key, limit=1, window_seconds=1)
        assert first.allowed is True

        second = await limiter.is_allowed(key=key, limit=1, window_seconds=1)
        assert second.allowed is False
        await asyncio.sleep(1.2)  # Wait for the window to expire
        third = await limiter.is_allowed(key=key, limit=1, window_seconds=1)
        assert third.allowed is True
        assert third.remaining == 0
    finally:
        await redis_client.delete(key)
