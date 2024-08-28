from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.transcription import Transcription
from app.core.database import async_session
from ..schemas.transcription import TranscriptionCreate, TranscriptionUpdate
from loguru import logger

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_transcription(db: AsyncSession, transcription_id: int):
    result = await db.execute(select(Transcription).where(Transcription.id == transcription_id))
    return result.scalars().first()


async def get_transcriptions(db: AsyncSession, skip: int=0, limit: int = 10):
    result = await db.execute(select(Transcription).offset(skip).limit(limit))    
    return result.scalars().all()
    

# Function to filter by given fields if 
async def get_filtered_transcriptions(db: AsyncSession,  field: str, value , skip: int=0, limit: int = 10):
    try:
        filter_column = getattr(Transcription, field)
        
        if field == "type":
            condition = filter_column == value
            stmt = select(Transcription).where(condition).offset(skip).limit(limit)
        else:   
            condition = filter_column.like(f"%{value}%")
            stmt = select(Transcription).filter(condition).offset(skip).limit(limit)

        result = await db.execute(stmt)           
        return True, result.scalars().all()
    
    except Exception as e:
        return False, e
    

async def get_transcriptions_in_batch(db: AsyncSession, limit: int = 10):
    try:
        offset = 0
        while True:
            # Perform the fetch operation
            status, batch = await get_transcriptions(db, skip=offset, limit=limit)
            
            if not status or len(batch) == 0:
                break
            yield batch
            offset += limit

    except Exception as ex:
        logger.error(f"There is a transcription fetch error: {ex}") 

async def create_transcription(db: AsyncSession, transcription: TranscriptionCreate):
    db_transcription = Transcription(**transcription.dict())
    db.add(db_transcription)
    await db.commit()
    await db.close()
    return db_transcription


async def update_transcription(db: AsyncSession, transcription_id: int, transcription: TranscriptionUpdate):
    db_transcription = await get_transcription(db, transcription_id)
    if db_transcription:
        for key, value in transcription.dict().items():
            setattr(db_transcription, key, value) 
        await db.commit()
        await db.close()
        return db_transcription
    else:
        raise Exception(f"transcription with id {id} not found")


async def delete_transcription(db: AsyncSession, transcription_id: int):
    db_transcription = await get_transcription(db, transcription_id)
    if db_transcription:
        await db.delete(db_transcription)
        await db.commit()
        await db.close()
        return db_transcription
    else:
        raise Exception(f"transcription with id {id} not found")


async def delete_transcriptions(db: AsyncSession):
    db_transcription = await get_transcriptions(db)
    if db_transcription:
        await db.delete(db_transcription)
        await db.commit()
        await db.close()
        return db_transcription
    else:
        raise Exception(f"Error deleting all the transcriptions")
