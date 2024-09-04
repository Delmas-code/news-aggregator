from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.recognition import Recognition
from app.core.database import async_session
from ..schemas.recognition import RecognitionCreate, RecognitionUpdate
from loguru import logger

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_recognition(db: AsyncSession, recognition_id: int):
    result = await db.execute(select(Recognition).where(Recognition.id == recognition_id))
    return result.scalars().first()


async def get_recognitions(db: AsyncSession, skip: int=0, limit: int = 10):
    result = await db.execute(select(Recognition).offset(skip).limit(limit))    
    return result.scalars().all()
    

# Function to filter by given fields if 
async def get_filtered_recognitions(db: AsyncSession,  field: str, value , skip: int=0, limit: int = 10):
    try:
        filter_column = getattr(Recognition, field)
        
        if field == "type":
            condition = filter_column == value
            stmt = select(Recognition).where(condition).offset(skip).limit(limit)
        else:   
            condition = filter_column.like(f"%{value}%")
            stmt = select(Recognition).filter(condition).offset(skip).limit(limit)

        result = await db.execute(stmt)           
        return True, result.scalars().all()
    
    except Exception as e:
        return False, e
    

async def get_recognitions_in_batch(db: AsyncSession, limit: int = 10):
    try:
        offset = 0
        while True:
            # Perform the fetch operation
            status, batch = await get_recognitions(db, skip=offset, limit=limit)
            
            if not status or len(batch) == 0:
                break
            yield batch
            offset += limit

    except Exception as ex:
        logger.error(f"There is a recognition fetch error: {ex}") 

async def create_recognition(db: AsyncSession, recognition: RecognitionCreate):
    db_recognition = Recognition(**recognition.dict())
    db.add(db_recognition)
    await db.commit()
    await db.close()
    return db_recognition


async def update_recognition(db: AsyncSession, recognition_id: int, recognition: RecognitionUpdate):
    db_recognition = await get_recognition(db, recognition_id)
    if db_recognition:
        for key, value in recognition.dict().items():
            setattr(db_recognition, key, value) 
        await db.commit()
        await db.close()
        return db_recognition
    else:
        raise Exception(f"recognition with id {id} not found")


async def delete_recognition(db: AsyncSession, recognition_id: int):
    db_recognition = await get_recognition(db, recognition_id)
    if db_recognition:
        await db.delete(db_recognition)
        await db.commit()
        await db.close()
        return db_recognition
    else:
        raise Exception(f"recognition with id {id} not found")


async def delete_recognitions(db: AsyncSession):
    db_recognition = await get_recognitions(db)
    if db_recognition:
        await db.delete(db_recognition)
        await db.commit()
        await db.close()
        return db_recognition
    else:
        raise Exception(f"Error deleting all the recognitions")
