from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.tag import TagCategory

# TagBase has the required fields for creating a tag
# Use this as the base class for TagCreate and TagUpdate

class TagBase(BaseModel):
    """
    '...' means that field is required
    """
    name: str = Field(..., example="instanvi")
    description: str = Field(..., example="some sample text")
    category: TagCategory = Field(..., example=TagCategory.Industry)
    

# TagCreate inherits from TagBase since it has the same fields
# Use this when creating a tag
class TagCreate(TagBase):
    pass

# TagUpdate inherits from TagBase and has optional fields
# Use this when updating a tag
class TagUpdate(BaseModel):
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None, example="instanvi")
    category: Optional[TagCategory] = Field(None, example=TagCategory.Industry)
  
# TagInDBBase inherits from TagBase and has additional fields for data from DB
class TagInDBBase(TagBase):
    id: int
    created_at: datetime
    last_fetched: datetime


# Tag inherits from TagInDBBase since it has the same fields
# Use this when returning data from the API
class Tag(TagInDBBase):
    pass


# TagInDB inherits from TagInDBBase since it has the same fields
# Use this when working with data in the database
class TagInDB(TagInDBBase):
    pass 