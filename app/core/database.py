from dotenv import load_dotenv
from databases import Database
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)


class DatabaseConnectionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


async def connect_to_database():
    try:
        await database.connect()
    except SQLAlchemyError as e:
        raise DatabaseConnectionError(f"SQLAlchemy error: {e}")
    except Exception as e:
        raise DatabaseConnectionError(f"General error: {e}")


async def disconnect_from_database():
    await database.disconnect()
