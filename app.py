import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

from data_handler import CryptoDataHandler
from model import PredictionEngine
from utils import setup_page_config, get_crypto_icon, format_large_number, format_percent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_processed_crypto_data(crypto_id: str, days: int):
    """Get and cache processed cryptocurrency data."""
    try:
        data_handler = CryptoDataHandler()
        df = data_handler.get_historical_data(crypto_id, days)
        logger.info(f"Successfully loaded data for {crypto_id}")
        return df
    except Exception as e:
        logger.error(f"Failed to load data for {crypto_id}: {e}")
        return None


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_market_data(crypto_id: str):
    """Get and cache market cap and volume data."""
    try:
        data_handler = CryptoDataHandler()
        market_cap = data_handler.get_market_cap(crypto_id)
        volume = data_handler.get_24h_volume(crypto_id)
        return market_cap, volume
    except Exception as e:
        logger.error(f"Failed to load market data for {crypto_id}: {e}")
        return None, None


def main():
    # Setup page configuration
    setup_page_config()
    
    # Initialize data handler
    data_handler = CryptoDataHandler()
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Cryptocurrency selector
        available_cryptos = data_handler.get_available_cryptocurrencies()
        selected_crypto = st.selectbox(
            "Select Cryptocurrency",
            options=available_cryptos,
            index=0,
            format_func=lambda x: f"{data_handler.get_crypto_name(x)} ({x.upper()})"
        )
        
        # Time period selector
        time_periods = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
            "1y": 365
        }
        selected_period = st.select_slider(
            "Historical Time Period",
            options=list(time_periods.keys()),
            value="30d"
        )
        days = time_periods[selected_period]
        
        # Prediction horizon selector
        prediction_horizons = {
            "1d": 1,
            "7d": 7,
            "30d": 30
        }
        prediction_horizon = st.select_slider(
            "Prediction Horizon",
            options=list(prediction_horizons.keys()),
            value="7d"
        )
        forecast_days = prediction_horizons[prediction_horizon]
        
        # Model selection
        available_models = [
            "Linear Regression",
            "ARIMA",
            "Random Forest",
            "SVR",
            "Moving Average",
            "Polynomial Regression"
        ]
        selected_model = st.radio("Prediction Model", available_models, index=0)
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            show_indicators = st.checkbox("Show Technical Indicators", value=False)
            show_confidence = st.checkbox("Show Confidence Intervals", value=True)
            
            st.info("💡 Model hyperparameters are automatically optimized")
    
    # Main content
    st.title("🪙 Crypto Price Predictor")
    st.markdown("*Predict cryptocurrency prices using machine learning models*")
    
    # Load data with spinner
    with st.spinner(f"📊 Loading {selected_crypto.upper()} data..."):
        df = get_processed_crypto_data(selected_crypto, days)
    
    # Handle data loading failures
    if df is None or len(df) == 0:
        st.error(f"❌ Failed to load data for {selected_crypto.upper()}")
        
        with st.expander("🔍 Troubleshooting"):
            st.markdown("""
            **Possible causes:**
            - API rate limit exceeded (wait a few minutes)
            - Network connectivity issues
            - Invalid cryptocurrency symbol
            - API service temporarily unavailable
            """)
        
        if st.button("🔄 Try Demo Data Instead"):
            with st.spinner("Generating demo data..."):
                df = data_handler._generate_mock_data(selected_crypto, days)
                st.success("✅ Loaded demo data successfully")
        else:
            st.stop()
    
    # Validate data quality
    if len(df) < 10:
        st.warning("⚠️ Limited data available. Predictions may be less accurate.")
    
    # Get market data
    market_cap, volume = get_market_data(selected_crypto)
    
    # Current price and info display
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    current_price = df['close'].iloc[-1]
    previous_price = df['close'].iloc[-2] if len(df) > 1 else current_price
    day_change = ((current_price / previous_price) - 1) * 100 if previous_price != 0 else 0
    
    with col1:
        try:
            icon_url = get_crypto_icon(selected_crypto)
            st.image(icon_url, width=50)
        except Exception as e:
            logger.warning(f"Failed to load icon: {e}")
        st.markdown(f"### {selected_crypto.upper()}")
        
    with col2:
        st.metric(
            "Current Price", 
            f"${current_price:.2f}", 
            f"{day_change:+.2f}%",
            delta_color="normal"
        )
        
    with col3:
        st.metric("Market Cap", format_large_number(market_cap))
    
    with col4:
        st.metric("24h Volume", format_large_number(volume))
    
    st.divider()
    
    # Price Chart
    st.subheader("📈 Historical Price")
    
    try:
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="OHLC"
            )
        )
        
        # Show technical indicators if enabled
        if show_indicators:
            # Add 20-day Moving Average
            if 'sma_20' in df.columns:
                ma20 = df['sma_20']
                fig.add_trace(go.Scatter(
                    x=df.index, 
                    y=ma20, 
                    line=dict(color='blue', width=2), 
                    name='20-day MA'
                ))
            
            # Add 50-day Moving Average if enough data
            if len(df) >= 50:
                ma50 = df['close'].rolling(window=50).mean()
                fig.add_trace(go.Scatter(
                    x=df.index, 
                    y=ma50, 
                    line=dict(color='orange', width=2), 
                    name='50-day MA'
                ))
        
        # Detect theme more reliably
        try:
            theme_base = st.get_option("theme.base")
            template = "plotly_dark" if theme_base == "dark" else "plotly_white"
        except:
            template = "plotly_white"  # Default fallback
        
        fig.update_layout(
            title=f"{selected_crypto.upper()} Price Chart ({selected_period})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            template=template,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error creating price chart: {e}")
        logger.error(f"Chart creation error: {e}")
    
    st.divider()
    
    # Price predictions
    st.subheader(f"🔮 Price Prediction ({prediction_horizon})")
    
    with st.spinner(f"🤖 Training {selected_model} model..."):
        try:
            # Initialize prediction engine
            prediction_engine = PredictionEngine(selected_model)
            
            # Prepare features from historical data
            prediction_data = prediction_engine.prepare_features(df)
            
            # Train model and make predictions
            predictions, confidence_intervals, accuracy = prediction_engine.predict(
                prediction_data, 
                forecast_days
            )
            
            # Format the prediction dates
            last_date = df.index[-1]
            future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
            
            # Create prediction DataFrame
            pred_df = pd.DataFrame({
                'date': future_dates,
                'predicted_price': predictions
            })
            
            if show_confidence and confidence_intervals is not None:
                pred_df['lower_bound'] = confidence_intervals[:, 0]
                pred_df['upper_bound'] = confidence_intervals[:, 1]
            
            # Display predicted change
            predicted_change_pct = ((predictions[-1] / current_price) - 1) * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    f"Predicted Price ({future_dates[-1].strftime('%Y-%m-%d')})", 
                    f"${predictions[-1]:.2f}", 
                    f"{predicted_change_pct:+.2f}%",
                    delta_color="normal"
                )
            
            with col2:
                price_range = predictions[-1] - predictions[0]
                st.metric(
                    "Price Range",
                    f"${abs(price_range):.2f}",
                    "Volatility" if abs(price_range) > current_price * 0.1 else "Stable"
                )
            
            with col3:
                trend = "📈 Uptrend" if predicted_change_pct > 2 else "📉 Downtrend" if predicted_change_pct < -2 else "➡️ Sideways"
                st.metric("Trend", trend)
            
            # Plot predictions
            try:
                fig2 = go.Figure()
                
                # Add historical prices (last 30 points for clarity)
                hist_data = df.tail(min(30, len(df)))
                fig2.add_trace(
                    go.Scatter(
                        x=hist_data.index,
                        y=hist_data['close'],
                        mode='lines',
                        name='Historical Price',
                        line=dict(color='#3b82f6', width=2)
                    )
                )
                
                # Add predictions
                fig2.add_trace(
                    go.Scatter(
                        x=pred_df['date'],
                        y=pred_df['predicted_price'],
                        mode='lines+markers',
                        name='Predicted Price',
                        line=dict(color='#10b981', width=2, dash='dash'),
                        marker=dict(size=6)
                    )
                )
                
                # Add confidence intervals if enabled
                if show_confidence and 'lower_bound' in pred_df.columns and 'upper_bound' in pred_df.columns:
                    fig2.add_trace(
                        go.Scatter(
                            x=pred_df['date'].tolist() + pred_df['date'].tolist()[::-1],
                            y=pred_df['upper_bound'].tolist() + pred_df['lower_bound'].tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(16, 185, 129, 0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='95% Confidence Interval',
                            showlegend=True
                        )
                    )
                
                fig2.update_layout(
                    title=f"{selected_crypto.upper()} Price Prediction - {selected_model}",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    height=500,
                    template=template,
                    hovermode='x unified',
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error creating prediction chart: {e}")
                logger.error(f"Prediction chart error: {e}")
            
            # Model performance metrics
            st.subheader("📊 Model Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Directional Accuracy", f"{accuracy['accuracy']:.2f}%")
            
            with col2:
                st.metric("RMSE", f"${accuracy['rmse']:.2f}")
            
            with col3:
                st.metric("MAE", f"${accuracy['mae']:.2f}")
            
            with col4:
                if 'mape' in accuracy:
                    st.metric("MAPE", f"{accuracy['mape']:.2f}%")
            
            # Display model details
            with st.expander("ℹ️ Model Details & Disclaimer"):
                st.markdown(f"""
                **Model Type:** {selected_model}
                
                **Training Data:** {len(df)} days of historical data
                
                **Features Used:**
                - Price (Open, High, Low, Close)
                - Volume
                - Moving Averages (SMA, EMA)
                - Volatility & Returns
                - Technical Indicators (RSI, MACD, Bollinger Bands)
                
                **Prediction Horizon:** {forecast_days} day(s)
                
                ---
                
                ⚠️ **Disclaimer:** This tool is for educational purposes only. 
                Cryptocurrency markets are highly volatile and unpredictable. 
                Past performance does not guarantee future results. 
                Always conduct your own research and consult with financial advisors 
                before making investment decisions.
                """)
        
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            logger.error(f"Prediction error: {e}", exc_info=True)
            
            st.info("💡 Try selecting a different model or time period.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application error: {e}")
        logger.critical(f"Critical application error: {e}", exc_info=True)