"""
Category matching service using OpenAI GPT-4.
"""
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from openai import OpenAI
from fastapi import HTTPException

from app.config import settings
from app.models.benefit_category import BenefitCategory
from app.models.category_keyword import CategoryKeyword


def get_openai_client():
    """Get OpenAI client instance."""
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=settings.OPENAI_API_KEY)


async def match_category(
    db: Session,
    invoice_text: str,
    items: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Match invoice to a benefit category using GPT-4 and keywords.
    
    Args:
        db: Database session
        invoice_text: Full text extracted from invoice
        items: List of invoice items (optional)
        
    Returns:
        Dictionary with category_id, confidence, matched_keywords, reasoning
    """
    try:
        # Fetch all categories with their keywords
        categories = db.query(BenefitCategory).all()
        
        if not categories:
            return {
                "category_id": None,
                "confidence": 0.0,
                "matched_keywords": [],
                "reasoning": "No categories available in the system"
            }
        
        # Build category context with keywords
        category_context = []
        for category in categories:
            keywords = [kw.keyword for kw in category.keywords]
            category_context.append({
                "id": str(category.id),
                "name": category.name,
                "keywords": keywords
            })
        
        # Prepare items text if available
        items_text = ""
        if items:
            items_descriptions = [item.get("description", "") for item in items]
            items_text = "\nItems: " + ", ".join(items_descriptions)
        
        # Create prompt for GPT-4
        prompt = f"""Analyze the following invoice text and match it to one of the provided benefit categories based on keywords and context.

Invoice text:
{invoice_text}
{items_text}

Available categories with keywords:
{json.dumps(category_context, indent=2)}

Your task:
1. Find keywords from the categories that appear in the invoice text
2. Match the invoice to the most appropriate category
3. Provide confidence score (0.0 to 1.0)
4. List matched keywords
5. Explain your reasoning

Return JSON only:
{{
    "category_id": "uuid of matched category or null if no match",
    "confidence": 0.0-1.0,
    "matched_keywords": ["keyword1", "keyword2"],
    "reasoning": "explanation of the match"
}}

If confidence is below 0.6, set category_id to null."""
        
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a benefit category classifier. Analyze invoices and match them to appropriate benefit categories based on keywords and context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500,
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Category matching failed: {str(e)}"
        )

