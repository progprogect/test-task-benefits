"""
Balance Pydantic schemas.
"""
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class BalanceResponse(BaseModel):
    """Schema for employee balance response."""
    category_id: UUID
    category_name: str
    year: int
    month: int
    annual_limit: Decimal
    monthly_limit: Decimal
    annual_used: Decimal
    monthly_used: Decimal
    annual_remaining: Decimal
    monthly_remaining: Decimal
    
    class Config:
        from_attributes = True

