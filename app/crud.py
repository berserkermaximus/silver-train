from .database import get_session
from fastapi import Depends
from .model import Contact
from .schema import Identity, Identify, Input
from fastapi.exceptions import HTTPException
from sqlalchemy import or_, text, update
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import now
from typing import List


async def identify(data: Input, session: Session = Depends(get_session)):
    email = data.email
    phoneNumber = str(data.phoneNumber) if data.phoneNumber else None
    print(email, phoneNumber)

    # checking if the email and phoneNumber are both not null.
    if email is None and phoneNumber is None:
        raise HTTPException(400, "email and phoneNumber both cannot be null.")

    # getting all the linkable contact where the email or phonenumber matches.
    linked_contact = session.query(Contact).filter(
        or_(Contact.email == email, Contact.phoneNumber == phoneNumber)).order_by(Contact.createdAt).all()

    # get the primary id of the group the contact is in.
    primary_id = check_exact_row(email, phoneNumber, linked_contact, session)

    # fetching the rows with the primary id.
    required_rows = session.query(Contact).filter(
        or_(Contact.id == primary_id, Contact.linkedId == primary_id)).order_by(Contact.createdAt).all()

    # molding the answer into Identity schema
    contact = Identity(primaryContatctId=required_rows[0].id, emails=[
                       i.email for i in required_rows], phoneNumbers=[i.phoneNumber for i in required_rows], secondaryContactIds=[i.id for i in required_rows[1:]])

    return Identify(contact=contact)


async def delete_all(session: Session = Depends(get_session)):
    # deleting all rows and resetting the autoincrement sequence for id column.
    session.query(Contact).delete()
    session.execute(text("ALTER SEQUENCE contact_id_seq RESTART WITH 1"))
    session.commit()
    return {"success": True}


def check_exact_row(email: str, phoneNumber: str, linked_contact: List[Contact], session: Session = Depends(get_session)):
    # fetching the exact row.
    exact_row = session.query(Contact).filter(Contact.email == email).filter(
        Contact.phoneNumber == phoneNumber).first()
    if not exact_row:
        if linked_contact == []:
            # if there are no linked contacts, the new contact is a primary one.
            row = Contact(email=email, phoneNumber=phoneNumber,
                          linkPrecedence='primary')
            session.add(row)
            session.commit()
            exact_row = session.query(Contact).filter(Contact.email == email).filter(
                Contact.phoneNumber == phoneNumber).first()
            return exact_row.id
        else:
            # aggregating for related primary or secondary ids.
            distinct_linked_id = [
                i.linkedId if i.linkedId is not None else i.id for i in linked_contact]
            distinct_linked_id = tuple(set(distinct_linked_id))

            # fetching the primary for all the distinct ids.
            primary_contacts = session.query(Contact).filter(
                Contact.id.in_(distinct_linked_id)).order_by(Contact.createdAt).all()

            # linking the cntact to the oldest primary contact.
            primary_contact = primary_contacts[0]
            row = Contact(email=email, phoneNumber=phoneNumber,
                          linkPrecedence='secondary', linkedId=primary_contact.id)
            session.add(row)
            session.commit()

            # as we have a primary contact, we have to updated other primaries and their secondary
            # to have the primary contact this one.
            other_ids = tuple([i.id for i in primary_contacts[1:]])
            stmt = (
                update(Contact).
                where(or_(Contact.id.in_(other_ids), Contact.linkedId.in_(other_ids))).
                values(linkedId=primary_contact.id,
                       linkPrecedence='secondary', updatedAt=now())
            )
            session.execute(stmt)
            session.commit()

            return primary_contact.id
    else:
        # if present, return its primary id or its id if it is primary.
        return exact_row.linkedId if exact_row.linkedId is not None else exact_row.id
