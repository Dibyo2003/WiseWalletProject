"""
WiseWallet - AI-Powered Personal Finance Analytics Dashboard

Main application entry point.
Handles routing, session management, and component coordination.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image

# Configure page
st.set_page_config(
    page_title="WiseWallet - Smart Analytics. Better Finances.",
    layout="wide",
    initial_sidebar_state="expanded"
)
logo = Image.open("assets/logo.png")

# Import components
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.analytics import render_analytics
from components.insights import render_insights
#from components.currency import render_currency_converter

# Import utilities
from utils.data_processor import DataProcessor
from utils.currency_service import currency_service
from config.currencies import DEFAULT_CURRENCY

# Load custom CSS
def load_css():
    """Load custom CSS for styling."""
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    if 'df_loaded' not in st.session_state:
        st.session_state['df_loaded'] = False
    if 'filters' not in st.session_state:
        st.session_state['filters'] = {}
    if 'processed_data' not in st.session_state:
        st.session_state['processed_data'] = None

def main():
    """Main application entry point."""
    
    # Initialize
    load_css()
    init_session_state()
    
    # Render sidebar and get selections
    page, original_currency, display_currency, uploaded_file = render_sidebar()
    
    # Process uploaded file (From Sidebar)
    if uploaded_file is not None:
        processor = DataProcessor()
        df, error = processor.process_uploaded_file(uploaded_file)
        
        if error:
            st.error(f"Error processing file: {error}")
        else:
            st.session_state['df'] = df
            st.session_state['df_loaded'] = True
            st.session_state['original_currency'] = original_currency
            st.session_state['display_currency'] = display_currency
    
    # ---------------------------------------------------------
    # BEAUTIFUL WELCOME SCREEN (When no data is loaded yet)
    # ---------------------------------------------------------
    if not st.session_state.get('df_loaded', False):
        
        # Add vertical space to push the content down slightly
        st.write("")
        st.write("")
        st.write("")
        
        # Use columns to center everything on the wide layout
        # The middle column (2.5) holds the content, left (1) and right (1) are empty spacers
        spacer_left, col_main, spacer_right = st.columns([1, 2.5, 1])

        with col_main:
            
            # --- LOGO & TITLE ALIGNMENT ---
            logo_col, text_col = st.columns([1, 4])
            
            with logo_col:
                # Add CSS styling to perfectly center the image vertically
                st.markdown('<div style="display: flex; align-items: center; height: 100%;">', unsafe_allow_html=True)
                st.image(logo, width=100)
                st.markdown('</div>', unsafe_allow_html=True)

            with text_col:
                # Flexbox to perfectly align the title and subtitle
                st.markdown("""
                <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
                    <h1 style="margin-bottom: 0px;font-family: 'Trebuchet MS', sans-serif; padding-bottom: 0px; font-size: 3.5rem; line-height: 1;">WiseWallet</h1>
                    <p style="margin-top: 5px; color: #a0aec0; letter-spacing: 2px; font-weight: 600; font-size: 0.95rem;">
                        SMART ANALYTICS. BETTER FINANCES.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider() # Subtle horizontal line
            
            # --- WELCOME MESSAGE BOX ---
            st.markdown("""
            <div style="text-align: center; padding: 2.5rem; background-color: rgba(255,255,255,0.03); border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin-top: 0; font-size: 2.2rem; font-weight: bold;">Welcome!</h2>
                <p style="font-size: 1.15rem; color: #e2e8f0; line-height: 1.6;">
                    Upload your expense CSV to transform your financial data
                    into interactive dashboards, insightful visualizations, 
                    and AI-powered analytics.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- MAIN UPLOAD WIDGET ---
            # Allows users to upload directly from the center of the screen instead of hunting for the sidebar
            st.markdown("<h4 style='text-align: center; color: #a0aec0; font-weight: 400;'>Get started by uploading your data:</h4>", unsafe_allow_html=True)
            main_uploaded_file = st.file_uploader("Upload Expense CSV", type="csv", label_visibility="collapsed", key="main_uploader")
            
            # Process upload from the main screen
            if main_uploaded_file is not None:
                processor = DataProcessor()
                df, error = processor.process_uploaded_file(main_uploaded_file)
                
                if error:
                    st.error(f"Error processing file: {error}")
                else:
                    st.session_state['df'] = df
                    st.session_state['df_loaded'] = True
                    st.session_state['original_currency'] = original_currency
                    st.session_state['display_currency'] = display_currency
                    st.rerun() # Instantly refreshes the page to show the dashboard
                    
        # Stop execution here so it doesn't try to render the dashboard without data
        return
    
    # ---------------------------------------------------------
    # DASHBOARD ROUTING (Executes only if data is loaded)
    # ---------------------------------------------------------
    
    # Get data and currency info
    df = st.session_state['df']
    original_currency = st.session_state.get('original_currency', DEFAULT_CURRENCY)
    display_currency = st.session_state.get('display_currency', DEFAULT_CURRENCY)
    
    # Get exchange rate
    exchange_rate = 1.0
    if original_currency != display_currency:
        rate = currency_service.get_exchange_rate(original_currency, display_currency)
        if rate:
            exchange_rate = rate
        else:
            st.warning(f"⚠️ Could not fetch exchange rate for {original_currency} to {display_currency}. Using 1:1 conversion.")
    
    # Apply filters
    if st.session_state.get('filters'):
        filters = st.session_state['filters']
        # Filter the data
        filtered_df = df.copy()
        if filters.get('month'):
            filtered_df = filtered_df[filtered_df['Date'].dt.month == filters['month']]
        if filters.get('year'):
            filtered_df = filtered_df[filtered_df['Date'].dt.year == filters['year']]
        if filters.get('category'):
            filtered_df = filtered_df[filtered_df['Category'] == filters['category']]
        if filters.get('type'):
            filtered_df = filtered_df[filtered_df['Type'] == filters['type']]
        df = filtered_df
    
    # Route to selected page
    if page == "📊 Dashboard":
        render_dashboard(df, original_currency, display_currency, exchange_rate)
    elif page == "📈 Analytics":
        render_analytics(df, original_currency, display_currency, exchange_rate)
    elif page == "🧠 AI Insights":
        render_insights(df, original_currency, display_currency, exchange_rate)
    #elif page == "💱 Currency Converter":
    #   render_currency_converter()
    
    # Show conversion info
    if original_currency != display_currency:
        st.sidebar.info(f"💱 Converting from {original_currency} to {display_currency} (Rate: {exchange_rate:.4f})")

if __name__ == "__main__":
    main()
    