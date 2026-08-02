"""
Currency configuration module.

This file defines all supported currencies with their symbols, codes, and names.
Centralized configuration ensures consistency across the application.
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Currency:
    """Currency data class containing code, symbol, and name."""
    code: str
    symbol: str
    name: str

# All supported currencies with their details
SUPPORTED_CURRENCIES: Dict[str, Currency] = {
    "INR": Currency("INR", "₹", "Indian Rupee"),
    "USD": Currency("USD", "$", "US Dollar"),
    "EUR": Currency("EUR", "€", "Euro"),
    "GBP": Currency("GBP", "£", "British Pound"),
    "CNY": Currency("CNY", "¥", "Chinese Yuan"),
    "JPY": Currency("JPY", "¥", "Japanese Yen"),
    "KRW": Currency("KRW", "₩", "South Korean Won"),
    "AUD": Currency("AUD", "A$", "Australian Dollar"),
    "CAD": Currency("CAD", "C$", "Canadian Dollar"),
    "SGD": Currency("SGD", "S$", "Singapore Dollar"),
    "AED": Currency("AED", "د.إ", "UAE Dirham"),
}

# Default currency
DEFAULT_CURRENCY = "INR"

# List of currency codes for dropdown menus
CURRENCY_CODES: List[str] = list(SUPPORTED_CURRENCIES.keys())

def get_currency_symbol(code: str) -> str:
    """Get the symbol for a given currency code."""
    return SUPPORTED_CURRENCIES.get(code, Currency("USD", "$", "US Dollar")).symbol

def format_currency(amount: float, currency_code: str = DEFAULT_CURRENCY) -> str:
    """Format a currency amount with the appropriate symbol."""
    symbol = get_currency_symbol(currency_code)
    return f"{symbol}{amount:,.2f}"