"""
Currency conversion service.
Converts amounts from any currency to USD for comparison with limits.
"""
import httpx
from decimal import Decimal, ROUND_DOWN
from typing import Optional
from fastapi import HTTPException

from app.config import settings


# Cache for exchange rates (simple in-memory cache)
_exchange_rate_cache = {}
_cache_timestamp = None
CACHE_DURATION_SECONDS = 3600  # Cache for 1 hour


async def get_exchange_rate_to_usd(currency: str) -> Decimal:
    """
    Get exchange rate from given currency to USD.
    
    Args:
        currency: Currency code (e.g., 'RUB', 'EUR', 'USD')
        
    Returns:
        Exchange rate (how many USD per 1 unit of currency)
        
    Raises:
        HTTPException: If currency conversion fails
    """
    currency = currency.upper()
    
    # USD to USD is 1.0
    if currency == "USD":
        return Decimal("1.0")
    
    # Check cache
    if currency in _exchange_rate_cache:
        return _exchange_rate_cache[currency]
    
    try:
        # Use exchangerate-api.com (free tier: 1500 requests/month)
        # Alternative: can use fixer.io, currencyapi.net, or other free APIs
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Using exchangerate-api.com free endpoint
            # Note: For production, you might want to add EXCHANGE_RATE_API_KEY to settings
            url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Get USD rate (how many USD per 1 unit of currency)
                usd_rate = Decimal(str(data["rates"]["USD"]))
                
                # Cache the rate
                _exchange_rate_cache[currency] = usd_rate
                
                return usd_rate
            else:
                # Fallback: try alternative API or use fixed rates for common currencies
                return await _get_fallback_rate(currency)
                
    except Exception as e:
        # Fallback to hardcoded rates for common currencies if API fails
        print(f"Exchange rate API error: {str(e)}, using fallback")
        return await _get_fallback_rate(currency)


async def _get_fallback_rate(currency: str) -> Decimal:
    """
    Fallback exchange rates for common currencies.
    These are approximate rates - should be updated periodically.
    """
    fallback_rates = {
        "RUB": Decimal("0.011"),  # ~90 RUB per USD
        "EUR": Decimal("1.10"),   # ~0.91 EUR per USD
        "GBP": Decimal("1.27"),   # ~0.79 GBP per USD
        "JPY": Decimal("0.0067"), # ~150 JPY per USD
        "CNY": Decimal("0.14"),   # ~7 CNY per USD
        "INR": Decimal("0.012"),  # ~83 INR per USD
        "CAD": Decimal("0.74"),   # ~1.35 CAD per USD
        "AUD": Decimal("0.66"),  # ~1.52 AUD per USD
    }
    
    rate = fallback_rates.get(currency.upper())
    if rate:
        print(f"Using fallback rate for {currency}: {rate}")
        return rate
    
    # If currency not found, raise error
    raise HTTPException(
        status_code=400,
        detail=f"Currency {currency} not supported. Please contact support."
    )


async def convert_to_usd(amount: Decimal, currency: str) -> Decimal:
    """
    Convert amount from given currency to USD.
    
    Args:
        amount: Amount in source currency
        currency: Source currency code
        
    Returns:
        Amount in USD (rounded to 2 decimal places)
    """
    if currency.upper() == "USD":
        return amount
    
    exchange_rate = await get_exchange_rate_to_usd(currency)
    usd_amount = amount * exchange_rate
    
    # Round down to 2 decimal places (more conservative for limits)
    return usd_amount.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

