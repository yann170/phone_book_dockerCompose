import uuid

from fastapi_users import schemas  # type: ignore
from pydantic import EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    email: EmailStr



class UserCreate(schemas.BaseUserCreate):
    username: str

  

class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = None
    email: EmailStr | None = None
    numero: str | None = None
