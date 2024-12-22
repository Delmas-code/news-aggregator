from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ARRAY,
    DateTime,
    Enum,
    ForeignKey,
    func,
    JSON
    )
from ..core.database import Base
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
import uuid
from .notification import Notification
from .transcription import Transcription
from .recognition import Recognition


class ContentType(PyEnum):
    """News content types."""
    Text = "text"
    Audio = "audio"
    Video = "video"

class ContentCategory(PyEnum):
    pass

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
    type = Column(Enum(ContentType), nullable=False, default="text")
    sentiment = Column(ARRAY(JSON))
    tags = Column(ARRAY(String))
    entities = Column(ARRAY(JSON))
    flags = Column(ARRAY(String))
    transcription = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    """parent-child relationship with the notification"""
    contents = relationship("Notification", backref="content")

    """parent-child relationship with the transcription"""
    contents = relationship("Transcription", backref="content")

    """parent-child relationship with the recognition"""
    contents = relationship("Recognition", backref="content")

    def __repr__(self):
        """Return a string representation of the content"""
        return f"<Content={self.title}, Type={self.type}>"
