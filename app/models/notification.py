from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey  # , UniqueConstraint
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

class NotificationStatus(PyEnum):
    """News content types."""
    Sent = "Sent"
    Failed = "Failed"
    Pending = "Pending"
    Read = "Read"
    UnRead = "UnRead"


class Notification(Base):
    """Notifications model."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, ForeignKey("contents.id"))
    message = Column(String, nullable=False)
    status = Column(Enum(NotificationStatus), nullable=False, default="UnRead")
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # How to implement the methods
    async def send_notification(self):
        """send the notification here"""
        pass
    
    async def mark_as_read(self):
        """mark the notification here"""
        pass
    
    async def get_pending_notification(self) ->list:
        """Get all the pending notifications"""
        pass

    def __repr__(self):
        """Return a string representation of the notification"""
        return f"Notification[{self.content_id}, Message = {self.message}]>"
