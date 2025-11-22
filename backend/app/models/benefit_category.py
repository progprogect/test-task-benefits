"""
Benefit category model.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class BenefitCategory(Base):
    """Benefit category model representing different benefit types."""
    
    __tablename__ = "benefit_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    max_transaction_amount = Column(Numeric(10, 2), nullable=False)
    annual_limit = Column(Numeric(10, 2), nullable=False)
    monthly_limit = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    keywords = relationship("CategoryKeyword", back_populates="category", cascade="all, delete-orphan")
    balances = relationship("EmployeeBenefitBalance", back_populates="category", cascade="all, delete-orphan")
    reimbursement_requests = relationship("ReimbursementRequest", back_populates="category")
    
    def __repr__(self):
        return f"<BenefitCategory(id={self.id}, name={self.name})>"

