"""test_models_and_database.py"""

import unittest
from datetime import datetime, timezone
from sqlalchemy.future.engine import Engine
from sqlmodel import SQLModel, create_engine, Session
from db.models import User, Instrument, UserInstrumentLink
from db.crud import (get_user_by_email, update_user_instruments,
                     get_user_instruments, get_instrument_by_id,
                     delete_user_by_email, delete_orphaned_instruments)


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

        no_instrument = get_instrument_by_id(99, self.engine)
        self.assertFalse(no_instrument)

        instrument_1 = get_instrument_by_id(1, self.engine)
        self.assertTrue(instrument_1)

        if instrument_1:
            self.assertEqual(instrument_1.id, 1)
            self.assertEqual(instrument_1.make, "Ibanez")
            self.assertEqual(instrument_1.model, "RG470")
            self.assertIsInstance(instrument_1.date_created, datetime)

        john = get_user_by_email(self.john_email, self.engine)
        david = get_user_by_email(self.david_email, self.engine)
        self.assertTrue(john)
        self.assertTrue(david)

        if john:
            john_instruments = get_user_instruments(john, self.engine)
            if john_instruments:
                john_instruments.sort(key=lambda x: x.make)
                self.assertEqual(john_instruments[0].make, "Gibson")
                self.assertEqual(john_instruments[1].make, "Ibanez")

        if david:
            david_instruments = get_user_instruments(david, self.engine)
            self.assertEqual(david_instruments[0].make, "Ibanez")

    def test_update_database(self) -> None:
        """Test updating the database."""
        _ = _create_data(self.engine)

        ceo_10 = Instrument(
            type="acoustic_guitar",
            make="Martin",
            model="CEO-10",
            date_created=datetime.now(timezone.utc),
        )

        david = get_user_by_email(self.david_email, self.engine)
        self.assertTrue(david)

        if david:
            update_user_instruments(david, ceo_10, self.engine)
            david_instruments = get_user_instruments(david, self.engine)
            self.assertEqual(david_instruments[1].make, "Martin")

    def test_delete_user(self) -> None:
        """Test deleting user from the database."""
        _ = _create_data(self.engine)

        delete_user_by_email(self.david_email, self.engine)
        delete_user_by_email(self.john_email, self.engine)
        delete_orphaned_instruments(self.engine)

        with Session(self.engine) as session:
            user_count = session.query(User).count()
            instrument_count = session.query(Instrument).count()
            link_count = session.query(UserInstrumentLink).count()
            self.assertEqual(user_count, 0)
            self.assertEqual(instrument_count, 0)
            self.assertEqual(link_count, 0)
