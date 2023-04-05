"""database.py"""

from os import getenv
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

load_dotenv()

POSTGRES = f"postgresql://{getenv('database')}?sslmode=require"
engine = create_engine(POSTGRES, echo=False)



def create_db_and_tables() -> None:
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)