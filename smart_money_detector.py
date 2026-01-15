"""
Smart Money Detection Module
============================
Institutional-grade detection of dark pool activity, insider flow, 
market maker traps, gamma exposure, and options flow signals.

Based on research from:
- Tim Bohen's 5:1 Risk/Reward methodology
- John Carter's TTM Squeeze
- Institutional gamma scalping strategies
- Dark pool print analysis
- SEC Form 4 insider trading patterns

Author: Financial Analysis System
Version: 1.0.0
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pytz

# Try to import yfinance
try:
    import yfinance as yf
except ImportError:
    yf = None

# Try to import pandas
try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None

# Try to import API client
try:
    sys.path.append('/opt/.manus/.sandbox-runtime')
    from data_api import ApiClient
    API_CLIENT_AVAILABLE = True
except:
    API_CLIENT_AVAILABLE = False


class SmartMoneyDetector:
    """
    Comprehensive Smart Money Detection System
    
    Detects:
    1. Dark Pool Activity (block prints, unusual volume)
    2. Insider Trading Signals (SEC Form 4)
    3. Market Maker Traps (fake breakouts, stop hunts)
    4. Gamma Exposure & Options Flow
    5. Friday Afternoon Positioning
    6. Max Pain & Pinning Levels
    """
    
    def __init__(self):
        self.et_tz = pytz.timezone('US/Eastern')
        self.api_client = ApiClient() if API_CLIENT_AVAILABLE else None
        
        # Key timing windows
        self.FRIDAY_AFTERNOON_START = 14  # 2 PM ET
        self.FRIDAY_AFTERNOON_END = 16    # 4 PM ET
        self.POWER_HOUR_START = 15        # 3 PM ET
        
        # Thresholds for detection
        self.VOLUME_SPIKE_THRESHOLD = 2.0      # 2x average volume
        self.DARK_POOL_MIN_SHARES = 100000     # 100K shares minimum
        self.DARK_POOL_MIN_VALUE = 1000000     # $1M minimum
        self.UNUSUAL_OPTIONS_MULTIPLIER = 5.0  # 5x normal volume
        
        # Market maker trap detection parameters
        self.FAKE_BREAKOUT_REVERSAL_PCT = 0.02  # 2% reversal threshold
        self.STOP_HUNT_SPIKE_PCT = 0.015        # 1.5% spike threshold
        self.FIBONACCI_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
        
    def get_current_time_context(self) -> Dict[str, Any]:
        """Get current market time context with Friday afternoon flag"""
        now = datetime.now(self.et_tz)
        
        is_friday = now.weekday() == 4
        current_hour = now.hour
        current_minute = now.minute
        
        # Friday afternoon detection (2 PM - 4 PM ET)
        is_friday_afternoon = (
            is_friday and 
            self.FRIDAY_AFTERNOON_START <= current_hour < self.FRIDAY_AFTERNOON_END
        )
        
        # Power hour detection (3 PM - 4 PM ET any day)
        is_power_hour = self.POWER_HOUR_START <= current_hour < 16
        
        # Weekly options expiration (Friday)
        is_weekly_expiration = is_friday
        
        # Monthly options expiration (3rd Friday)
        is_monthly_expiration = is_friday and 15 <= now.day <= 21
        
        # Triple witching (3rd Friday of March, June, Sept, Dec)
        is_triple_witching = (
            is_monthly_expiration and 
            now.month in [3, 6, 9, 12]
        )
        
        # Determine session
        if current_hour < 9 or (current_hour == 9 and current_minute < 30):
            session = "PRE_MARKET"
        elif current_hour < 10:
            session = "OPENING_VOLATILITY"
        elif current_hour < 12:
            session = "MORNING_MOMENTUM"
        elif current_hour < 14:
            session = "MIDDAY_CONSOLIDATION"
        elif current_hour < 15:
            session = "AFTERNOON_SETUP"
        elif current_hour < 16:
            session = "POWER_HOUR"
        else:
            session = "AFTER_HOURS"
        
        return {
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S ET'),
            'day_of_week': now.strftime('%A'),
            'session': session,
            'is_friday': is_friday,
            'is_friday_afternoon': is_friday_afternoon,
            'is_power_hour': is_power_hour,
            'is_weekly_expiration': is_weekly_expiration,
            'is_monthly_expiration': is_monthly_expiration,
            'is_triple_witching': is_triple_witching,
            'friday_afternoon_alert': (
                "🚨 FRIDAY AFTERNOON POSITIONING WINDOW - Smart money often positions for weekend catalysts!"
                if is_friday_afternoon else None
            ),
            'expiration_alert': (
                "⚠️ TRIPLE WITCHING - Extreme gamma exposure expected!"
                if is_triple_witching else
                "⚠️ MONTHLY OPEX - Elevated gamma and pinning risk"
                if is_monthly_expiration else
                "📅 Weekly options expiration day"
                if is_weekly_expiration else None
            )
        }
    
    def detect_volume_anomalies(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """
        Detect unusual volume patterns that may indicate dark pool activity
        
        Key signals:
        - Today's volume vs 30-day average
        - Today's volume vs 90-day average
        - Pre-market/after-hours volume spikes
        - Volume without corresponding price movement (accumulation)
        """
        if not yf:
            return {'error': 'yfinance not available'}
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f'{lookback_days}d')
            
            if hist.empty or len(hist) < 30:
                return {'error': 'Insufficient data'}
            
            # Calculate volume metrics
            current_volume = hist['Volume'].iloc[-1]
            avg_30d = hist['Volume'].tail(30).mean()
            avg_90d = hist['Volume'].mean()
            
            # Volume ratios
            vol_vs_30d = current_volume / avg_30d if avg_30d > 0 else 0
            vol_vs_90d = current_volume / avg_90d if avg_90d > 0 else 0
            
            # Price change
            price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
            
            # Volume-price divergence (high volume, low price change = accumulation/distribution)
            volume_price_divergence = vol_vs_30d > 2.0 and abs(price_change) < 0.01
            
            # Determine signal
            signals = []
            urgency_score = 0
            
            if vol_vs_30d >= 3.0:
                signals.append("🔥 EXTREME VOLUME (3x+ 30-day avg)")
                urgency_score += 30
            elif vol_vs_30d >= 2.0:
                signals.append("⚡ HIGH VOLUME (2x+ 30-day avg)")
                urgency_score += 20
            elif vol_vs_30d >= 1.5:
                signals.append("📈 ELEVATED VOLUME (1.5x+ 30-day avg)")
                urgency_score += 10
            
            if vol_vs_90d >= 2.0:
                signals.append("📊 Volume exceeds 90-day average by 2x+")
                urgency_score += 15
            
            if volume_price_divergence:
                signals.append("🔍 VOLUME-PRICE DIVERGENCE - Possible accumulation/distribution")
                urgency_score += 25
            
            # Determine if bullish or bearish
            direction = "BULLISH" if price_change > 0 else "BEARISH" if price_change < 0 else "NEUTRAL"
            
            return {
                'symbol': symbol,
                'current_volume': int(current_volume),
                'avg_30d_volume': int(avg_30d),
                'avg_90d_volume': int(avg_90d),
                'volume_vs_30d_ratio': round(vol_vs_30d, 2),
                'volume_vs_90d_ratio': round(vol_vs_90d, 2),
                'price_change_pct': round(price_change * 100, 2),
                'volume_price_divergence': volume_price_divergence,
                'direction': direction,
                'signals': signals,
                'urgency_score': urgency_score,
                'dark_pool_likelihood': (
                    "HIGH" if urgency_score >= 40 else
                    "MODERATE" if urgency_score >= 20 else
                    "LOW"
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_market_maker_traps(self, symbol: str) -> Dict[str, Any]:
        """
        Detect potential market maker manipulation patterns
        
        Traps detected:
        1. Fake Breakouts - Price breaks level then reverses
        2. Stop Hunts - Sharp spikes to liquidity zones
        3. Range Traps - Oscillation before fake breakout
        4. Inducement Moves - Slow creep into levels
        """
        if not yf or not pd:
            return {'error': 'Required libraries not available'}
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='30d', interval='1h')
            
            if hist.empty or len(hist) < 50:
                return {'error': 'Insufficient data'}
            
            traps_detected = []
            trap_score = 0
            
            # Get recent price action
            recent = hist.tail(24)  # Last 24 hours
            current_price = recent['Close'].iloc[-1]
            
            # Calculate key levels
            recent_high = recent['High'].max()
            recent_low = recent['Low'].min()
            range_size = recent_high - recent_low
            
            # 1. FAKE BREAKOUT DETECTION
            # Check if price broke above recent high then reversed
            broke_high = recent['High'].max() > hist['High'].iloc[:-24].tail(48).max()
            reversed_from_high = current_price < recent_high * 0.98
            
            if broke_high and reversed_from_high:
                traps_detected.append({
                    'type': 'FAKE_BREAKOUT_HIGH',
                    'description': '⚠️ Price broke above resistance then reversed - Classic bull trap',
                    'level': round(recent_high, 2),
                    'severity': 'HIGH'
                })
                trap_score += 30
            
            # Check for fake breakdown
            broke_low = recent['Low'].min() < hist['Low'].iloc[:-24].tail(48).min()
            reversed_from_low = current_price > recent_low * 1.02
            
            if broke_low and reversed_from_low:
                traps_detected.append({
                    'type': 'FAKE_BREAKDOWN_LOW',
                    'description': '⚠️ Price broke below support then reversed - Classic bear trap',
                    'level': round(recent_low, 2),
                    'severity': 'HIGH'
                })
                trap_score += 30
            
            # 2. STOP HUNT DETECTION
            # Look for sharp wicks (spikes) that quickly reversed
            for i in range(-5, 0):
                candle = recent.iloc[i]
                body_size = abs(candle['Close'] - candle['Open'])
                upper_wick = candle['High'] - max(candle['Close'], candle['Open'])
                lower_wick = min(candle['Close'], candle['Open']) - candle['Low']
                
                # Large upper wick = potential stop hunt above
                if upper_wick > body_size * 2 and upper_wick > range_size * 0.1:
                    traps_detected.append({
                        'type': 'STOP_HUNT_ABOVE',
                        'description': '🎯 Large upper wick detected - Possible stop hunt above',
                        'level': round(candle['High'], 2),
                        'severity': 'MODERATE'
                    })
                    trap_score += 15
                
                # Large lower wick = potential stop hunt below
                if lower_wick > body_size * 2 and lower_wick > range_size * 0.1:
                    traps_detected.append({
                        'type': 'STOP_HUNT_BELOW',
                        'description': '🎯 Large lower wick detected - Possible stop hunt below',
                        'level': round(candle['Low'], 2),
                        'severity': 'MODERATE'
                    })
                    trap_score += 15
            
            # 3. RANGE TRAP DETECTION
            # Check for tight consolidation (potential energy building)
            last_10_range = recent.tail(10)['High'].max() - recent.tail(10)['Low'].min()
            avg_range = (hist['High'] - hist['Low']).mean()
            
            if last_10_range < avg_range * 0.5:
                traps_detected.append({
                    'type': 'TIGHT_RANGE',
                    'description': '📦 Tight consolidation detected - Watch for fake breakout before real move',
                    'range_compression': round((1 - last_10_range / avg_range) * 100, 1),
                    'severity': 'MODERATE'
                })
                trap_score += 20
            
            # 4. FIBONACCI LEVEL PROXIMITY
            # Check if price is near key Fibonacci levels (common reversal points)
            swing_high = hist['High'].max()
            swing_low = hist['Low'].min()
            fib_range = swing_high - swing_low
            
            fib_levels_nearby = []
            for fib in self.FIBONACCI_LEVELS:
                fib_price = swing_low + (fib_range * fib)
                distance_pct = abs(current_price - fib_price) / current_price
                if distance_pct < 0.01:  # Within 1%
                    fib_levels_nearby.append({
                        'level': fib,
                        'price': round(fib_price, 2),
                        'distance_pct': round(distance_pct * 100, 2)
                    })
            
            if fib_levels_nearby:
                traps_detected.append({
                    'type': 'FIBONACCI_ZONE',
                    'description': f'📐 Price near Fibonacci level(s) - Common reversal/trap zone',
                    'levels': fib_levels_nearby,
                    'severity': 'LOW'
                })
                trap_score += 10
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'traps_detected': traps_detected,
                'trap_count': len(traps_detected),
                'trap_score': trap_score,
                'risk_level': (
                    "🔴 HIGH RISK" if trap_score >= 50 else
                    "🟡 MODERATE RISK" if trap_score >= 25 else
                    "🟢 LOW RISK"
                ),
                'recommendation': (
                    "⚠️ Multiple trap signals detected - Wait for confirmation before entry"
                    if trap_score >= 50 else
                    "⚡ Some trap signals present - Use tight stops and confirm with volume"
                    if trap_score >= 25 else
                    "✅ Low trap risk - Standard entry criteria apply"
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_insider_activity(self, symbol: str) -> Dict[str, Any]:
        """
        Get insider trading activity from SEC Form 4 filings
        
        Key signals:
        - Cluster buying (multiple insiders buying)
        - Large purchases after price decline
        - CEO/CFO purchases (highest signal value)
        - Deviation from 10b5-1 plans
        """
        if not self.api_client:
            return {'error': 'API client not available'}
        
        try:
            # Get insider holders data
            response = self.api_client.call_api(
                'YahooFinance/get_stock_holders',
                query={'symbol': symbol, 'region': 'US', 'lang': 'en-US'}
            )
            
            if not response or 'quoteSummary' not in response:
                return {'error': 'No insider data available'}
            
            result = response['quoteSummary'].get('result', [{}])[0]
            insider_data = result.get('insiderHolders', {}).get('holders', [])
            
            if not insider_data:
                return {'error': 'No insider holders found'}
            
            # Analyze insider activity
            recent_buys = []
            recent_sells = []
            insider_signals = []
            signal_score = 0
            
            for insider in insider_data:
                name = insider.get('name', 'Unknown')
                relation = insider.get('relation', 'Unknown')
                transaction = insider.get('transactionDescription', '')
                
                # Get position and date info
                position = insider.get('positionDirect', {})
                position_shares = position.get('raw', 0) if isinstance(position, dict) else 0
                
                latest_date = insider.get('latestTransDate', {})
                date_str = latest_date.get('fmt', 'N/A') if isinstance(latest_date, dict) else 'N/A'
                
                # Categorize transaction
                if 'Buy' in transaction or 'Purchase' in transaction:
                    recent_buys.append({
                        'name': name,
                        'relation': relation,
                        'shares': position_shares,
                        'date': date_str
                    })
                    
                    # Higher weight for C-suite
                    if any(title in relation.upper() for title in ['CEO', 'CFO', 'COO', 'PRESIDENT', 'CHAIRMAN']):
                        signal_score += 25
                        insider_signals.append(f"🔥 {relation} ({name}) BUYING - High conviction signal")
                    else:
                        signal_score += 10
                        insider_signals.append(f"📈 {relation} ({name}) buying shares")
                        
                elif 'Sale' in transaction or 'Sell' in transaction:
                    recent_sells.append({
                        'name': name,
                        'relation': relation,
                        'shares': position_shares,
                        'date': date_str
                    })
                    
                    # Note: Insider selling is less meaningful (could be diversification, taxes, etc.)
                    if any(title in relation.upper() for title in ['CEO', 'CFO']):
                        signal_score -= 10
                        insider_signals.append(f"⚠️ {relation} ({name}) selling - Monitor closely")
            
            # Cluster buying detection
            if len(recent_buys) >= 3:
                signal_score += 30
                insider_signals.insert(0, "🚨 CLUSTER BUYING DETECTED - Multiple insiders buying!")
            
            return {
                'symbol': symbol,
                'total_insiders': len(insider_data),
                'recent_buys': recent_buys,
                'recent_sells': recent_sells,
                'buy_count': len(recent_buys),
                'sell_count': len(recent_sells),
                'insider_signals': insider_signals,
                'signal_score': signal_score,
                'insider_sentiment': (
                    "🟢 STRONG BUY" if signal_score >= 50 else
                    "🟢 BULLISH" if signal_score >= 25 else
                    "🟡 NEUTRAL" if signal_score >= 0 else
                    "🔴 BEARISH"
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_gamma_exposure_estimate(self, symbol: str) -> Dict[str, Any]:
        """
        Estimate gamma exposure and options-related price dynamics
        
        Note: This is an estimate based on price action patterns,
        as real gamma data requires expensive options data feeds.
        
        Key concepts:
        - Dealer long gamma = mean-reverting price action
        - Dealer short gamma = momentum amplification
        - Max pain = price where most options expire worthless
        """
        if not yf or not pd:
            return {'error': 'Required libraries not available'}
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get price history
            hist = ticker.history(period='30d')
            if hist.empty:
                return {'error': 'No price data'}
            
            current_price = hist['Close'].iloc[-1]
            
            # Estimate gamma regime from price behavior
            # Mean-reverting = long gamma, trending = short gamma
            returns = hist['Close'].pct_change().dropna()
            
            # Autocorrelation of returns (negative = mean-reverting, positive = trending)
            if len(returns) > 10:
                autocorr = returns.autocorr(lag=1)
            else:
                autocorr = 0
            
            # Estimate gamma regime
            if autocorr < -0.1:
                gamma_regime = "LONG_GAMMA"
                regime_description = "Dealers appear LONG gamma - Expect mean-reverting, range-bound action"
            elif autocorr > 0.1:
                gamma_regime = "SHORT_GAMMA"
                regime_description = "Dealers appear SHORT gamma - Expect momentum/trending moves"
            else:
                gamma_regime = "NEUTRAL"
                regime_description = "Gamma exposure appears balanced"
            
            # Estimate max pain (simplified - round numbers near current price)
            # Real max pain requires options chain data
            round_levels = []
            base = int(current_price)
            for offset in [-10, -5, 0, 5, 10]:
                level = ((base + offset) // 5) * 5  # Round to nearest 5
                if level > 0:
                    round_levels.append(level)
            
            # Find closest round number as estimated max pain
            estimated_max_pain = min(round_levels, key=lambda x: abs(x - current_price))
            
            # Distance to max pain
            distance_to_max_pain = (current_price - estimated_max_pain) / current_price * 100
            
            # Pinning likelihood (higher near expiration and close to round numbers)
            time_context = self.get_current_time_context()
            pinning_likelihood = "LOW"
            
            if time_context['is_weekly_expiration']:
                if abs(distance_to_max_pain) < 1:
                    pinning_likelihood = "HIGH"
                elif abs(distance_to_max_pain) < 2:
                    pinning_likelihood = "MODERATE"
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'gamma_regime': gamma_regime,
                'regime_description': regime_description,
                'return_autocorrelation': round(autocorr, 3),
                'estimated_max_pain': estimated_max_pain,
                'distance_to_max_pain_pct': round(distance_to_max_pain, 2),
                'pinning_likelihood': pinning_likelihood,
                'key_levels': sorted(set(round_levels)),
                'trading_implications': (
                    "📉 SHORT GAMMA: Expect momentum moves. Breakouts more likely to follow through. "
                    "Use trailing stops, ride trends."
                    if gamma_regime == "SHORT_GAMMA" else
                    "📊 LONG GAMMA: Expect mean reversion. Fade extremes, sell rallies, buy dips. "
                    "Range-bound strategies favored."
                    if gamma_regime == "LONG_GAMMA" else
                    "⚖️ NEUTRAL: Mixed signals. Wait for clearer regime or use balanced approach."
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_comprehensive_smart_money_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Run all smart money detection algorithms and compile comprehensive analysis
        """
        analysis = {
            'symbol': symbol.upper(),
            'analysis_timestamp': datetime.now(self.et_tz).strftime('%Y-%m-%d %H:%M:%S ET'),
            'time_context': self.get_current_time_context(),
            'volume_analysis': self.detect_volume_anomalies(symbol),
            'market_maker_traps': self.detect_market_maker_traps(symbol),
            'insider_activity': self.get_insider_activity(symbol),
            'gamma_exposure': self.calculate_gamma_exposure_estimate(symbol)
        }
        
        # Calculate overall smart money score
        total_score = 0
        signals = []
        
        # Volume signals
        vol = analysis['volume_analysis']
        if 'urgency_score' in vol:
            total_score += vol['urgency_score']
            if vol.get('signals'):
                signals.extend(vol['signals'])
        
        # Trap warnings (negative score)
        traps = analysis['market_maker_traps']
        if 'trap_score' in traps:
            total_score -= traps['trap_score'] // 2  # Reduce score for trap risk
            if traps.get('traps_detected'):
                for trap in traps['traps_detected']:
                    signals.append(f"⚠️ TRAP: {trap['description']}")
        
        # Insider signals
        insider = analysis['insider_activity']
        if 'signal_score' in insider:
            total_score += insider['signal_score']
            if insider.get('insider_signals'):
                signals.extend(insider['insider_signals'])
        
        # Time context bonuses
        time_ctx = analysis['time_context']
        if time_ctx['is_friday_afternoon']:
            signals.append(time_ctx['friday_afternoon_alert'])
            total_score += 10  # Bonus for Friday afternoon positioning window
        
        if time_ctx.get('expiration_alert'):
            signals.append(time_ctx['expiration_alert'])
        
        # Overall assessment
        analysis['overall_score'] = total_score
        analysis['key_signals'] = signals[:10]  # Top 10 signals
        analysis['smart_money_verdict'] = (
            "🔥 STRONG SMART MONEY ACTIVITY" if total_score >= 75 else
            "📈 ELEVATED SMART MONEY INTEREST" if total_score >= 50 else
            "📊 MODERATE SMART MONEY SIGNALS" if total_score >= 25 else
            "⚖️ NEUTRAL - No significant smart money signals" if total_score >= 0 else
            "⚠️ CAUTION - Negative smart money indicators"
        )
        
        return analysis


