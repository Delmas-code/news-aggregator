import os, sys
current_dir = os.getcwd()
sys.path.append(current_dir)

from app.crud import source as source_crud
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.crud.content import create_content 
from loguru import logger
from app.schemas.content import ContentCreate

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_sources_in_batch(limit: int = 10, field="type", value="RSS"):
    try:
        offset = 0
        async for db_session in get_db():
            while True:
                # Perform the fetch operation
                status, batch = await source_crud.get_sources(db_session, skip=offset, limit=limit, field=field, value=value)

                if not status or len(batch) == 0:
                    break

                yield batch
                offset += limit

    except Exception as ex:
        logger.error(f"There is an error: {ex}") 

async def create_item(item : ContentCreate):
    try:
        async for db_session in get_db():
            created_item = await create_content(db_session, item)
            return created_item
    
    except Exception as ex:
        logger.error(f"There is an error: {ex}") 

