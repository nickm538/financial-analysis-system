"""
STOCK DATA CLIENT v7.1 - STEALTH EDITION
Fixes "429 Too Many Requests" by spoofing browser headers and bypassing system proxies.
"""

import yfinance as yf
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import random
import time

# API Configuration
FMP_API_KEY = "qy7DU7wlhqMWYSOykfm3I1Y8vYEZlCQz"
FMP_BASE_URL = "https://financialmodelingprep.com/stable"

FINNHUB_API_KEY = "d47ssnpr01qk80bicu4gd47ssnpr01qk80bicu50"
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

class StockDataClient:
    """
    Stock data client with 'Stealth Mode' to bypass Yahoo 429 errors.
    """
    
    def __init__(self):
        self.name = "StockDataClient v7.1 (Stealth)"
        print(f"✅ {self.name} initialized")
        print("   - Strategy: Browser Spoofing + Proxy Bypass")
        
        # 1. Create a custom session to hijack yfinance's requests
        self.session = self._create_stealth_session()
        
    def _create_stealth_session(self) -> requests.Session:
        """
        Creates a session that looks like a real browser and ignores corporate proxies.
        """
        session = requests.Session()

        # CRITICAL: Ignore corporate/system proxies that cause handshake failures
        session.trust_env = False 

        # Fake a real browser (User-Agent is key to fixing 429s)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })

        # Smart Retry Logic: Wait longer if we hit a limit
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,  # Wait 1s, 2s, 4s, 8s...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "HEAD"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session

    def get_realtime_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time quote using FMP -> yfinance (with stealth session)
        """
        # Try FMP first (API Key based, rarely blocks)
        fmp_quote = self.get_fmp_quote(symbol)
        if fmp_quote:
            return fmp_quote
        
        # Fallback to yfinance with our stealth session
        try:
            # Inject our custom session into yfinance
            ticker = yf.Ticker(symbol, session=self.session)
            
            # Force a small random sleep to look human
            time.sleep(random.uniform(0.5, 1.5))
            
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                print(f"   ⚠️  No quote data available for {symbol}")
                return None
            
            # Get historical data
            hist_1y = ticker.history(period='1y')
            
            if hist_1y.empty:
                high_52 = None
                low_52 = None
            else:
                high_52 = float(hist_1y['High'].max())
                low_52 = float(hist_1y['Low'].min())
            
            quote = {
                'symbol': symbol,
                'price': float(info.get('regularMarketPrice', info.get('currentPrice', 0))),
                'change': float(info.get('regularMarketChange', 0)),
                'change_percent': float(info.get('regularMarketChangePercent', 0)),
                'volume': int(info.get('regularMarketVolume', info.get('volume', 0))),
                'avg_volume': int(info.get('averageVolume', 0)),
                'market_cap': int(info.get('marketCap', 0)),
                'day_high': float(info.get('dayHigh', 0)),
                'day_low': float(info.get('dayLow', 0)),
                'open': float(info.get('regularMarketOpen', info.get('open', 0))),
                'previous_close': float(info.get('previousClose', 0)),
                'fifty_two_week_high': high_52,
                'fifty_two_week_low': low_52,
                'pe_ratio': float(info.get('trailingPE', 0)) if info.get('trailingPE') else None,
                'dividend_yield': float(info.get('dividendYield', 0)) if info.get('dividendYield') else None,
                'beta': float(info.get('beta', 0)) if info.get('beta') else None,
                'source': 'yfinance (stealth)',
                'timestamp': datetime.now().isoformat(),
                'data_quality': 'complete'
            }
            return quote
            
        except Exception as e:
            print(f"   ERROR: yfinance quote failed for {symbol}: {e}")
            return None

    def get_fmp_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote from FMP"""
        try:
            url = f"{FMP_BASE_URL}/quote/{symbol}"
            params = {'apikey': FMP_API_KEY}
            response = self.session.get(url, params=params, timeout=10) # Use stealth session here too
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    q = data[0]
                    return {
                        'symbol': q.get('symbol'),
                        'price': float(q.get('price', 0)),
                        'change': float(q.get('change', 0)),
                        'change_percent': float(q.get('changesPercentage', 0)),
                        'volume': int(q.get('volume', 0)),
                        'avg_volume': int(q.get('avgVolume', 0)),
                        'market_cap': int(q.get('marketCap', 0)),
                        'day_high': float(q.get('dayHigh', 0)),
                        'day_low': float(q.get('dayLow', 0)),
                        'open': float(q.get('open', 0)),
                        'previous_close': float(q.get('previousClose', 0)),
                        'fifty_two_week_high': float(q.get('yearHigh', 0)),
                        'fifty_two_week_low': float(q.get('yearLow', 0)),
                        'pe_ratio': float(q.get('pe', 0)),
                        'eps': float(q.get('eps', 0)),
                        'source': 'fmp',
                        'data_quality': 'complete'
                    }
            return None
        except Exception as e:
            print(f"   ERROR: FMP quote failed: {e}")
            return None

    # ... (Keep remaining methods: get_fmp_profile, get_intraday_data, etc. 
    # ensuring they ALL use self.session.get() instead of requests.get()) ...

    def get_fmp_profile(self, symbol: str) -> Optional[Dict]:
        try:
            url = f"{FMP_BASE_URL}/profile/{symbol}"
            params = {'apikey': FMP_API_KEY}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]
            return None
        except Exception:
            return None

    def get_intraday_data(self, symbol: str, interval: str = '5m', period: str = '1d') -> Optional[pd.DataFrame]:
        try:
            ticker = yf.Ticker(symbol, session=self.session)
            return ticker.history(period=period, interval=interval)
        except Exception:
            return None

    def get_historical_data(self, symbol: str, period: str = '1y') -> Optional[pd.DataFrame]:
        try:
            ticker = yf.Ticker(symbol, session=self.session)
            return ticker.history(period=period)
        except Exception:
            return None

    def get_finnhub_news(self, symbol: str, days: int = 7) -> List[Dict]:
        try:
            end = datetime.now()
            start = end - timedelta(days=days)
            url = f"{FINNHUB_BASE_URL}/company-news"
            params = {
                'symbol': symbol, 
                'from': start.strftime('%Y-%m-%d'), 
                'to': end.strftime('%Y-%m-%d'), 
                'token': FINNHUB_API_KEY
            }
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()[:10]
            return []
        except Exception:
            return []

    def get_finnhub_sentiment(self, symbol: str) -> Optional[Dict]:
        try:
            url = f"{FINNHUB_BASE_URL}/news-sentiment"
            params = {'symbol': symbol, 'token': FINNHUB_API_KEY}
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

# Global client instance
_client = None

def get_client() -> StockDataClient:
    global _client
    if _client is None:
        _client = StockDataClient()
    return _client

# Convenience wrappers
def get_real_time_quote(symbol: str): return get_client().get_realtime_quote(symbol)
def get_fmp_quote(symbol: str): return get_client().get_fmp_quote(symbol)
def get_fmp_profile(symbol: str): return get_client().get_fmp_profile(symbol)
def get_intraday_data(symbol: str, interval='5m', period='1d'): return get_client().get_intraday_data(symbol, interval, period)
def get_historical_data(symbol: str, period='1y'): return get_client().get_historical_data(symbol, period)
def get_finnhub_news(symbol: str): return get_client().get_finnhub_news(symbol)
def get_finnhub_sentiment(symbol: str): return get_client().get_finnhub_sentiment(symbol)

if __name__ == "__main__":
    c = StockDataClient()
    print(c.get_realtime_quote("AAPL"))