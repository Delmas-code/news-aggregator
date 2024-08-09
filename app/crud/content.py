from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.content import Content
from ..schemas.content import ContentCreate, ContentUpdate

async def get_content(db: AsyncSession, content_id: int):
    result = await db.execute(select(Content).where(Content.id == content_id))
    return result.scalars().first()


# modify to filter by given fields if any
async def get_contents(db: AsyncSession, skip: int=2, limit: int =1, field : str = None, value: str = None):
    try:
        if field:
            if field == "type":
                stmt = select(Content).where(getattr(Content, field) == value)
            else:
                stmt = select(Content).where(getattr(Content, field) == value.lower())
            result = await db.execute(stmt)
        else:  
            result = await db.execute(select(Content).offset(skip).limit(limit))
            print("\n\nThis is where i am\n\n")
        
        print(f"\n\n {result.scalars().all()}\n\n") 
        return True, result.scalars().all()
    
    except Exception as e:
        return False, e


async def create_content(db: AsyncSession, content: ContentCreate):
    print(f"\n\n{content}\n\n")
    db_content = Content(**content.dict())
    print(db_content)
    # db.add(db_content)
    # await db.commit()
    # await db.close()
    # return db_content


async def update_content(db: AsyncSession, content_id: int, content: ContentUpdate):
    db_content = await get_content(db, content_id)
    if db_content:
        for key, value in Content.dict().items():
            setattr(db_content, key, value) 
        await db.commit()
        await db.close()
        return db_content
    else:
        raise Exception(f"content with id {id} not found")


async def delete_content(db: AsyncSession, content_id: int):
    db_content = await get_content(db, content_id)
    if db_content:
        await db.delete(db_content)
        await db.commit()
        await db.close()
        return db_content
    else:
        raise Exception(f"content with id {id} not found")


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
    
