from sqlalchemy import Column, Integer, String, DateTime, Enum  # , UniqueConstraint
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

class SourceType(PyEnum):
    """News source types."""
    RSS = "rss"
    Website = "website"
    Audio = "audio"
    Video = "video"


class Source(Base):
    """News source model."""
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    content_category = Column(String, nullable=False)
    last_fetched = Column(DateTime, default=datetime.utcnow)
    frequency = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    """parent-child relationship with the content"""
    contents = relationship("Content", backref="source")
    
    def __repr__(self):
        """Return a string representation of the source"""
        return f"Source[{self.name}, Type={self.type}]>"
