from pydantic import BaseModel, PositiveInt, Field
from datetime import datetime, date

class PromoBase(BaseModel):
    """Base schema with common promo fields"""
    name: str
    productId: int
    discount: PositiveInt = Field(gt=0, lt=100)
    expDate: date

class PromoCreate(PromoBase):
    """Schema for creating a new promo"""
    pass

class PromoResponse(PromoBase):
    """Schema with promo response"""
    # Allow conversion from ORM objects
    class Config:
        from_attributes = True

class PromoUpdate(PromoBase):
    """Schema for updating promo"""
    pass
