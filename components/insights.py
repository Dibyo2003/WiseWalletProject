"""
AI Insights component for financial analysis and Q&A.

Uses Claude AI to generate:
- Financial insights
- Spending recommendations
- Q&A about financial data
"""

import streamlit as st
from ai.claude_client import claude_client
from services.finance_analytics import FinanceAnalytics
from dotenv import load_dotenv
import os

load_dotenv()

print("ENV TEST:", os.getenv("ANTHROPIC_API_KEY"))
def render_insights(df, original_currency, display_currency, exchange_rate=1.0):
    """
    Render AI insights and Q&A panel.
    
    Args:
        df: Transaction DataFrame
        original_currency: Original currency code
        display_currency: Display currency code
        exchange_rate: Exchange rate for conversion
    """
    st.markdown("<h1 class='dashboard-title'>🧠 AI Insights</h1>", unsafe_allow_html=True)
    
    # Check if AI is available
    if not claude_client.is_available():
        st.warning("⚠️ Claude API key not found. Please set your ANTHROPIC_API_KEY in the .env file.")
        st.info("Without AI, you can still use the dashboard and analytics features.")
        return
    
    # Prepare data summary for AI
    analytics = FinanceAnalytics(df)
    kpis = analytics.get_kpis()
    
    # Get top categories
    category_data = analytics.get_category_spending()
    top_categories = []
    for _, row in category_data.head(5).iterrows():
        top_categories.append(f"{row['Category']}: {original_currency} {row['Amount']:,.2f} ({display_currency} {row['Amount'] * exchange_rate:,.2f})")
    
    # Get monthly trend
    monthly_data = analytics.get_monthly_trend()
    monthly_trend = []
    for _, row in monthly_data.tail(6).iterrows():
        monthly_trend.append(f"{row['Date']}: Income {original_currency} {row['CREDIT']:,.2f}, Expenses {original_currency} {row['DEBIT']:,.2f}")
    
    # Get largest expense
    largest_expense = kpis.get('largest_expense')
    largest_expense_info = {
        'description': largest_expense['Description'] if largest_expense is not None else 'N/A',
        'amount': largest_expense['Amount'] if largest_expense is not None else 0,
        'category': largest_expense['Category'] if largest_expense is not None else 'N/A'
    }
    
    # Prepare data summary
    data_summary = {
        'total_income': kpis['total_income'],
        'total_expenses': kpis['total_expenses'],
        'savings': kpis['savings'],
        'savings_rate': kpis['savings_rate'],
        'avg_daily_spending': kpis['avg_daily_spending'],
        'largest_expense': largest_expense_info,
        'top_categories': top_categories,
        'monthly_trend': monthly_trend,
        'transactions_sample': df.head(10).to_dict('records')
    }
    
    currency_info = {
        'original_currency': original_currency,
        'display_currency': display_currency,
        'exchange_rate': exchange_rate
    }
    
    # Generate Insights
    st.markdown("### 💡 Financial Insights")
    
    with st.spinner("Analyzing your financial data..."):
        # Generate insights
        insights = claude_client.generate_insights(data_summary, currency_info)
    import re

    insights = re.sub(r"\n{3,}", "\n\n", insights)
    if insights:
        st.markdown(f"""
        <div class="ai-insight-card fade-in">
            <h3 style="margin-bottom: 12px;">
            <div style="white-space:pre-wrap; line-height: 1.6; color: rgba(255,255,255,0.9);">
                {insights.strip()}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Unable to generate insights at this time. Please try again later.")
    
    # Q&A Section
    st.markdown("---")
    st.markdown("### ❓ Ask WiseWallet")
    st.markdown("""
    <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin-bottom: 16px;">
        Ask any question about your spending habits and get instant AI-powered answers.
    </p>
    """, unsafe_allow_html=True)
    
    # Create a form for the Q&A
    with st.form(key="qa_form"):
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input(
                "Your question",
                placeholder="e.g., Where did I spend the most money?",
                label_visibility="collapsed"
            )
        with col2:
            submit_question = st.form_submit_button(
                "Ask 💬",
                type="primary",
                use_container_width=True
            )
    
    # Process the question
    if submit_question and question:
        with st.spinner("🤔 Thinking about your question..."):
            answer = claude_client.answer_question(question, data_summary, currency_info)
        
        if answer:
            st.markdown(f"""
            <div class="ai-insight-card" style="margin-top: 12px; border-color: rgba(108,99,255,0.5);">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="font-size: 20px;">💬</span>
                    <span style="font-weight: 600; font-size: 16px;">Answer</span>
                </div>
                <div style="white-space:pre-wrap; line-height: 1.6; color: rgba(255,255,255,0.9);">
                    {answer.strip()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Unable to answer your question. Please try again.")
    
    elif submit_question and not question:
        st.warning("⚠️ Please enter a question first.")
    
    # Quick question suggestions
    st.markdown("---")
    st.markdown("### 🔍 Quick Questions to Ask")
    
    # Create clickable buttons for quick questions
    col1, col2, col3 = st.columns(3)
    
    quick_questions = [
        ("💰 Where did I spend the most?", "Where did I spend the most money?"),
        ("💎 How much did I save?", "How much did I save this month?"),
        ("📊 Which month was most expensive?", "Which month was most expensive?")
    ]
    
    for col, (label, q) in zip([col1, col2, col3], quick_questions):
        with col:
            if st.button(label, key=f"quick_{label}", use_container_width=True):
                with st.spinner("🤔 Thinking..."):
                    answer = claude_client.answer_question(q, data_summary, currency_info)
                if answer:
                    st.markdown(f"""
                    <div class="ai-insight-card" style="margin-top: 12px; border-color: rgba(108,99,255,0.5);">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                            <span style="font-size: 20px;">💬</span>
                            <span style="font-weight: 600; font-size: 16px;">Answer</span>
                        </div>
                        <div style="white-space:pre-wrap; line-height: 1.6; color: rgba(255,255,255,0.9);">
                            {answer.strip()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Display the original data context
    st.markdown("---")
    with st.expander("📊 Data Context (What the AI sees)"):
        st.markdown(f"""
        **Currency Information:**
        - Original Currency: {original_currency}
        - Display Currency: {display_currency}
        - Exchange Rate: {exchange_rate:.4f}
        
        **Financial Summary:**
        - Total Income: {original_currency} {kpis['total_income']:,.2f} ({display_currency} {kpis['total_income'] * exchange_rate:,.2f})
        - Total Expenses: {original_currency} {kpis['total_expenses']:,.2f} ({display_currency} {kpis['total_expenses'] * exchange_rate:,.2f})
        - Savings: {original_currency} {kpis['savings']:,.2f} ({display_currency} {kpis['savings'] * exchange_rate:,.2f})
        - Savings Rate: {kpis['savings_rate']:.1f}%
        - Average Daily Spending: {original_currency} {kpis['avg_daily_spending']:,.2f} ({display_currency} {kpis['avg_daily_spending'] * exchange_rate:,.2f})
        - Total Transactions: {kpis['transaction_count']}
        
        **Top 5 Categories:**
        """)
        for category in top_categories:
            st.markdown(f"- {category}")
        
        if monthly_trend:
            st.markdown("**Recent Monthly Trends:**")
            for trend in monthly_trend[-6:]:
                st.markdown(f"- {trend}")