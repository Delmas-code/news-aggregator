from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey  # , UniqueConstraint
from ..core.database import Base
from datetime import datetime
from enum import Enum as PyEnum


class Category(Base):
    """Category model."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_fetched = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    def __repr__(self):
        """Return a string representation of the category"""
        return f"Category{self.name}, Description = {self.description}]>"
