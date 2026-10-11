from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalars().first()

    async def create_user(self, *, email: str, password: str) -> User:
        user = User(email=email.lower(), password=password)
        self.session.add(user)
        await self.session.flush()
        return user
