"""
Reimbursement request Pydantic schemas.
"""
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.models.reimbursement_request import RequestStatus


class InvoiceItem(BaseModel):
    """Schema for invoice item."""
    description: str
    amount: Optional[Decimal] = None


class InvoiceData(BaseModel):
    """Schema for extracted invoice data."""
    vendor_name: Optional[str] = None
    purchase_date: Optional[date] = None
    items: Optional[List[InvoiceItem]] = None
    total_amount: Decimal
    currency: str
    invoice_number: Optional[str] = None
    extracted_text: Optional[str] = None


class ReimbursementSubmitRequest(BaseModel):
    """Schema for submitting a reimbursement request."""
    employee_id: UUID


class ReimbursementResponse(BaseModel):
    """Schema for reimbursement request response."""
    id: UUID
    employee_id: UUID
    employee_name: str
    employee_employee_id: str
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    status: RequestStatus
    amount: Decimal
    currency: str
    cloudinary_url: str
    submission_timestamp: datetime
    rejection_reason: Optional[str] = None
    invoice: Optional[InvoiceData] = None
    remaining_balance: Optional[Decimal] = None  # Always in USD
    remaining_balance_currency: str = "USD"  # Always USD
    
    class Config:
        from_attributes = True

