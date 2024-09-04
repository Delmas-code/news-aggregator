from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.notification import NotificationStatus

# NotificationBase has the required fields for creating a notification
# Use this as the base class for NotificationCreate and NotificationUpdate

class NotificationBase(BaseModel):
    """
    '...' means that field is required
    """
    content_id: str = Field(..., example="instanvi")
    message: str = Field(..., example="https://instanvi.com")
    status: NotificationStatus = Field(..., example=NotificationStatus.Sent)
    

# NotificationCreate inherits from NotificationBase since it has the same fields
# Use this when creating a notification
class NotificationCreate(NotificationBase):
    pass

# NotificationUpdate inherits from NotificationBase and has optional fields
# Use this when updating a notification
class   NotificationUpdate(BaseModel):
    content_id: Optional[str] = Field(None)
    message: Optional[str] = Field(None, example="instanvi")
    status: Optional[NotificationStatus] = Field(None, example=NotificationStatus.Pending)
  
# NotificationInDBBase inherits from NotificationBase and has additional fields for data from DB
class NotificationInDBBase(NotificationBase):
    id: int
    created_at: datetime
    sent_at: datetime


# Notification inherits from NotificationInDBBase since it has the same fields
# Use this when returning data from the API
class Notification(NotificationInDBBase):
    pass


# NotificationInDB inherits from NotificationInDBBase since it has the same fields
# Use this when working with data in the database
class NotificationInDB(NotificationInDBBase):
    pass 