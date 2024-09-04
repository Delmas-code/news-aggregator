from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.tag import Tag
from app.core.database import async_session
from ..schemas.tag import TagCreate, TagUpdate
from loguru import logger

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_tag(db: AsyncSession, tag_id: int):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    return result.scalars().first()


async def get_tags(db: AsyncSession, skip: int=0, limit: int = 10):
    result = await db.execute(select(Tag).offset(skip).limit(limit))    
    return result.scalars().all()
    

# Function to filter by given fields
async def get_filtered_tags(db: AsyncSession,  field: str, value , skip: int=0, limit: int = 10):
    try:
        filter_column = getattr(Tag, field)
        
        if field == "type":
            condition = filter_column == value
            stmt = select(Tag).where(condition).offset(skip).limit(limit)
        else:   
            condition = filter_column.like(f"%{value}%")
            stmt = select(Tag).filter(condition).offset(skip).limit(limit)

        result = await db.execute(stmt)           
        return True, result.scalars().all()
    
    except Exception as e:
        return False, e
    

async def get_tags_in_batch(db: AsyncSession, limit: int = 10):
    try:
        offset = 0
        while True:
            # Perform the fetch operation
            status, batch = await get_tags(db, skip=offset, limit=limit)
            
            if not status or len(batch) == 0:
                break
            yield batch
            offset += limit

    except Exception as ex:
        logger.error(f"There is a tag fetch error: {ex}") 

async def create_tag(db: AsyncSession, tag: TagCreate):
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    await db.commit()
    await db.close()
    return db_tag


async def update_tag(db: AsyncSession, tag_id: int, tag: TagUpdate):
    db_tag = await get_tag(db, tag_id)
    if db_tag:
        for key, value in tag.dict().items():
            setattr(db_tag, key, value) 
        await db.commit()
        await db.close()
        return db_tag
    else:
        raise Exception(f"tag with id {id} not found")


async def delete_tag(db: AsyncSession, tag_id: int):
    db_tag = await get_tag(db, tag_id)
    if db_tag:
        await db.delete(db_tag)
        await db.commit()
        await db.close()
        return db_tag
    else:
        raise Exception(f"tag with id {id} not found")


async def delete_tags(db: AsyncSession):
    db_tag = await get_tags(db)
    if db_tag:
        await db.delete(db_tag)
        await db.commit()
        await db.close()
        return db_tag
    else:
        raise Exception(f"Error deleting all the tags")
