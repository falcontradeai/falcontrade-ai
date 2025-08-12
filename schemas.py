from pydantic import BaseModel, EmailStr
from typing import List

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CommodityIn(BaseModel):
    name: str
    unit: str = "$/ton"
    price: float
    source: str = "manual"

class CommodityOut(BaseModel):
    id: int
    name: str
    unit: str
    price: float
    source: str
    class Config:
        from_attributes = True