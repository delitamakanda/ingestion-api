from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from redis.exceptions import ConnectionError as RedisConnectionError

from ingestion_api.api.dependencies.auth import get_current_user
from ingestion_api.api.dependencies.rate_limit import (
    RateLimitPolicy,
    get_rate_limit_redis,
    require_rate_limit,
)


@pytest.mark.integration
async def test_rate_limit_returns_429(redis_client):
    app = FastAPI()

    policy_rate = RateLimitPolicy(name=f"test-{uuid4()}", limit=2, window_seconds=60)

    @app.get("/limited", dependencies=[Depends(require_rate_limit(policy_rate))])
    async def limited():
        return {"message": "success"}

    class FakeUser:
        id = uuid4()

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    app.dependency_overrides[get_rate_limit_redis] = lambda: redis_client

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.get("/limited")
        second = await client.get("/limited")
        third = await client.get("/limited")

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json()["detail"] == "Rate limit exceeded"
    assert int(third.headers["Retry-After"]) > 0


@pytest.mark.integration
async def test_rate_limit_returns_503_when_redis_fails():
    app = FastAPI()

    policy_rate = RateLimitPolicy(name="test-redis-failure", limit=2, window_seconds=60)

    @app.get("/limited", dependencies=[Depends(require_rate_limit(policy_rate))])
    async def limited():
        return {"message": "success"}

    class FakeUser:
        id = uuid4()

    failing_redis = AsyncMock()
    failing_redis.eval.side_effect = RedisConnectionError("Redis is down")

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    app.dependency_overrides[get_rate_limit_redis] = lambda: failing_redis

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/limited")

    assert response.status_code == 503
    assert response.json()["detail"] == "Rate limit service unavailable"
