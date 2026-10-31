import streamlit as st
import logging

logger = logging.getLogger(__name__)


def setup_page_config():
    """
    Configure the Streamlit page settings with modern styling.
    """
    st.set_page_config(
        page_title="Crypto Price Predictor",
        page_icon="🪙",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/crypto-price-predictor',
            'Report a bug': 'https://github.com/yourusername/crypto-price-predictor/issues',
            'About': """
            # Crypto Price Predictor
            
            A machine learning-powered cryptocurrency price prediction application.
            
            **Features:**
            - Multiple ML models (Linear Regression, ARIMA, Random Forest, SVR, etc.)
            - Real-time data from CoinGecko API
            - Technical indicators (RSI, MACD, Bollinger Bands)
            - Interactive charts with Plotly
            
            **Disclaimer:** For educational purposes only. Not financial advice.
            """
        }
    )
    
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #fafafa;
    }
    
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: #0e1117;
        }
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Selectbox and slider labels */
    .stSelectbox label, .stSlider label, .stRadio label {
        font-weight: 600;
        font-size: 1rem;
        color: #1f2937;
    }
    
    @media (prefers-color-scheme: dark) {
        .stSelectbox label, .stSlider label, .stRadio label {
            color: #f3f4f6;
        }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 2px solid #e5e7eb;
    }
    
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: #1a1d24;
            border-right: 2px solid #374151;
        }
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e5e7eb;
    }
    
    @media (prefers-color-scheme: dark) {
        hr {
            border-top: 2px solid #374151;
        }
    }
    
    /* Chart container */
    .js-plotly-plot {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Responsive padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    logger.info("Page configuration set up successfully")


def format_large_number(num: float) -> str:
    """
    Format large numbers in a readable format (K, M, B, T).
    
    Args:
        num: Number to format
        
    Returns:
        Formatted number string with appropriate suffix
    """
    if num is None or np.isnan(num):
        return "N/A"
    
    try:
        num = float(num)
        
        if num >= 1_000_000_000_000:
            return f"${num / 1_000_000_000_000:.2f}T"
        elif num >= 1_000_000_000:
            return f"${num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"${num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"${num / 1_000:.2f}K"
        else:
            return f"${num:.2f}"
    except (ValueError, TypeError):
        logger.warning(f"Failed to format number: {num}")
        return "N/A"


def format_percent(value: float) -> str:
    """
    Format percentage values with appropriate sign.
    
    Args:
        value: Percentage value
        
    Returns:
        Formatted percentage string
    """
    if value is None or np.isnan(value):
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.2f}%"
    except (ValueError, TypeError):
        logger.warning(f"Failed to format percent: {value}")
        return "N/A"


def get_crypto_icon(crypto_id: str, fallback_icon: str = None) -> str:
    """
    Get the cryptocurrency logo/icon URL with reliable fallback.
    
    Args:
        crypto_id: Cryptocurrency ID (e.g., 'bitcoin', 'ethereum')
        fallback_icon: Optional custom fallback icon URL
        
    Returns:
        URL of the cryptocurrency icon
    """
    # Icon mapping for popular cryptocurrencies
    icon_mapping = {
        'bitcoin': 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png',
        'ethereum': 'https://assets.coingecko.com/coins/images/279/small/ethereum.png',
        'tether': 'https://assets.coingecko.com/coins/images/325/small/Tether.png',
        'binancecoin': 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png',
        'solana': 'https://assets.coingecko.com/coins/images/4128/small/solana.png',
        'xrp': 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png',
        'usdc': 'https://assets.coingecko.com/coins/images/6319/small/USD_Coin_icon.png',
        'cardano': 'https://assets.coingecko.com/coins/images/975/small/cardano.png',
        'dogecoin': 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png',
        'polkadot': 'https://assets.coingecko.com/coins/images/12171/small/polkadot.png',
        'tron': 'https://assets.coingecko.com/coins/images/1094/small/tron-logo.png',
        'chainlink': 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png',
        'polygon': 'https://assets.coingecko.com/coins/images/4713/small/matic-token-icon.png',
        'litecoin': 'https://assets.coingecko.com/coins/images/2/small/litecoin.png',
        'bitcoin-cash': 'https://assets.coingecko.com/coins/images/780/small/bitcoin-cash-circle.png',
        'stellar': 'https://assets.coingecko.com/coins/images/100/small/Stellar_symbol_black_RGB.png',
        'uniswap': 'https://assets.coingecko.com/coins/images/12504/small/uniswap-uni.png',
        'monero': 'https://assets.coingecko.com/coins/images/69/small/monero_logo.png',
        'cosmos': 'https://assets.coingecko.com/coins/images/1481/small/cosmos_hub.png',
        'ethereum-classic': 'https://assets.coingecko.com/coins/images/453/small/ethereum-classic-logo.png',
    }
    
    # Check if we have a cached icon
    crypto_id_lower = crypto_id.lower()
    if crypto_id_lower in icon_mapping:
        logger.debug(f"Using cached icon for {crypto_id}")
        return icon_mapping[crypto_id_lower]
    
    # Use custom fallback if provided
    if fallback_icon:
        logger.debug(f"Using custom fallback icon for {crypto_id}")
        return fallback_icon
    
    # Generate a consistent avatar using DiceBear API
    # This creates a unique, consistent icon for each crypto
    avatar_url = f"https://api.dicebear.com/7.x/identicon/svg?seed={crypto_id}&backgroundColor=667eea"
    logger.debug(f"Using generated avatar for {crypto_id}")
    return avatar_url


def validate_crypto_id(crypto_id: str) -> bool:
    """
    Validate cryptocurrency ID format.
    
    Args:
        crypto_id: Cryptocurrency ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not crypto_id or not isinstance(crypto_id, str):
        return False
    
    # Allow alphanumeric and hyphens
    if not all(c.isalnum() or c == '-' for c in crypto_id):
        return False
    
    # Length check (reasonable bounds)
    if len(crypto_id) < 2 or len(crypto_id) > 50:
        return False
    
    return True


def format_error_message(context: str, error: Exception) -> str:
    """
    Format error messages consistently.
    
    Args:
        context: Context where the error occurred
        error: Exception object
        
    Returns:
        Formatted error message
    """
    return f"❌ {context}: {str(error)}"


def get_trend_emoji(change_percent: float) -> str:
    """
    Get appropriate emoji for price trend.
    
    Args:
        change_percent: Percentage change
        
    Returns:
        Emoji representing the trend
    """
    if change_percent > 5:
        return "🚀"
    elif change_percent > 2:
        return "📈"
    elif change_percent > 0:
        return "↗️"
    elif change_percent > -2:
        return "↘️"
    elif change_percent > -5:
        return "📉"
    else:
        return "💥"


def calculate_price_stats(prices: list) -> dict:
    """
    Calculate statistical measures for price data.
    
    Args:
        prices: List of price values
        
    Returns:
        Dictionary with statistical measures
    """
    import numpy as np
    
    if not prices or len(prices) == 0:
        return {
            'mean': 0,
            'median': 0,
            'std': 0,
            'min': 0,
            'max': 0,
            'range': 0
        }
    
    prices = np.array(prices)
    
    return {
        'mean': float(np.mean(prices)),
        'median': float(np.median(prices)),
        'std': float(np.std(prices)),
        'min': float(np.min(prices)),
        'max': float(np.max(prices)),
        'range': float(np.max(prices) - np.min(prices))
    }


# Import numpy for utility functions
import numpy as np