"""
Reimbursement request model.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class RequestStatus(str, enum.Enum):
    """Reimbursement request status enumeration."""
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"


class ReimbursementRequest(Base):
    """Reimbursement request model representing employee reimbursement submissions."""
    
    __tablename__ = "reimbursement_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("benefit_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PROCESSING, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    cloudinary_url = Column(String(500), nullable=False)
    cloudinary_public_id = Column(String(255), nullable=False)
    submission_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="reimbursement_requests")
    category = relationship("BenefitCategory", back_populates="reimbursement_requests")
    invoice = relationship("Invoice", back_populates="request", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ReimbursementRequest(id={self.id}, employee_id={self.employee_id}, status={self.status})>"

