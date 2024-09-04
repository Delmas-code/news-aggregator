from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, Enum, ForeignKey, func
from ..core.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import bcrypt   
from enum import Enum as PyEnum


class WebhookEvents(PyEnum):
    """Webhook events"""
    Detection = "ContentDetected"
    Update = "ContentUpdated"

class Webhook(Base):
    """News article/webhook model."""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    event = Column(Enum(WebhookEvents), index=True, nullable=False)
    secret = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, index=True, nullable=False, default=func.now())
    last_triggered = Column(DateTime, nullable=False, default=datetime.utcnow(), onupdate=func.now())    
    
    # How to implement the methods
    def set_secret(self, plain_secret: str) ->str:
        salt = bcrypt.gensalt()
        plain_secret = plain_secret.encode('utf-8')
        self.secret = bcrypt.hashpw(plain_secret, salt=salt)
        self.secret = self.secret.decode('utf-8')


    def check_secret(self, plain_secret: str) -> bool:
        return bcrypt.checkpw(plain_secret.encode('utf-8'), self.secret.encode('utf-8'))

    async def trigger_webhook(self, trigger):
        """trigger the webhook here"""
        pass
    async def validate_webhook(self)-> bool:
        """categorize webhook"""
        pass
    async def update_event(self, event) -> None:
        """save webhook"""
        pass
    
    def __repr__(self):
        """Return a string representation of the webhook"""
        return f"<webhook_url={self.url}, webhook_event = {self.event}, webhook_secret = {self.secret}>"
