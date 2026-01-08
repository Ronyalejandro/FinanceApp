"""Data Models and Schemas."""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from utils.constants import *

class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    tipo: Literal["Ingreso", "Gasto", "PagoCredito"]
    categoria: str
    monto: float = Field(..., gt=0, description="Amount must be greater than zero")
    fecha: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    descripcion: Optional[str] = ""
    metodo_pago: str

    @field_validator('categoria')
    def validate_category(cls, v, values):
        # We could strictly enforce categories here if desired
        return v

class CreditUpdate(BaseModel):
    """Schema for updating credit limit."""
    new_limit: float = Field(..., gt=0)

class SavingsGoalCreate(BaseModel):
    """Schema for creating a savings goal."""
    nombre: str = Field(..., min_length=1)
    monto_objetivo: float = Field(..., gt=0)
