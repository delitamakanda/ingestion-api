from ingestion_api.core.security.password import hash_password
from ingestion_api.domain.users.models import User
from ingestion_api.domain.users.repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, *, email: str, password: str) -> User:
        existing_user = await self.repository.get_user_by_email(email=email)
        if existing_user:
            raise ValueError("User with this email already exists")
        hashed_password = hash_password(password)
        return await self.repository.create_user(email=email, password=hashed_password)
