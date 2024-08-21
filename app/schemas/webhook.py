from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# WebhookBase has the required fields for creating a Webhook
# Use this as the base class for WebhookCreate and WebhookUpdate

class WebhookBase(BaseModel):
    """
    '...' means that field is required
    """
    id: str = Field(..., examples="90ou278w-date")
    url: str = Field(..., example="https://instanvi.com")
    secret: str = Field(..., example="sharedWithMe")
    event: str = Field(..., example="content_detected")


# # WebhookCreate inherits from WebhookBase since it has the same fields
# # Use this when creating a Webhook
class WebhookCreate(WebhookBase):
    pass

# WebhookUpdate inherits from WebhookBase and has optional fields
# Use this when updating a Webhook
class  WebhookUpdate(BaseModel):
    event: Optional[str] = Field(None, example="instanvi")
    secret: Optional[str] = Field(None, example="instanvi")
    url: Optional[str] = Field(None, example="https://instanvi.com")


# WebhookInDBBase inherits from WebhookBase and has additional fields for data from DB
class WebhookInDBBase(WebhookBase):
    last_triggered: datetime
    created_at: datetime


# Webhook inherits from WebhookInDBBase since it has the same fields
# Use this when returning data from the API
class Webhook(WebhookInDBBase):
    pass


# WebhookInDB inherits from WebhookInDBBase since it has the same fields
# Use this when working with data in the database
class WebhookInDB(WebhookInDBBase):
    pass 