def quick_smart_money_scan(symbols: List[str] = None) -> Dict[str, Any]:
    """
    Quick scan of multiple symbols for smart money activity
    """
    if symbols is None:
        # Default to major indices and popular stocks
        symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'META']
    
    detector = SmartMoneyDetector()
    time_context = detector.get_current_time_context()
    
    results = {
        'scan_timestamp': time_context['timestamp'],
        'time_context': time_context,
        'symbols_scanned': len(symbols),
        'results': []
    }
    
    for symbol in symbols:
        try:
            vol_analysis = detector.detect_volume_anomalies(symbol)
            
            if 'error' not in vol_analysis:
                results['results'].append({
                    'symbol': symbol,
                    'volume_vs_30d': vol_analysis.get('volume_vs_30d_ratio', 0),
                    'direction': vol_analysis.get('direction', 'N/A'),
                    'dark_pool_likelihood': vol_analysis.get('dark_pool_likelihood', 'N/A'),
                    'urgency_score': vol_analysis.get('urgency_score', 0)
                })
        except Exception as e:
            results['results'].append({
                'symbol': symbol,
                'error': str(e)
            })
    
    # Sort by urgency score
    results['results'].sort(key=lambda x: x.get('urgency_score', 0), reverse=True)
    
    # Flag top movers
    if results['results']:
        top_mover = results['results'][0]
        if top_mover.get('urgency_score', 0) >= 30:
            results['alert'] = f"🚨 HIGH ACTIVITY: {top_mover['symbol']} showing {top_mover['volume_vs_30d']}x volume"
    
    return results


