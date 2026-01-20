from fastapi import APIRouter, Depends, HTTPException, Query

from apps.schema.contact import ContactRead
from ..crud.user import get_user_by_id
from auth_app.config.database import get_async_session
from ..models.models import ListContact, User
from ..schema.user import UserReadSimple, UserUpdate
from auth_app.service.authenticate import current_active_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import User, Contact
from ..schema.contactList import contactlistCreate, contactlistRead, contactlistUpdate
from auth_app.service.authenticate import current_active_user
from sqlalchemy.orm import selectinload


router = APIRouter(
    prefix="/contact_list",
    tags=["contact_list"],
    dependencies=[Depends(current_active_user)],
)

# --- LISTES DE CONTACTS ---


@router.post("/lists/", response_model=contactlistRead)
async def create_contact_list(
    contactlist: contactlistCreate, session: AsyncSession = Depends(get_async_session)
):
    db_list = ListContact.model_validate(contactlist)
    session.add(db_list)
    await session.commit()  # Obligatoire en async
    await session.refresh(db_list)
    return db_list


@router.get("/lists/", response_model=List[contactlistRead])
async def get_all_lists(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(ListContact))
    lists = result.scalars().all()
    if not lists:
        raise HTTPException(status_code=404, detail="No lists found")
    return lists


@router.patch("/update_list/{list_id}", response_model=contactlistRead)
async def update_list_contact(
    list_id: int,
    list_data: contactlistUpdate,  # Ton schéma avec list_name optionnel
    session: AsyncSession = Depends(get_async_session),
):
    # 1. Récupérer la liste existante
    db_list = await session.get(ListContact, list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="Liste de contacts non trouvée")

    # 2. Extraire les données envoyées (exclure les champs non définis)
    update_dict = list_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(db_list, key, value)

    # 3. Sauvegarder
    session.add(db_list)
    await session.commit()
    await session.refresh(db_list)
    return db_list


@router.delete("/delete_list/{list_id}", status_code=204)
async def delete_list_contact(
    list_id: int, session: AsyncSession = Depends(get_async_session)
):
    # 1. Récupérer la liste
    db_list = await session.get(ListContact, list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="Liste de contacts non trouvée")

    # 2. Supprimer la liste
    # SQLAlchemy/SQLModel va supprimer automatiquement les lignes dans ContactListLink
    await session.delete(db_list)
    await session.commit()

    return None  # Retourne un 204 No Content


# -------------------------------
# GET CONTACTS FROM A LIST
# -------------------------------


@router.get("/list/{id_list}/contacts", response_model=List[ContactRead])
async def get_contacts_from_list(
    id_list: int, session: AsyncSession = Depends(get_async_session)
):
    # On récupère la liste en chargeant ses contacts
    statement = select(ListContact).where(ListContact.id == id_list).options(selectinload(ListContact.contacts))  # type: ignore
    result = await session.execute(statement)
    db_list = result.scalar_one_or_none()

    if not db_list:
        raise HTTPException(status_code=404, detail="Liste introuvable")

    return db_list.contacts


# -------------------------------
# LINK LIST TO CONTACT
# -------------------------------


@router.post("/link-list-to-contact/")
async def add_list_to_contact(
    id_list: int, id_contact: int, session: AsyncSession = Depends(get_async_session)
):
    # 1. On charge la LISTE en premier, avec ses CONTACTS (important pour le Many-to-Many)
    statement = (
        select(ListContact)
        .where(ListContact.id == id_list)
        .options(selectinload(ListContact.contacts))  # type: ignore
    )
    result = await session.execute(statement)
    db_list = result.scalar_one_or_none()

    # 2. On récupère le CONTACT
    db_contact = await session.get(Contact, id_contact)

    # 3. Vérifications
    if not db_list or not db_contact:
        raise HTTPException(status_code=404, detail="Liste ou Contact introuvable")

    # 4. LOGIQUE INVERSÉE : On ajoute le contact à la liste
    if db_contact not in db_list.contacts:
        db_list.contacts.append(db_contact)  # On part de la liste vers le contact
        await session.commit()
        # Optionnel : rafraîchir pour être sûr que tout est à jour
        await session.refresh(db_list)
        return {
            "message": f"Le contact {db_contact.name} a été ajouté à la liste {db_list.list_name}"
        }

    return {"message": "Ce contact est déjà présent dans cette liste"}
