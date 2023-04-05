"""database.py"""

from sqlmodel import SQLModel, create_engine

SQLITE_FILE_NAME = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(SQLITE_URL, echo=False)


def create_db_and_tables() -> None:
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)
