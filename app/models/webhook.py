from sqlalchemy import Column, Integer, String, DateTime, Enum
from ..core.database import Base
from datetime import datetime
import bcrypt
from enum import Enum as PyEnum


class WebhookEvents(PyEnum):
    """Webhook events"""

    updates = "updates"
    batch_ready = "batch_ready"
    no_data = "no_data"


class Webhook(Base):
    """News article/webhook model."""

    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    event = Column(Enum(WebhookEvents), nullable=False)
    last_triggered = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the webhook"""
        return f"<webhook_url={self.url}, webhook_event = {self.event}, webhook_secret = {self.secret}>"
