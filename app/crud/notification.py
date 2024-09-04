from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.notification import Notification
from app.core.database import async_session
from ..schemas.notification import NotificationCreate, NotificationUpdate
from loguru import logger

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_notification(db: AsyncSession, notification_id: int):
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    return result.scalars().first()


async def get_notifications(db: AsyncSession, skip: int=0, limit: int = 10):
    result = await db.execute(select(Notification).offset(skip).limit(limit))    
    return result.scalars().all()
    

# Function to filter by given fields if 
async def get_filtered_notifications(db: AsyncSession,  field: str, value , skip: int=0, limit: int = 10):
    try:
        filter_column = getattr(Notification, field)
        
        if field == "type":
            condition = filter_column == value
            stmt = select(Notification).where(condition).offset(skip).limit(limit)
        else:   
            condition = filter_column.like(f"%{value}%")
            stmt = select(Notification).filter(condition).offset(skip).limit(limit)

        result = await db.execute(stmt)           
        return True, result.scalars().all()
    
    except Exception as e:
        return False, e
    

async def get_notifications_in_batch(db: AsyncSession, limit: int = 10):
    try:
        offset = 0
        while True:
            # Perform the fetch operation
            status, batch = await get_notifications(db, skip=offset, limit=limit)
            
            if not status or len(batch) == 0:
                break
            yield batch
            offset += limit

    except Exception as ex:
        logger.error(f"There is a notification fetch error: {ex}") 

async def create_notification(db: AsyncSession, notification: NotificationCreate):
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    await db.commit()
    await db.close()
    return db_notification


async def update_notification(db: AsyncSession, notification_id: int, notification: NotificationUpdate):
    db_notification = await get_notification(db, notification_id)
    if db_notification:
        for key, value in notification.dict().items():
            setattr(db_notification, key, value) 
        await db.commit()
        await db.close()
        return db_notification
    else:
        raise Exception(f"notification with id {id} not found")


async def delete_notification(db: AsyncSession, notification_id: int):
    db_notification = await get_notification(db, notification_id)
    if db_notification:
        await db.delete(db_notification)
        await db.commit()
        await db.close()
        return db_notification
    else:
        raise Exception(f"notification with id {id} not found")


async def delete_notifications(db: AsyncSession):
    db_notification = await get_notifications(db)
    if db_notification:
        await db.delete(db_notification)
        await db.commit()
        await db.close()
        return db_notification
    else:
        raise Exception(f"Error deleting all the notifications")
