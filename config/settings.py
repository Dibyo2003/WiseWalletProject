"""
Application settings and configuration.

Centralized configuration for the WiseWallet application.
All settings can be overridden via environment variables.
"""

import os
from typing import Optional

class Settings:
    """Application settings class."""
    
    # API Keys (should be set via environment variables)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Exchange Rate API
    EXCHANGE_RATE_API_URL: str = "https://api.exchangerate-api.com/v4/latest/"
    EXCHANGE_RATE_CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Data Processing
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".csv"]
    
    # AI Settings
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    AI_MAX_TOKENS: int = 1000
    
    # Application
    APP_NAME: str = "WiseWallet"
    APP_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_PATH: str = "wisewallet.db"

settings = Settings()