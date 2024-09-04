from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey  # , UniqueConstraint
from ..core.database import Base
from datetime import datetime
from enum import Enum as PyEnum

class TagCategory(PyEnum):
    """predefined tag categories"""
    Industry = "Industry"
    Company = "Company"


class Tag(Base):
    """Tags model."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(Enum(TagCategory), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_fetched = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    def __repr__(self):
        """Return a string representation of the tag"""
        return f"Tag[{self.name}, Message = {self.description}]>"
