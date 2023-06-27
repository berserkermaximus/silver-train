from .database import get_session
from fastapi import Depends
from .model import Contact
from .schema import Identity, Identify, Input
from fastapi.exceptions import HTTPException
from sqlalchemy import or_, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import now


async def identify(data: Input, session: Session = Depends(get_session)):
    email = data.email
    phoneNumber = str(data.phoneNumber) if data.phoneNumber else None
    if email is None and phoneNumber is None:
        raise HTTPException(405, "email and phoneNumber both cannot be null.")

    exact_row = session.query(Contact).filter(Contact.email == email).filter(
        Contact.phoneNumber == phoneNumber).first()

    if not exact_row:
        row = Contact(email=email, phoneNumber=phoneNumber,
                      linkPrecedence='primary')
        session.add(row)
        session.commit()
    if exact_row.deletedAt is not None:
        exact_row.deletedAt = None
        exact_row.updatedAt = now()
        session.commit()

    exact_row = session.query(Contact).filter(Contact.email == email).filter(
        Contact.phoneNumber == phoneNumber).first()

    contact = Identity(primaryContatctId=exact_row.id, emails=[
                       exact_row.email], phoneNumbers=[exact_row.phoneNumber], secondaryContactIds=[])

    return Identify(contact=contact)


async def delete(data: Input, session: Session = Depends(get_session)):
    email = data.email
    phoneNumber = str(data.phoneNumber) if data.phoneNumber else None
    row = session.query(Contact).filter(Contact.email == email).filter(
        Contact.phoneNumber == phoneNumber).first()
    if row is None:
        raise HTTPException(404, "could not find the contact")
    else:
        row.deletedAt = now()
        session.commit()
        return {"success": True}


async def delete_all(session: Session = Depends(get_session)):
    session.query(Contact).delete()
    session.execute(text("ALTER SEQUENCE contact_id_seq RESTART WITH 1"))
    session.commit()
    return {"success": True}
