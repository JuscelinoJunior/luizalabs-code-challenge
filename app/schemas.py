from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


class UserBase(BaseModel):
    email: EmailStr = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=2, max_length=100)
    role: Literal["admin", "customer"] = "customer"

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = Field(None, min_length=5, max_length=255)
    role: Literal["admin", "customer"] | None = None

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class WishlistProductResponse(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=255)
    image: str = Field(..., min_length=5, max_length=500)
    price: float
    reviewScore: float

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
