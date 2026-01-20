from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from fastapi_users_db_sqlmodel import  SQLModelBaseUserDB  # type: ignore


# === Table d'association (N-N entre Contact et ContactList) ===
class ContactListLink(SQLModel, table=True):
    contact_id: Optional[int] = Field(
        default=None, foreign_key="contact.id", primary_key=True, 
    )
    list_id: Optional[int] = Field(
        default=None, foreign_key="listcontact.id", primary_key=True
    )


# === Liste de contacts (ex: Famille, Amis, Collègues) ===
#class ContactList(SQLModel, table=True):
class ListContact(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    list_name: str = Field(index=True, nullable=False, unique=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    # Relation N-N avec les contacts
    contacts: List["Contact"] = Relationship(
        back_populates="listes", link_model=ContactListLink,
    )
    # Chaque liste est créée par un utilisateur
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="listes")


# === Contact individuel ===
class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name : str = Field(index=True, nullable=False)
    address: str = Field(index=True, nullable=False)
    prenom: Optional[str] = None
    company: str = Field(index=True, nullable=False)
    email: Optional[EmailStr] = None
    phone: str = Field(nullable=False, unique=True)
    created_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    image_url: Optional[str] = None
    favorite: bool = Field(default=False, nullable=False)
    Blocked: bool = Field(default=False, nullable=False)
    # Relation N-N : un contact peut appartenir à plusieurs listes
    listes: List[ListContact] = Relationship(
        back_populates="contacts", link_model=ContactListLink,
    )


# === Utilisateur (propriétaire des listes de contacts) ===
class User(SQLModelBaseUserDB, table=True):  # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True, nullable=False)
    numero: Optional[str] = None
    photo: str = Field(default="default.jpg", nullable=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    listes: List[ListContact] = Relationship(back_populates="user")
