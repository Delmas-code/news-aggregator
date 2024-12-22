from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.source import Source
from ..schemas.source import SourceCreate, SourceUpdate


async def get_source(db: AsyncSession, source_id: int):
    result = await db.execute(select(Source).where(Source.id == source_id))
    return result.scalars().first()


async def get_sources(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Source).order_by(desc(Source.created_at)).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_filtered_sources(
    db: AsyncSession, field: str, value, skip: int = 0, limit: int = 10
):
    try:
        filter_column = getattr(Source, field)

        if field == "type":
            condition = filter_column == value
            stmt = (
                select(Source)
                .where(condition)
                .order_by(desc(Source.created_at))
                .offset(skip)
                .limit(limit)
            )
        else:
            condition = filter_column.like(f"%{value}%")
            stmt = (
                select(Source)
                .filter(condition)
                .order_by(desc(Source.created_at))
                .offset(skip)
                .limit(limit)
            )

        result = await db.execute(stmt)
        return True, result.scalars().all()

    except Exception as e:
        return False, e


async def get_sources_in_batch(db: AsyncSession, limit: int = 10):
    offset = 0
    while True:
        # Perform the fetch operation
        batch = await get_sources(db, skip=offset, limit=limit)

        if len(batch) == 0:
            break
        yield batch
        offset += limit


async def create_source(db: AsyncSession, source: SourceCreate):
    db_source = Source(**source.dict())
    db.add(db_source)
    await db.commit()
    return db_source


async def update_source(db: AsyncSession, source_id: int, source: SourceUpdate):
    db_source = await get_source(db, source_id)
    if db_source:
        for key, value in source.dict().items():
            setattr(db_source, key, value)
        await db.commit()

        return db_source
    else:
        raise Exception(f"source with id {id} not found")


async def delete_source(db: AsyncSession, source_id: int):
    db_source = await get_source(db, source_id)
    if db_source:
        await db.delete(db_source)
        await db.commit()

        return db_source
    else:
        raise Exception(f"source with id {id} not found")


async def delete_sources(db: AsyncSession):
    # Delete all sources
    stmt = select(Source)
    result = await db.execute(stmt)
    db_sources = result.scalars().all()
    
    for db_source in db_sources:
        await db.delete(db_source)
        
    await db.commit()
    return db_sources
