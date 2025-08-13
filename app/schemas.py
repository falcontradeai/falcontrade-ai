from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    email: EmailStr
    is_admin: bool

class ListingBase(BaseModel):
    type: str
    category: str
    title: str
    details: Dict[str, Any] = {}
    quantity: str = ""
    incoterm: str = ""
    country: str = ""
    city: str = ""

class ListingIn(ListingBase):
    pass

class ListingOut(ListingBase):
    id: int
    status: str
    created_at: datetime
    owner_email: EmailStr
    class Config:
        from_attributes = True

class MessageIn(BaseModel):
    body: str

class MessageOut(BaseModel):
    id: int
    body: str
    created_at: datetime
    sender_email: EmailStr
    class Config:
        from_attributes = True
