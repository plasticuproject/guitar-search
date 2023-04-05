"""test_database.py"""

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
        sqlite_file_name = ":memory:"
        sqlite_url = f"sqlite:///{sqlite_file_name}"
        self.engine = create_engine(sqlite_url)
        SQLModel.metadata.create_all(self.engine)

    def tearDown(self) -> None:
        pass

    def test_user_model(self) -> None:
        """Test User model."""

        user_1 = _create_data(self.engine)
        self.assertEqual(user_1.id, 1)
        self.assertEqual(user_1.email, "david@test.com")
        self.assertTrue(user_1.active)
        self.assertIsInstance(user_1.date_created, datetime)

    def test_read_data_and_instrument_model(self) -> None:
        """Test the Instrument model and reading from
        database."""
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
                           .where(User.email == "john@test.com"))
            john = list(session.exec(statement_2))
            self.assertEqual(john[0].make, "Ibanez")
            self.assertEqual(john[1].make, "Gibson")

            statement_3 = (select(Instrument)
                           .join(UserInstrumentLink)
                           .join(User)
                           .where(User.email == "david@test.com"))
            david = list(session.exec(statement_3))
            self.assertEqual(david[0].make, "Ibanez")

# TODO: Test other CRUD methods
