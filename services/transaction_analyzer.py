"""
Transaction categorization service.

Uses keyword matching to categorize transactions into predefined categories.
The keyword list is easily configurable and extendable.
"""

from typing import Dict, List

class TransactionCategorizer:
    """Categorize transactions based on description keywords."""
    
    # Category definitions with associated keywords
    CATEGORY_KEYWORDS: Dict[str, List[str]] = {
        'Food': ['food', 'restaurant', 'cafe', 'coffee', 'lunch', 'dinner', 'breakfast', 
                 'pizza', 'burger', 'meal', 'snack', 'grocery', 'supermarket', 'store'],
        'Transport': ['uber', 'ola', 'taxi', 'metro', 'bus', 'train', 'flight', 'fuel', 
                      'petrol', 'diesel', 'gas', 'transport', 'commute', 'parking', 'toll'],
        'Shopping': ['amazon', 'flipkart', 'mall', 'retail', 'bazaar', 'department', 
                     'shop', 'purchase', 'clothing', 'apparel', 'footwear', 'accessories'],
        'Bills': ['electricity', 'water', 'gas', 'utility', 'bill', 'maintenance', 
                  'rent', 'emi', 'loan', 'mortgage', 'property', 'tax'],
        'Healthcare': ['hospital', 'clinic', 'doctor', 'medical', 'pharmacy', 'chemist', 
                       'health', 'insurance', 'medicare', 'dental', 'vision', 'therapy'],
        'Entertainment': ['netflix', 'amazon prime', 'hotstar', 'spotify', 'concert', 
                         'movie', 'cinema', 'theatre', 'game', 'event', 'show', 'ticket'],
        'Salary': ['salary', 'wage', 'payroll', 'income', 'earnings', 'pay', 'bonus', 
                   'commission', 'freelance', 'consulting', 'contract'],
        'Investment': ['mutual fund', 'stocks', 'shares', 'bond', 'deposit', 'saving', 
                       'investment', 'sip', 'dividend', 'interest', 'return'],
        'Education': ['tuition', 'fees', 'course', 'training', 'workshop', 'seminar', 
                      'book', 'education', 'university', 'college', 'school', 'class'],
        'Travel': ['hotel', 'booking', 'airbnb', 'travel', 'tour', 'vacation', 'holiday', 
                   'trip', 'resort', 'destination', 'journey', 'cruise'],
        'Subscriptions': ['subscription', 'renewal', 'membership', 'premium', 'monthly', 
                          'annual', 'fee', 'service', 'app', 'software'],
        'Other': []  # Default category
    }
    
    def __init__(self):
        """Initialize the categorizer with keyword mappings."""
        # Convert all keywords to lowercase for case-insensitive matching
        self.keyword_mappings = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                self.keyword_mappings[keyword.lower()] = category
    
    def categorize(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description
            
        Returns:
            Category name
        """
        if pd.isna(description):
            return 'Other'
        
        description_lower = description.lower()
        
        # Check each keyword
        for keyword, category in self.keyword_mappings.items():
            if keyword in description_lower:
                return category
        
        return 'Other'
    
    def add_category(self, category: str, keywords: List[str]):
        """
        Add a new category or add keywords to an existing category.
        
        Args:
            category: Category name
            keywords: List of keywords for this category
        """
        if category not in self.CATEGORY_KEYWORDS:
            self.CATEGORY_KEYWORDS[category] = []
        
        self.CATEGORY_KEYWORDS[category].extend(keywords)
        
        # Update keyword mappings
        for keyword in keywords:
            self.keyword_mappings[keyword.lower()] = category

# Import pandas for type checking
import pandas as pd