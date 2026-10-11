from uuid import UUID

from pydantic import BaseModel, EmailStr

from ingestion_api.domain.users.enums import UserRole


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str


class UserReadSchema(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    is_active: bool

    class Config:
        orm_mode = True
