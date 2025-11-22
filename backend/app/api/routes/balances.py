"""
Balances API routes.
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.database import get_db
from app.models.employee import Employee
from app.models.employee_benefit_balance import EmployeeBenefitBalance
from app.models.benefit_category import BenefitCategory
from app.schemas.balance import BalanceResponse

router = APIRouter()


@router.get("/employees/{employee_id}/balances", response_model=List[BalanceResponse])
async def get_employee_balances(
    employee_id: UUID,
    year: Optional[int] = Query(None, description="Year (defaults to current year)"),
    month: Optional[int] = Query(None, description="Month (defaults to current month)"),
    db: Session = Depends(get_db)
):
    """Get employee benefit balances for all categories."""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Use current year/month if not provided
    if year is None or month is None:
        now = datetime.utcnow()
        year = year or now.year
        month = month or now.month
    
    # Get all categories
    categories = db.query(BenefitCategory).all()
    
    balances = []
    for category in categories:
        # Get balance record for this category
        balance = db.query(EmployeeBenefitBalance).filter(
            and_(
                EmployeeBenefitBalance.employee_id == employee_id,
                EmployeeBenefitBalance.category_id == category.id,
                EmployeeBenefitBalance.year == year,
                EmployeeBenefitBalance.month == month
            )
        ).first()
        
        monthly_used = Decimal("0.00")
        if balance:
            monthly_used = balance.monthly_used
        
        # Calculate annual_used by summing all months in the year
        annual_balances = db.query(EmployeeBenefitBalance).filter(
            and_(
                EmployeeBenefitBalance.employee_id == employee_id,
                EmployeeBenefitBalance.category_id == category.id,
                EmployeeBenefitBalance.year == year
            )
        ).all()
        annual_used = sum(b.monthly_used for b in annual_balances)
        
        annual_remaining = category.annual_limit - annual_used
        monthly_remaining = category.monthly_limit - monthly_used
        
        balances.append({
            "category_id": category.id,
            "category_name": category.name,
            "year": year,
            "month": month,
            "annual_limit": category.annual_limit,
            "monthly_limit": category.monthly_limit,
            "annual_used": annual_used,
            "monthly_used": monthly_used,
            "annual_remaining": annual_remaining,
            "monthly_remaining": monthly_remaining
        })
    
    return balances

