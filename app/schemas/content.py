from pydantic import BaseModel, Field
from typing import Optional, List
from ..models.content import ContentType

# ContentBase has the required fields for creating a Content
# Use this as the base class for ContentCreate and ContentUpdate
class Entity(BaseModel):
    entity: str
    score: float
    start: int
    end: int

class Sentiment(BaseModel):
    label: str
    score: float

class ContentBase(BaseModel):
    """
    '...' means that field is required
    """
    id: Optional[str] = Field(None, examples="https://instanvi.com?90ou278w-date")
    source_id: int = Field(..., example="1")
    title: str = Field(..., example="The macth of today")
    body: str = Field(..., example="The macth of today ...")
    url: str = Field(..., example="https://instanvi.com")
    type: Optional[str] = Field(None, example=ContentType.Text)
    tags: List[str] = Field(None, example="news, instanvi.com")
    sentiment: List[Sentiment] = Field(None, example="Positive")
    entities: List[Entity] = Field(None)
    image_url: Optional[str] = Field(None)


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
    tags: Optional[str] = Field(None, example="news, instanvi.com")
    sentiment: Optional[str] = Field(None, example="Positive")
    #last_fetched: datetime = Field(None, example=datetime.utcnow())
    #published_at: datetime = Field(None, example=datetime.utcnow())

# ContentInDBBase inherits from ContentBase and has additional fields for data from DB
class ContentInDBBase(ContentBase):
    #last_fetched: datetime
    #published_at: datetime
    pass

# Content inherits from ContentInDBBase since it has the same fields
# Use this when returning data from the API
class Content(ContentInDBBase):
    pass


# ContentInDB inherits from ContentInDBBase since it has the same fields
# Use this when working with data in the database
class ContentInDB(ContentInDBBase):
    pass 

class ContentBase(BaseModel):
    class Config:
        extra = "allow"