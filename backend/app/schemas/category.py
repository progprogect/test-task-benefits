"""
Category Pydantic schemas.
"""
from uuid import UUID
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class KeywordResponse(BaseModel):
    """Schema for keyword response."""
    id: UUID
    keyword: str
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str
    max_transaction_amount: Decimal
    annual_limit: Decimal
    monthly_limit: Decimal


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = None
    max_transaction_amount: Optional[Decimal] = None
    annual_limit: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: UUID
    keywords: List[KeywordResponse] = []
    
    class Config:
        from_attributes = True


class KeywordCreate(BaseModel):
    """Schema for creating a keyword."""
    keyword: str

