from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import ForwardRef

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "editor"
