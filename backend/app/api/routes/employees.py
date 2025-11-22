"""
Employees API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeResponse

router = APIRouter()


@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(db: Session = Depends(get_db)):
    """Get list of all employees."""
    employees = db.query(Employee).all()
    return employees

