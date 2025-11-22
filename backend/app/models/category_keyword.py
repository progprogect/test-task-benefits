"""
Category keyword model.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CategoryKeyword(Base):
    """Category keyword model for matching invoices to categories."""
    
    __tablename__ = "category_keywords"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("benefit_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("BenefitCategory", back_populates="keywords")
    
    def __repr__(self):
        return f"<CategoryKeyword(id={self.id}, category_id={self.category_id}, keyword={self.keyword})>"

