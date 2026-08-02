"""
Financial analytics service for computing KPIs and metrics.

Provides functions for calculating:
- Income, expenses, savings
- Daily averages
- Largest transactions
- Monthly trends
- Category distributions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class FinanceAnalytics:
    """Calculate financial metrics from transaction data."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with transaction data.
        
        Args:
            df: Cleaned transaction DataFrame
        """
        self.df = df
        
    def get_kpis(self) -> Dict:
        """
        Calculate key performance indicators.
        
        Returns:
            Dictionary of KPIs
        """
        income_df = self.df[self.df['Type'] == 'CREDIT']
        expense_df = self.df[self.df['Type'] == 'DEBIT']
        
        total_income = income_df['Amount'].sum()
        total_expenses = expense_df['Amount'].sum()
        savings = total_income - total_expenses
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0
        
        # Average daily spending
        if len(self.df) > 0:
            date_range = (self.df['Date'].max() - self.df['Date'].min()).days + 1
            avg_daily_spending = total_expenses / date_range if date_range > 0 else 0
        else:
            avg_daily_spending = 0
        
        # Largest expense
        largest_expense = expense_df.loc[expense_df['Amount'].idxmax()] if len(expense_df) > 0 else None
        
        # Highest income
        highest_income = income_df.loc[income_df['Amount'].idxmax()] if len(income_df) > 0 else None
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'savings': savings,
            'savings_rate': savings_rate,
            'avg_daily_spending': avg_daily_spending,
            'largest_expense': largest_expense,
            'highest_income': highest_income,
            'transaction_count': len(self.df),
            'date_range': (self.df['Date'].min(), self.df['Date'].max())
        }
    
    def get_monthly_trend(self) -> pd.DataFrame:
        """
        Calculate monthly income and expense trends.
        
        Returns:
            DataFrame with monthly aggregates
        """
        df_monthly = self.df.groupby(self.df['Date'].dt.to_period('M')).agg({
            'Amount': lambda x: x[self.df.loc[x.index, 'Type'] == 'CREDIT'].sum(),
            'Type': lambda x: (x == 'CREDIT').sum()
        }).reset_index()
        
        # Separate income and expenses
        income_expense = self.df.pivot_table(
            index=self.df['Date'].dt.to_period('M'),
            columns='Type',
            values='Amount',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        return income_expense
    
    def get_category_spending(self) -> pd.DataFrame:
        """
        Calculate spending by category.
        
        Returns:
            DataFrame with category aggregates
        """
        expense_df = self.df[self.df['Type'] == 'DEBIT']
        category_spending = expense_df.groupby('Category')['Amount'].sum().reset_index()
        category_spending = category_spending.sort_values('Amount', ascending=False)
        return category_spending
    
    def get_top_expenses(self, n: int = 10) -> pd.DataFrame:
        """
        Get the top N expenses.
        
        Args:
            n: Number of top expenses to return
            
        Returns:
            DataFrame with top expenses
        """
        expense_df = self.df[self.df['Type'] == 'DEBIT']
        top_expenses = expense_df.nlargest(n, 'Amount')[['Date', 'Description', 'Amount', 'Category']]
        return top_expenses
    
    def get_category_distribution(self) -> Dict:
        """
        Get the distribution of transactions across categories.
        
        Returns:
            Dictionary with category distributions
        """
        category_counts = self.df['Category'].value_counts().to_dict()
        return category_counts
    
    def get_filtered_data(self, month: Optional[int] = None, 
                          year: Optional[int] = None,
                          category: Optional[str] = None,
                          transaction_type: Optional[str] = None) -> pd.DataFrame:
        """
        Apply filters to the transaction data.
        
        Args:
            month: Month number (1-12)
            year: Year
            category: Category name
            transaction_type: 'CREDIT' or 'DEBIT'
            
        Returns:
            Filtered DataFrame
        """
        df_filtered = self.df.copy()
        
        if month is not None:
            df_filtered = df_filtered[df_filtered['Date'].dt.month == month]
        
        if year is not None:
            df_filtered = df_filtered[df_filtered['Date'].dt.year == year]
        
        if category is not None:
            df_filtered = df_filtered[df_filtered['Category'] == category]
        
        if transaction_type is not None:
            df_filtered = df_filtered[df_filtered['Type'] == transaction_type]
        
        return df_filtered