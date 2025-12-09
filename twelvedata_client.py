"""
TWELVEDATA CLIENT v3.0 - COMPLETE TECHNICAL INDICATORS
=======================================================
✅ All technical indicators with proper API calls
✅ Stochastic RSI, Williams %R, DMI, ADX, MACD
✅ Composite indicators: Ultimate Oscillator, Awesome Oscillator, Chaikin Oscillator
✅ Rate limiting and caching
✅ Precise value extraction and normalization
"""

import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class TwelveDataClient:
    """
    Professional technical indicators from TwelveData API.
    Hardcoded API key with rate limiting and caching.
    """
    
    def __init__(self):
        self.api_key = "5e7a5daaf41d46a8966963106ebef210"
        self.base_url = "https://api.twelvedata.com"
        self.min_delay_between_requests = 8.0  # 8 seconds (8 req/min free tier)
        self.last_request_time = 0
        self._cache = {}
        self.cache_ttl = 300  # 5 minutes

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay_between_requests:
            sleep_time = self.min_delay_between_requests - elapsed
            print(f"   ⏳ Rate limiting: Waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Get cached data if still valid"""
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                print(f"   ✅ Using cached data for {cache_key}")
                return cached_data
        return None

    def _set_cache(self, cache_key: str, data: Dict):
        """Store data in cache"""
        self._cache[cache_key] = (data, time.time())

    def _fetch_indicator(self, symbol: str, indicator: str, interval: str = "1day", 
                         time_period: int = 14, **extra_params) -> Dict:
        """
        Fetch a single indicator from TwelveData API.
        
        Args:
            symbol: Stock ticker
            indicator: Indicator name (rsi, macd, adx, etc.)
            interval: Time interval (1min, 5min, 1day, etc.)
            time_period: Lookback period for calculation
            **extra_params: Additional indicator-specific parameters
        """
        cache_key = f"{symbol}_{indicator}_{interval}_{time_period}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        self._rate_limit()

        url = f"{self.base_url}/{indicator}"
        params = {
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key,
            'outputsize': 1  # Only get the latest value
        }
        
        # Add time_period if applicable
        if indicator not in ['macd', 'bbands', 'stoch']:  # These have their own period params
            params['time_period'] = time_period
        
        # Add extra parameters
        params.update(extra_params)

        try:
            print(f"   🔍 TwelveData: Fetching {indicator.upper()} for {symbol}...")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️ TwelveData API Error: HTTP {response.status_code}")
                return {}

            data = response.json()
            
            # Check for API errors
            if 'status' in data and data['status'] == 'error':
                print(f"   ⚠️ TwelveData API Error: {data.get('message', 'Unknown error')}")
                return {}
            
            # Check if we have values
            if 'values' not in data or not data['values']:
                print(f"   ⚠️ TwelveData: No values returned for {indicator}")
                print(f"      Response keys: {list(data.keys())}")
                return {}
            
            # Get the latest value
            latest = data['values'][0]
            
            # Debug: Show what we got
            print(f"   ✅ TwelveData: {indicator.upper()} fetched successfully")
            print(f"      Data keys: {list(latest.keys())}")
            print(f"      Sample value: {list(latest.values())[0] if latest else 'N/A'}")
            
            self._set_cache(cache_key, latest)
            return latest

        except requests.exceptions.Timeout:
            print(f"   ⚠️ TwelveData: Request timed out for {indicator}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ TwelveData: Connection error for {indicator} - {e}")
            return {}
        except Exception as e:
            print(f"   ⚠️ TwelveData: Unexpected error for {indicator} - {e}")
            return {}

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None or value == '':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_all_for_dashboard(self, symbol: str, interval: str = "1day") -> Dict:
        """
        Fetch all critical technical indicators for dashboard display.
        Returns normalized data structure ready for consumption.
        """
        print(f"\n📊 Fetching all technical indicators for {symbol} ({interval})...")
        
        indicators = {}
        
        # ========== MOMENTUM INDICATORS ==========
        
        # RSI (Relative Strength Index)
        rsi_data = self._fetch_indicator(symbol, 'rsi', interval, time_period=14)
        if rsi_data:
            indicators['rsi'] = self._safe_float(rsi_data.get('rsi', 0))
        
        # Stochastic RSI (Stochastic applied to RSI)
        stochrsi_data = self._fetch_indicator(symbol, 'stochrsi', interval, time_period=14)
        if stochrsi_data:
            # TwelveData returns 'k' and 'd' (not 'fast_k' and 'fast_d')
            k_value = self._safe_float(stochrsi_data.get('k', 0))
            if k_value == 0:
                k_value = self._safe_float(stochrsi_data.get('fast_k', 0))
            if k_value == 0:
                k_value = self._safe_float(stochrsi_data.get('fastk', 0))
            
            d_value = self._safe_float(stochrsi_data.get('d', 0))
            if d_value == 0:
                d_value = self._safe_float(stochrsi_data.get('fast_d', 0))
            if d_value == 0:
                d_value = self._safe_float(stochrsi_data.get('fastd', 0))
            
            indicators['stochrsi'] = {
                'valueK': k_value,
                'valueD': d_value
            }
            
            if k_value == 0 and d_value == 0:
                print(f"   ⚠️ Stochastic RSI: Both K and D are 0 for {symbol}. Available fields: {list(stochrsi_data.keys())}")
            else:
                print(f"   ✅ Stochastic RSI: K={k_value:.2f}, D={d_value:.2f}")
        
        # MACD (Moving Average Convergence Divergence)
        macd_data = self._fetch_indicator(symbol, 'macd', interval, 
                                          fast_period=12, slow_period=26, signal_period=9)
        if macd_data:
            indicators['macd'] = {
                'valueMACD': self._safe_float(macd_data.get('macd', 0)),
                'valueMACDSignal': self._safe_float(macd_data.get('macd_signal', 0)),
                'valueMACDHist': self._safe_float(macd_data.get('macd_hist', 0))
            }
        
        # CCI (Commodity Channel Index)
        cci_data = self._fetch_indicator(symbol, 'cci', interval, time_period=20)
        if cci_data:
            indicators['cci'] = self._safe_float(cci_data.get('cci', 0))
        
        # Stochastic Oscillator
        stoch_data = self._fetch_indicator(symbol, 'stoch', interval, 
                                           fast_k_period=14, slow_k_period=3, slow_d_period=3)
        if stoch_data:
            indicators['stoch'] = {
                'valueK': self._safe_float(stoch_data.get('slow_k', 0)),
                'valueD': self._safe_float(stoch_data.get('slow_d', 0))
            }
        
        # Williams %R
        willr_data = self._fetch_indicator(symbol, 'willr', interval, time_period=14)
        if willr_data:
            willr_value = self._safe_float(willr_data.get('willr', 0))
            if willr_value == 0:
                willr_value = self._safe_float(willr_data.get('williams', 0))
            if willr_value == 0:
                willr_value = self._safe_float(willr_data.get('williams_r', 0))
            
            indicators['williams_r'] = willr_value
            
            if willr_value == 0:
                print(f"   ⚠️ Williams %R: Value is 0 for {symbol}. Available fields: {list(willr_data.keys())}")
        
        # ========== TREND INDICATORS ==========
        
        # ADX (Average Directional Index)
        adx_data = self._fetch_indicator(symbol, 'adx', interval, time_period=14)
        if adx_data:
            indicators['adx'] = {
                'value': self._safe_float(adx_data.get('adx', 0))
            }
        
        # DMI (Directional Movement Index) - Plus DI and Minus DI
        plus_di_data = self._fetch_indicator(symbol, 'plus_di', interval, time_period=14)
        minus_di_data = self._fetch_indicator(symbol, 'minus_di', interval, time_period=14)
        
        if plus_di_data and minus_di_data:
            plus_di = self._safe_float(plus_di_data.get('plus_di', 0))
            minus_di = self._safe_float(minus_di_data.get('minus_di', 0))
            indicators['dmi'] = {
                'plus_di': plus_di,
                'minus_di': minus_di,
                'value': plus_di - minus_di  # Net directional movement
            }
        
        # Bollinger Bands
        bbands_data = self._fetch_indicator(symbol, 'bbands', interval, 
                                            time_period=20, sd=2)
        if bbands_data:
            indicators['bbands'] = {
                'upper': self._safe_float(bbands_data.get('upper_band', 0)),
                'middle': self._safe_float(bbands_data.get('middle_band', 0)),
                'lower': self._safe_float(bbands_data.get('lower_band', 0))
            }
        
        # ATR (Average True Range) - Volatility
        atr_data = self._fetch_indicator(symbol, 'atr', interval, time_period=14)
        if atr_data:
            indicators['atr'] = self._safe_float(atr_data.get('atr', 0))
        
        # EMA (Exponential Moving Average)
        ema_data = self._fetch_indicator(symbol, 'ema', interval, time_period=20)
        if ema_data:
            indicators['ema'] = self._safe_float(ema_data.get('ema', 0))
        
        # SMA (Simple Moving Average)
        sma_data = self._fetch_indicator(symbol, 'sma', interval, time_period=50)
        if sma_data:
            indicators['sma'] = self._safe_float(sma_data.get('sma', 0))
        
        # ========== VOLUME INDICATORS ==========
        
        # OBV (On Balance Volume)
        obv_data = self._fetch_indicator(symbol, 'obv', interval)
        if obv_data:
            indicators['obv'] = self._safe_float(obv_data.get('obv', 0))
        
        # ========== COMPOSITE INDICATORS ==========
        
        # Ultimate Oscillator (combines short, medium, and long-term momentum)
        ultosc_data = self._fetch_indicator(symbol, 'ultosc', interval, 
                                            time_period=28, time_period2=14, time_period3=7)
        if ultosc_data:
            ultosc_value = self._safe_float(ultosc_data.get('ultosc', 0))
            if ultosc_value == 0:
                ultosc_value = self._safe_float(ultosc_data.get('ultimate_oscillator', 0))
            if ultosc_value == 0:
                ultosc_value = self._safe_float(ultosc_data.get('value', 0))
            
            indicators['ultimate_oscillator'] = ultosc_value
        
        # Awesome Oscillator (AO) - Momentum indicator
        ao_data = self._fetch_indicator(symbol, 'ao', interval)
        if ao_data:
            ao_value = self._safe_float(ao_data.get('ao', 0))
            if ao_value == 0:
                # Try alternate field names
                ao_value = self._safe_float(ao_data.get('awesome_oscillator', 0))
            if ao_value == 0:
                ao_value = self._safe_float(ao_data.get('value', 0))
            
            indicators['awesome_oscillator'] = ao_value
            
            if ao_value == 0:
                print(f"   ⚠️ Awesome Oscillator: Value is 0 for {symbol}. Available fields: {list(ao_data.keys())}")
        
        # Chaikin Oscillator - Volume-weighted momentum
        adosc_data = self._fetch_indicator(symbol, 'adosc', interval, 
                                           fast_period=3, slow_period=10)
        if adosc_data:
            indicators['chaikin_oscillator'] = self._safe_float(adosc_data.get('adosc', 0))
        
        # ========== PRICE INDICATORS ==========
        
        # VWAP (Volume Weighted Average Price)
        vwap_data = self._fetch_indicator(symbol, 'vwap', interval)
        if vwap_data:
            indicators['vwap'] = self._safe_float(vwap_data.get('vwap', 0))
        
        print(f"✅ Fetched {len(indicators)} technical indicators for {symbol}\n")
        
        return {
            'indicators': indicators,
            'patterns': {}  # Patterns can be added later if needed
        }

    def get_rsi(self, symbol: str, interval: str = "1day", period: int = 14) -> float:
        """Get RSI value"""
        data = self._fetch_indicator(symbol, 'rsi', interval, period)
        return self._safe_float(data.get('rsi', 0))

    def get_macd(self, symbol: str, interval: str = "1day") -> Dict:
        """Get MACD values"""
        data = self._fetch_indicator(symbol, 'macd', interval, 
                                     fast_period=12, slow_period=26, signal_period=9)
        return {
            'valueMACD': self._safe_float(data.get('macd', 0)),
            'valueMACDSignal': self._safe_float(data.get('macd_signal', 0)),
            'valueMACDHist': self._safe_float(data.get('macd_hist', 0))
        }

    def get_adx(self, symbol: str, interval: str = "1day", period: int = 14) -> float:
        """Get ADX value"""
        data = self._fetch_indicator(symbol, 'adx', interval, period)
        return self._safe_float(data.get('adx', 0))

    def get_stochastic(self, symbol: str, interval: str = "1day") -> Dict:
        """Get Stochastic Oscillator values"""
        data = self._fetch_indicator(symbol, 'stoch', interval, 
                                     fast_k_period=14, slow_k_period=3, slow_d_period=3)
        return {
            'valueK': self._safe_float(data.get('slow_k', 0)),
            'valueD': self._safe_float(data.get('slow_d', 0))
        }

    def get_williams_r(self, symbol: str, interval: str = "1day", period: int = 14) -> float:
        """Get Williams %R value"""
        data = self._fetch_indicator(symbol, 'williams', interval, period)
        return self._safe_float(data.get('williams', 0))

    def get_bbands(self, symbol: str, interval: str = "1day", period: int = 20) -> Dict:
        """Get Bollinger Bands values"""
        data = self._fetch_indicator(symbol, 'bbands', interval, time_period=period, sd=2)
        return {
            'upper': self._safe_float(data.get('upper_band', 0)),
            'middle': self._safe_float(data.get('middle_band', 0)),
            'lower': self._safe_float(data.get('lower_band', 0))
        }

    def get_dmi(self, symbol: str, interval: str = "1day", period: int = 14) -> Dict:
        """Get DMI (Directional Movement Index) values"""
        plus_di_data = self._fetch_indicator(symbol, 'plus_di', interval, period)
        minus_di_data = self._fetch_indicator(symbol, 'minus_di', interval, period)
        
        plus_di = self._safe_float(plus_di_data.get('plus_di', 0))
        minus_di = self._safe_float(minus_di_data.get('minus_di', 0))
        
        return {
            'plus_di': plus_di,
            'minus_di': minus_di,
            'value': plus_di - minus_di
        }

    def get_composite_indicators(self, symbol: str, interval: str = "1day") -> Dict:
        """Get all composite indicators"""
        ultosc_data = self._fetch_indicator(symbol, 'ultosc', interval, 
                                            time_period=28, time_period2=14, time_period3=7)
        ao_data = self._fetch_indicator(symbol, 'ao', interval)
        adosc_data = self._fetch_indicator(symbol, 'adosc', interval, 
                                           fast_period=3, slow_period=10)
        
        return {
            'ultimate_oscillator': self._safe_float(ultosc_data.get('ultosc', 0)),
            'awesome_oscillator': self._safe_float(ao_data.get('ao', 0)),
            'chaikin_oscillator': self._safe_float(adosc_data.get('adosc', 0))
        }
