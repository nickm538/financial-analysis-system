# 📊 Financial Analysis System

A comprehensive, production-ready financial analysis system with real-time data from multiple APIs, 40+ fundamental metrics, and 19+ technical indicators.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Features

### **Fundamental Analysis**
- **40+ Metrics** including EBITDA, PEG Ratio, P/E, ROE, ROA
- **Liquidity Metrics**: Current Ratio, Quick Ratio, Cash Ratio
- **Leverage & Solvency**: Debt-to-Equity, Interest Coverage
- **Cash Flow Analysis**: Operating CF, Free CF, CF Ratios
- **Per-Share Metrics**: EPS, Revenue/Share, Cash Flow/Share
- **Growth Metrics**: Revenue Growth, EPS Growth, Projected EPS

### **Technical Analysis**
- **19+ Indicators** from TwelveData API
- **Momentum**: RSI, MACD, Stochastic, CCI
- **Trend**: ADX, Williams %R, ATR, Bollinger Bands, DMI
- **Volume**: OBV, VWAP
- **Composite**: Ultimate Oscillator, Awesome Oscillator, Chaikin Oscillator

### **Data Sources**
- **AlphaVantage** - Comprehensive company data
- **Finnhub** - Real-time metrics and ratios
- **Massive API** - Financial statements
- **TwelveData** - Professional technical indicators

### **Advanced Features**
- **Multi-API Fallback**: Automatic fallback across 3+ APIs
- **Internal Calculations**: Calculates metrics when APIs don't provide them
- **Smart Caching**: 5-minute TTL to reduce API calls
- **Rate Limiting**: Respects free tier limits (8s between TwelveData calls)
- **Comprehensive Scoring**: AI-powered stock scoring with confidence levels

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+
- API Keys (see Configuration section)

### **Installation**

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/financial-analysis-system.git
cd financial-analysis-system

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run streamlit_dashboard_PRODUCTION_FIXED.py
```

### **Configuration**

Create a `.env` file or set environment variables:

```bash
# Required API Keys
ALPHAVANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
MASSIVE_API_KEY=your_key_here

# TwelveData API Key (hardcoded in twelvedata_client.py)
# Default: 5e7a5daaf41d46a8966963106ebef210
```

**Get Free API Keys:**
- [AlphaVantage](https://www.alphavantage.co/support/#api-key) - Free tier: 25 requests/day
- [Finnhub](https://finnhub.io/register) - Free tier: 60 calls/minute
- [Massive API](https://massive.io/) - Free tier available
- [TwelveData](https://twelvedata.com/pricing) - Free tier: 800 requests/day

---

## 📖 Usage

### **Basic Usage**

```python
# Run the Streamlit dashboard
streamlit run streamlit_dashboard_PRODUCTION_FIXED.py
```

Enter a stock symbol (e.g., `AAPL`, `MSFT`, `GOOGL`) and explore:

1. **AI Summary Tab** - Quick overview with key metrics
2. **Comprehensive Fundamentals** - All 40+ fundamental metrics
3. **Technical Analysis** - All 19+ technical indicators
4. **Comprehensive Scoring** - AI-powered stock scoring

### **Programmatic Usage**

```python
from comprehensive_fundamentals_FIXED import ComprehensiveFundamentals
from technical_analysis import TechnicalAnalysis
from comprehensive_scoring import ComprehensiveScoring

# Initialize clients
fundamentals_engine = ComprehensiveFundamentals(
    alphavantage_key="your_key",
    finnhub_key="your_key",
    massive_api_key="your_key"
)

technical_engine = TechnicalAnalysis()
scoring_engine = ComprehensiveScoring()

# Get data
symbol = "AAPL"
fundamentals = fundamentals_engine.get_all_metrics(symbol)
technicals = technical_engine.get_all_indicators(symbol)

# Calculate scores
fund_score = scoring_engine.calculate_fundamental_score(fundamentals)
tech_score = scoring_engine.calculate_technical_score(technicals)
overall_score = scoring_engine.calculate_overall_score(fund_score, tech_score)

print(f"Overall Score: {overall_score['score']}/100")
print(f"Signal: {overall_score['signal']}")
print(f"Confidence: {overall_score['confidence']}")
```

---

## 🏗️ Architecture

### **Project Structure**

```
financial-analysis-system/
├── streamlit_dashboard_PRODUCTION_FIXED.py  # Main dashboard
├── comprehensive_fundamentals_FIXED.py       # Fundamental analysis engine
├── technical_analysis.py                     # Technical analysis engine
├── comprehensive_scoring.py                  # Scoring algorithm
├── alphavantage_client.py                    # AlphaVantage API client
├── twelvedata_client.py                      # TwelveData API client
├── api_client.py                             # Base API client
├── requirements.txt                          # Python dependencies
├── .gitignore                                # Git ignore rules
└── README.md                                 # This file
```

### **Data Flow**

```
User Input (Stock Symbol)
    ↓
