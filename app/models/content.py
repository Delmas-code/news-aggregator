from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, Enum, ForeignKey, func
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid


class ContentType(PyEnum):
    """News content types."""
    Text = "Text"
    Audio = "Audio"
    Video = "Video"

def generate_key():
    return str(uuid.uuid4())

class Content(Base):
    """News article/content model."""
    __tablename__ = "contents"

    # A content, based on the rss feed
    # has a guid and a pub date that can uniquely identify it.

    id = Column(String, primary_key=True, default=generate_key, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(String, unique=True, nullable=False)
    body = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=True, default=None)
    type = Column(Enum(ContentType), nullable=False, default="Text")
    published_at = Column(DateTime, nullable=False, default=func.now())
    last_fetched = Column(DateTime, nullable=False, default=datetime.utcnow(), onupdate=func.now())    
    sentiment = Column(String)
    Tags = Column(ARRAY(String))
    transcription = Column(Text)
    
    # How to implement the methods

    async def analyze_sentiment(self):
        """call the analyze service here"""
        pass
    async def categorize_content(self, category):
        """categorize content"""
        pass
    async def save_content(self, content) -> None:
        """save content"""
        pass
    async def flag_content(self, flag) -> None:
        """flag the content"""
        pass
    
    def __repr__(self):
        """Return a string representation of the content"""
        return f"<Content={self.title}, Type={self.type}>"
