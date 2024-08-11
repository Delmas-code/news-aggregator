from ....crud import source as source_crud
from sqlalchemy.ext.asyncio import AsyncSession
from ....core.database import async_session

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
        raise Exception(ex)