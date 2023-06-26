from .database import Base
from sqlalchemy import Column, String, Integer, Enum, DateTime, Constraint, ForeignKeyConstraint, Index
from sqlalchemy.sql.functions import now
from .schema import Precedence
from .database import engine


class Contact(Base):
    __tablename__ = "contact"
    # adding columns
    id = Column(Integer, autoincrement="auto",
                nullable=False, primary_key=True)
    email = Column(String, nullable=True)
    phoneNumber = Column(String, nullable=True)
    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(Enum(Precedence), nullable=False)
    createdAt = Column(DateTime, nullable=False, default=now())
    updatedAt = Column(DateTime, nullable=False, default=now())
    deletedAt = Column(DateTime, nullable=True)

    # adding constraints

    # both email and phoneNumber cannot be null
    Constraint("contact_phoneNumber_email_not_null",
               comment="phoneNumber is not NULL or email is not NULL")

    # linkedId is a foreignkey from id
    ForeignKeyConstraint(name="contact_linkedid_fkey",
                         columns=[linkedId], refcolumns=[id])

    # creating unique index on phoneNumber and email
    Index("contact_phoneNumber_email_idx", phoneNumber, email, unique=True)

    class Config:
        orm_mode = True


if __name__ == '__main__':
    Contact.__table__.drop(engine)
    Base.metadata.create_all(engine)
