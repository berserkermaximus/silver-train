from pydantic import BaseModel
from typing import List, Any
from datetime import datetime
import enum


class Precedence(str, enum.Enum):
    primary = "primary"
    secondary = "secondary"


class Input(BaseModel):
    email: str = None
    phoneNumber: int = None


class Contact(BaseModel):
    id: int
    phoneNumber: str
    email: str
    linkedId: int
    linkPrecedence: Precedence
    createdAt: datetime
    updatedAt: datetime
    deletedAt: datetime = None


class Identity(BaseModel):
    primaryContatctId: int
    emails: List[Any]
    phoneNumbers: List[Any]
    secondaryContactIds: List[int] = None


class Identify(BaseModel):
    contact: Identity
