"""
ALPHAVANTAGE CLIENT MODULE v2.0 - HISTORICAL DATA ENABLED
Professional-grade stock data from AlphaVantage API
- Fetches Daily Time Series for local technical calculation
- Reliable caching and retry logic
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import urllib3
import pandas as pd
from typing import Dict, Optional, Any

# AlphaVantage Configuration
ALPHAVANTAGE_API_KEY = "M9ZCKXLUYNU342JY"
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"

class AlphaVantageClient:
    """
    AlphaVantage API Client for stock data
    """

    # Class-level cache (shared across instances)
    _av_cache = {}
    _av_cache_timestamp = {}
    _cache_duration = 300  # 5 minutes

    def __init__(self):
        self.name = "AlphaVantage Client v2.0"
        self.api_key = ALPHAVANTAGE_API_KEY
        self.base_url = ALPHAVANTAGE_BASE_URL
        self.session = self._create_reliable_session()
        self.last_api_call = 0
        self.min_delay_between_calls = 12.0  # 5 calls/minute

    def _create_reliable_session(self) -> requests.Session:
        session = requests.Session()
        session.trust_env = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _rate_limit_api_call(self):
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_delay_between_calls:
            time.sleep(self.min_delay_between_calls - time_since_last_call)
        self.last_api_call = time.time()

    def get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetch daily historical data for technical analysis.
        Returns DataFrame with: open, high, low, close, volume
        """
        print(f"   📊 AlphaVantage: Fetching historical candles for {symbol}...")
        
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact', # 100 candles is enough for tech analysis
            'apikey': self.api_key
        }
        
        try:
            self._rate_limit_api_call()
            response = self.session.get(self.base_url, params=params, verify=False, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️ AlphaVantage History Error: {response.status_code}")
                return None
                
            data = response.json()
            if "Time Series (Daily)" not in data:
                print(f"   ⚠️ AlphaVantage: No time series data found.")
                return None
                
            # Convert JSON to DataFrame
            ts_data = data["Time Series (Daily)"]
            df = pd.DataFrame.from_dict(ts_data, orient='index')
            
            # Rename columns to standard names
            df = df.rename(columns={
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close',
                '5. volume': 'volume'
            })
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
                
            # Sort by date (ascending)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            print(f"   ✅ AlphaVantage: Fetched {len(df)} daily candles.")
            return df
            
        except Exception as e:
            print(f"   ❌ AlphaVantage History Exception: {e}")
            return None

    def get_global_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time price data"""
        self._rate_limit_api_call()
        params = {'function': 'GLOBAL_QUOTE', 'symbol': symbol, 'apikey': self.api_key}
        try:
            response = self.session.get(self.base_url, params=params, verify=False, timeout=15)
            data = response.json()
            if 'Global Quote' in data:
                q = data['Global Quote']
                return {
                    'current_price': float(q.get('05. price', 0)),
                    'change': float(q.get('09. change', 0)),
                    'change_percent': float(q.get('10. change percent', '0').strip('%')),
                    'volume': int(q.get('06. volume', 0)),
                    'previous_close': float(q.get('08. previous close', 0))
                }
        except Exception as e:
            print(f"   ⚠️ Global Quote Error: {e}")
        return {}

    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Get fundamentals"""
        self._rate_limit_api_call()
        params = {'function': 'OVERVIEW', 'symbol': symbol, 'apikey': self.api_key}
        try:
            response = self.session.get(self.base_url, params=params, verify=False, timeout=15)
            data = response.json()
            if 'Symbol' in data:
                return {
                    'market_cap': float(data.get('MarketCapitalization', 0)),
                    'pe_ratio': float(data.get('TrailingPE', 0)),
                    'fifty_two_week_high': float(data.get('52WeekHigh', 0)),
                    'fifty_two_week_low': float(data.get('52WeekLow', 0))
                }
        except Exception as e:
            print(f"   ⚠️ Overview Error: {e}")
        return {}

    def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive fundamental data for a stock.
        This method is called by ComprehensiveFundamentals.
        Returns normalized data structure for fundamental analysis.
        """
        print(f"   📊 AlphaVantage: Fetching comprehensive data for {symbol}...")
        
        self._rate_limit_api_call()
        params = {'function': 'OVERVIEW', 'symbol': symbol, 'apikey': self.api_key}
        
        try:
            response = self.session.get(self.base_url, params=params, verify=False, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️ AlphaVantage Comprehensive Error: HTTP {response.status_code}")
                return {}
            
            data = response.json()
            
            if 'Symbol' not in data:
                print(f"   ⚠️ AlphaVantage: No overview data for {symbol}")
                return {}
            
            # Extract and normalize comprehensive data
            comprehensive = {
                # Valuation metrics
                'trailing_pe': self._safe_float(data.get('TrailingPE', 0)),
                'forward_pe': self._safe_float(data.get('ForwardPE', 0)),
                'peg_ratio': self._safe_float(data.get('PEGRatio', 0)),
                'price_to_book': self._safe_float(data.get('PriceToBookRatio', 0)),
                'price_to_sales': self._safe_float(data.get('PriceToSalesRatioTTM', 0)),
                
                # Market data
                'market_cap': self._safe_float(data.get('MarketCapitalization', 0)),
                'enterprise_value': self._safe_float(data.get('EnterpriseValue', 0)),
                'beta': self._safe_float(data.get('Beta', 0)),
                
                # Profitability metrics
                'profit_margin': self._safe_float(data.get('ProfitMargin', 0)) * 100,  # Convert to percentage
                'operating_margin': self._safe_float(data.get('OperatingMarginTTM', 0)) * 100,
                'return_on_assets': self._safe_float(data.get('ReturnOnAssetsTTM', 0)) * 100,
                'return_on_equity': self._safe_float(data.get('ReturnOnEquityTTM', 0)) * 100,
                
                # Financial health
                'revenue_ttm': self._safe_float(data.get('RevenueTTM', 0)),
                'revenue_per_share': self._safe_float(data.get('RevenuePerShareTTM', 0)),
                'quarterly_earnings_growth': self._safe_float(data.get('QuarterlyEarningsGrowthYOY', 0)) * 100,
                'quarterly_revenue_growth': self._safe_float(data.get('QuarterlyRevenueGrowthYOY', 0)) * 100,
                'gross_profit': self._safe_float(data.get('GrossProfitTTM', 0)),
                'ebitda': self._safe_float(data.get('EBITDA', 0)),
                'diluted_eps': self._safe_float(data.get('DilutedEPSTTM', 0)),
                'eps': self._safe_float(data.get('EPS', 0)),
                
                # Dividend data
                'dividend_yield': self._safe_float(data.get('DividendYield', 0)) * 100,
                'dividend_per_share': self._safe_float(data.get('DividendPerShare', 0)),
                'dividend_date': data.get('DividendDate', ''),
                'ex_dividend_date': data.get('ExDividendDate', ''),
                
                # Trading data
                'fifty_two_week_high': self._safe_float(data.get('52WeekHigh', 0)),
                'fifty_two_week_low': self._safe_float(data.get('52WeekLow', 0)),
                'fifty_day_ma': self._safe_float(data.get('50DayMovingAverage', 0)),
                'two_hundred_day_ma': self._safe_float(data.get('200DayMovingAverage', 0)),
                'shares_outstanding': self._safe_float(data.get('SharesOutstanding', 0)),
                
                # Company info
                'sector': data.get('Sector', ''),
                'industry': data.get('Industry', ''),
                'description': data.get('Description', ''),
                'exchange': data.get('Exchange', ''),
                'currency': data.get('Currency', ''),
                'country': data.get('Country', '')
            }
            
            print(f"   ✅ AlphaVantage: Comprehensive data fetched successfully")
            return comprehensive
            
        except Exception as e:
            print(f"   ❌ AlphaVantage Comprehensive Exception: {e}")
            return {}
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None or value == 'None' or value == '':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default