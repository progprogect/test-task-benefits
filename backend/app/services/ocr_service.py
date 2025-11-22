"""
OCR service using OpenAI Vision API.
"""
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from fastapi import HTTPException

from app.config import settings


def get_openai_client():
    """Get OpenAI client instance."""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


async def extract_invoice_data(image_url: str) -> Dict[str, Any]:
    """
    Extract invoice data from image using OpenAI Vision API.
    
    Args:
        image_url: URL of the invoice image
        
    Returns:
        Dictionary with extracted invoice data
        
    Raises:
        HTTPException: If OCR fails
    """
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Extract the following information from this invoice/receipt image and return it as JSON:
{
    "vendor_name": "name of the merchant/vendor",
    "purchase_date": "YYYY-MM-DD format or null if not found",
    "items": [
        {
            "description": "item description",
            "amount": "amount as number or null"
        }
    ],
    "total_amount": "total amount as number",
    "currency": "currency code (USD, EUR, etc.)",
    "invoice_number": "invoice/receipt number or null if not found",
    "extracted_text": "full text content extracted from the invoice"
}

Be as accurate as possible. If a field is not found, use null."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content
        
        # Try to parse JSON (might be wrapped in markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        invoice_data = json.loads(content)
        
        return invoice_data
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse OCR response as JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR extraction failed: {str(e)}"
        )

