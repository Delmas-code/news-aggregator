from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from ..models.recognition import RecognitionType

# RecognitionBase has the required fields for creating a recognition
# Use this as the base class for RecognitionCreate and RecognitionUpdate

class RecognitionBase(BaseModel):
    """
    '...' means that field is required
    """
    content_id: str = Field(..., example="instanvi")
    details: str = Field(..., example="https://instanvi.com")
    type: RecognitionType = Field(..., example=RecognitionType.Ad)
    

# RecognitionCreate inherits from RecognitionBase since it has the same fields
# Use this when creating a recognition
class RecognitionCreate(RecognitionBase):
    pass

# RecognitionUpdate inherits from RecognitionBase and has optional fields
# Use this when updating a recognition
class   RecognitionUpdate(BaseModel):
    content_id: Optional[str] = Field(None)
    details: Optional[str] = Field(None, example="instanvi")
    type: Optional[RecognitionType] = Field(None, example=RecognitionType.Ad)
  
# RecognitionInDBBase inherits from RecognitionBase and has additional fields for data from DB
class RecognitionInDBBase(RecognitionBase):
    id: int
    created_at: datetime
    last_fetched: datetime


# Recognition inherits from RecognitionInDBBase since it has the same fields
# Use this when returning data from the API
class Recognition(RecognitionInDBBase):
    pass


# RecognitionInDB inherits from RecognitionInDBBase since it has the same fields
# Use this when working with data in the database
class RecognitionInDB(RecognitionInDBBase):
    pass 