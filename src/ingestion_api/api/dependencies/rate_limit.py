from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import RedisError

from ingestion_api.api.dependencies.auth import CurrentUser
from ingestion_api.core.config import settings
from ingestion_api.core.logging import get_logger
from ingestion_api.core.security.rate_limit import RedisRateLimiter

logger = get_logger(__name__)


async def get_rate_limit_redis() -> AsyncGenerator[Redis]:
    redis = Redis.from_url(settings.redis_url)
    try:
        yield redis
    finally:
        await redis.aclose()


RedisClient = Annotated[Redis, Depends(get_rate_limit_redis)]


@dataclass(frozen=True)
class RateLimitPolicy:
    name: str
    limit: int
    window_seconds: int


DEFAULT_RATE_LIMIT = RateLimitPolicy(name="authenticated", limit=10, window_seconds=60)


def require_rate_limit(
    policy: RateLimitPolicy,
) -> Callable:
    async def rate_limit_checker(current_user: CurrentUser, redis: RedisClient) -> None:
        key = f"rate-limit:{policy.name}:{current_user.id}"
        limiter = RedisRateLimiter(redis)

        try:
            result = await limiter.is_allowed(
                key=key, limit=policy.limit, window_seconds=policy.window_seconds
            )
        except RedisError as exc:
            logger.error(
                "rate_limit.redis.unavailable",
                policy=policy.name,
                error_type=type(exc).__name__,
            )

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limit service unavailable",
            ) from exc

        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(result.retry_after)},
            )

    return rate_limit_checker
