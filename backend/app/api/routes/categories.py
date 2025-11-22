"""
Categories API routes.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.benefit_category import BenefitCategory
from app.models.category_keyword import CategoryKeyword
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    KeywordCreate,
    KeywordResponse
)

router = APIRouter()


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """Get list of all categories with keywords."""
    categories = db.query(BenefitCategory).all()
    return categories


@router.post("/categories", response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new benefit category."""
    # Check if category with same name exists
    existing = db.query(BenefitCategory).filter(BenefitCategory.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category = BenefitCategory(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a benefit category."""
    category = db.query(BenefitCategory).filter(BenefitCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
async def delete_category(category_id: UUID, db: Session = Depends(get_db)):
    """Delete a benefit category."""
    category = db.query(BenefitCategory).filter(BenefitCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


@router.get("/categories/{category_id}/keywords", response_model=List[KeywordResponse])
async def list_keywords(category_id: UUID, db: Session = Depends(get_db)):
    """Get keywords for a category."""
    category = db.query(BenefitCategory).filter(BenefitCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category.keywords


@router.post("/categories/{category_id}/keywords", response_model=KeywordResponse)
async def create_keyword(
    category_id: UUID,
    keyword_data: KeywordCreate,
    db: Session = Depends(get_db)
):
    """Add a keyword to a category."""
    category = db.query(BenefitCategory).filter(BenefitCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if keyword already exists for this category
    existing = db.query(CategoryKeyword).filter(
        CategoryKeyword.category_id == category_id,
        CategoryKeyword.keyword == keyword_data.keyword
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Keyword already exists for this category")
    
    keyword = CategoryKeyword(category_id=category_id, keyword=keyword_data.keyword)
    db.add(keyword)
    db.commit()
    db.refresh(keyword)
    return keyword


@router.delete("/categories/{category_id}/keywords/{keyword_id}")
async def delete_keyword(
    category_id: UUID,
    keyword_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a keyword from a category."""
    keyword = db.query(CategoryKeyword).filter(
        CategoryKeyword.id == keyword_id,
        CategoryKeyword.category_id == category_id
    ).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    db.delete(keyword)
    db.commit()
    return {"message": "Keyword deleted successfully"}

