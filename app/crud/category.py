from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.category import Category
from app.core.database import async_session
from ..schemas.category import CategoryCreate, CategoryUpdate
from loguru import logger

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_category(db: AsyncSession, category_id: int):
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalars().first()


async def get_categories(db: AsyncSession, skip: int=0, limit: int = 10):
    result = await db.execute(select(Category).offset(skip).limit(limit))    
    return result.scalars().all()
    

# Function to filter by given fields
async def get_filtered_categories(db: AsyncSession,  field: str, value , skip: int=0, limit: int = 10):
    try:
        filter_column = getattr(Category, field)
        
        if field == "type":
            condition = filter_column == value
            stmt = select(Category).where(condition).offset(skip).limit(limit)
        else:   
            condition = filter_column.like(f"%{value}%")
            stmt = select(Category).filter(condition).offset(skip).limit(limit)

        result = await db.execute(stmt)           
        return True, result.scalars().all()
    
    except Exception as e:
        return False, e
    

async def get_categories_in_batch(db: AsyncSession, limit: int = 10):
    try:
        offset = 0
        while True:
            # Perform the fetch operation
            status, batch = await get_categories(db, skip=offset, limit=limit)
            
            if not status or len(batch) == 0:
                break
            yield batch
            offset += limit

    except Exception as ex:
        logger.error(f"There is a category fetch error: {ex}") 

async def create_category(db: AsyncSession, category: CategoryCreate):
    db_category = Category(**category.dict())
    db.add(db_category)
    await db.commit()
    await db.close()
    return db_category


async def update_category(db: AsyncSession, category_id: int, category: CategoryUpdate):
    db_category = await get_category(db, category_id)
    if db_category:
        for key, value in category.dict().items():
            setattr(db_category, key, value) 
        await db.commit()
        await db.close()
        return db_category
    else:
        raise Exception(f"category with id {id} not found")


async def delete_category(db: AsyncSession, category_id: int):
    db_category = await get_category(db, category_id)
    if db_category:
        await db.delete(db_category)
        await db.commit()
        await db.close()
        return db_category
    else:
        raise Exception(f"category with id {id} not found")


async def delete_categories(db: AsyncSession):
    db_category = await get_categories(db)
    if db_category:
        await db.delete(db_category)
        await db.commit()
        await db.close()
        return db_category
    else:
        raise Exception(f"Error deleting all the categories")
