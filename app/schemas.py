from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ClientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Client full name")
    email: EmailStr = Field(..., description="Valid email address")

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None

class ClientResponse(ClientBase):
    id: int

    class Config:
        orm_mode = True
