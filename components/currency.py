"""
Currency converter component for WiseWallet.

This module provides the currency conversion UI and functionality.
Users can convert amounts between different currencies using live exchange rates.
"""

import streamlit as st
from config.currencies import CURRENCY_CODES, format_currency, SUPPORTED_CURRENCIES
from utils.currency_service import currency_service

def render_currency_converter():
    """
    Render the currency converter page.
    
    This function displays a beautiful currency converter interface with:
    - Amount input
    - Source currency selector
    - Target currency selector
    - Convert button
    - Result display with exchange rate
    """
    
    # Page header with glass design
    st.markdown("""
    <div class="glass-card fade-in" style="margin-bottom: 24px;">
        <h1 style="font-size: 32px; font-weight: 700; margin-bottom: 8px;">
            💱 Currency Converter
        </h1>
        <p style="color: rgba(255,255,255,0.7); font-size: 16px;">
            Convert any amount between different currencies using live exchange rates
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main converter card
    st.markdown('<div class="currency-converter">', unsafe_allow_html=True)
    
    # Create two columns for the converter
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Amount")
        amount = st.number_input(
            "Enter amount",
            min_value=0.01,
            value=100.00,
            step=10.00,
            format="%.2f",
            key="converter_amount",
            help="Enter the amount you want to convert"
        )
        
        st.markdown("### 📤 From")
        from_currency = st.selectbox(
            "Source currency",
            options=CURRENCY_CODES,
            index=0,
            key="from_currency",
            help="Select the currency you are converting from"
        )
        
        # Show the currency symbol and name
        from_symbol = SUPPORTED_CURRENCIES[from_currency].symbol
        from_name = SUPPORTED_CURRENCIES[from_currency].name
        st.caption(f"💡 {from_symbol} - {from_name}")
    
    with col2:
        st.markdown("### 📥 To")
        to_currency = st.selectbox(
            "Target currency",
            options=CURRENCY_CODES,
            index=1,
            key="to_currency",
            help="Select the currency you are converting to"
        )
        
        # Show the currency symbol and name
        to_symbol = SUPPORTED_CURRENCIES[to_currency].symbol
        to_name = SUPPORTED_CURRENCIES[to_currency].name
        st.caption(f"💡 {to_symbol} - {to_name}")
        
        # Show current exchange rate (if available and currencies are different)
        if from_currency != to_currency:
            rate = currency_service.get_exchange_rate(from_currency, to_currency)
            if rate:
                st.info(f"💱 Current rate: 1 {from_currency} = {rate:.4f} {to_currency}")
            else:
                st.warning("⚠️ Exchange rate temporarily unavailable")
    
    # Convert button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        convert_button = st.button(
            "🔄 Convert Currency",
            type="primary",
            use_container_width=True
        )
    
    # Handle conversion
    if convert_button:
        if amount <= 0:
            st.error("❌ Please enter a valid amount greater than 0")
            return
        
        if from_currency == to_currency:
            st.warning("⚠️ Source and target currencies are the same. No conversion needed.")
            return
        
        with st.spinner("🔄 Getting exchange rate..."):
            converted_amount, exchange_rate = currency_service.convert_amount(
                amount, 
                from_currency, 
                to_currency
            )
        
        if converted_amount is not None:
            # Display results in a beautiful card
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(108,99,255,0.1) 0%, rgba(255,255,255,0.02) 100%);
                border: 1px solid rgba(108,99,255,0.3);
                border-radius: 16px;
                padding: 24px;
                margin: 16px 0;
                text-align: center;
            ">
                <div style="font-size: 16px; color: rgba(255,255,255,0.7);">
                    {format_currency(amount, from_currency)} = 
                    <span style="font-size: 36px; font-weight: 700; background: linear-gradient(135deg, #6C63FF, #3F3D9E); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        {format_currency(converted_amount, to_currency)}
                    </span>
                </div>
                <div style="
                    background: rgba(255,255,255,0.05);
                    border-radius: 8px;
                    padding: 12px;
                    margin-top: 12px;
                    color: rgba(255,255,255,0.5);
                    font-size: 14px;
                ">
                    <strong>Exchange Rate:</strong> 1 {from_currency} = {exchange_rate:.6f} {to_currency}
                    <br>
                    <span style="font-size: 12px;">Last updated: Live</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show additional info
            st.success(f"✅ Successfully converted {format_currency(amount, from_currency)} to {format_currency(converted_amount, to_currency)}")
            
            # Show the conversion formula
            with st.expander("📊 View Conversion Details"):
                st.markdown(f"""
                **Conversion Formula:**
                - Amount: {amount:,.2f} {from_currency}
                - Exchange Rate: {exchange_rate:.6f}
                - Converted Amount: {amount} × {exchange_rate:.6f} = {converted_amount:,.2f} {to_currency}
                """)
        else:
            st.error("❌ Failed to get exchange rate. Please try again later.")
            
            # Offer alternative suggestion
            st.info("💡 You can still use the dashboard with the original currency values.")
    
    # Quick reference section
    st.markdown("---")
    st.markdown("### 📋 Supported Currencies")
    
    # Display all supported currencies in a grid
    cols = st.columns(4)
    for i, (code, currency) in enumerate(SUPPORTED_CURRENCIES.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 8px;
                padding: 8px 12px;
                margin: 4px 0;
                text-align: center;
                font-size: 13px;
            ">
                <strong>{currency.symbol}</strong> {code}
                <br>
                <span style="font-size: 11px; color: rgba(255,255,255,0.5);">{currency.name}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Exchange rate info
    st.markdown("---")
    st.caption("💱 Exchange rates are provided by ExchangeRate-API.com and updated hourly.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_currency_selector(label, key, default_index=0):
    """
    Helper function to render a currency selector dropdown.
    
    Args:
        label: The label for the selector
        key: Unique key for the component
        default_index: Default selection index
    
    Returns:
        Selected currency code
    """
    return st.selectbox(
        label,
        options=CURRENCY_CODES,
        index=default_index,
        key=key,
        help=f"Select the currency for {label.lower()}"
    )


def get_currency_display_info(currency_code: str) -> dict:
    """
    Get display information for a currency.
    
    Args:
        currency_code: The currency code (e.g., 'USD')
    
    Returns:
        Dictionary with symbol, name, and code
    """
    if currency_code in SUPPORTED_CURRENCIES:
        return {
            'code': currency_code,
            'symbol': SUPPORTED_CURRENCIES[currency_code].symbol,
            'name': SUPPORTED_CURRENCIES[currency_code].name
        }
    return None
