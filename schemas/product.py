from pydantic import BaseModel, PositiveInt

class ProductBase(BaseModel):
    """Base schema with common product fields"""
    name: str
    price: PositiveInt

class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass

class ProductResponse(ProductBase):
    """Schema with product response"""
    id: int
    # Allow conversion from ORM objects
    class Config:
        from_attributes = True

class ProductUpdate(ProductBase):
    """Schema for updating product"""
    pass
