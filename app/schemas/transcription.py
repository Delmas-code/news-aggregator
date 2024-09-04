from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# TranscriptionBase has the required fields for creating a transcription
# Use this as the base class for TranscriptionCreate and TranscriptionUpdate

class TranscriptionBase(BaseModel):
    """
    '...' means that field is required
    """
    content_id: str = Field(..., example="instanvi")
    text: str = Field(..., example="https://instanvi.com")
    

# TranscriptionCreate inherits from TranscriptionBase since it has the same fields
# Use this when creating a transcription
class TranscriptionCreate(TranscriptionBase):
    pass

# TranscriptionUpdate inherits from TranscriptionBase and has optional fields
# Use this when updating a transcription
class   TranscriptionUpdate(BaseModel):
    content_id: Optional[str] = Field(None)
    text: Optional[str] = Field(None, example="instanvi")

# TranscriptionInDBBase inherits from TranscriptionBase and has additional fields for data from DB
class TranscriptionInDBBase(TranscriptionBase):
    id: int
    created_at: datetime
    last_fetched: datetime


# Transcription inherits from TranscriptionInDBBase since it has the same fields
# Use this when returning data from the API
class Transcription(TranscriptionInDBBase):
    pass


# TranscriptionInDB inherits from TranscriptionInDBBase since it has the same fields
# Use this when working with data in the database
class TranscriptionInDB(TranscriptionInDBBase):
    pass 