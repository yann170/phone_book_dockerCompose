from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import uuid
from fastapi_users import  FastAPIUsers # type: ignore
from apps.models.models import User
from .user_manager import get_user_manager

load_dotenv()

SECRET = os.getenv("SECRET_KEY")


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
def get_jwt_strategy() -> JWTStrategy:
    if not SECRET:
        raise ValueError("SECRET is not set in the environment variables.")
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user_is_superUser = fastapi_users.current_user(active=True, superuser = True)

current_active_user = fastapi_users.current_user(active=True)
