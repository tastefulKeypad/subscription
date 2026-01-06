from pydantic import BaseModel 
from datetime import datetime

class TransactionBase(BaseModel):
    """Base schema with common transaction fields"""
    userId: int
    productId: int
    action: str
    dateTime: datetime
    status: str
    moneyChange: int

class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    pass

class TransactionResponse(TransactionBase):
    """Schema with transaction response"""
    id: int
    # Allow conversion from ORM objects
    class Config:
        from_attributes = True
