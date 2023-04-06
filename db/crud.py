"""crud.py"""

from typing import Optional, List
from sqlalchemy.future.engine import Engine
from sqlmodel import Session, select
from db.models import User, Instrument, UserInstrumentLink


def get_user_by_email(email_address: str,
                      engine: Engine) -> Optional[User]:
    """Get User object by email address."""
    with Session(engine) as session:
        stmt = select(User).where(User.email == email_address)
        user = session.exec(stmt).first()

    return user


def get_instrument_by_id(instrument_id: int,
                         engine: Engine) -> Optional[Instrument]:
    """Get Instrument object by id."""
    with Session(engine) as session:
        stmt = select(Instrument).where(Instrument.id == instrument_id)
        instrument = session.exec(stmt).first()

    if instrument:
        return instrument
    return None


def update_user_instruments(user: User,
                            instrument: Instrument,
                            engine: Engine) -> None:
    """Update a Users instruments."""
    with Session(engine) as session:
        session.add(instrument)
        session.commit()
        link = UserInstrumentLink(user_id=user.id, instrument_id=instrument.id)
        session.add(link)
        session.commit()


def get_user_instruments(user: User,
                         engine: Engine) -> List[Instrument]:
    """Get a Users Instrument Objects."""
    with Session(engine) as session:
        stmt = (select(Instrument)
                .join(UserInstrumentLink)
                .join(User)
                .where(User.id == user.id))
        instruments = list(session.exec(stmt))

    return instruments


def delete_user_by_email(email: str,
                         engine: Engine) -> None:
    """Delete a User using their email addres."""
    with Session(engine) as session:
        user = get_user_by_email(email, engine)
        session.delete(user)
        session.commit()


def delete_orphaned_instruments(engine: Engine) -> None:
    """Delete all orphaned Instruments from database."""
    with Session(engine) as session:
        orphan_instrument_ids = (session.query(Instrument.id)
                                 .filter(Instrument.users is not None)
                                 .all()
                                 )
        for instrument_id in orphan_instrument_ids:
            instrument = session.get(Instrument, instrument_id[0])
            session.delete(instrument)
        session.commit()
