from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from sqlalchemy import or_, and_, extract, select, func
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas.contacts import ContactModel
from static.colors import GRAY, RESET
from typing import List


async def create_contact(contact: ContactModel, user: User, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def read_contacts(db: Session = Depends(get_db), q: str = "", user = User):
    if q:
        return (
            db.query(Contact)
            .filter(
                and_(
                or_(
                    Contact.first_name.ilike(f"%{q}%"),
                    Contact.last_name.ilike(f"%{q}%"),
                    Contact.email.ilike(f"%{q}%"),
                ),
                Contact.user_id == user.id

            ))
            .all()
        )

    return db.query(Contact).filter(Contact.user_id == user.id).all()


async def find_contact(contact_id: int, user: User, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact is None:
        raise HTTPException(
            status_code=404, detail=f"Contact with id: {contact_id} was not found"
        )
    return contact


async def update_contact(contact_id: int, user: User, body: ContactModel, db: Session):
    contact = (
        db.query(Contact)
        .filter(and_(Contact.user_id == user.id,  Contact.id == contact_id))
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=404, detail=f"Contact with id: {contact_id} was not found"
        )

    if contact:
        for key, value in body.model_dump().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, user: User, db: Session = Depends(get_db)):
    db_contact = (
        db.query(Contact)
        .filter(and_(Contact.user_id == user.id, Contact.id == contact_id))
        .first()
    )
    if db_contact is None:
        raise HTTPException(
            status_code=404, detail=f"Contact with id: {contact_id} was not found"
        )
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact successfully deleted"}


async def next_week_birthdays(user: User, db: Session = Depends(get_db), days_range: int = 7):

    today = datetime.today().date()
    start_period = today.strftime("%m-%d")
    end_period = (today + timedelta(days_range)).strftime("%m-%d")
    # print(f"{start_period = }")
    # print(f"  {end_period = }")

    statement = (
        select(Contact)
        .filter_by(user=user)
        .filter(
            func.to_char(Contact.birthday, "MM-DD").between(start_period, end_period)
        )
    )
    contacts = db.execute(statement)
    return contacts.scalars().all()


async def get_week_birthdays(user: User, db: Session = Depends(get_db), days_=7):
    
    def debug_print():
        print(GRAY, end="")
        print(f"from {RESET}{today_.strftime("%Y-%m-%d")}{GRAY}")
        print(f"till {RESET}{end_date.strftime("%Y-%m-%d")}{GRAY}")
        if result == []:
            print(f"     there are no contacts whose birthday is in the next {days_} days")
        else:
            print("     ----------")
            num = 1
            for r in result:
                print(f"{"  " if num < 10 else " "}{num}. {RESET}{r.birthday}{GRAY}", end=" -> ")
                blank = " " * (3 - len(str(r.id)))
                print(f"id = {blank}{r.id}, {r.first_name } {r.last_name}")
                num += 1
        print(RESET)

    today_ = datetime.today().date()
    # today_ = datetime(year=2023, month=12, day=30) # debugging
    end_date = today_ + timedelta(days=days_)

    result = (
        db.query(Contact)
        .filter(
            or_(
                and_(
                    extract("day", Contact.birthday) >= today_.day,
                    extract("month", Contact.birthday) == today_.month,
                    Contact.user_id == user.id,
                ),
                and_(
                    extract("day", Contact.birthday) <= end_date.day,
                    extract("month", Contact.birthday) == end_date.month,
                    Contact.user_id == user.id,
                ),
            )
        )
        .all()
    )
    debug_print() # debugging
    return result
