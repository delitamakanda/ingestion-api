from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from ingestion_api.core.config import settings


class InvalidTokenError(Exception):
    pass


def create_access_token(
    *, sub: str, role: str, expires_delta: timedelta | None = None
) -> str:
    now = datetime.now(UTC)

    expires_at = now + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expires_minutes)
    )

    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError() from exc
