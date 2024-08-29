from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..crud import notification as crud_notification
from ..schemas import notification as schema_notification

# get a database session
from ..core.database import get_db

router = APIRouter(
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schema_notification.Notification, status_code=201)
async def create_notification(
    notification: schema_notification.NotificationCreate, db: AsyncSession = Depends(get_db)
):
    try: 
        created_notification = await crud_notification.create_notification(db, notification)
        return created_notification
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Add some optional params, such that the notification can be filtered,
#  not just by the id
# but also by other fields

@router.get("/")
async def get_notifications(
    field: Optional[str] = None,
    value = None,
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncSession = Depends(get_db),
):   
    """handle the inputed fields"""
    if field:
       return await get_by_fields(db, skip, limit, field, value)

    return await crud_notification.get_notifications(db, skip, limit)


# Function to handle optional fields
async def get_by_fields(db: AsyncSession, skip: int, limit: int, field: str, value):

    field = field.lower()
    # Create an array of all the model fields
    model_dict = schema_notification.Notification.__dict__.items()
    model_fields = {key: value for key, value in model_dict if not key.startswith('__')}
    model_fields = model_fields['model_fields'].keys()
    
    if field not in model_fields:
        raise HTTPException(status_code=404, detail=f"Provided field, {field} is not found")  
    
    status, notifications = await crud_notification.get_filtered_notifications(db, field, value, skip, limit)
    if not status:
        raise HTTPException(status_code=404, detail=f"No such record found: {notifications}")  

    return notifications


@router.get("/{notification_id}", response_model=schema_notification.Notification)
async def get_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    notification = await crud_notification.get_notification(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.patch("/{notification_id}", response_model=schema_notification.Notification, status_code=200)
async def update_notification(
    notification_id: int,
    notification: schema_notification.NotificationUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_notification = await crud_notification.update_notification(db, notification_id, notification)
    return updated_notification


@router.delete("/{notification_id}", response_model=schema_notification.Notification)
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    deleted_notification = await crud_notification.delete_notification(db, notification_id)
    return deleted_notification


# Delete all notifications
@router.delete("/", response_model=schema_notification.Notification)
async def delete_notification(db: AsyncSession = Depends(get_db)):
    deleted_notifications = await crud_notification.delete_notifications(db)
    return deleted_notifications