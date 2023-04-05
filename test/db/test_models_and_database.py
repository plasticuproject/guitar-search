"""test_models_and_database.py"""

import unittest
from datetime import datetime, timezone
from sqlalchemy.future.engine import Engine
from sqlmodel import SQLModel, create_engine, Session, select
from db.models import User, Instrument, UserInstrumentLink


def _create_data(engine: Engine) -> User:
    """Helper function to create database tables
    and populate them with test data."""
    with Session(engine) as session:
        instrument_1 = Instrument(
            type="electric_guitar",
            make="Ibanez",
            model="RG470",
            date_created=datetime.now(timezone.utc),
        )

        instrument_2 = Instrument(
            type="electric_guitar",
            make="Gibson",
            model="Les Paul",
            date_created=datetime.now(timezone.utc),
        )

        user_1 = User(
            email="david@test.com",
            active=True,
            date_created=datetime.now(timezone.utc),
            instruments=[instrument_1],
        )

        user_2 = User(
            email="john@test.com",
            active=True,
            date_created=datetime.now(timezone.utc),
            instruments=[instrument_1, instrument_2],
        )
        session.add(user_1)
        session.add(user_2)
        session.commit()

        session.refresh(user_1)
        session.refresh(user_2)

    return user_1


class ModelsAndDatabaseTests(unittest.TestCase):
    """Test database models."""

    def setUp(self) -> None:
        """Set up sqlite database for testing."""
        self.david_email = "david@test.com"
        self.john_email = "john@test.com"

        sqlite_file_name = ":memory:"
        sqlite_url = f"sqlite:///{sqlite_file_name}"
        self.engine = create_engine(sqlite_url)
        SQLModel.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        """Deconstruct the test fixture
        after testing it."""

    def test_user_model(self) -> None:
        """Test User model."""
        user_1 = _create_data(self.engine)
        self.assertEqual(user_1.id, 1)
        self.assertEqual(user_1.email, self.david_email)
        self.assertTrue(user_1.active)
        self.assertIsInstance(user_1.date_created, datetime)

    def test_read_database(self) -> None:
        """Test reading data from the database."""
        _ = _create_data(self.engine)
        with Session(self.engine) as session:
            statement_1 = select(Instrument).where(Instrument.id == 1)
            result_1 = session.exec(statement_1)
            instrument_1 = result_1.one()
            self.assertEqual(instrument_1.id, 1)
            self.assertEqual(instrument_1.make, "Ibanez")
            self.assertEqual(instrument_1.model, "RG470")
            self.assertIsInstance(instrument_1.date_created, datetime)

            statement_2 = (select(Instrument)
                           .join(UserInstrumentLink)
                           .join(User)
                           .where(User.email == self.john_email and
                                  User.active))
            john = list(session.exec(statement_2))
            self.assertEqual(john[0].make, "Ibanez")
            self.assertEqual(john[1].make, "Gibson")

            statement_3 = (select(Instrument)
                           .join(UserInstrumentLink)
                           .join(User)
                           .where(User.email == self.david_email and
                                  User.active))
            david = list(session.exec(statement_3))
            self.assertEqual(david[0].make, "Ibanez")

    def test_update_database(self) -> None:
        """Test updating the database."""
        _ = _create_data(self.engine)
        with Session(self.engine) as session:
            ceo_10 = Instrument(
                type="acoustic_guitar",
                make="Martin",
                model="CEO-10",
                date_created=datetime.now(timezone.utc),
            )

            statement_1 = select(User).where(User.email == self.david_email)
            david = session.exec(statement_1).first()
            if david:
                session.add(ceo_10)
                session.commit()
                link = UserInstrumentLink(user_id=david.id,
                                          instrument_id=ceo_10.id)
                session.add(link)
                session.commit()

            statement_2 = (select(Instrument)
                           .join(UserInstrumentLink)
                           .join(User)
                           .where(User.email == self.david_email and
                                  User.active))
            new_david = list(session.exec(statement_2))
            self.assertEqual(new_david[1].make, "Martin")

    def test_delete_user(self) -> None:
        """Test deleting user from the database."""
        _ = _create_data(self.engine)
        with Session(self.engine) as session:
            statement_1 = select(User).where(User.email == self.david_email)
            david = session.exec(statement_1).first()
            session.delete(david)
            statement_2 = select(User).where(User.email == self.john_email)
            john = session.exec(statement_2).first()
            session.delete(john)
            session.commit()

            orphan_instrument_ids = (session.query(Instrument.id)
                                     .filter(Instrument.users is not None)
                                     .all()
                                     )
            for instrument_id in orphan_instrument_ids:
                instrument = session.get(Instrument, instrument_id[0])
                session.delete(instrument)
            session.commit()

            user_count = session.query(User).count()
            instrument_count = session.query(Instrument).count()
            link_count = session.query(UserInstrumentLink).count()
            self.assertEqual(user_count, 0)
            self.assertEqual(instrument_count, 0)
            self.assertEqual(link_count, 0)
