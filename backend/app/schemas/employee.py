"""
Employee Pydantic schemas.
"""
from uuid import UUID
from pydantic import BaseModel


class EmployeeBase(BaseModel):
    """Base employee schema."""
    name: str
    employee_id: str


class EmployeeCreate(EmployeeBase):
    """Schema for creating an employee."""
    pass


class EmployeeResponse(EmployeeBase):
    """Schema for employee response."""
    id: UUID
    
    class Config:
        from_attributes = True

