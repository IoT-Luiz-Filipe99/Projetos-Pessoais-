from pydantic import BaseModel, EmailStr
from typing import Optional

# Auth
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# Users (apenas saída simples quando necessário)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    class Config:
        from_attributes = True

# Entities
class TechnicianIn(BaseModel):
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    skills: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

class TechnicianOut(TechnicianIn):
    id: int
    class Config:
        from_attributes = True

class ClientIn(BaseModel):
    name: str
    document: Optional[str] = None
    contact: Optional[str] = None
    is_active: Optional[bool] = True

class ClientOut(ClientIn):
    id: int
    class Config:
        from_attributes = True

class OrderIn(BaseModel):
    client_id: int
    technician_id: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    status: Optional[str] = "Pendente"
    description: Optional[str] = None
    total_value: Optional[float] = 0.0

class OrderOut(OrderIn):
    id: int
    attachment_url: Optional[str] = None
    class Config:
        from_attributes = True
