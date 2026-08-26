from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class OrganizationCreate(BaseModel):
    name: str

class OrganizationOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]
    organization_name: Optional[str]

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    organization_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
