"""
Currency service for handling exchange rates and conversions.

This module provides functionality for:
- Fetching live exchange rates from an API
- Converting amounts between currencies
- Caching exchange rates to reduce API calls
- Handling API failures gracefully
"""

import json
import time
from typing import Dict, Optional, Tuple
import requests
from config.currencies import SUPPORTED_CURRENCIES, DEFAULT_CURRENCY
from config.settings import settings

class CurrencyService:
    """Service for currency conversion and exchange rate management."""
    
    def __init__(self):
        """Initialize the currency service with an empty cache."""
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamp: Dict[str, float] = {}
    
    def _get_exchange_rates(self, base_currency: str) -> Optional[Dict]:
        """
        Fetch exchange rates from the API with caching.
        
        Args:
            base_currency: The base currency code (e.g., 'USD')
            
        Returns:
            Dictionary of exchange rates or None if the API call fails
        """
        # Check cache first
        cache_key = base_currency
        if cache_key in self._cache_timestamp:
            elapsed = time.time() - self._cache_timestamp[cache_key]
            if elapsed < settings.EXCHANGE_RATE_CACHE_TTL:
                return self._cache.get(cache_key)
        
        try:
            url = f"{settings.EXCHANGE_RATE_API_URL}{base_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "rates" in data:
                # Cache the response
                self._cache[cache_key] = data
                self._cache_timestamp[cache_key] = time.time()
                return data
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rates: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding exchange rates: {e}")
            return None
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get the exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate as float or None if unavailable
        """
        # If currencies are the same, return 1.0
        if from_currency == to_currency:
            return 1.0
        
        # Check if currencies are supported
        if from_currency not in SUPPORTED_CURRENCIES:
            return None
        if to_currency not in SUPPORTED_CURRENCIES:
            return None
        
        # Try to get rates with the source currency as base
        rates_data = self._get_exchange_rates(from_currency)
        if rates_data:
            rates = rates_data.get("rates", {})
            if to_currency in rates:
                return rates[to_currency]
        
        # If the API call with from_currency fails, try with to_currency
        rates_data = self._get_exchange_rates(to_currency)
        if rates_data:
            rates = rates_data.get("rates", {})
            if from_currency in rates:
                return 1.0 / rates[from_currency]
        
        return None
    
    def convert_amount(self, amount: float, from_currency: str, 
                       to_currency: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert an amount from one currency to another.
        
        Args:
            amount: The amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Tuple of (converted_amount, exchange_rate) or (None, None) if conversion fails
        """
        if from_currency == to_currency:
            return amount, 1.0
        
        exchange_rate = self.get_exchange_rate(from_currency, to_currency)
        if exchange_rate is None:
            return None, None
        
        converted_amount = amount * exchange_rate
        return converted_amount, exchange_rate
    
    def get_currency_timestamp(self, base_currency: str) -> Optional[str]:
        """Get the timestamp of the exchange rate for a given base currency."""
        rates_data = self._cache.get(base_currency)
        if rates_data:
            return rates_data.get("date")
        return None

# Singleton instance for the application
currency_service = CurrencyService()