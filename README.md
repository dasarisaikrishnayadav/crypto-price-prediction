# Crypto Price Predictor - Fixed Version 🪙

A production-ready cryptocurrency price prediction application using machine learning. This version includes all bug fixes and improvements.

## 🚀 Features

- **Multiple ML Models**: Linear Regression, ARIMA, Random Forest, SVR, Moving Average, Polynomial Regression
- **Real-time Data**: Fetches live data from CoinGecko API with intelligent fallbacks
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Interactive Visualizations**: Plotly-based charts with confidence intervals
- **Robust Error Handling**: Comprehensive logging and user-friendly error messages
- **Performance Optimized**: Caching and efficient data processing

## 🐛 Bug Fixes Included

### Critical Fixes
- ✅ Removed duplicate `PredictionEngine` classes
- ✅ Fixed rate limiting with proper backoff mechanism
- ✅ Improved theme detection for charts
- ✅ Enhanced error handling throughout the application

### Major Improvements
- ✅ Fixed data alignment issues in volume processing
- ✅ Improved OHLC price estimation using volatility
- ✅ Enhanced accuracy metrics calculation
- ✅ Proper train/test split without data leakage
- ✅ Added comprehensive logging
- ✅ Implemented data caching for better performance

### Code Quality
- ✅ Added type hints for better IDE support
- ✅ Consistent error message formatting
- ✅ Input validation for user inputs
- ✅ Better code organization and documentation

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection (for API data fetching)

## 🔧 Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone https://github.com/yourusername/crypto-price-predictor.git
cd crypto-price-predictor

# Or download and extract the ZIP file
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration (Optional)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferences (optional)
# The app works out of the box with default settings
```

## 🎯 Usage

### Running the Application

```bash
streamlit run main.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Interface

1. **Select Cryptocurrency**: Choose from 20+ popular cryptocurrencies
2. **Choose Time Period**: Select historical data range (7d, 30d, 90d, 1y)
3. **Set Prediction Horizon**: Choose forecast period (1d, 7d, 30d)
4. **Select Model**: Pick from 6 different prediction models
5. **Advanced Settings**: Toggle technical indicators and confidence intervals

## 📁 Project Structure

```
crypto-price-predictor/
├── main.py                 # Main application entry point
├── data_handler.py         # Data fetching and processing
├── model.py                # ML prediction models
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── .env.example           # Configuration template
├── README.md              # This file
└── crypto_predictor.log   # Application logs (created at runtime)
```

## 🤖 Available Models

### 1. Linear Regression
- Fast and interpretable
- Good for trending markets
- Uses Ridge regularization

### 2. ARIMA
- Time series specific
- Captures seasonality
- Auto-fallback if fitting fails

### 3. Random Forest
- Ensemble method
- Provides prediction intervals
- Robust to outliers

### 4. SVR (Support Vector Regression)
- Non-linear patterns
- Scaled features
- Kernel-based approach

### 5. Moving Average
- Simple and reliable
- Good baseline
- Volatility-based confidence

### 6. Polynomial Regression
- Captures non-linear trends
- Regularized to prevent overfitting
- Degree 2 polynomials

## 📊 Metrics Explained

- **Directional Accuracy**: % of correct price direction predictions
- **RMSE**: Root Mean Square Error (lower is better)
- **MAE**: Mean Absolute Error (average prediction error)
- **MAPE**: Mean Absolute Percentage Error
- **R² Score**: Model fit quality (1.0 is perfect)

## 🔒 API Rate Limiting

The application implements intelligent rate limiting:
- Maximum 10 requests per minute to CoinGecko API
- Automatic backoff on rate limit hits
- User-friendly waiting indicators
- Automatic fallback to cached/mock data

## 🎨 Customization

### Adding New Cryptocurrencies

Edit `data_handler.py`:

```python
self.top_cryptos = {
    'bitcoin': 'Bitcoin',
    'your-crypto': 'Your Crypto Name',
    # Add more here
}
```

### Adjusting Model Parameters

Edit `model.py` in the specific model's `_predict_*` method:

```python
# Example: Random Forest
model = RandomForestRegressor(
    n_estimators=200,  # Increase trees
    max_depth=15,      # Adjust depth
    random_state=42
)
```

### Changing Cache Duration

Edit `main.py`:

```python
@st.cache_data(ttl=7200)  # 2 hours instead of 1 hour
def get_processed_crypto_data(crypto_id: str, days: int):
    # ...
```

## 🐛 Troubleshooting

### "Module not found" error
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "API rate limit exceeded"
- Wait 60 seconds for rate limit to reset
- Click "Use Demo Data Instead" button
- The app will automatically use mock data

### Charts not displaying
- Check browser console for errors
- Try refreshing the page
- Ensure Plotly is properly installed: `pip install plotly --upgrade`

### Slow performance
- Reduce historical data period
- Use simpler models (Moving Average, Linear Regression)
- Check internet connection speed

## 📈 Performance Tips

1. **Use caching**: The app caches data for 1 hour by default
2. **Start with shorter periods**: Use 7d or 30d for faster loading
3. **Simple models first**: Try Moving Average or Linear Regression before complex models
4. **Avoid rapid switching**: Give each model time to train

## ⚠️ Disclaimer

This application is for **educational and research purposes only**.

- Cryptocurrency markets are highly volatile and unpredictable
- Past performance does not guarantee future results
- Model predictions should not be used as the sole basis for investment decisions
- Always conduct your own research (DYOR)
- Consider consulting with financial advisors before investing
- The developers are not responsible for any financial losses

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Install development dependencies
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Data provided by [CoinGecko API](https://www.coingecko.com/en/api)
- Built with [Streamlit](https://streamlit.io/)
- ML models powered by [scikit-learn](https://scikit-learn.org/)
- Time series analysis with [statsmodels](https://www.statsmodels.org/)

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing issues for solutions
- Read the troubleshooting section above

## 🔄 Version History

### v2.0.0 (Fixed Version)
- Fixed all critical bugs
- Improved error handling
- Enhanced performance with caching
- Better data validation
- Comprehensive logging
- Improved UI/UX

### v1.0.0 (Original Version)
- Initial release
- Basic prediction functionality
- Multiple ML models

---

**Made with ❤️ for the crypto community**

*Remember: This is a tool for learning and exploration. Always trade responsibly!*