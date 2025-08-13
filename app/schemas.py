from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Dict, Any
from datetime import datetime
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
        if not pattern.match(value):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
            )
        return value

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
    details: Dict[str, Any] = Field(default_factory=dict)
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
