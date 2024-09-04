from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey  # , UniqueConstraint
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum


class Transcription(Base):
    """Transcriptions model."""
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, ForeignKey("contents.id"))
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_fetched = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    def __repr__(self):
        """Return a string representation of the transcription"""
        return f"Transcription[{self.content_id}, Message = {self.text}]>"
