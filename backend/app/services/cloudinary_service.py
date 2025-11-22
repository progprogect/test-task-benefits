"""
Cloudinary service for file uploads.
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from typing import Union

from app.config import settings


# Configure Cloudinary
# Prefer CLOUDINARY_URL if provided, otherwise use individual variables
if settings.CLOUDINARY_URL:
    cloudinary.config(settings.CLOUDINARY_URL)
else:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )


async def upload_file(file: UploadFile) -> tuple[str, str]:
    """
    Upload file to Cloudinary from UploadFile object.
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Tuple of (url, public_id)
        
    Raises:
        HTTPException: If upload fails
    """
    file_content = await file.read()
    return await upload_file_from_bytes(file_content, file.filename or "invoice")


async def upload_file_from_bytes(file_content: bytes, filename: str = "invoice") -> tuple[str, str]:
    """
    Upload file to Cloudinary from bytes.
    
    Args:
        file_content: File content as bytes
        filename: Original filename (optional)
        
    Returns:
        Tuple of (url, public_id)
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_content,
            resource_type="auto",  # Auto-detect image/pdf
            folder="benefit-reimbursements",
        )
        
        url = upload_result.get("secure_url") or upload_result.get("url")
        public_id = upload_result.get("public_id")
        
        if not url or not public_id:
            raise HTTPException(status_code=500, detail="Failed to get upload result from Cloudinary")
        
        return url, public_id
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to Cloudinary: {str(e)}"
        )

