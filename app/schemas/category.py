from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# CategoryBase has the required fields for creating a category
# Use this as the base class for CategoryCreate and CategoryUpdate

class CategoryBase(BaseModel):
    """
    '...' means that field is required
    """
    name: str = Field(..., example="instanvi")
    description: str = Field(..., example="some sample text")
    

# CategoryCreate inherits from CategoryBase since it has the same fields
# Use this when creating a category
class CategoryCreate(CategoryBase):
    pass

# CategoryUpdate inherits from CategoryBase and has optional fields
# Use this when updating a category
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None, example="instanvi")
  
# CategoryInDBBase inherits from CategoryBase and has additional fields for data from DB
class CategoryInDBBase(CategoryBase):
    id: int
    created_at: datetime
    last_fetched: datetime


# Category inherits from CategoryInDBBase since it has the same fields
# Use this when returning data from the API
class Category(CategoryInDBBase):
    pass


# CategoryInDB inherits from CategoryInDBBase since it has the same fields
# Use this when working with data in the database
class CategoryInDB(CategoryInDBBase):
    pass 