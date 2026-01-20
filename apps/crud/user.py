# crud/user.py
from typing import Optional, List
from uuid import UUID
from sqlmodel import Session, select
from ..models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlmodel import SQLModel


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await session.execute(
        select(User).where(User.id == user_id and User.is_active != "delete")
    )
    return result.scalar_one_or_none()


""" 
async def get_user_by_username(session: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).first()
    if not user or user.statut == "delete":
        raise HTTPException(status_code=404, detail="User not found")
    print("User found:", user)    
    return user


async def get_role_by_username(session: Session, username: str) -> Optional[str]:
    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).first()
    if user and user.statut != "delete":
        return user.rol
    return None              """
