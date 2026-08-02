"""
Validation utilities for WiseWallet.

This module provides validation functions for:
- CSV file validation
- Data type validation
- Currency validation
- Amount validation
- Date validation
- Transaction validation

All validators return (is_valid, error_message) tuples for easy error handling.
"""

import pandas as pd
import re
from datetime import datetime
from typing import Tuple, Optional, List, Any
from config.currencies import SUPPORTED_CURRENCIES


class Validators:
    """
    Collection of validation functions for financial data.
    Each function returns (is_valid: bool, error_message: Optional[str])
    """
    
    # ===== FILE VALIDATION =====
    
    @staticmethod
    def validate_csv_file(file) -> Tuple[bool, Optional[str]]:
        """
        Validate that the uploaded file is a CSV.
        
        Args:
            file: Uploaded file object from Streamlit
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if file is None:
            return False, "No file uploaded"
        
        # Check file extension
        if not file.name.lower().endswith('.csv'):
            return False, f"File must be a CSV. Got: {file.name.split('.')[-1]}"
        
        # Check file size (max 10MB)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return False, f"File too large. Max size: 10MB. Got: {file_size / (1024*1024):.2f}MB"
        
        return True, None
    
    @staticmethod
    def validate_csv_columns(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validate that the CSV has the required columns.
        
        Required columns: Date, Description, Amount, Type
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_columns = ['Date', 'Description', 'Amount', 'Type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        return True, None
    
    @staticmethod
    def validate_csv_empty(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validate that the CSV is not empty.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if df.empty:
            return False, "CSV file is empty"
        
        return True, None
    
    # ===== TRANSACTION VALIDATION =====
    
    @staticmethod
    def validate_date(date_value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a date value.
        
        Args:
            date_value: The date to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pd.isna(date_value):
            return False, "Date cannot be null"
        
        # Try to convert to datetime
        try:
            pd.to_datetime(date_value)
            return True, None
        except:
            return False, f"Invalid date format: {date_value}"
    
    @staticmethod
    def validate_amount(amount: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate an amount value.
        
        Args:
            amount: The amount to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pd.isna(amount):
            return False, "Amount cannot be null"
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return False, f"Amount must be positive. Got: {amount_float}"
            if amount_float > 1e12:  # Max 1 trillion
                return False, f"Amount too large: {amount_float}"
            return True, None
        except (ValueError, TypeError):
            return False, f"Invalid amount format: {amount}"
    
    @staticmethod
    def validate_transaction_type(transaction_type: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a transaction type (Credit/Debit).
        
        Args:
            transaction_type: The type to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pd.isna(transaction_type):
            return False, "Transaction type cannot be null"
        
        type_str = str(transaction_type).strip().upper()
        if type_str not in ['CREDIT', 'DEBIT']:
            return False, f"Invalid transaction type: {type_str}. Must be 'Credit' or 'Debit'"
        
        return True, None
    
    @staticmethod
    def validate_description(description: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a transaction description.
        
        Args:
            description: The description to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pd.isna(description):
            return False, "Description cannot be null"
        
        desc_str = str(description).strip()
        if len(desc_str) == 0:
            return False, "Description cannot be empty"
        
        if len(desc_str) > 500:
            return False, f"Description too long: {len(desc_str)} characters. Max: 500"
        
        return True, None
    
    # ===== CURRENCY VALIDATION =====
    
    @staticmethod
    def validate_currency_code(currency_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a currency code.
        
        Args:
            currency_code: The currency code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not currency_code:
            return False, "Currency code cannot be empty"
        
        currency_code = currency_code.upper()
        if currency_code not in SUPPORTED_CURRENCIES:
            supported = ', '.join(SUPPORTED_CURRENCIES.keys())
            return False, f"Unsupported currency: {currency_code}. Supported: {supported}"
        
        return True, None
    
    @staticmethod
    def validate_currency_amount(amount: float, currency_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that an amount is valid for a given currency.
        
        Args:
            amount: The amount to validate
            currency_code: The currency code
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # First validate the amount
        amount_valid, amount_error = Validators.validate_amount(amount)
        if not amount_valid:
            return amount_valid, amount_error
        
        # Then validate the currency
        currency_valid, currency_error = Validators.validate_currency_code(currency_code)
        if not currency_valid:
            return currency_valid, currency_error
        
        return True, None
    
    # ===== DATA FRAME VALIDATION =====
    
    @staticmethod
    def validate_transaction_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate all transactions in a DataFrame.
        
        Args:
            df: DataFrame with transaction data
            
        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []
        
        if df.empty:
            return False, ["DataFrame is empty"]
        
        # Check required columns
        cols_valid, col_error = Validators.validate_csv_columns(df)
        if not cols_valid:
            return False, [col_error]
        
        # Check each row
        for idx, row in df.iterrows():
            row_errors = []
            
            # Validate date
            date_valid, date_error = Validators.validate_date(row.get('Date'))
            if not date_valid:
                row_errors.append(f"Row {idx}: Date - {date_error}")
            
            # Validate amount
            amount_valid, amount_error = Validators.validate_amount(row.get('Amount'))
            if not amount_valid:
                row_errors.append(f"Row {idx}: Amount - {amount_error}")
            
            # Validate type
            type_valid, type_error = Validators.validate_transaction_type(row.get('Type'))
            if not type_valid:
                row_errors.append(f"Row {idx}: Type - {type_error}")
            
            # Validate description
            desc_valid, desc_error = Validators.validate_description(row.get('Description'))
            if not desc_valid:
                row_errors.append(f"Row {idx}: Description - {desc_error}")
            
            errors.extend(row_errors)
        
        return len(errors) == 0, errors
    
    # ===== INPUT VALIDATION =====
    
    @staticmethod
    def validate_numeric_input(value: Any, min_value: float = 0, 
                              max_value: float = float('inf')) -> Tuple[bool, Optional[str]]:
        """
        Validate a numeric input.
        
        Args:
            value: The value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            num_value = float(value)
            if num_value < min_value:
                return False, f"Value must be at least {min_value}"
            if num_value > max_value:
                return False, f"Value must be at most {max_value}"
            return True, None
        except (ValueError, TypeError):
            return False, f"Invalid number: {value}"
    
    @staticmethod
    def validate_string_input(value: Any, min_length: int = 1, 
                             max_length: int = 500) -> Tuple[bool, Optional[str]]:
        """
        Validate a string input.
        
        Args:
            value: The value to validate
            min_length: Minimum string length
            max_length: Maximum string length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if pd.isna(value):
            return False, "Value cannot be null"
        
        str_value = str(value).strip()
        if len(str_value) < min_length:
            return False, f"Value must be at least {min_length} characters"
        if len(str_value) > max_length:
            return False, f"Value must be at most {max_length} characters"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an email address.
        
        Args:
            email: The email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email cannot be empty"
        
        # Simple email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, f"Invalid email format: {email}"
        
        return True, None
    
    # ===== BATCH VALIDATION =====
    
    @staticmethod
    def validate_batch(data: List[Any], validator_func) -> Tuple[bool, List[str]]:
        """
        Validate a batch of items using a validator function.
        
        Args:
            data: List of items to validate
            validator_func: Function that returns (is_valid, error_message)
            
        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []
        for idx, item in enumerate(data):
            is_valid, error = validator_func(item)
            if not is_valid:
                errors.append(f"Item {idx}: {error}")
        
        return len(errors) == 0, errors
    
    # ===== DATE RANGE VALIDATION =====
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, Optional[str]]:
        """
        Validate that a date range is valid.
        
        Args:
            start_date: The start date
            end_date: The end date
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_date > end_date:
            return False, f"Start date ({start_date}) cannot be after end date ({end_date})"
        
        # Check if the date range is too large
        date_diff = (end_date - start_date).days
        if date_diff > 365 * 10:  # Max 10 years
            return False, f"Date range too large: {date_diff} days. Max: 3650 days"
        
        return True, None


# ===== CONVENIENCE FUNCTIONS =====

def safe_validate(validator_func, *args) -> Tuple[bool, Optional[str]]:
    """
    Safely call a validator function and handle exceptions.
    
    Args:
        validator_func: The validator function to call
        *args: Arguments to pass to the validator
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        return validator_func(*args)
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_all_transactions(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate all transactions in a DataFrame.
    
    Args:
        df: DataFrame with transaction data
        
    Returns:
        Tuple of (all_valid, list_of_errors)
    """
    return Validators.validate_transaction_dataframe(df)


def is_valid_currency_code(currency_code: str) -> bool:
    """
    Simple check if a currency code is valid.
    
    Args:
        currency_code: The currency code to check
        
    Returns:
        Boolean indicating if the currency is valid
    """
    is_valid, _ = Validators.validate_currency_code(currency_code)
    return is_valid


def clean_transaction_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate transaction data.
    
    This function:
    1. Validates all transactions
    2. Removes invalid rows
    3. Standardizes formats
    
    Args:
        df: Raw transaction DataFrame
        
    Returns:
        Cleaned DataFrame with only valid transactions
    """
    clean_df = df.copy()
    
    # Remove rows with missing required columns
    required = ['Date', 'Description', 'Amount', 'Type']
    clean_df = clean_df.dropna(subset=required)
    
    # Convert and validate date
    clean_df['Date'] = pd.to_datetime(clean_df['Date'], errors='coerce')
    clean_df = clean_df.dropna(subset=['Date'])
    
    # Convert and validate amount
    clean_df['Amount'] = pd.to_numeric(clean_df['Amount'], errors='coerce')
    clean_df = clean_df.dropna(subset=['Amount'])
    clean_df = clean_df[clean_df['Amount'] > 0]
    
    # Validate type
    clean_df['Type'] = clean_df['Type'].str.strip().str.upper()
    clean_df = clean_df[clean_df['Type'].isin(['CREDIT', 'DEBIT'])]
    
    # Clean description
    clean_df['Description'] = clean_df['Description'].str.strip()
    clean_df = clean_df[clean_df['Description'].str.len() > 0]
    
    # Remove duplicates
    clean_df = clean_df.drop_duplicates()
    
    return clean_df


# ===== USAGE EXAMPLE =====
"""
How to use these validators:

from utils.validators import Validators, clean_transaction_data

# Validate a single transaction
amount_valid, error = Validators.validate_amount(100.50)
if not amount_valid:
    print(f"Error: {error}")

# Validate a CSV file
file_valid, error = Validators.validate_csv_file(uploaded_file)
if not file_valid:
    st.error(error)

# Validate all transactions
df = pd.read_csv('transactions.csv')
all_valid, errors = Validators.validate_transaction_dataframe(df)
if not all_valid:
    for error in errors:
        print(error)
else:
    print("All transactions are valid!")

# Clean and validate data
clean_df = clean_transaction_data(df)
print(f"Cleaned {len(clean_df)} valid transactions")
"""