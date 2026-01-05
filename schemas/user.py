from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """Base schema with common user fields"""
    name: str
    email: EmailStr
    isAdmin: bool

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str

class UserResponse(UserBase):
    """Schema with user response"""
    id: int
    # Allow conversion from ORM objects
    class Config:
        from_attributes = True
