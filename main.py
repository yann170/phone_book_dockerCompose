import os
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from apps.core.core import origins
import uuid
from fastapi import FastAPI, Depends
from apps.models.models import User
from fastapi_users import FastAPIUsers  # type: ignore
from apps.routes import user, contact, list_contact
from apps.auth_app.schema.schema import UserRead, UserUpdate
from apps.auth_app.service.authenticate import auth_backend
from apps.auth_app.service.user_manager import get_user_manager
from apps.auth_app.schema.schema import UserRead, UserUpdate, UserCreate
import uuid
from fastapi import FastAPI
from fastapi_users import FastAPIUsers  # type: ignore


app = FastAPI(
    title="application fastapi minimaliste",
    version="0.1.0",
    description="backend d'authentification avec fastapi-users et sqlmodel",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in origins if origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# auth_app configuration
app.include_router(user.router)
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)

app.include_router(
    contact.router,
)
app.include_router(list_contact.router)
