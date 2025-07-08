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
    LIM_DB_URL = os.getenv("LIM_DB_URL")

else:
    DATABASE_URL = os.getenv("DEV_DATABASE_URL")
    LIM_DB_URL = os.getenv("LIM_DB_URL")


# create sync and async engine with connection pooling
async_engine = create_async_engine(DATABASE_URL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW, echo=False)

# create an async session maker
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# create a lim sync and async engine with connection pooling
lim_async_engine = create_async_engine(LIM_DB_URL, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW, echo=False)

# create an async session maker for lim
lim_async_session = sessionmaker(lim_async_engine, class_=AsyncSession, expire_on_commit=False)


# add the db session creator
async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# initialize the database
database = Database(DATABASE_URL)
lim_database = Database(LIM_DB_URL)

Base = declarative_base()
LIM_Base = declarative_base()

# initialize database
async def init_db():
    """Initialize the database tables."""
    async with async_engine.begin() as conn:
       await conn.run_sync(Base.metadata.create_all)

# initialize LIM database
async def init_lim_db():
    """Initialize the database tables."""
    async with lim_async_engine.begin() as conn:
       await conn.run_sync(LIM_Base.metadata.create_all)


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


async def connect_to_lim_database():
    """Connect to the LIM database."""
    # initialize the database
    
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            await lim_database.connect()
            logger.info("LIM Database connection established")
            break
        except SQLAlchemyError as e:
            logger.error(f"Error connecting to LIM database: {e}")
            retry_count += 1
        except Exception as e:
            logger.error(f"Error connecting to LIM database: {e}")
            retry_count += 1
        raise DatabaseConnectionError(f"Failed to connect to LIM database after {retry_count} retries")

async def disconnect_from_lim_database():
    """Disconnect from the LIM database."""
    try:
        await lim_database.disconnect()
        logger.info("LIM Database connection closed")
    except Exception as e:
        logger.error(f"Error disconnecting from LIM database: {e}")
        raise DatabaseConnectionError("Failed to disconnect from LIM database")