┌─────────────────────────────────────────┐
│  Streamlit Dashboard                    │
│  (streamlit_dashboard_PRODUCTION_FIXED) │
└─────────────────────────────────────────┘
    ↓                           ↓
┌──────────────────┐    ┌──────────────────┐
│  Fundamentals    │    │  Technicals      │
│  Engine          │    │  Engine          │
└──────────────────┘    └──────────────────┘
    ↓                           ↓
┌──────────────────┐    ┌──────────────────┐
│  Multi-API       │    │  TwelveData      │
│  Aggregation     │    │  API             │
│  (AV+Finnhub+    │    │                  │
│   Massive)       │    │                  │
└──────────────────┘    └──────────────────┘
    ↓                           ↓
┌─────────────────────────────────────────┐
│  Scoring Engine                         │
│  (comprehensive_scoring)                │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Final Output                           │
│  - Scores                               │
│  - Signals (BUY/HOLD/SELL)             │
│  - Confidence Levels                    │
└─────────────────────────────────────────┘
```

---

## 💡 Key Features Explained

### **1. Multi-API Fallback**

The system tries multiple APIs for each metric:

```python
# Example: P/E Ratio
pe_ratio = alphavantage_data.get('pe_ratio', 0)
if pe_ratio == 0:
    pe_ratio = finnhub_data.get('peBasicExclExtraTTM', 0)
if pe_ratio == 0:
    pe_ratio = finnhub_data.get('peNormalizedAnnual', 0)
```

### **2. Internal Calculations**

When APIs don't provide data, the system calculates it:

```python
# Operating Cash Flow Calculation
if operating_cf == 0:
    operating_cf = net_income + depreciation_and_amortization
```

### **3. Smart Caching**

Reduces API calls with TTL-based caching:

```python
@st.cache_data(ttl=300)  # 5-minute cache
def load_fundamentals(symbol):
    return fundamentals_engine.get_all_metrics(symbol)
```

### **4. Rate Limiting**

Respects API rate limits:

```python
# TwelveData: 8 seconds between calls
time.sleep(8)
```

---

## 📊 Metrics Reference

### **Fundamental Metrics (40+)**

| Category | Metrics |
|----------|---------|
| **Valuation** | P/E, Forward P/E, PEG, P/S, P/B, EV/EBITDA |
| **Profitability** | ROE, ROA, Net Margin, Operating Margin, Gross Margin |
| **Liquidity** | Current Ratio, Quick Ratio, Cash Ratio |
| **Leverage** | Debt-to-Equity, Debt-to-Assets, Interest Coverage, Equity Multiplier |
| **Cash Flow** | Operating CF, Free CF, Operating CF Ratio, CF to Debt |
| **Per-Share** | EPS, Revenue/Share, Cash Flow/Share, Book Value/Share |
| **Growth** | Revenue Growth, EPS Growth, Projected EPS |
| **EBITDA** | EBITDA, EBITDA Margin |
| **Dividends** | Dividend Yield, Payout Ratio |
| **Risk** | Beta |

### **Technical Indicators (19+)**

| Category | Indicators |
|----------|------------|
| **Momentum** | RSI, MACD, Stochastic, CCI |
| **Trend** | ADX, Williams %R, ATR, Bollinger Bands, +DI, -DI, DMI |
| **Volume** | OBV, VWAP |
| **Composite** | Ultimate Oscillator, Awesome Oscillator, Chaikin Oscillator |
| **Moving Averages** | EMA, SMA |

---

## 🔧 Troubleshooting

### **Common Issues**

**1. API Rate Limits**
```
Error: 429 Too Many Requests
```
**Solution:** Wait 60 seconds or upgrade to paid API tier

**2. Missing Data**
```
Warning: Operating CF = 0
```
**Solution:** System will calculate internally from Net Income + D&A

**3. Cache Issues**
```
Data seems stale
```
**Solution:** Clear Streamlit cache: `Ctrl+Shift+R` or restart dashboard

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **AlphaVantage** for comprehensive financial data
- **Finnhub** for real-time market metrics
- **TwelveData** for professional technical indicators
- **Streamlit** for the amazing dashboard framework

---

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/YOUR_USERNAME/financial-analysis-system/issues)
- Submit a [Pull Request](https://github.com/YOUR_USERNAME/financial-analysis-system/pulls)

---

## 🎯 Roadmap

- [ ] Add more technical indicators (Ichimoku, Fibonacci)
- [ ] Implement backtesting framework
- [ ] Add portfolio analysis
- [ ] Create REST API endpoint
- [ ] Add real-time WebSocket data
- [ ] Implement machine learning predictions

---

## ⚠️ Disclaimer

This software is for educational and informational purposes only. It is not financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.

---

**Built with ❤️ for the financial analysis community**
