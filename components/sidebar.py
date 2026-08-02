"""
Sidebar component for WiseWallet navigation and controls.

Provides:
- Navigation menu
- Currency selectors
- File upload
- Data filters
"""

import streamlit as st
from typing import Optional, Tuple
from config.currencies import SUPPORTED_CURRENCIES, CURRENCY_CODES, DEFAULT_CURRENCY

def render_sidebar():
    """
    Render the sidebar with navigation and controls.
    
    Returns:
        Tuple of (selected_page, original_currency, display_currency, file_uploaded)
    """
    # Sidebar container with glass effect
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-content">
            <h1 class="app-title">WiseWallet</h1>
            <p class="app-subtitle">Smart Analytics. Better Finances.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "",
            ["📊 Dashboard", "📈 Analytics", "🧠 AI Insights" ],
            label_visibility="collapsed"
        )
        
        # Currency selectors
        st.markdown("---")
        st.markdown("### 💰 Currency Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            original_currency = st.selectbox(
                "Original Currency",
                options=CURRENCY_CODES,
                index=CURRENCY_CODES.index(DEFAULT_CURRENCY),
                help="Currency of your uploaded data"
            )
        
        with col2:
            display_currency = st.selectbox(
                "Display Currency",
                options=CURRENCY_CODES,
                index=CURRENCY_CODES.index(DEFAULT_CURRENCY),
                help="Currency for dashboard display"
            )
        
        # Show conversion status
        if original_currency != display_currency:
            st.info(f"🔄 Dashboard values will be converted from {original_currency} to {display_currency}")
        else:
            st.success("✓ No conversion needed (same currency)")
        
        # File upload
        st.markdown("---")
        st.markdown("### 📤 Upload Data")
        uploaded_file = st.file_uploader(
            "Upload your bank statement (CSV)",
            type=['csv'],
            help="CSV should contain: Date, Description, Amount, Type (Credit/Debit)"
        )
        
        if uploaded_file is not None:
            st.success("✅ File uploaded successfully!")
            st.session_state["uploaded_file"] = uploaded_file
        # Filters section
        if st.session_state.get('df_loaded', False):
            st.markdown("---")
            st.markdown("### 🔍 Filters")
            
            df = st.session_state.get('df')
            if df is not None and len(df) > 0:
                # Month filter
                months = sorted(df['Date'].dt.month.unique())
                month_options = ['All'] + [f"{m:02d}" for m in months]
                selected_month = st.selectbox("Month", month_options)
                
                # Year filter
                years = sorted(df['Date'].dt.year.unique())
                year_options = ['All'] + [str(y) for y in years]
                selected_year = st.selectbox("Year", year_options)
                
                # Category filter
                categories = ['All'] + sorted(df['Category'].unique())
                selected_category = st.selectbox("Category", categories)
                
                # Type filter
                types = ['All'] + sorted(df['Type'].unique())
                selected_type = st.selectbox("Transaction Type", types)
                
                # Store filters in session state
                st.session_state['filters'] = {
                    'month': None if selected_month == 'All' else int(selected_month),
                    'year': None if selected_year == 'All' else int(selected_year),
                    'category': None if selected_category == 'All' else selected_category,
                    'type': None if selected_type == 'All' else selected_type
                }
        
        # Version info
        st.markdown("---")
        st.caption("v1.0.0 | Made with ❤️")
    
    return page, original_currency, display_currency, uploaded_file