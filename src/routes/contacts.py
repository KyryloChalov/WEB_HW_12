from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contacts import ContactModel, ContactResponse
from src.services.auth import auth_service
from typing import List

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return await repository_contacts.create_contact(contact, current_user, db)


# всі контакти без зайвих питань - чи воно треба?
# @router.get("/", response_model=List[ContactResponse])
# async def read_all_contacts(db: Session = Depends(get_db)):
#     contacts = await repository_contacts.read_contacts(db)
#     return contacts


# пошук рядка find_string в полях first_name, last_name, email
# якшо рядок пошуку порожній - виводяться всі контакти
@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    db: Session = Depends(get_db),
    find_string: str = "",
    current_user: User = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.read_contacts(db, find_string, current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def find_contact_id(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.find_contact(contact_id, current_user, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.update_contact(
        contact_id, current_user, contact, db
    )
    return contact


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_week_birthdays(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contacts = await repository_contacts.get_week_birthdays(current_user, db)
    return contacts


@router.get("/birthdays_/", response_model=List[ContactResponse])
async def next_week_birthdays(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contacts = await repository_contacts.next_week_birthdays(current_user, db)
    return contacts
