"""models.py"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class UserInstrumentLink(SQLModel, table=True):
    """Link table for many-to-many user/instrument
    relationships."""
    instrument_id: Optional[int] = Field(
        default=None, foreign_key="instrument.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )


class Instrument(SQLModel, table=True):
    """Instrument table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    make: str
    model: str
    date_created: datetime
    users: List["User"] = Relationship(back_populates="instruments",
                                       link_model=UserInstrumentLink)


class User(SQLModel, table=True):
    """User table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    active: bool
    date_created: datetime
    instruments: Optional[Instrument] = Relationship(
        back_populates="users",
        link_model=UserInstrumentLink
    )
