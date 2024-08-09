from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, Enum, ForeignKey, func # , UniqueConstraint
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum


class ContentType(PyEnum):
    """News source types."""
    Text = "text"
    Audio = "audio"
    Video = "video"


class Content(Base):
    """News source model."""
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(String, unique=True, index=True, nullable=False)
    body = Column(Text, unique=True, index=True, nullable=False)
    url = Column(String, index=True, nullable=False)
    image_url = Column(String, nullable=True)
    published_at = Column(DateTime, index=True, nullable=False, default=func.now())
    last_fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow(), onupdate=func.now())
    sentiment = Column(String)
    Tags = Column(ARRAY(String))
    type = Column(Enum(ContentType), nullable=False, index=True, default="Text")
    transcription = Column(Text)

    # source = relationship('Source', back_populates="content")
    
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
        """Return a string representation of the source"""
        return f"<Source={self.name}, Type={self.type}>"
