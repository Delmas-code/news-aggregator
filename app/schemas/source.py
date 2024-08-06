from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.source import SourceType

# SourceBase has the required fields for creating a source
# Use this as the base class for SourceCreate and SourceUpdate
class SourceBase(BaseModel):
    """
    '...' means that field is required
    """

    name: str = Field(..., example="instanvi")
    url: str = Field(..., example="https://instanvi.com")
    type: SourceType = Field(..., example=SourceType.Website)
    content_category: str = Field(..., example="news")
    frequency: str = Field(..., example="1h")

# SourceCreate inherits from SourceBase since it has the same fields
# Use this when creating a source
class SourceCreate(SourceBase):
    pass

# SourceUpdate inherits from SourceBase and has optional fields
# Use this when updating a source
class SourceUpdate(BaseModel):
    name: Optional[str] = Field(None, example="instanvi")
    url: Optional[str] = Field(None, example="https://instanvi.com")
    type: Optional[SourceType] = Field(None, example=SourceType.Website)
    content_category: Optional[str] = Field(None, example="Startups")
    frequency: Optional[str] = Field(None, example="30m")

# SourceInDBBase inherits from SourceBase and has additional fields for data from DB
class SourceInDBBase(SourceBase):
    id: int
    last_fetched: datetime
    created_at: datetime
    updated_at: datetime


# Source inherits from SourceInDBBase since it has the same fields
# Use this when returning data from the API
class Source(SourceInDBBase):
    pass

# SourceInDB inherits from SourceInDBBase since it has the same fields
# Use this when working with data in the database
class SourceInDB(SourceInDBBase):
    pass