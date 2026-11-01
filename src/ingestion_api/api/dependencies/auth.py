from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.core.database import get_db
from ingestion_api.core.security.tokens import InvalidTokenError, decode_access_token
from ingestion_api.domain.users.enums import UserRole
from ingestion_api.domain.users.models import User
from ingestion_api.domain.users.repository import UserRepository

bearer_scheme = HTTPBearer()


def require_role(*allowed_roles: UserRole) -> Callable:
    async def role_checker(
        current_user: CurrentUser,
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:
        raise unauthorized() from exc

    sub = payload.get("sub")
    if sub is None:
        raise unauthorized()

    try:
        user_id = UUID(sub)
    except ValueError as exc:
        raise unauthorized() from exc

    repo = UserRepository(db)
    user = await repo.get_user_by_id(user_id)
    if user is None:
        raise unauthorized()
    if not user.is_active:
        raise unauthorized()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role(UserRole.ADMIN))]
