from dotenv import load_dotenv
from databases import Database

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

import os
import logging

load_dotenv()

# configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 5
POOL_SIZE = 20
MAX_OVERFLOW = 10

if os.getenv("PRODUCTION") == "TRUE":
    DATABASE_URL = os.getenv("PROD_DATABASE_URL")
else:
    DATABASE_URL = os.getenv("DEV_DATABASE_URL")


# create sync and async engine with connection pooling
async_engine = create_async_engine(DATABASE_URL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW, echo=False)

# create an async session maker
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# initialize the database
database = Database(DATABASE_URL)

Base = declarative_base()

# initialize database
async def init_db():
    """Initialize the database tables."""
    async with async_engine.begin() as conn:
       await conn.run_sync(Base.metadata.create_all)

class DatabaseConnectionError(Exception):
    """Database connection error."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

async def connect_to_database():
    """Connect to the database."""
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            await database.connect()
            logger.info("Database connection established")
            break
        except SQLAlchemyError as e:
            logger.error(f"Error connecting to database: {e}")
            retry_count += 1
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            retry_count += 1
        raise DatabaseConnectionError("Failed to connect to database after retries")

async def disconnect_from_database():
    """Disconnect from the database."""
    try:
        await database.disconnect()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}")
        raise DatabaseConnectionError("Failed to disconnect from database")
