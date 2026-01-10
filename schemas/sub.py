from pydantic import BaseModel, PositiveInt
from datetime import datetime

class SubBase(BaseModel):
    """Base schema with common sub fields"""
    userId: int
    productId: int
    price: PositiveInt
    status: str
    dateTime: datetime

class SubCreate(SubBase):
    """Schema for creating a new sub"""
    pass

class SubResponse(SubBase):
    """Schema with sub response"""
    id: int
    # Allow conversion from ORM objects
    class Config:
        from_attributes = True
