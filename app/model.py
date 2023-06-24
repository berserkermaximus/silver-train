from .database import Base
from sqlalchemy import Column, String, Integer, Enum, DateTime
from sqlalchemy.sql.functions import now
from .schema import Precedence


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, autoincrement="auto",
                nullable=False, primary_key=True)
    email = Column(String, nullable=True)
    phoneNumber = Column(String, nullable=True)
    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(Enum(Precedence), nullable=False)
    createdAt = Column(DateTime, nullable=False, default=now())
    updatedAt = Column(DateTime, nullable=False, default=now())
    deletedAt = Column(DateTime, nullable=True)

    class Config:
        orm_mode = True
