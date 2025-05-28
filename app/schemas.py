from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Customer full name")
    email: EmailStr = Field(..., description="Valid email address")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None

class CustomerResponse(CustomerBase):
    id: int

    class Config:
        orm_mode = True

class WishlistProductResponse(BaseModel):
    id: int
    title: str
    image: str
    price: float
    reviewScore: float

    class Config:
        orm_mode = True