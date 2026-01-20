# routers/user.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated, List
from ..crud.user import get_user_by_id
from auth_app.config.database import get_async_session
from ..models.models import User
from ..schema.user import  UserReadSimple, UserUpdate  
from auth_app.service.authenticate import current_active_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import User
from ..schema.user import UserReadSimple, UserUpdate  
from auth_app.service.authenticate import current_active_user, current_active_user_is_superUser

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(current_active_user_is_superUser)])

# -------------------------------
# READ LIST (maintenant async)
# -------------------------------
@router.get("/get_users/", response_model=List[UserReadSimple], )
async def read_users(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = Query(100, le=100)
):
    result = await session.execute(select(User).offset(offset).limit(limit))
    users = result.scalars().all()
    return users

# -------------------------------
# READ SINGLE
# -------------------------------
@router.get("/user/{user_id}", response_model=UserReadSimple)
async def read_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or user.is_active == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------------
# UPDATE (maintenant async)
# -------------------------------
@router.patch("/user/{user_id}", response_model=UserReadSimple)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user or db_user.is_active == "delete":
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)

    # Vérifier si l'email est déjà pris
    if "email" in update_data and update_data["email"] != db_user.email:
        result = await session.execute(
            select(User).where(
                User.email == update_data["email"],
                User.id != user_id
            )
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")

    # Mise à jour des champs
    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Update failed")

    return db_user

# -------------------------------
# DELETE (maintenant async)
# -------------------------------
@router.delete("/user/{user_id}")
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user or db_user.is_active == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.active = "delete"
    session.add(db_user)
    await session.commit()
    return {"ok": True}