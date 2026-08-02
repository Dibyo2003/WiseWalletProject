"""
Dashboard component for displaying financial KPIs and overview.

Shows:
- Key metrics in glass cards
- Summary statistics
- Quick insights
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict
from config.currencies import format_currency
from services.finance_analytics import FinanceAnalytics

def render_kpi_card(label, value, change="", card_type="blue", icon="📊"):
    """Render a KPI card with glass effect."""
    color_class = {
        "green": "green",
        "red": "red",
        "blue": "blue",
        "gold": "gold"
    }.get(card_type, "blue")
    
    st.markdown(f"""
    <div class="kpi-card {color_class} fade-in">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {f'<div class="kpi-change {change["type"]}">{change["text"]}</div>' if change else ''}
    </div>
    """, unsafe_allow_html=True)

def render_dashboard(df, original_currency, display_currency, exchange_rate=1.0):
    """
    Render the main dashboard with KPIs and charts.
    
    Args:
        df: Transaction DataFrame
        original_currency: Original currency code
        display_currency: Display currency code
        exchange_rate: Exchange rate for conversion
    """
    # Initialize analytics
    analytics = FinanceAnalytics(df)
    kpis = analytics.get_kpis()
    
    # Convert amounts if needed
    def convert_amount(amount):
        if amount is None:
            return None
        if original_currency != display_currency:
            return amount * exchange_rate
        return amount
    
    # Header
    st.markdown("<h1 class='dashboard-title'>📊 Financial Dashboard</h1>", unsafe_allow_html=True)
    
    # KPI Cards - 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_kpi_card(
            "Total Income",
            format_currency(convert_amount(kpis['total_income']), display_currency),
            icon="💰",
            card_type="green"
        )
    
    with col2:
        render_kpi_card(
            "Total Expenses",
            format_currency(convert_amount(kpis['total_expenses']), display_currency),
            icon="💳",
            card_type="red"
        )
    
    with col3:
        render_kpi_card(
            "Savings",
            format_currency(convert_amount(kpis['savings']), display_currency),
            icon="💎",
            card_type="blue"
        )
    
    with col4:
        render_kpi_card(
            "Savings Rate",
            f"{kpis['savings_rate']:.1f}%",
            icon="📈",
            card_type="gold"
        )
    st.markdown("<br>", unsafe_allow_html=True)
    # Second row of KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_kpi_card(
            "Avg Daily Spending",
            format_currency(convert_amount(kpis['avg_daily_spending']), display_currency),
            icon="📊",
            card_type="blue"
        )
    
    with col2:
        largest_expense = kpis.get('largest_expense')
        if largest_expense is not None:
            render_kpi_card(
                "Largest Expense",
                format_currency(convert_amount(largest_expense['Amount']), display_currency),
                icon="🔴",
                card_type="red"
            )
        else:
            render_kpi_card("🔴 Largest Expense", "N/A", icon="🔴", card_type="red")
    
    with col3:
        highest_income = kpis.get('highest_income')
        if highest_income is not None:
            render_kpi_card(
                "Highest Income",
                format_currency(convert_amount(highest_income['Amount']), display_currency),
                icon="🟢",
                card_type="green"
            )
        else:
            render_kpi_card("🟢 Highest Income", "N/A", icon="🟢", card_type="green")
    
    # Charts Section
    st.markdown("---")
    
    # Monthly Trend Chart
    st.markdown("<h3>📈 Monthly Income vs Expenses</h3>", unsafe_allow_html=True)
    monthly_data = analytics.get_monthly_trend()
    if len(monthly_data) > 0:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_data['Date'].astype(str),
            y=monthly_data['CREDIT'] * exchange_rate if original_currency != display_currency else monthly_data['CREDIT'],
            name='Income',
            marker_color='#00D4AA'
        ))
        fig.add_trace(go.Bar(
            x=monthly_data['Date'].astype(str),
            y=monthly_data['DEBIT'] * exchange_rate if original_currency != display_currency else monthly_data['DEBIT'],
            name='Expenses',
            marker_color='#FF6B6B'
        ))
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Two columns for category charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>🍕Spending by Category</h3>", unsafe_allow_html=True)
        category_data = analytics.get_category_spending()
        if len(category_data) > 0:
            category_data['Converted Amount'] = category_data['Amount'] * exchange_rate if original_currency != display_currency else category_data['Amount']
            fig = px.pie(
                category_data,
                values='Converted Amount',
                names='Category',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3>🏆Top 10 Expenses</h3>", unsafe_allow_html=True)
        top_expenses = analytics.get_top_expenses(10)
        if len(top_expenses) > 0:
            top_expenses['Converted Amount'] = top_expenses['Amount'] * exchange_rate if original_currency != display_currency else top_expenses['Amount']
            fig = px.bar(
                top_expenses,
                x='Converted Amount',
                y='Description',
                orientation='h',
                color='Category',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                xaxis_title=f"Amount ({display_currency})"
            )
            st.plotly_chart(fig, use_container_width=True)