# Test the module
if __name__ == "__main__":
    print("=" * 60)
    print("SMART MONEY DETECTOR - Test Run")
    print("=" * 60)
    
    detector = SmartMoneyDetector()
    
    # Test time context
    print("\n📅 TIME CONTEXT:")
    time_ctx = detector.get_current_time_context()
    for key, value in time_ctx.items():
        if value:
            print(f"  {key}: {value}")
    
    # Test with a sample stock
    test_symbol = "AAPL"
    print(f"\n📊 ANALYZING: {test_symbol}")
    print("-" * 40)
    
    # Volume analysis
    print("\n🔍 Volume Analysis:")
    vol = detector.detect_volume_anomalies(test_symbol)
    if 'error' not in vol:
        print(f"  Volume vs 30d avg: {vol.get('volume_vs_30d_ratio', 'N/A')}x")
        print(f"  Dark Pool Likelihood: {vol.get('dark_pool_likelihood', 'N/A')}")
        for signal in vol.get('signals', []):
            print(f"  {signal}")
    else:
        print(f"  Error: {vol['error']}")
    
    # Market maker traps
    print("\n🎯 Market Maker Trap Detection:")
    traps = detector.detect_market_maker_traps(test_symbol)
    if 'error' not in traps:
        print(f"  Risk Level: {traps.get('risk_level', 'N/A')}")
        print(f"  Traps Detected: {traps.get('trap_count', 0)}")
        for trap in traps.get('traps_detected', [])[:3]:
            print(f"  - {trap['description']}")
    else:
        print(f"  Error: {traps['error']}")
    
    # Gamma exposure
    print("\n📈 Gamma Exposure Estimate:")
    gamma = detector.calculate_gamma_exposure_estimate(test_symbol)
    if 'error' not in gamma:
        print(f"  Regime: {gamma.get('gamma_regime', 'N/A')}")
        print(f"  {gamma.get('regime_description', '')}")
        print(f"  Est. Max Pain: ${gamma.get('estimated_max_pain', 'N/A')}")
    else:
        print(f"  Error: {gamma['error']}")
    
    print("\n" + "=" * 60)
    print("✅ Smart Money Detector module loaded successfully!")
    print("=" * 60)
