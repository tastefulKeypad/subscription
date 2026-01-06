from pydantic import BaseModel 

class Token(BaseModel):
    """Base schema with JWT token fields"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Converts token into user data"""
    username: str | None = None
