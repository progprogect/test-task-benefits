"""
Reimbursement API routes.
"""
from decimal import Decimal
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.config import settings
from app.models.employee import Employee
from app.models.reimbursement_request import ReimbursementRequest, RequestStatus
from app.models.invoice import Invoice
from app.models.employee_benefit_balance import EmployeeBenefitBalance
from app.models.benefit_category import BenefitCategory
from app.schemas.request import ReimbursementResponse
from app.services.cloudinary_service import upload_file_from_bytes
from app.services.ocr_service import extract_invoice_data
from app.services.category_matcher import match_category
from app.services.validator import validate_reimbursement

router = APIRouter()


@router.post("/reimbursement/submit", response_model=ReimbursementResponse)
async def submit_reimbursement(
    employee_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Submit a reimbursement request with invoice file."""
    # Validate file type
    if not file.content_type or file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File type not allowed. Please upload JPG, PNG, or PDF")
    
    # Read file to check size
    file_content = await file.read()
    
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed size (10MB)")
    
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        # Upload file to Cloudinary (pass file_content as bytes)
        cloudinary_url, cloudinary_public_id = await upload_file_from_bytes(file_content, file.filename or "invoice")
        
        # Create reimbursement request
        request = ReimbursementRequest(
            employee_id=employee_id,
            status=RequestStatus.PROCESSING,
            amount=Decimal("0.00"),  # Will be updated after OCR
            currency="USD",  # Will be updated after OCR
            cloudinary_url=cloudinary_url,
            cloudinary_public_id=cloudinary_public_id
        )
        db.add(request)
        db.flush()
        
        # Extract invoice data using OCR
        invoice_data = await extract_invoice_data(cloudinary_url)
        
        # Update request with extracted amount and currency
        request.amount = Decimal(str(invoice_data.get("total_amount", 0)))
        request.currency = invoice_data.get("currency", "USD")
        
        # Save invoice data
        purchase_date = None
        if invoice_data.get("purchase_date"):
            try:
                purchase_date = datetime.strptime(invoice_data["purchase_date"], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                # Invalid date format, leave as None
                pass
        
        invoice = Invoice(
            request_id=request.id,
            vendor_name=invoice_data.get("vendor_name"),
            purchase_date=purchase_date,
            items=invoice_data.get("items", []),
            total_amount=request.amount,
            currency=request.currency,
            invoice_number=invoice_data.get("invoice_number"),
            extracted_text=invoice_data.get("extracted_text", "")
        )
        db.add(invoice)
        
        # Match category
        match_result = await match_category(
            db=db,
            invoice_text=invoice_data.get("extracted_text", ""),
            items=invoice_data.get("items", [])
        )
        
        category_id = None
        status = RequestStatus.PENDING_REVIEW
        
        if match_result.get("category_id") and match_result.get("confidence", 0) >= 0.7:
            category_id = UUID(match_result["category_id"])
            request.category_id = category_id
            
            # Validate reimbursement
            validation_result = await validate_reimbursement(
                db=db,
                employee_id=employee_id,
                category_id=category_id,
                amount=request.amount,
                currency=request.currency
            )
            
            if validation_result["valid"]:
                status = RequestStatus.APPROVED
                # Update balance
                now = datetime.utcnow()
                balance = db.query(EmployeeBenefitBalance).filter(
                    and_(
                        EmployeeBenefitBalance.employee_id == employee_id,
                        EmployeeBenefitBalance.category_id == category_id,
                        EmployeeBenefitBalance.year == now.year,
                        EmployeeBenefitBalance.month == now.month
                    )
                ).first()
                
                if not balance:
                    balance = EmployeeBenefitBalance(
                        employee_id=employee_id,
                        category_id=category_id,
                        year=now.year,
                        month=now.month,
                        annual_used=Decimal("0.00"),
                        monthly_used=Decimal("0.00")
                    )
                    db.add(balance)
                
                # Convert amount to USD before updating balance (all balances stored in USD)
                from app.services.currency_service import convert_to_usd
                amount_usd = await convert_to_usd(request.amount, request.currency)
                
                # Only update monthly_used - annual limit is checked by summing all months
                # Store in USD for consistent comparison
                balance.monthly_used += amount_usd
            else:
                status = RequestStatus.REJECTED
                request.rejection_reason = validation_result["reason"]
        else:
            # Low confidence or no match
            status = RequestStatus.PENDING_REVIEW
            if match_result.get("category_id"):
                category_id = UUID(match_result["category_id"])
                request.category_id = category_id
        
        request.status = status
        db.commit()
        db.refresh(request)
        
        # Build response
        remaining_balance = None
        if request.category_id and status == RequestStatus.APPROVED:
            now = datetime.utcnow()
            balance = db.query(EmployeeBenefitBalance).filter(
                and_(
                    EmployeeBenefitBalance.employee_id == employee_id,
                    EmployeeBenefitBalance.category_id == request.category_id,
                    EmployeeBenefitBalance.year == now.year,
                    EmployeeBenefitBalance.month == now.month
                )
            ).first()
            if balance:
                category = db.query(BenefitCategory).filter(
                    BenefitCategory.id == request.category_id
                ).first()
                if category:
                    # Calculate annual_used by summing all months in the year
                    annual_balances = db.query(EmployeeBenefitBalance).filter(
                        and_(
                            EmployeeBenefitBalance.employee_id == employee_id,
                            EmployeeBenefitBalance.category_id == request.category_id,
                            EmployeeBenefitBalance.year == now.year
                        )
                    ).all()
                    total_annual_used = sum(b.monthly_used for b in annual_balances)
                    
                    remaining_balance = min(
                        category.monthly_limit - balance.monthly_used,
                        category.annual_limit - total_annual_used
                    )
        
        return {
            "id": request.id,
            "employee_id": request.employee_id,
            "employee_name": employee.name,
            "employee_employee_id": employee.employee_id,
            "category_id": request.category_id,
            "category_name": request.category.name if request.category else None,
            "status": request.status,
            "amount": request.amount,
            "currency": request.currency,
            "cloudinary_url": request.cloudinary_url,
            "submission_timestamp": request.submission_timestamp,
            "rejection_reason": request.rejection_reason,
            "invoice": {
                "vendor_name": invoice.vendor_name,
                "purchase_date": invoice.purchase_date,
                "items": invoice.items,
                "total_amount": invoice.total_amount,
                "currency": invoice.currency,
                "invoice_number": invoice.invoice_number,
                "extracted_text": invoice.extracted_text
            } if invoice else None,
            "remaining_balance": remaining_balance,  # Always in USD
            "remaining_balance_currency": "USD"  # Explicitly indicate USD
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (they already have proper status codes)
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        # Log the full error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing reimbursement: {str(e)}")
        print(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process reimbursement: {str(e)}"
        )


@router.get("/reimbursement/{request_id}", response_model=ReimbursementResponse)
async def get_reimbursement(request_id: UUID, db: Session = Depends(get_db)):
    """Get reimbursement request details."""
    request = db.query(ReimbursementRequest).filter(ReimbursementRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Reimbursement request not found")
    
    invoice = db.query(Invoice).filter(Invoice.request_id == request_id).first()
    
    # Calculate remaining balance if approved
    remaining_balance = None
    if request.status == RequestStatus.APPROVED and request.category_id:
        now = datetime.utcnow()
        balance = db.query(EmployeeBenefitBalance).filter(
            and_(
                EmployeeBenefitBalance.employee_id == request.employee_id,
                EmployeeBenefitBalance.category_id == request.category_id,
                EmployeeBenefitBalance.year == now.year,
                EmployeeBenefitBalance.month == now.month
            )
        ).first()
        if balance and request.category:
            # Calculate annual_used by summing all months in the year
            annual_balances = db.query(EmployeeBenefitBalance).filter(
                and_(
                    EmployeeBenefitBalance.employee_id == request.employee_id,
                    EmployeeBenefitBalance.category_id == request.category_id,
                    EmployeeBenefitBalance.year == now.year
                )
            ).all()
            total_annual_used = sum(b.monthly_used for b in annual_balances)
            
            remaining_balance = min(
                request.category.monthly_limit - balance.monthly_used,
                request.category.annual_limit - total_annual_used
            )
    
    return {
        "id": request.id,
        "employee_id": request.employee_id,
        "employee_name": request.employee.name,
        "employee_employee_id": request.employee.employee_id,
        "category_id": request.category_id,
        "category_name": request.category.name if request.category else None,
        "status": request.status,
        "amount": request.amount,
        "currency": request.currency,
        "cloudinary_url": request.cloudinary_url,
        "submission_timestamp": request.submission_timestamp,
        "rejection_reason": request.rejection_reason,
        "invoice": {
            "vendor_name": invoice.vendor_name,
            "purchase_date": invoice.purchase_date,
            "items": invoice.items,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "invoice_number": invoice.invoice_number,
            "extracted_text": invoice.extracted_text
        } if invoice else None,
        "remaining_balance": remaining_balance
    }

