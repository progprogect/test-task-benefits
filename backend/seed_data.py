"""
Seed script to populate database with initial data.
"""
import sys
from decimal import Decimal
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models.employee import Employee
from app.models.benefit_category import BenefitCategory
from app.models.category_keyword import CategoryKeyword
from app.models.employee_benefit_balance import EmployeeBenefitBalance


def seed_database():
    """Seed database with initial categories, keywords, and employees."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(BenefitCategory).count() > 0:
            print("Database already seeded. Skipping seed.")
            return
        
        # Create benefit categories
        categories_data = [
            {
                "name": "Wellness & Fitness",
                "max_transaction_amount": Decimal("500.00"),
                "annual_limit": Decimal("5000.00"),
                "monthly_limit": Decimal("500.00"),
                "keywords": ["gym", "fitness", "yoga", "workout", "exercise", "sports", "personal trainer", "fitness center"]
            },
            {
                "name": "Professional Development",
                "max_transaction_amount": Decimal("1000.00"),
                "annual_limit": Decimal("3000.00"),
                "monthly_limit": Decimal("500.00"),
                "keywords": ["course", "training", "certification", "conference", "workshop", "book", "education", "learning"]
            },
            {
                "name": "Home Office Equipment",
                "max_transaction_amount": Decimal("2000.00"),
                "annual_limit": Decimal("5000.00"),
                "monthly_limit": Decimal("1000.00"),
                "keywords": ["monitor", "keyboard", "mouse", "desk", "chair", "laptop stand", "headphones", "webcam"]
            },
            {
                "name": "Transportation",
                "max_transaction_amount": Decimal("200.00"),
                "annual_limit": Decimal("2000.00"),
                "monthly_limit": Decimal("300.00"),
                "keywords": ["taxi", "uber", "fuel", "parking", "public transport", "metro", "bus", "train"]
            },
            {
                "name": "Health & Medical",
                "max_transaction_amount": Decimal("500.00"),
                "annual_limit": Decimal("3000.00"),
                "monthly_limit": Decimal("500.00"),
                "keywords": ["doctor", "medical", "pharmacy", "prescription", "health check", "clinic", "hospital"]
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            keywords = cat_data.pop("keywords")
            category = BenefitCategory(**cat_data)
            db.add(category)
            db.flush()
            
            # Add keywords
            for keyword in keywords:
                keyword_obj = CategoryKeyword(category_id=category.id, keyword=keyword)
                db.add(keyword_obj)
            
            categories.append(category)
        
        # Create employees
        employees_data = [
            {"name": "John Smith", "employee_id": "EMP001"},
            {"name": "Sarah Johnson", "employee_id": "EMP002"},
            {"name": "Michael Brown", "employee_id": "EMP003"},
            {"name": "Emily Davis", "employee_id": "EMP004"},
            {"name": "David Wilson", "employee_id": "EMP005"}
        ]
        
        employees = []
        for emp_data in employees_data:
            employee = Employee(**emp_data)
            db.add(employee)
            db.flush()
            employees.append(employee)
        
        db.commit()
        print(f"Successfully seeded database:")
        print(f"  - {len(categories)} categories created")
        print(f"  - {len(employees)} employees created")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

