from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.content import ContentType

# ContentBase has the required fields for creating a Content
# Use this as the base class for ContentCreate and ContentUpdate
class ContentBase(BaseModel):
    """
    '...' means that field is required
    """
    id: Optional[str] = Field(None, examples="https://instanvi.com?90ou278w-date")
    source_id: int = Field(..., example="1")
    title: str = Field(..., example="The macth of today")
    body: str = Field(..., example="The macth of today ...")
    url: str = Field(..., example="https://instanvi.com")
    type: ContentType = Field(..., example=ContentType.Text)
    image_url: Optional[str] = Field(None, examples="https://benevenite.com/wp-content/uploads/2024/07/cropped-favicon-32x32.jpg")


# # ContentCreate inherits from ContentBase since it has the same fields
# # Use this when creating a Content
class ContentCreate(ContentBase):
    pass

# ContentUpdate inherits from ContentBase and has optional fields
# Use this when updating a Content
class  ContentUpdate(BaseModel):
    source_id: Optional[int] = Field(None)
    title: Optional[str] = Field(None, example="instanvi")
    body: Optional[str] = Field(None, example="instanvi")
    url: Optional[str] = Field(None, example="https://instanvi.com")
    type: Optional[ContentType] = Field(None, example=ContentType.Text)
    image_url: Optional[str] = Field(None, example="https://instanvi.com/image.jpg")

# ContentInDBBase inherits from ContentBase and has additional fields for data from DB
class ContentInDBBase(ContentBase):
    last_fetched: datetime
    published_at: datetime


# Content inherits from ContentInDBBase since it has the same fields
# Use this when returning data from the API
class Content(ContentInDBBase):
    pass


# ContentInDB inherits from ContentInDBBase since it has the same fields
# Use this when working with data in the database
class ContentInDB(ContentInDBBase):
    pass 