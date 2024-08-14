from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.content import Content
from ..schemas.content import ContentCreate, ContentUpdate
from sqlalchemy import func

async def get_content(db: AsyncSession, content_id: int):
    result = await db.execute(select(Content).where(Content.id == content_id))
    return result.scalars().first()

# modify to filter by given fields and values, if any

async def get_contents(db: AsyncSession, skip: int = 0, limit: int =10, field : str = None, value: str = None):
    try:
        if field and value:
            value = int(value) if field == "source_id" else value
            if field == "type" or field == "source_id":
                stmt = select(Content).where(getattr(Content, field) == value).limit(limit).offset(skip)
            else:
                stmt = select(Content).where(getattr(Content, field) == value.lower()).offset(skip).limit(limit)
            result = await db.execute(stmt)
        else:  
            result = await db.execute(select(Content).offset(skip).limit(limit))
        
        result = result.scalars().all()
        return True, result
    
    except Exception as e:
        return False, e


"""Get a column, adding this for the ids"""
async def get_content_by_column(db: AsyncSession, field, limit: int = None, skip : int = 0, cond_field = None, cond_value = None):
    if cond_field and cond_value:
        stmt = select(getattr(Content, field)).where(getattr(Content, cond_field) == cond_value).offset(skip).limit(limit)   
    else:
        stmt = select(getattr(Content, field)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    
    return result.scalars().all()

async def create_content(db: AsyncSession, content: ContentCreate):
    db_content = Content(**content.dict())
    db.add(db_content)
    await db.commit()
    await db.close()

    return db_content

async def update_content(db: AsyncSession, content_id: str, content: ContentUpdate):
    db_content = await get_content(db, content_id)
    if db_content:
        for key, value in Content.dict().items():
            setattr(db_content, key, value) 
        await db.commit()
        await db.close()
        return db_content
    else:
        raise Exception(f"content with id {id} not found")

async def delete_content(db: AsyncSession, content_id: str):
    db_content = await get_content(db, content_id)
    if db_content:
        await db.delete(db_content)
        await db.commit()
        await db.close()
        return db_content
    else:
        raise Exception(f"content with id {content_id} not found")

async def delete_contents(db: AsyncSession):
    db_contents = await get_contents(db)

    try:
        if db_contents:
            await db.delete(db_contents)
            await db.commit()
            await db.close()
            return db_contents
        else:
            raise Exception("No contents found")
        
    except Exception as e:
        raise Exception(e)
    
