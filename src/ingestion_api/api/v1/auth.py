from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.core.database import get_db
from ingestion_api.core.security.tokens import create_access_token
from ingestion_api.domain.auth.schemas import LoginRequest, TokenResponse
from ingestion_api.domain.users.repository import UserRepository
from ingestion_api.domain.users.service import InvalidCredentialsError, UserService

router = APIRouter(prefix="/auth", tags=["auth"])

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DatabaseSession):
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)

    try:
        user = await user_service.authenticate_user(
            email=request.email, password=request.password
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    access_token = create_access_token(sub=str(user.id), role=user.role.value)
    return TokenResponse(access_token=access_token, token_type="bearer")
