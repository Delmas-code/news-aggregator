from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey  # , UniqueConstraint
from ..core.database import Base
from datetime import datetime
from enum import Enum as PyEnum

class RecognitionType(PyEnum):
    """Recognition types."""
    Ad = "Ad"
    Specific = "Specific"


class Recognition(Base):
    """Recognitions model."""
    __tablename__ = "recognitions"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, ForeignKey("contents.id"))
    type = Column(Enum(RecognitionType), nullable=False, default="UnRead")
    details = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_fetched = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # How to implement the methods
    async def detect_content(self):
        """detect the recognition here"""
        pass
    
    async def log_recognition(self):
        """log the recognition here"""
        pass
    
    async def get_recognition_details(self) ->list:
        """Get all the pending recognitions"""
        pass

    def __repr__(self):
        """Return a string representation of the recognition"""
        return f"Recognition[{self.content_id}, Message = {self.details}]>"
