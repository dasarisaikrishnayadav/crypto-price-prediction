import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CryptoDataHandler:
    """
    Handles cryptocurrency data retrieval and processing from CoinGecko API.
    Implements proper rate limiting and fallback mechanisms.
    """

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.request_count = 0
        self.last_request_time = time.time()
        self.rate_limit = 10  # Maximum requests per minute
        self.rate_limit_reset = 60  # seconds to reset rate limit

        self.top_cryptos = {
            'bitcoin': 'Bitcoin',
            'ethereum': 'Ethereum',
            'tether': 'Tether',
            'binancecoin': 'Binance Coin',
            'solana': 'Solana',
            'xrp': 'XRP',
            'usdc': 'USD Coin',
            'cardano': 'Cardano',
            'dogecoin': 'Dogecoin',
            'polkadot': 'Polkadot',
            'tron': 'TRON',
            'chainlink': 'Chainlink',
            'polygon': 'Polygon',
            'litecoin': 'Litecoin',
            'bitcoin-cash': 'Bitcoin Cash',
            'stellar': 'Stellar',
            'uniswap': 'Uniswap',
            'monero': 'Monero',
            'cosmos': 'Cosmos',
            'ethereum-classic': 'Ethereum Classic'
        }

    def get_available_cryptocurrencies(self):
        """
        Return list of available cryptocurrency ids.
        """
        return list(self.top_cryptos.keys())

    def get_crypto_name(self, crypto_id: str) -> str:
        """Get the display name for a cryptocurrency."""
        return self.top_cryptos.get(crypto_id, crypto_id.capitalize())

    def _make_api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """
        Rate-limited request helper with proper backoff and user feedback.
        """
        current_time = time.time()
        
        # Reset counter if window has passed
        if current_time - self.last_request_time >= self.rate_limit_reset:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Check if we're over limit
        if self.request_count >= self.rate_limit:
            wait_time = self.rate_limit_reset - (current_time - self.last_request_time)
            if wait_time > 0:
                logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s")
                with st.spinner(f"⏳ API rate limit reached. Waiting {wait_time:.0f}s..."):
                    time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()

        url = f"{self.base_url}/{endpoint}"

        try:
            resp = requests.get(url, params=params, timeout=15)
            self.request_count += 1
            
            # Handle rate limit response
            if resp.status_code == 429:
                retry_after = int(resp.headers.get('Retry-After', 60))
                logger.warning(f"API rate limit hit. Retrying after {retry_after}s")
                st.warning(f"⏳ Rate limit hit. Retrying in {retry_after}s...")
                time.sleep(retry_after)
                return self._make_api_request(endpoint, params)  # Retry once
            
            if resp.status_code == 200:
                logger.info(f"Successfully fetched: {endpoint}")
                return resp.json()
            else:
                logger.warning(f"API request failed: {resp.status_code}")
                st.warning(f"⚠️ API returned status {resp.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {endpoint}")
            st.error("❌ Request timeout. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            st.error(f"❌ Network error: {str(e)}")
            return None

    def get_historical_data(self, crypto_id: str, days: int) -> pd.DataFrame:
        """
        Fetch daily historical price data with proper alignment and validation.
        """
        try:
            endpoint = f"coins/{crypto_id}/market_chart"
            params = {'vs_currency': 'usd', 'days': days, 'interval': 'daily'}
            data = self._make_api_request(endpoint, params)

            if not data or 'prices' not in data or len(data.get('prices', [])) == 0:
                logger.warning(f"No data from API for {crypto_id}, using mock data")
                return self._generate_mock_data(crypto_id, days)

            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])

            # Build DataFrame with proper timestamp alignment
            prices_df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
            prices_df.set_index('timestamp', inplace=True)

            # Handle volumes with proper alignment
            if volumes and len(volumes) > 0:
                volumes_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
                volumes_df['timestamp'] = pd.to_datetime(volumes_df['timestamp'], unit='ms')
                volumes_df.set_index('timestamp', inplace=True)
                
                # Merge on timestamp for proper alignment
                df = prices_df.join(volumes_df, how='left')
                
                # Interpolate missing volume values
                df['volume'] = df['volume'].interpolate(method='linear').bfill().ffill()
            else:
                df = prices_df
                df['volume'] = df['price'] * 1000  # Estimate volume if not available

            # Create OHLC estimates based on volatility
            df['close'] = df['price']
            
            # Calculate rolling volatility for realistic OHLC
            rolling_std = df['price'].rolling(window=min(20, len(df)), min_periods=1).std()
            
            # Use volatility to create realistic high/low
            df['high'] = df['price'] + rolling_std * 0.5
            df['low'] = df['price'] - rolling_std * 0.5
            
            # Open is previous close with small noise
            df['open'] = df['price'].shift(1)
            df['open'] = df['open'].fillna(df['price'])
            
            # Ensure logical constraints: high >= close, low <= close
            df['high'] = df[['high', 'close', 'open']].max(axis=1)
            df['low'] = df[['low', 'close', 'open']].min(axis=1)

            # Remove the temporary price column
            df = df.drop('price', axis=1)
            
            # Fill any remaining NaN values
            df = df.bfill().ffill()

            # Add technical indicators
            df = self._add_technical_indicators(df)
            
            # Validate data quality
            if df.isnull().any().any():
                logger.warning("Data contains NaN values after processing")
                df = df.ffill().bfill()

            logger.info(f"Successfully processed {len(df)} rows for {crypto_id}")
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}", exc_info=True)
            st.warning(f"⚠️ Using demo data due to error: {str(e)}")
            return self._generate_mock_data(crypto_id, days)

    def _generate_mock_data(self, crypto_id: str, days: int) -> pd.DataFrame:
        """
        Deterministic mock data generator with realistic patterns.
        """
        seed = sum(ord(c) for c in crypto_id)
        rng = np.random.RandomState(seed)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        n = len(date_range)
        
        if n == 0:
            date_range = pd.date_range(end=end_date, periods=1, freq='D')
            n = 1

        # Realistic price parameters
        if crypto_id == 'bitcoin':
            base_price = 45000.0
            volatility = 0.03
        elif crypto_id == 'ethereum':
            base_price = 2500.0
            volatility = 0.04
        else:
            base_price = float(rng.uniform(1.0, 1000.0))
            volatility = float(rng.uniform(0.02, 0.08))

        # Generate price with trend and cycles
        trend = np.linspace(0, 0.2, n)  # Slight upward trend
        cyclical = 0.1 * np.sin(np.linspace(0, 4 * np.pi, n))  # Market cycles
        noise = rng.normal(0, volatility, size=n)
        
        returns = trend + cyclical + noise
        price_factor = (1 + returns).cumprod()
        close_prices = base_price * price_factor

        df = pd.DataFrame(index=date_range)
        df['close'] = close_prices
        
        # Generate OHLC with realistic intraday movements
        intraday_vol = volatility * 0.5
        df['open'] = df['close'].shift(1).fillna(df['close'].iloc[0])
        
        high_noise = np.abs(rng.normal(0, intraday_vol, size=n))
        low_noise = np.abs(rng.normal(0, intraday_vol, size=n))
        
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + high_noise)
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - low_noise)
        
        # Volume with realistic patterns
        base_volume = base_price * 5000
        volume_multiplier = 1 + np.abs(returns) * 5  # Higher volume on big moves
        df['volume'] = base_volume * volume_multiplier * rng.uniform(0.5, 1.5, size=n)

        # Clean up any NaN values
        df = df.bfill().ffill()

        # Add technical indicators
        df = self._add_technical_indicators(df)
        
        logger.info(f"Generated {len(df)} rows of mock data for {crypto_id}")
        return df

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add comprehensive technical indicators with proper error handling.
        """
        try:
            # Simple Moving Averages
            df['sma_5'] = df['close'].rolling(window=5, min_periods=1).mean()
            df['sma_20'] = df['close'].rolling(window=20, min_periods=1).mean()

            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12, adjust=False, min_periods=1).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False, min_periods=1).mean()

            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False, min_periods=1).mean()

            # RSI with proper handling
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            
            # Avoid division by zero
            rs = gain / loss.replace(0, np.nan)
            df['rsi'] = 100 - (100 / (1 + rs))
            df['rsi'] = df['rsi'].fillna(50)  # Neutral RSI for NaN values

            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20, min_periods=1).mean()
            bb_std = df['close'].rolling(window=20, min_periods=1).std()
            df['bb_std'] = bb_std.fillna(0)
            df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
            df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']

            # Returns & volatility
            df['returns'] = df['close'].pct_change().fillna(0)
            df['volatility'] = df['returns'].rolling(window=20, min_periods=1).std().fillna(0)

            # Final cleanup
            df = df.ffill().bfill().fillna(0)

            logger.debug("Successfully added technical indicators")
            return df
            
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return df

    def get_market_cap(self, crypto_id: str) -> float:
        """
        Return USD market cap with fallback values.
        """
        try:
            endpoint = f"coins/{crypto_id}"
            data = self._make_api_request(endpoint)
            
            if data and 'market_data' in data:
                market_cap = data['market_data'].get('market_cap', {}).get('usd')
                if market_cap:
                    logger.info(f"Retrieved market cap for {crypto_id}: ${market_cap:,.0f}")
                    return float(market_cap)
            
            # Fallback values
            fallback_caps = {
                'bitcoin': 850_000_000_000.0,
                'ethereum': 300_000_000_000.0,
                'binancecoin': 50_000_000_000.0,
                'solana': 40_000_000_000.0,
                'xrp': 30_000_000_000.0,
            }
            
            if crypto_id in fallback_caps:
                logger.info(f"Using fallback market cap for {crypto_id}")
                return fallback_caps[crypto_id]
            
            # Generate consistent fallback
            seed = sum(ord(c) for c in crypto_id)
            rng = np.random.RandomState(seed)
            return float(rng.randint(500_000_000, 20_000_000_000))
            
        except Exception as e:
            logger.error(f"Error fetching market cap: {e}")
            return 1_000_000_000.0

    def get_24h_volume(self, crypto_id: str) -> float:
        """
        Return 24h volume in USD with fallback values.
        """
        try:
            endpoint = f"coins/{crypto_id}"
            data = self._make_api_request(endpoint)
            
            if data and 'market_data' in data:
                volume = data['market_data'].get('total_volume', {}).get('usd')
                if volume:
                    logger.info(f"Retrieved 24h volume for {crypto_id}: ${volume:,.0f}")
                    return float(volume)
            
            # Fallback values
            fallback_volumes = {
                'bitcoin': 35_000_000_000.0,
                'ethereum': 18_000_000_000.0,
                'binancecoin': 2_000_000_000.0,
                'solana': 3_000_000_000.0,
                'xrp': 1_500_000_000.0,
            }
            
            if crypto_id in fallback_volumes:
                logger.info(f"Using fallback volume for {crypto_id}")
                return fallback_volumes[crypto_id]
            
            # Generate consistent fallback
            seed = sum(ord(c) for c in crypto_id)
            rng = np.random.RandomState(seed + 1)  # Different seed than market cap
            return float(rng.randint(50_000_000, 5_000_000_000))
            
        except Exception as e:
            logger.error(f"Error fetching 24h volume: {e}")
            return 100_000_000.0