import uuid
from typing import Optional
from fastapi import Depends, Request  # type: ignore
from fastapi_users import BaseUserManager, UUIDIDMixin  # type: ignore
from apps.models.models import User
import os
from dotenv import load_dotenv  # type: ignore
from ..config.database import get_user_db


load_dotenv()
SECRET = os.getenv("SECRET_KEY")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    if not SECRET:
        raise ValueError("SECRET is not set in the environment variables.")
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
