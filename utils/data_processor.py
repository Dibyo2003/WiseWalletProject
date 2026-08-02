"""
Data processing module for cleaning and preparing financial data.

Handles:
- CSV validation and loading
- Data cleaning (missing values, duplicates)
- Transaction categorization
- Date parsing and formatting
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config.currencies import DEFAULT_CURRENCY
from services.transaction_analyzer import TransactionCategorizer

class DataProcessor:
    """Process and clean financial transaction data."""
    
    def __init__(self):
        """Initialize the data processor with a categorizer."""
        self.categorizer = TransactionCategorizer()
    
    def load_csv(self, file) -> pd.DataFrame:
        """
        Load and validate a CSV file.
        
        Args:
            file: Uploaded CSV file object
            
        Returns:
            DataFrame with cleaned data
            
        Raises:
            ValueError: If the CSV format is invalid
        """
        try:
            df = pd.read_csv(file)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {e}")
        
        # Validate required columns
        required_columns = ['Date', 'Description', 'Amount', 'Type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the transaction data.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Make a copy to avoid modifying the original
        df_clean = df.copy()
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        # Convert date to datetime
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')
        
        # Remove rows with invalid dates
        df_clean = df_clean.dropna(subset=['Date'])
        
        # Clean amount column
        df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce')
        df_clean = df_clean.dropna(subset=['Amount'])
        
        # Ensure Amount is positive
        df_clean['Amount'] = df_clean['Amount'].abs()
        
        # Clean Type column
        df_clean['Type'] = df_clean['Type'].str.strip().str.upper()
        valid_types = ['CREDIT', 'DEBIT']
        df_clean = df_clean[df_clean['Type'].isin(valid_types)]
        
        # Clean Description
        df_clean['Description'] = df_clean['Description'].str.strip()
        
        # Categorize transactions
        df_clean['Category'] = df_clean['Description'].apply(self.categorizer.categorize)
        
        # Add useful derived columns
        df_clean['Month'] = df_clean['Date'].dt.to_period('M')
        df_clean['Year'] = df_clean['Date'].dt.year
        df_clean['MonthName'] = df_clean['Date'].dt.strftime('%B')
        df_clean['Day'] = df_clean['Date'].dt.day
        
        return df_clean
    
    def process_uploaded_file(self, file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Process an uploaded CSV file with full pipeline.
        
        Args:
            file: Uploaded CSV file
            
        Returns:
            Tuple of (processed DataFrame, error_message)
        """
        try:
            df = self.load_csv(file)
            df_clean = self.clean_data(df)
            return df_clean, None
        except Exception as e:
            return None, str(e)

    def get_original_currency(self, df: pd.DataFrame) -> str:
        """
        Try to detect the original currency from the data.
        Returns the default currency if detection fails.
        """
        # In a real implementation, you might detect from the data or ask the user
        # For now, we'll assume the default currency
        return DEFAULT_CURRENCY