"""
Analytics component for detailed financial analysis.

Shows:
- Full analytics dashboard
- Filtered views
- Deep dive into spending patterns
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from services.finance_analytics import FinanceAnalytics
from config.currencies import format_currency

def render_analytics(df, original_currency, display_currency, exchange_rate=1.0):
    """
    Render detailed analytics page.
    
    Args:
        df: Transaction DataFrame
        original_currency: Original currency code
        display_currency: Display currency code
        exchange_rate: Exchange rate for conversion
    """
    # Initialize analytics
    analytics = FinanceAnalytics(df)
    
    # Convert function
    def convert_amount(amount):
        if amount is None:
            return 0
        if original_currency != display_currency:
            return amount * exchange_rate
        return amount
    
    st.markdown("<h1 class='dashboard-title'>📈 Advanced Analytics</h1>", unsafe_allow_html=True)
    
    # Summary Statistics
    st.markdown("### 📊 Transaction Summary")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    kpis = analytics.get_kpis()
    
    with col1:
        st.metric(
            "Total Transactions",
            f"{kpis['transaction_count']}",
            help="Total number of transactions in the dataset"
        )
    
    with col2:
        st.metric(
            "Date Range",
            f"{kpis['date_range'][0].strftime('%m/%d/%y')} - {kpis['date_range'][1].strftime('%m/%d/%y')}",
            help="Date range of transactions"
        )
    
    with col3:
        st.metric(
            "Avg Transaction",
            format_currency(convert_amount(df['Amount'].mean()), display_currency),
            help="Average transaction amount"
        )
    
    # Category Distribution Details
    st.markdown("---")
    st.markdown("### 📊 Category Distribution")
    
    category_data = analytics.get_category_spending()
    if len(category_data) > 0:
        category_data['Converted Amount'] = category_data['Amount'] * exchange_rate if original_currency != display_currency else category_data['Amount']
        
        # Treemap
        fig = px.treemap(
            category_data,
            path=['Category'],
            values='Converted Amount',
            color='Converted Amount',
            color_continuous_scale='Viridis',
            title="Spending Distribution by Category"
        )
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("#### Detailed Category Breakdown")
        table_data = category_data.copy()
        table_data['Amount'] = table_data['Converted Amount'].apply(lambda x: format_currency(x, display_currency))
        table_data['Percentage'] = (table_data['Converted Amount'] / table_data['Converted Amount'].sum() * 100).round(1).astype(str) + '%'
        st.dataframe(
            table_data[['Category', 'Amount', 'Percentage']],
            use_container_width=True,
            hide_index=True
        )
    
    # Monthly Analysis
    st.markdown("---")
    st.markdown("### 📅 Monthly Analysis")
    
    monthly_data = analytics.get_monthly_trend()
    if len(monthly_data) > 0:
        # Line chart for trends
        fig = go.Figure()
        
        # Convert amounts
        income_vals = monthly_data['CREDIT'] * exchange_rate if original_currency != display_currency else monthly_data['CREDIT']
        expense_vals = monthly_data['DEBIT'] * exchange_rate if original_currency != display_currency else monthly_data['DEBIT']
        
        fig.add_trace(go.Scatter(
            x=monthly_data['Date'].astype(str),
            y=income_vals,
            name='Income',
            line=dict(color='#00D4AA', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 170, 0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=monthly_data['Date'].astype(str),
            y=expense_vals,
            name='Expenses',
            line=dict(color='#FF6B6B', width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.1)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            xaxis_title="Month",
            yaxis_title=f"Amount ({display_currency})",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly table
        st.markdown("#### Monthly Breakdown")
        table_data = monthly_data.copy()
        table_data['Income'] = table_data['CREDIT'].apply(lambda x: format_currency(x * exchange_rate if original_currency != display_currency else x, display_currency))
        table_data['Expenses'] = table_data['DEBIT'].apply(lambda x: format_currency(x * exchange_rate if original_currency != display_currency else x, display_currency))
        table_data['Savings'] = (table_data['CREDIT'] - table_data['DEBIT']).apply(lambda x: format_currency(x * exchange_rate if original_currency != display_currency else x, display_currency))
        table_data['Month'] = table_data['Date'].astype(str)
        st.dataframe(
            table_data[['Month', 'Income', 'Expenses', 'Savings']],
            use_container_width=True,
            hide_index=True
        )