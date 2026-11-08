import hashlib
import hmac
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from redis.exceptions import RedisError

from ingestion_api.api.dependencies.rate_limit import RedisClient
from ingestion_api.core.config import settings
from ingestion_api.core.logging import get_logger
from ingestion_api.core.security.rate_limit import RedisRateLimiter
from ingestion_api.domain.auth.schemas import LoginRequest

logger = get_logger(__name__)


def hash_identifier(value: str) -> str:
    return hmac.new(
        settings.jwt_secret_key.encode(), value.encode(), hashlib.sha256
    ).hexdigest()


async def check_login_rate_limit(
    request: Request, payload: LoginRequest, redis: RedisClient
) -> None:
    client_ip = request.client.host if request.client is not None else "unknown"

    normalized_email = payload.email.strip().lower()

    ip_key = f"rate-limit:login:ip:{hash_identifier(client_ip)}"

    email_key = f"rate-limit:login:email:{hash_identifier(normalized_email)}"

    limiter = RedisRateLimiter(redis)

    policies = (
        (ip_key, settings.login_ip_limit),
        (email_key, settings.login_email_limit),
    )

    try:
        results = []

        for key, limit in policies:
            result = await limiter.is_allowed(
                key=key,
                limit=limit,
                window_seconds=settings.login_rate_limit_window_seconds,
            )
            results.append(result)
    except RedisError as exc:
        logger.error(
            "login_rate_limit.redis.unavailable",
            error_type=type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limit service unavailable",
        ) from exc

    rejected = [result for result in results if not result.allowed]

    if rejected:
        retry_after = max(result.retry_after for result in rejected)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )


LoginRateLimit = Annotated[None, Depends(check_login_rate_limit)]
