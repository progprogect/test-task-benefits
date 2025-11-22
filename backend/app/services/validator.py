"""
Validation service for reimbursement requests.
"""
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.employee_benefit_balance import EmployeeBenefitBalance
from app.models.benefit_category import BenefitCategory


async def validate_reimbursement(
    db: Session,
    employee_id: UUID,
    category_id: UUID,
    amount: Decimal,
    currency: str
) -> Dict[str, Any]:
    """
    Validate reimbursement request against employee balances and category limits.
    
    Args:
        db: Database session
        employee_id: UUID of employee
        category_id: UUID of benefit category
        amount: Requested reimbursement amount
        currency: Currency code
        
    Returns:
        Dictionary with validation result, reasons, and remaining balance
    """
    try:
        # Get category
        category = db.query(BenefitCategory).filter(BenefitCategory.id == category_id).first()
        if not category:
            return {
                "valid": False,
                "reason": "Category not found",
                "remaining_balance": None
            }
        
        # Check transaction limit
        if amount > category.max_transaction_amount:
            return {
                "valid": False,
                "reason": f"Amount {amount} exceeds maximum transaction limit of {category.max_transaction_amount}",
                "remaining_balance": None
            }
        
        # Get current year and month
        now = datetime.utcnow()
        current_year = now.year
        current_month = now.month
        
        # Get or create employee balance record
        balance = db.query(EmployeeBenefitBalance).filter(
            and_(
                EmployeeBenefitBalance.employee_id == employee_id,
                EmployeeBenefitBalance.category_id == category_id,
                EmployeeBenefitBalance.year == current_year,
                EmployeeBenefitBalance.month == current_month
            )
        ).first()
        
        if not balance:
            # Create new balance record
            balance = EmployeeBenefitBalance(
                employee_id=employee_id,
                category_id=category_id,
                year=current_year,
                month=current_month,
                annual_used=Decimal("0.00"),
                monthly_used=Decimal("0.00")
            )
            db.add(balance)
            db.flush()
        
        # Check monthly limit
        monthly_remaining = category.monthly_limit - balance.monthly_used
        if amount > monthly_remaining:
            return {
                "valid": False,
                "reason": f"Insufficient monthly balance. Remaining: {monthly_remaining}, Requested: {amount}",
                "remaining_balance": monthly_remaining
            }
        
        # Check annual limit - sum monthly_used from all months in the year
        annual_balances = db.query(EmployeeBenefitBalance).filter(
            and_(
                EmployeeBenefitBalance.employee_id == employee_id,
                EmployeeBenefitBalance.category_id == category_id,
                EmployeeBenefitBalance.year == current_year
            )
        ).all()
        
        total_annual_used = sum(b.monthly_used for b in annual_balances)
        annual_remaining = category.annual_limit - total_annual_used
        if amount > annual_remaining:
            return {
                "valid": False,
                "reason": f"Insufficient annual balance. Remaining: {annual_remaining}, Requested: {amount}",
                "remaining_balance": annual_remaining
            }
        
        # All checks passed
        return {
            "valid": True,
            "reason": None,
            "remaining_balance": min(monthly_remaining, annual_remaining)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "reason": f"Validation error: {str(e)}",
            "remaining_balance": None
        }

