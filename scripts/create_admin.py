import asyncio
import getpass

from ingestion_api.core.database import AsyncSessionFactory
from ingestion_api.domain.users.enums import UserRole
from ingestion_api.domain.users.repository import UserRepository
from ingestion_api.domain.users.service import UserService


async def main():
    email = input("Enter admin email: ")
    password = getpass.getpass("Enter admin password: ")
    async with AsyncSessionFactory() as session:
        repository = UserRepository(session)
        service = UserService(repository)
        await service.create_user(email=email, password=password, role=UserRole.ADMIN)

        await session.commit()

        print(f"Admin user created with email: {email}")


if __name__ == "__main__":
    asyncio.run(main())
