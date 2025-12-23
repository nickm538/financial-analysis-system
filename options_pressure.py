"""
OPTIONS PRESSURE INDICATOR
===========================
Free options flow analysis using yfinance.

Calculates buying vs selling pressure from options data:
- Put/Call Ratio (volume-based)
- Call Pressure vs Put Pressure
- Unusual Activity Detection
- Visual Pressure Bar metrics

For integration with Streamlit dashboard.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time


class OptionsPressure:
    """
    Options Pressure Indicator
    
    Analyzes options flow to determine bullish/bearish pressure.
    Uses free yfinance data (15-min delay).
    """
    
    def __init__(self):
        """Initialize Options Pressure analyzer."""
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def get_pressure_analysis(self, ticker: str) -> Dict:
        """
        Get comprehensive options pressure analysis for a ticker.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Dict with pressure metrics and visualization data
        """
        try:
            # Check cache
            cache_key = f"{ticker}_pressure"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if time.time() - cached_time < self.cache_duration:
                    return cached_data
            
            # Fetch options data
            stock = yf.Ticker(ticker)
            
            # Get available expiration dates
            expirations = stock.options
            if not expirations:
                return self._empty_result(ticker, "No options data available")
            
            # Analyze nearest 3 expirations for comprehensive view
            all_calls = []
            all_puts = []
            
            for exp in expirations[:3]:  # First 3 expirations
                try:
                    chain = stock.option_chain(exp)
                    all_calls.append(chain.calls)
                    all_puts.append(chain.puts)
                except Exception:
                    continue
            
            if not all_calls or not all_puts:
                return self._empty_result(ticker, "Failed to fetch options chain")
            
            # Combine all data
            calls_df = pd.concat(all_calls, ignore_index=True)
            puts_df = pd.concat(all_puts, ignore_index=True)
            
            # Calculate pressure metrics
            result = self._calculate_pressure(ticker, calls_df, puts_df)
            
            # Cache result
            self.cache[cache_key] = (time.time(), result)
            
            return result
            
        except Exception as e:
            return self._empty_result(ticker, str(e))
    
    def _calculate_pressure(self, ticker: str, calls: pd.DataFrame, puts: pd.DataFrame) -> Dict:
        """
        Calculate all pressure metrics from options data.
        
        Args:
            ticker: Stock symbol
            calls: DataFrame of call options
            puts: DataFrame of put options
            
        Returns:
            Dict with all pressure metrics
        """
        # Volume metrics - fillna(0) BEFORE sum to handle NaN contracts
        call_volume = calls['volume'].fillna(0).sum() if 'volume' in calls.columns else 0
        put_volume = puts['volume'].fillna(0).sum() if 'volume' in puts.columns else 0
        
        # Ensure numeric types (handle any remaining edge cases)
        call_volume = float(call_volume) if not pd.isna(call_volume) else 0.0
        put_volume = float(put_volume) if not pd.isna(put_volume) else 0.0
        total_volume = call_volume + put_volume
        
        # Open Interest metrics - fillna(0) BEFORE sum
        call_oi = calls['openInterest'].fillna(0).sum() if 'openInterest' in calls.columns else 0
        put_oi = puts['openInterest'].fillna(0).sum() if 'openInterest' in puts.columns else 0
        
        # Ensure numeric types
        call_oi = float(call_oi) if not pd.isna(call_oi) else 0.0
        put_oi = float(put_oi) if not pd.isna(put_oi) else 0.0
        total_oi = call_oi + put_oi
        
        # Put/Call Ratio (Volume-based)
        pcr_volume = put_volume / call_volume if call_volume > 0 else 0
        
        # Put/Call Ratio (Open Interest-based)
        pcr_oi = put_oi / call_oi if call_oi > 0 else 0
        
        # Pressure Calculation
        # Buying Pressure = Call activity weighted by volume
        # Selling Pressure = Put activity weighted by volume
        call_pressure = call_volume * 100  # Simplified weighting
        put_pressure = put_volume * 100
        
        # Net Pressure (-100 to +100 scale)
        # Positive = Bullish, Negative = Bearish
        if total_volume > 0:
            net_pressure = ((call_volume - put_volume) / total_volume) * 100
        else:
            net_pressure = 0
        
        # Pressure Bar Value (0 to 100, where 50 is neutral)
        # 0 = Maximum Bearish, 100 = Maximum Bullish
        pressure_bar = 50 + (net_pressure / 2)
        pressure_bar = max(0, min(100, pressure_bar))  # Clamp to 0-100
        
        # Sentiment Classification
        if net_pressure > 20:
            sentiment = "VERY_BULLISH"
            sentiment_color = "#00c851"
        elif net_pressure > 5:
            sentiment = "BULLISH"
            sentiment_color = "#4CAF50"
        elif net_pressure > -5:
            sentiment = "NEUTRAL"
            sentiment_color = "#9E9E9E"
        elif net_pressure > -20:
            sentiment = "BEARISH"
            sentiment_color = "#FF5722"
        else:
            sentiment = "VERY_BEARISH"
            sentiment_color = "#F44336"
        
        # Unusual Activity Detection
        unusual_calls = self._detect_unusual_activity(calls)
        unusual_puts = self._detect_unusual_activity(puts)
        
        # Most Active Strikes
        top_call_strikes = self._get_top_strikes(calls, 5)
        top_put_strikes = self._get_top_strikes(puts, 5)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            
            # Core Pressure Metrics
            'pressure_bar': round(pressure_bar, 1),
            'net_pressure': round(net_pressure, 1),
            'sentiment': sentiment,
            'sentiment_color': sentiment_color,
            
            # Volume Metrics
            'call_volume': int(call_volume),
            'put_volume': int(put_volume),
            'total_volume': int(total_volume),
            
            # Open Interest
            'call_oi': int(call_oi),
            'put_oi': int(put_oi),
            'total_oi': int(total_oi),
            
            # Ratios
            'pcr_volume': round(pcr_volume, 2),
            'pcr_oi': round(pcr_oi, 2),
            
            # Unusual Activity
            'unusual_calls': unusual_calls,
            'unusual_puts': unusual_puts,
            'has_unusual_activity': len(unusual_calls) > 0 or len(unusual_puts) > 0,
            
            # Top Strikes
            'top_call_strikes': top_call_strikes,
            'top_put_strikes': top_put_strikes,
            
            # Status
            'status': 'success',
            'data_delay': '15-min delayed',
            'error': None
        }
    
    def _detect_unusual_activity(self, options_df: pd.DataFrame, threshold: float = 2.0) -> List[Dict]:
        """
        Detect unusual options activity (volume > threshold × open interest).
        
        Args:
            options_df: DataFrame of options
            threshold: Volume/OI ratio threshold
            
        Returns:
            List of unusual activity items
        """
        unusual = []
        
        if options_df.empty:
            return unusual
        
        for _, row in options_df.iterrows():
            volume = row.get('volume', 0)
            oi = row.get('openInterest', 0)
            
            # Skip if no data
            if pd.isna(volume) or pd.isna(oi) or oi == 0:
                continue
            
            vol_oi_ratio = volume / oi
            
            if vol_oi_ratio >= threshold and volume >= 100:
                unusual.append({
                    'strike': row.get('strike', 0),
                    'volume': int(volume),
                    'open_interest': int(oi),
                    'vol_oi_ratio': round(vol_oi_ratio, 2),
                    'last_price': row.get('lastPrice', 0),
                    'implied_volatility': round(row.get('impliedVolatility', 0) * 100, 1)
                })
        
        # Sort by volume/OI ratio
        unusual.sort(key=lambda x: x['vol_oi_ratio'], reverse=True)
        
        return unusual[:5]  # Top 5 unusual
    
    def _get_top_strikes(self, options_df: pd.DataFrame, n: int = 5) -> List[Dict]:
        """
        Get top N most active strikes by volume.
        
        Args:
            options_df: DataFrame of options
            n: Number of top strikes to return
            
        Returns:
            List of top strike data
        """
        if options_df.empty:
            return []
        
        # Sort by volume
        sorted_df = options_df.sort_values('volume', ascending=False).head(n)
        
        top_strikes = []
        for _, row in sorted_df.iterrows():
            volume = row.get('volume', 0)
            if pd.isna(volume) or volume == 0:
                continue
                
            top_strikes.append({
                'strike': row.get('strike', 0),
                'volume': int(volume),
                'open_interest': int(row.get('openInterest', 0)) if not pd.isna(row.get('openInterest', 0)) else 0,
                'last_price': round(row.get('lastPrice', 0), 2),
                'bid': round(row.get('bid', 0), 2),
                'ask': round(row.get('ask', 0), 2)
            })
        
        return top_strikes
    
    def _empty_result(self, ticker: str, error: str) -> Dict:
        """Return empty result structure with error."""
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            
            # Core Pressure Metrics
            'pressure_bar': 50,  # Neutral
            'net_pressure': 0,
            'sentiment': 'UNKNOWN',
            'sentiment_color': '#9E9E9E',
            
            # Volume Metrics
            'call_volume': 0,
            'put_volume': 0,
            'total_volume': 0,
            
            # Open Interest
            'call_oi': 0,
            'put_oi': 0,
            'total_oi': 0,
            
            # Ratios
            'pcr_volume': 0,
            'pcr_oi': 0,
            
            # Unusual Activity
            'unusual_calls': [],
            'unusual_puts': [],
            'has_unusual_activity': False,
            
            # Top Strikes
            'top_call_strikes': [],
            'top_put_strikes': [],
            
            # Status
            'status': 'error',
            'data_delay': 'N/A',
            'error': error
        }
    
    def get_pressure_bar_html(self, pressure_data: Dict) -> str:
        """
        Generate HTML for the visual pressure bar.
        
        Args:
            pressure_data: Result from get_pressure_analysis()
            
        Returns:
            HTML string for the pressure bar visualization
        """
        pressure_bar = pressure_data.get('pressure_bar', 50)
        sentiment = pressure_data.get('sentiment', 'NEUTRAL')
        sentiment_color = pressure_data.get('sentiment_color', '#9E9E9E')
        net_pressure = pressure_data.get('net_pressure', 0)
        
        # Determine bar fill direction
        # Left side (0-50) = Bearish (red)
        # Right side (50-100) = Bullish (green)
        
        if net_pressure >= 0:
            # Bullish - fill from center to right
            left_width = 50
            right_width = pressure_bar - 50
            left_color = "#2d2d2d"
            right_color = "#00c851"
        else:
            # Bearish - fill from center to left
            left_width = 50 - (50 - pressure_bar)
            right_width = 0
            left_color = "#F44336"
            right_color = "#2d2d2d"
        
        html = f"""
        <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="color: #F44336; font-weight: bold;">🐻 BEARISH</span>
                <span style="color: {sentiment_color}; font-weight: bold; font-size: 1.2em;">{sentiment}</span>
                <span style="color: #00c851; font-weight: bold;">BULLISH 🐂</span>
            </div>
            
            <div style="background: #2d2d2d; border-radius: 10px; height: 40px; position: relative; overflow: hidden;">
                <!-- Center line -->
                <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: #fff; z-index: 2;"></div>
                
                <!-- Pressure fill -->
                <div style="
                    position: absolute;
                    left: {min(pressure_bar, 50)}%;
                    width: {abs(pressure_bar - 50)}%;
                    height: 100%;
                    background: linear-gradient(90deg, {left_color if net_pressure < 0 else '#2d2d2d'}, {sentiment_color});
                    border-radius: 5px;
                    transition: all 0.5s ease;
                "></div>
                
                <!-- Pressure indicator -->
                <div style="
                    position: absolute;
                    left: {pressure_bar}%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                    width: 20px;
                    height: 20px;
                    background: {sentiment_color};
                    border-radius: 50%;
                    border: 3px solid white;
                    z-index: 3;
                    box-shadow: 0 0 10px {sentiment_color};
                "></div>
            </div>
            
            <div style="display: flex; justify-content: space-between; margin-top: 10px; color: #888;">
                <span>0</span>
                <span style="color: {sentiment_color}; font-weight: bold;">{net_pressure:+.1f}%</span>
                <span>100</span>
            </div>
        </div>
        """
        
        return html


# Test function
if __name__ == "__main__":
    print("Testing Options Pressure Indicator...")
    
    pressure = OptionsPressure()
    result = pressure.get_pressure_analysis("AAPL")
    
    print(f"\nTicker: {result['ticker']}")
    print(f"Pressure Bar: {result['pressure_bar']}/100")
    print(f"Net Pressure: {result['net_pressure']}%")
    print(f"Sentiment: {result['sentiment']}")
    print(f"\nCall Volume: {result['call_volume']:,}")
    print(f"Put Volume: {result['put_volume']:,}")
    print(f"Put/Call Ratio: {result['pcr_volume']}")
    print(f"\nUnusual Activity: {result['has_unusual_activity']}")
    
    if result['unusual_calls']:
        print("\nUnusual Calls:")
        for item in result['unusual_calls'][:3]:
            print(f"  Strike ${item['strike']}: Vol {item['volume']:,}, V/OI {item['vol_oi_ratio']}x")
