import os, sys
current_dir = os.getcwd()
sys.path.append(current_dir)

from app.crud import source as source_crud
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.crud import content as content_crud
from loguru import logger
from app.schemas.content import ContentCreate

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session



