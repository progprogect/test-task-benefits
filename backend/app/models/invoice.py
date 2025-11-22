"""
Invoice model for extracted invoice data.
"""
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Date, Numeric, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Invoice(Base):
    """Invoice model storing extracted data from invoice images."""
    
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("reimbursement_requests.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    vendor_name = Column(String(255), nullable=True)
    purchase_date = Column(Date, nullable=True)
    items = Column(JSONB, nullable=True)  # Array of item objects
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    invoice_number = Column(String(100), nullable=True)
    extracted_text = Column(Text, nullable=True)  # Full OCR text
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    request = relationship("ReimbursementRequest", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, request_id={self.request_id}, vendor_name={self.vendor_name})>"

