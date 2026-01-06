from pydantic import BaseModel 
from datetime import datetime

class PromoBase(BaseModel):
    """Base schema with common promo fields"""
    name: str
    productId: int
    discount: int
    expDate: datetime

class PromoCreate(PromoBase):
    """Schema for creating a new promo"""
    pass

class PromoResponse(PromoBase):
    """Schema with promo response"""
    id: int
    # Allow conversion from ORM objects
    class Config:
        from_attributes = True

class PromoUpdate(PromoBase):
    """Schema for updating promo"""
    pass
