"""
Employee benefit balance model.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class EmployeeBenefitBalance(Base):
    """Employee benefit balance model tracking usage per category per period."""
    
    __tablename__ = "employee_benefit_balances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("benefit_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    annual_used = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    monthly_used = Column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="balances")
    category = relationship("BenefitCategory", back_populates="balances")
    
    # Unique constraint: one balance record per employee-category-year-month
    __table_args__ = (
        UniqueConstraint("employee_id", "category_id", "year", "month", name="uq_employee_category_period"),
    )
    
    def __repr__(self):
        return f"<EmployeeBenefitBalance(employee_id={self.employee_id}, category_id={self.category_id}, year={self.year}, month={self.month})>"

