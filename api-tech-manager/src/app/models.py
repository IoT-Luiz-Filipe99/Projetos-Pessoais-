from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# Usuário para login (RBAC simples)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    role: str = Field(default="operator")  # admin | operator
    failed_attempts: int = Field(default=0)
    lock_until: Optional[datetime] = None
    is_active: bool = Field(default=True)

class Technician(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    skills: Optional[str] = None  # ex: "rede, fibra, cftv"
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = Field(default=True)

class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    document: Optional[str] = None
    contact: Optional[str] = None
    is_active: bool = Field(default=True)

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    technician_id: Optional[int] = Field(default=None, foreign_key="technician.id")
    city: Optional[str] = None
    state: Optional[str] = None
    status: str = Field(default="Pendente")  # Pendente/Agendado/Em campo/Finalizado/Cancelado
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_value: Optional[float] = 0.0
    attachment_url: Optional[str] = None
