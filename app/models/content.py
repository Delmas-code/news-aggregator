from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, Enum, ForeignKey, func
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum


class ContentType(PyEnum):
    """News content types."""
    Text = "Text"
    Audio = "Audio"
    Video = "Video"


class Content(Base):
    """News article/content model."""
    __tablename__ = "contents"

    # A content, based on the rss feed
    # has a guid and a pub date that can uniquely identify it.

    id = Column(String, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(String, unique=True, index=True, nullable=False)
    body = Column(Text, unique=True, index=True, nullable=False)
    url = Column(String, index=True, nullable=False)
    image_url = Column(String, nullable=True)
    type = Column(Enum(ContentType), nullable=False, index=True, default="Text")
    published_at = Column(DateTime, index=True, nullable=False, default=func.now())
    last_fetched = Column(DateTime, nullable=False, default=datetime.utcnow(), onupdate=func.now())    
    sentiment = Column(String)
    Tags = Column(ARRAY(String))
    transcription = Column(Text)
    
    # How to implement the methods
    async def fetch_content(self) -> list:
        """call the fetch service here"""
        pass
    async def parse_content(self):
        """Parse content"""
        pass
    async def update_frequency(self, frequency) -> None:
        """update frequency"""
        pass
    async def update_last_fetched(self, new_fetch_time) -> None:
        """update last fetched"""
        pass
    def validate_content(self):
        pass
    
    def __repr__(self):
        """Return a string representation of the content"""
        return f"<Content={self.title}, Type={self.type}>"
