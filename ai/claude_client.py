"""
AI client for generating financial insights.

Handles communication with Claude API, prompt construction,
and response parsing for financial insights and Q&A.
"""
from dotenv import load_dotenv
load_dotenv()

import os
from typing import Dict, Optional

from google import genai

from config.settings import settings
from ai.prompts import (
    INSIGHTS_PROMPT_TEMPLATE,
    QA_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
)


class ClaudeClient:
    """Gemini client (kept same class name so rest of app doesn't change)."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        print("Gemini key loaded:", bool(self.api_key))

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("Gemini client created:", self.client is not None)
            except Exception as e:
                print("Gemini initialization failed:")
                print(e)

    def is_available(self) -> bool:
        return self.client is not None

    def generate_insights(
        self,
        data_summary: Dict,
        currency_info: Dict,
    ) -> Optional[str]:

        if not self.is_available():
            return "Gemini API not available."

        total_income = data_summary.get("total_income", 0)
        total_expenses = data_summary.get("total_expenses", 0)
        savings = data_summary.get("savings", 0)
        savings_rate = data_summary.get("savings_rate", 0)
        avg_daily_spending = data_summary.get("avg_daily_spending", 0)

        original_currency = currency_info.get("original_currency", "INR")
        display_currency = currency_info.get("display_currency", "INR")
        exchange_rate = currency_info.get("exchange_rate", 1.0)

        converted_income = total_income * exchange_rate
        converted_expenses = total_expenses * exchange_rate
        converted_savings = savings * exchange_rate
        converted_avg_daily_spending = avg_daily_spending * exchange_rate

        top_categories = data_summary.get("top_categories", [])
        top_categories_str = "\n".join(top_categories[:5])

        monthly_trend = data_summary.get("monthly_trend", [])
        monthly_trend_str = "\n".join(monthly_trend[-6:])

        largest_expense = data_summary.get("largest_expense", {})
        largest_expense_str = (
            f"{largest_expense.get('description','N/A')}: "
            f"{original_currency} {largest_expense.get('amount',0):,.2f}"
        )

        prompt = INSIGHTS_PROMPT_TEMPLATE.format(
            total_income=total_income,
            total_expenses=total_expenses,
            savings=savings,
            savings_rate=savings_rate,
            avg_daily_spending=avg_daily_spending,
            largest_expense=largest_expense_str,
            top_categories=top_categories_str,
            monthly_trend=monthly_trend_str,
            original_currency=original_currency,
            display_currency=display_currency,
            exchange_rate=exchange_rate,
            converted_income=converted_income,
            converted_expenses=converted_expenses,
            converted_savings=converted_savings,
            converted_avg_daily_spending=converted_avg_daily_spending,
        )

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
            )

            return response.text

        except Exception as e:
            return f"Error generating insights: {e}"
    
    
    def answer_question(
        self,
        question: str,
        data_summary: Dict,
        currency_info: Dict,
    ) -> Optional[str]:

        if not self.is_available():
            return "Gemini API not available."

        total_income = data_summary.get("total_income", 0)
        total_expenses = data_summary.get("total_expenses", 0)
        savings = data_summary.get("savings", 0)
        savings_rate = data_summary.get("savings_rate", 0)
        avg_daily_spending = data_summary.get("avg_daily_spending", 0)

        original_currency = currency_info.get("original_currency", "INR")
        display_currency = currency_info.get("display_currency", "INR")
        exchange_rate = currency_info.get("exchange_rate", 1.0)

        converted_income = total_income * exchange_rate
        converted_expenses = total_expenses * exchange_rate
        converted_savings = savings * exchange_rate
        converted_avg_daily_spending = avg_daily_spending * exchange_rate

        top_categories = data_summary.get("top_categories", [])
        top_categories_str = "\n".join(top_categories[:5])

        transactions = data_summary.get("transactions_sample", [])
        transactions_str = "\n".join(
            [
                f"- {t.get('Date','')}: {t.get('Description','')} - "
                f"{original_currency} {t.get('Amount',0):,.2f}"
                for t in transactions[:10]
            ]
        )

        prompt = QA_PROMPT_TEMPLATE.format(
            question=question,
            total_income=total_income,
            total_expenses=total_expenses,
            savings=savings,
            savings_rate=savings_rate,
            avg_daily_spending=avg_daily_spending,
            top_categories=top_categories_str,
            transactions=transactions_str,
            original_currency=original_currency,
            display_currency=display_currency,
            exchange_rate=exchange_rate,
            converted_income=converted_income,
            converted_expenses=converted_expenses,
            converted_savings=converted_savings,
            converted_avg_daily_spending=converted_avg_daily_spending,
        )

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
            )

            return response.text

        except Exception as e:
            return f"Error answering question: {e}"


claude_client = ClaudeClient()   
        
        
        