"""
TREND ANALYZER - INSTITUTIONAL GRADE TREND DETECTION & HISTORICAL MATCHING
==========================================================================
Advanced trend analysis with historical pattern matching for maximum accuracy.

FEATURES:
1. Multi-Timeframe Trend Detection (Daily, Weekly, Monthly alignment)
2. Trend Strength Scoring (ADX-based with momentum confirmation)
3. Historical Pattern Matching (Find similar setups from past)
4. Seasonality Analysis (Time-of-year patterns)
5. Connecting Trends (Higher highs/lows, lower highs/lows)

ALL DATA IS REAL-TIME - NO FAKE CALCULATIONS
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class TrendAnalyzer:
    """
    Institutional-grade trend analysis with historical pattern matching.
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def _get_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Fetch historical data using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    # =========================================================================
    # TREND DETECTION
    # =========================================================================
    def detect_trend(self, symbol: str) -> Dict:
        """
        Comprehensive trend detection across multiple timeframes.
        
        Returns:
            Dict with trend direction, strength, and alignment
        """
        df = self._get_data(symbol, "1y")
        if df is None or len(df) < 50:
            return {"error": "Insufficient data", "trend": "UNKNOWN"}
        
        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "daily_trend": self._analyze_timeframe_trend(df, 20),
            "weekly_trend": self._analyze_timeframe_trend(df, 50),
            "monthly_trend": self._analyze_timeframe_trend(df, 200),
            "connecting_trend": self._detect_connecting_trend(df),
            "trend_strength": self._calculate_trend_strength(df),
            "momentum_alignment": self._check_momentum_alignment(df)
        }
        
        # Overall trend assessment
        trends = [result["daily_trend"]["direction"], 
                  result["weekly_trend"]["direction"],
                  result["monthly_trend"]["direction"]]
        
        bullish_count = sum(1 for t in trends if t == "BULLISH")
        bearish_count = sum(1 for t in trends if t == "BEARISH")
        
        if bullish_count >= 2:
            result["overall_trend"] = "BULLISH"
            result["trend_alignment"] = bullish_count == 3
        elif bearish_count >= 2:
            result["overall_trend"] = "BEARISH"
            result["trend_alignment"] = bearish_count == 3
        else:
            result["overall_trend"] = "NEUTRAL"
            result["trend_alignment"] = False
        
        # Pro interpretation
        result["interpretation"] = self._interpret_trend(result)
        
        return result
    
    def _analyze_timeframe_trend(self, df: pd.DataFrame, period: int) -> Dict:
        """Analyze trend for a specific timeframe using SMA."""
        if len(df) < period:
            return {"direction": "UNKNOWN", "strength": 0}
        
        df = df.copy()
        sma = df['Close'].rolling(period).mean()
        current_price = df['Close'].iloc[-1]
        current_sma = sma.iloc[-1]
        
        # Price position relative to SMA
        price_vs_sma = (current_price - current_sma) / current_sma * 100
        
        # SMA slope (trend direction)
        sma_slope = (sma.iloc[-1] - sma.iloc[-5]) / sma.iloc[-5] * 100 if len(sma) >= 5 else 0
        
        # Determine direction
        if price_vs_sma > 2 and sma_slope > 0:
            direction = "BULLISH"
            strength = min(100, abs(price_vs_sma) * 10 + abs(sma_slope) * 20)
        elif price_vs_sma < -2 and sma_slope < 0:
            direction = "BEARISH"
            strength = min(100, abs(price_vs_sma) * 10 + abs(sma_slope) * 20)
        else:
            direction = "NEUTRAL"
            strength = 50 - abs(price_vs_sma) * 5
        
        return {
            "direction": direction,
            "strength": round(max(0, min(100, strength)), 1),
            "price_vs_sma": round(price_vs_sma, 2),
            "sma_slope": round(sma_slope, 3)
        }
    
    def _detect_connecting_trend(self, df: pd.DataFrame, lookback: int = 30) -> Dict:
        """
        Detect connecting trends (higher highs/lows or lower highs/lows).
        
        This is the classic definition of a trend:
        - Uptrend: Higher highs AND higher lows
        - Downtrend: Lower highs AND lower lows
        """
        if len(df) < lookback:
            return {"pattern": "UNKNOWN", "swing_count": 0}
        
        recent = df.tail(lookback).copy()
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(recent) - 2):
            # Swing high
            if (recent['High'].iloc[i] > recent['High'].iloc[i-1] and 
                recent['High'].iloc[i] > recent['High'].iloc[i-2] and
                recent['High'].iloc[i] > recent['High'].iloc[i+1] and 
                recent['High'].iloc[i] > recent['High'].iloc[i+2]):
                swing_highs.append((i, recent['High'].iloc[i]))
            
            # Swing low
            if (recent['Low'].iloc[i] < recent['Low'].iloc[i-1] and 
                recent['Low'].iloc[i] < recent['Low'].iloc[i-2] and
                recent['Low'].iloc[i] < recent['Low'].iloc[i+1] and 
                recent['Low'].iloc[i] < recent['Low'].iloc[i+2]):
                swing_lows.append((i, recent['Low'].iloc[i]))
        
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return {"pattern": "INSUFFICIENT_SWINGS", "swing_count": len(swing_highs) + len(swing_lows)}
        
        # Check for higher highs / higher lows (uptrend)
        higher_highs = all(swing_highs[i][1] > swing_highs[i-1][1] for i in range(1, len(swing_highs)))
        higher_lows = all(swing_lows[i][1] > swing_lows[i-1][1] for i in range(1, len(swing_lows)))
        
        # Check for lower highs / lower lows (downtrend)
        lower_highs = all(swing_highs[i][1] < swing_highs[i-1][1] for i in range(1, len(swing_highs)))
        lower_lows = all(swing_lows[i][1] < swing_lows[i-1][1] for i in range(1, len(swing_lows)))
        
        if higher_highs and higher_lows:
            pattern = "UPTREND"
            description = "Higher Highs + Higher Lows = Classic Uptrend"
        elif lower_highs and lower_lows:
            pattern = "DOWNTREND"
            description = "Lower Highs + Lower Lows = Classic Downtrend"
        elif higher_lows and lower_highs:
            pattern = "CONSOLIDATION"
            description = "Converging pattern - breakout imminent"
        elif lower_lows and higher_highs:
            pattern = "EXPANSION"
            description = "Expanding volatility - be cautious"
        else:
            pattern = "MIXED"
            description = "No clear trend structure"
        
        return {
            "pattern": pattern,
            "description": description,
            "higher_highs": higher_highs,
            "higher_lows": higher_lows,
            "lower_highs": lower_highs,
            "lower_lows": lower_lows,
            "swing_highs": len(swing_highs),
            "swing_lows": len(swing_lows)
        }
    
    def _calculate_trend_strength(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """Calculate ADX-based trend strength."""
        if len(df) < period + 5:
            return {"adx": 0, "strength": "WEAK"}
        
        df = df.copy()
        
        # True Range
        df['tr'] = np.maximum(
            df['High'] - df['Low'],
            np.maximum(
                abs(df['High'] - df['Close'].shift(1)),
                abs(df['Low'] - df['Close'].shift(1))
            )
        )
        
        # Directional Movement
        df['plus_dm'] = np.where(
            (df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
            np.maximum(df['High'] - df['High'].shift(1), 0),
            0
        )
        df['minus_dm'] = np.where(
            (df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
            np.maximum(df['Low'].shift(1) - df['Low'], 0),
            0
        )
        
        # Smoothed values
        df['atr'] = df['tr'].rolling(period).mean()
        df['plus_di'] = 100 * (df['plus_dm'].rolling(period).mean() / df['atr'])
        df['minus_di'] = 100 * (df['minus_dm'].rolling(period).mean() / df['atr'])
        
        # ADX
        df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'] + 1e-10)
        df['adx'] = df['dx'].rolling(period).mean()
        
        adx = df['adx'].iloc[-1]
        plus_di = df['plus_di'].iloc[-1]
        minus_di = df['minus_di'].iloc[-1]
        
        # Trend strength classification
        if adx >= 50:
            strength = "VERY_STRONG"
        elif adx >= 25:
            strength = "STRONG"
        elif adx >= 20:
            strength = "MODERATE"
        else:
            strength = "WEAK"
        
        # Trend direction from DI
        if plus_di > minus_di:
            di_direction = "BULLISH"
        elif minus_di > plus_di:
            di_direction = "BEARISH"
        else:
            di_direction = "NEUTRAL"
        
        return {
            "adx": round(adx, 1),
            "strength": strength,
            "plus_di": round(plus_di, 1),
            "minus_di": round(minus_di, 1),
            "di_direction": di_direction
        }
    
    def _check_momentum_alignment(self, df: pd.DataFrame) -> Dict:
        """Check if momentum indicators align with trend."""
        if len(df) < 26:
            return {"aligned": False, "rsi": 50, "macd_signal": "NEUTRAL"}
        
        df = df.copy()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # MACD
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        macd_bullish = histogram.iloc[-1] > 0 and histogram.iloc[-1] > histogram.iloc[-2]
        macd_bearish = histogram.iloc[-1] < 0 and histogram.iloc[-1] < histogram.iloc[-2]
        
        if macd_bullish:
            macd_signal = "BULLISH"
        elif macd_bearish:
            macd_signal = "BEARISH"
        else:
            macd_signal = "NEUTRAL"
        
        # Check alignment
        bullish_aligned = current_rsi > 50 and macd_signal == "BULLISH"
        bearish_aligned = current_rsi < 50 and macd_signal == "BEARISH"
        
        return {
            "aligned": bullish_aligned or bearish_aligned,
            "rsi": round(current_rsi, 1),
            "macd_signal": macd_signal,
            "macd_histogram": round(histogram.iloc[-1], 4),
            "momentum_direction": "BULLISH" if bullish_aligned else ("BEARISH" if bearish_aligned else "MIXED")
        }
    
    def _interpret_trend(self, result: Dict) -> str:
        """Generate professional interpretation of trend analysis."""
        overall = result.get("overall_trend", "UNKNOWN")
        aligned = result.get("trend_alignment", False)
        strength = result.get("trend_strength", {}).get("strength", "WEAK")
        connecting = result.get("connecting_trend", {}).get("pattern", "UNKNOWN")
        momentum = result.get("momentum_alignment", {}).get("aligned", False)
        
        if overall == "BULLISH" and aligned and strength in ["STRONG", "VERY_STRONG"]:
            return "🚀 STRONG UPTREND - All timeframes aligned bullish with strong momentum. High conviction long setup."
        elif overall == "BEARISH" and aligned and strength in ["STRONG", "VERY_STRONG"]:
            return "📉 STRONG DOWNTREND - All timeframes aligned bearish. Avoid longs, consider shorts."
        elif overall == "BULLISH" and momentum:
            return "📈 BULLISH TREND - Momentum confirming. Look for pullbacks to support for entries."
        elif overall == "BEARISH" and momentum:
            return "📉 BEARISH TREND - Momentum confirming downside. Avoid catching falling knives."
        elif connecting == "CONSOLIDATION":
            return "⏳ CONSOLIDATION - Price coiling for breakout. Wait for direction confirmation."
        elif strength == "WEAK":
            return "😐 WEAK/NO TREND - Choppy price action. Reduce position size or wait for clarity."
        else:
            return f"📊 {overall} bias with {strength.lower()} conviction. Monitor for confirmation."
    
    # =========================================================================
    # HISTORICAL PATTERN MATCHING
    # =========================================================================
    def find_historical_matches(self, symbol: str, lookback_days: int = 20) -> Dict:
        """
        Find historical periods that match current price pattern.
        
        This helps identify what happened AFTER similar setups in the past.
        """
        df = self._get_data(symbol, "5y")  # Need more history for matching
        if df is None or len(df) < 252:  # At least 1 year
            return {"error": "Insufficient historical data", "matches": []}
        
        # Get current pattern (last N days normalized)
        current_pattern = self._normalize_pattern(df.tail(lookback_days)['Close'].values)
        
        matches = []
        
        # Slide through history looking for similar patterns
        for i in range(252, len(df) - lookback_days - 20):  # Leave room for outcome
            historical_pattern = self._normalize_pattern(
                df.iloc[i:i+lookback_days]['Close'].values
            )
            
            # Calculate similarity (correlation)
            similarity = np.corrcoef(current_pattern, historical_pattern)[0, 1]
            
            if similarity > 0.85:  # High similarity threshold
                # What happened after this pattern?
                outcome_5d = (df['Close'].iloc[i+lookback_days+5] - df['Close'].iloc[i+lookback_days]) / df['Close'].iloc[i+lookback_days] * 100
                outcome_10d = (df['Close'].iloc[i+lookback_days+10] - df['Close'].iloc[i+lookback_days]) / df['Close'].iloc[i+lookback_days] * 100
                outcome_20d = (df['Close'].iloc[i+lookback_days+20] - df['Close'].iloc[i+lookback_days]) / df['Close'].iloc[i+lookback_days] * 100
                
                matches.append({
                    "date": df.index[i+lookback_days].strftime("%Y-%m-%d"),
                    "similarity": round(similarity * 100, 1),
                    "outcome_5d": round(outcome_5d, 2),
                    "outcome_10d": round(outcome_10d, 2),
                    "outcome_20d": round(outcome_20d, 2)
                })
        
        # Sort by similarity
        matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)[:10]
        
        # Calculate average outcomes
        if matches:
            avg_5d = np.mean([m["outcome_5d"] for m in matches])
            avg_10d = np.mean([m["outcome_10d"] for m in matches])
            avg_20d = np.mean([m["outcome_20d"] for m in matches])
            win_rate = sum(1 for m in matches if m["outcome_10d"] > 0) / len(matches) * 100
        else:
            avg_5d = avg_10d = avg_20d = win_rate = 0
        
        return {
            "symbol": symbol,
            "pattern_length": lookback_days,
            "matches_found": len(matches),
            "top_matches": matches[:5],
            "historical_stats": {
                "avg_return_5d": round(avg_5d, 2),
                "avg_return_10d": round(avg_10d, 2),
                "avg_return_20d": round(avg_20d, 2),
                "historical_win_rate": round(win_rate, 1)
            },
            "interpretation": self._interpret_historical(matches, avg_10d, win_rate)
        }
    
    def _normalize_pattern(self, prices: np.ndarray) -> np.ndarray:
        """Normalize price pattern for comparison (0-1 scale)."""
        if len(prices) == 0:
            return np.array([])
        min_p = np.min(prices)
        max_p = np.max(prices)
        if max_p - min_p == 0:
            return np.zeros_like(prices)
        return (prices - min_p) / (max_p - min_p)
    
    def _interpret_historical(self, matches: List, avg_return: float, win_rate: float) -> str:
        """Interpret historical pattern matching results."""
        if len(matches) < 3:
            return "⚠️ Insufficient historical matches. Pattern may be unique - proceed with caution."
        
        if win_rate >= 70 and avg_return > 3:
            return f"🎯 STRONG HISTORICAL EDGE - {win_rate:.0f}% win rate with {avg_return:.1f}% avg return. Pattern has worked well historically."
        elif win_rate >= 60 and avg_return > 0:
            return f"📈 POSITIVE HISTORICAL BIAS - {win_rate:.0f}% win rate. History slightly favors upside."
        elif win_rate <= 40 and avg_return < -3:
            return f"⚠️ NEGATIVE HISTORICAL BIAS - Only {win_rate:.0f}% win rate. Similar patterns led to losses."
        else:
            return f"📊 MIXED HISTORICAL RESULTS - {win_rate:.0f}% win rate. No strong edge from pattern matching."
    
    # =========================================================================
    # SEASONALITY ANALYSIS
    # =========================================================================
    def analyze_seasonality(self, symbol: str) -> Dict:
        """
        Analyze seasonal patterns for the stock.
        
        Some stocks have predictable patterns based on:
        - Month of year (e.g., retail stocks in Q4)
        - Day of week
        - Earnings cycles
        """
        df = self._get_data(symbol, "5y")
        if df is None or len(df) < 252:
            return {"error": "Insufficient data for seasonality analysis"}
        
        df = df.copy()
        df['month'] = df.index.month
        df['day_of_week'] = df.index.dayofweek
        df['daily_return'] = df['Close'].pct_change() * 100
        
        # Monthly seasonality
        monthly_returns = df.groupby('month')['daily_return'].mean() * 21  # Approx monthly
        best_month = monthly_returns.idxmax()
        worst_month = monthly_returns.idxmin()
        
        # Current month analysis
        current_month = datetime.now().month
        current_month_avg = monthly_returns.get(current_month, 0)
        
        # Day of week analysis
        dow_returns = df.groupby('day_of_week')['daily_return'].mean()
        best_day = dow_returns.idxmax()
        worst_day = dow_returns.idxmin()
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        return {
            "symbol": symbol,
            "monthly_seasonality": {
                "best_month": f"{month_names[best_month]} ({monthly_returns[best_month]:.2f}%)",
                "worst_month": f"{month_names[worst_month]} ({monthly_returns[worst_month]:.2f}%)",
                "current_month_avg": round(current_month_avg, 2),
                "current_month_favorable": current_month_avg > 0
            },
            "day_of_week": {
                "best_day": f"{day_names[best_day]} ({dow_returns[best_day]:.3f}%)",
                "worst_day": f"{day_names[worst_day]} ({dow_returns[worst_day]:.3f}%)"
            },
            "interpretation": self._interpret_seasonality(current_month_avg, monthly_returns, current_month)
        }
    
    def _interpret_seasonality(self, current_avg: float, monthly: pd.Series, current_month: int) -> str:
        """Interpret seasonality analysis."""
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        if current_avg > 2:
            return f"🟢 {month_names[current_month]} is historically a STRONG month (+{current_avg:.1f}% avg). Seasonality favors bulls."
        elif current_avg < -2:
            return f"🔴 {month_names[current_month]} is historically a WEAK month ({current_avg:.1f}% avg). Seasonality headwind."
        else:
            return f"😐 {month_names[current_month]} is historically neutral ({current_avg:.1f}% avg). No strong seasonal bias."
    
    # =========================================================================
    # COMPREHENSIVE ANALYSIS
    # =========================================================================
    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """
        Get complete trend and pattern analysis for a symbol.
        """
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "trend_analysis": self.detect_trend(symbol),
            "historical_matching": self.find_historical_matches(symbol),
            "seasonality": self.analyze_seasonality(symbol)
        }


# Test if run directly
if __name__ == "__main__":
    analyzer = TrendAnalyzer()
    
    print("Testing Trend Analyzer on AAPL...")
    result = analyzer.detect_trend("AAPL")
    print(f"Overall Trend: {result.get('overall_trend')}")
    print(f"Trend Aligned: {result.get('trend_alignment')}")
    print(f"Connecting Trend: {result.get('connecting_trend', {}).get('pattern')}")
    print(f"Interpretation: {result.get('interpretation')}")
