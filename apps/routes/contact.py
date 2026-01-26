from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from typing import List

from ..schema.contactList import contactlistRead
from ..util.contact import verified_email
from ..auth_app.config.database import get_async_session
from ..models.models import Contact, ListContact
from ..auth_app.service.authenticate import current_active_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from typing import List
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.models import Contact
from ..schema.contact import ContactRead, ContactCreate, ContactUpdate
from ..auth_app.service.authenticate import current_active_user


router = APIRouter(
    prefix="/contact", tags=["contact"], dependencies=[Depends(current_active_user)]
)


# -------------------------------
# CREATE CONTACT
# -------------------------------
@router.post("/", response_model=ContactRead)
async def create_contact(
    contact: ContactCreate, session: AsyncSession = Depends(get_async_session)
):
    if not verified_email(contact.email):
        raise HTTPException(status_code=400, detail="Invalid email format")

    db_list = await session.get(ListContact, contact.list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="ListContact not found")

    db_contact = Contact.model_validate(contact)
    session.add(db_contact)
    await session.commit()
    await session.refresh(db_contact)
    return db_contact


# -------------------------------
# READ LIST
# -------------------------------
@router.get(
    "/get_contact/",
    response_model=List[ContactRead],
)
async def read_contacts(
    session: AsyncSession = Depends(get_async_session),
    offset: int = 0,
    limit: int = Query(100, le=100),
):
    result = await session.execute(select(Contact).offset(offset).limit(limit))
    contact = result.scalars().all()
    return contact


# -------------------------------
# read LIST by id
# -------------------------------


@router.get("/contact/{contact_id}", response_model=ContactRead)
async def read_contact(
    contact_id: int, session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="contact not found")
    return contact


# -------------------------------
# ADD CONTACT TO LIST (async)
# -------------------------------
@router.post("/add-to-list")
async def add_contact_to_list(
    id_contact: int,
    id_list_contact: int,
    session: AsyncSession = Depends(get_async_session),
):
    # Logique asynchrone pour lier les deux

    result_contact = await session.execute(select(Contact).where(Contact.id == id_contact).options(selectinload(Contact.listes)))  # type: ignore
    db_contact = result_contact.scalar_one_or_none()

    result_list = await session.execute(select(ListContact).where(ListContact.id == id_list_contact).options(selectinload(ListContact.contacts)))  # type: ignore
    db_list = result_list.scalar_one_or_none()

    if not db_contact or not db_list:
        raise HTTPException(status_code=404, detail="Contact ou Liste introuvable")

    if db_list in db_contact.listes:
        return {"message": "Le contact est déjà dans cette liste"}
    # Si c'est une relation Many-to-Many
    db_contact.listes.append(db_list)
    await session.commit()
    return {"status": "success"}


# -------------------------------
# DELETE CONTACT
# -------------------------------


@router.delete("/delete_contact/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int, session: AsyncSession = Depends(get_async_session)
):
    # On récupère le contact
    db_contact = await session.get(Contact, contact_id)

    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact non trouvé")

    await session.delete(db_contact)
    await session.commit()
    return None


# -------------------------------
# UPDATE CONTACT
# -------------------------------
@router.patch("/update_contact/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    db_contact = await session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact non trouvé")

    # On transforme les données envoyées en dictionnaire, en excluant ce qui n'est pas rempli
    update_data = contact_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_contact, key, value)

    session.add(db_contact)
    await session.commit()
    await session.refresh(db_contact)
    return db_contact


# -------------------------------
# REMOVE CONTACT FROM LIST
# -------------------------------
@router.post("/remove_contact_from_list/")
async def remove_contact_from_list(
    id_contact: int,
    id_list_contact: int,
    session: AsyncSession = Depends(get_async_session),
):
    # On charge le contact avec ses listes (important pour l'asynchrone)*

    result = await session.execute(
        select(Contact)
        .where(Contact.id == id_contact)
        .options(selectinload(Contact.listes))  # type: ignore
    )
    db_contact = result.scalar_one_or_none()

    db_list = await session.get(ListContact, id_list_contact)

    if not db_contact or not db_list:
        raise HTTPException(status_code=404, detail="Contact ou Liste introuvable")

    # On retire la liste de la collection du contact
    if db_list in db_contact.listes:
        db_contact.listes.remove(db_list)
        await session.commit()
        return {"message": f"Contact retiré de la liste {db_list.list_name}"}

    return {"message": "Le contact n'était pas dans cette liste"}


# -------------------------------
# GET LISTS FOR A CONTACT
# -------------------------------


@router.get("/contact/{id_contact}/lists", response_model=List[contactlistRead])
async def get_lists_for_contact(
    id_contact: int, session: AsyncSession = Depends(get_async_session)
):
    # On récupère le contact en chargeant ses listes
    statement = select(Contact).where(Contact.id == id_contact).options(selectinload(Contact.listes))  # type: ignore
    result = await session.execute(statement)
    db_contact = result.scalar_one_or_none()

    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact introuvable")

    return db_contact.listes
