from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.webhook import WebhookEvents

class WebhookBase(BaseModel):
    """
    '...' means that field is required
    """
    url: str = Field(..., example="https://instanvi.com")
    event: Optional[WebhookEvents] = Field(..., example=WebhookEvents.updates)

# # WebhookCreate inherits from WebhookBase since it has the same fields
# # Use this when creating a Webhook
class WebhookCreate(WebhookBase):
    pass

# WebhookUpdate inherits from WebhookBase and has optional fields
# Use this when updating a Webhook
class WebhookUpdate(BaseModel):
    event: Optional[str] = Field(None, example="instanvi")
    url: Optional[str] = Field(None, example="https://instanvi.com")


# WebhookInDBBase inherits from WebhookBase and has additional fields for data from DB
class WebhookInDBBase(WebhookBase):
    id: int
    last_triggered: datetime
    created_at: datetime
    updated_at: datetime

# Webhook inherits from WebhookInDBBase since it has the same fields
# Use this when returning data from the API
class Webhook(WebhookInDBBase):
    pass


# WebhookInDB inherits from WebhookInDBBase since it has the same fields
# Use this when working with data in the database
class WebhookInDB(WebhookInDBBase):
    pass 
