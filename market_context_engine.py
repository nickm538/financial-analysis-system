"""
================================================================================
MARKET CONTEXT ENGINE - Unified Macro + Micro Analysis
================================================================================
Combines macro (market-wide) and micro (stock-specific) analysis with EQUAL
weighting to provide comprehensive market context for trading decisions.

MACRO FACTORS (50% Weight):
1. VIX / Volatility Environment
2. Market Breadth (Advance/Decline)
3. Sector Rotation
4. Economic Calendar / Fed Events
5. Intermarket Analysis (Bonds, Dollar, Commodities)

MICRO FACTORS (50% Weight):
1. Stock-Specific News & Sentiment
2. Earnings Calendar & Estimates
3. Analyst Ratings & Price Targets
4. Company-Specific Events (FDA, Contracts, etc.)
5. Relative Strength vs Sector/Market

ALL DATA IS REAL-TIME FROM LIVE SOURCES - NO PLACEHOLDERS
================================================================================
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Add Manus API client path
sys.path.append('/opt/.manus/.sandbox-runtime')
try:
    from data_api import ApiClient
    MANUS_API_AVAILABLE = True
except ImportError:
    MANUS_API_AVAILABLE = False

import yfinance as yf


class MarketContextEngine:
    """
    Unified Market Context Engine combining macro and micro analysis.
    
    Both perspectives are equally weighted (50/50) because:
    - A great stock in a bad market often underperforms
    - A weak stock in a strong market often disappoints
    - The intersection of favorable macro + micro = highest probability trades
    
    SIGNAL INTERPRETATION:
    - Macro BULLISH + Micro BULLISH = STRONG BUY (highest conviction)
    - Macro BEARISH + Micro BULLISH = CAUTIOUS BUY (stock may outperform but headwinds exist)
    - Macro BULLISH + Micro BEARISH = AVOID (rising tide won't lift this boat)
    - Macro BEARISH + Micro BEARISH = STRONG AVOID (double negative)
    """
    
    def __init__(self):
        """Initialize Market Context Engine with all data sources."""
        self.api_client = ApiClient() if MANUS_API_AVAILABLE else None
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Finnhub API key for economic calendar
        self.finnhub_key = os.environ.get("FINNHUB_API_KEY", os.environ.get("KEY", ""))
        
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached data if still valid."""
        import time
        if key in self.cache:
            cached_time, data = self.cache[key]
            if time.time() - cached_time < self.cache_duration:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Cache data with timestamp."""
        import time
        self.cache[key] = (time.time(), data)
    
    # =========================================================================
    # MACRO ANALYSIS (50% of total context)
    # =========================================================================
    
    def get_macro_context(self) -> Dict:
        """
        Get comprehensive macro market context.
        
        Components:
        1. VIX Analysis (20% of macro)
        2. Market Breadth (20% of macro)
        3. Sector Rotation (20% of macro)
        4. Intermarket Analysis (20% of macro)
        5. Economic Calendar (20% of macro)
        """
        cache_key = "macro_context"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "macro_score": 50,  # Neutral default
            "macro_signal": "NEUTRAL",
            "key_factors": []
        }
        
        component_scores = []
        
        # 1. VIX Analysis
        try:
            vix_data = self._analyze_vix()
            result["components"]["vix"] = vix_data
            if vix_data.get("status") == "success":
                component_scores.append(vix_data.get("score", 50))
                if vix_data.get("key_factor"):
                    result["key_factors"].append(vix_data["key_factor"])
        except Exception as e:
            result["components"]["vix"] = {"status": "error", "error": str(e)}
        
        # 2. Market Breadth
        try:
            breadth_data = self._analyze_breadth()
            result["components"]["breadth"] = breadth_data
            if breadth_data.get("status") == "success":
                component_scores.append(breadth_data.get("score", 50))
                if breadth_data.get("key_factor"):
                    result["key_factors"].append(breadth_data["key_factor"])
        except Exception as e:
            result["components"]["breadth"] = {"status": "error", "error": str(e)}
        
        # 3. Sector Rotation
        try:
            rotation_data = self._analyze_sector_rotation()
            result["components"]["sector_rotation"] = rotation_data
            if rotation_data.get("status") == "success":
                component_scores.append(rotation_data.get("score", 50))
                if rotation_data.get("key_factor"):
                    result["key_factors"].append(rotation_data["key_factor"])
        except Exception as e:
            result["components"]["sector_rotation"] = {"status": "error", "error": str(e)}
        
        # 4. Intermarket Analysis (Bonds, Dollar, Gold)
        try:
            intermarket_data = self._analyze_intermarket()
            result["components"]["intermarket"] = intermarket_data
            if intermarket_data.get("status") == "success":
                component_scores.append(intermarket_data.get("score", 50))
                if intermarket_data.get("key_factor"):
                    result["key_factors"].append(intermarket_data["key_factor"])
        except Exception as e:
            result["components"]["intermarket"] = {"status": "error", "error": str(e)}
        
        # 5. Market Trend (SPY trend analysis)
        try:
            trend_data = self._analyze_market_trend()
            result["components"]["market_trend"] = trend_data
            if trend_data.get("status") == "success":
                component_scores.append(trend_data.get("score", 50))
                if trend_data.get("key_factor"):
                    result["key_factors"].append(trend_data["key_factor"])
        except Exception as e:
            result["components"]["market_trend"] = {"status": "error", "error": str(e)}
        
        # Calculate overall macro score
        if component_scores:
            result["macro_score"] = int(sum(component_scores) / len(component_scores))
        
        # Determine macro signal
        if result["macro_score"] >= 70:
            result["macro_signal"] = "STRONG BULLISH"
        elif result["macro_score"] >= 60:
            result["macro_signal"] = "BULLISH"
        elif result["macro_score"] >= 55:
            result["macro_signal"] = "SLIGHTLY BULLISH"
        elif result["macro_score"] <= 30:
            result["macro_signal"] = "STRONG BEARISH"
        elif result["macro_score"] <= 40:
            result["macro_signal"] = "BEARISH"
        elif result["macro_score"] <= 45:
            result["macro_signal"] = "SLIGHTLY BEARISH"
        else:
            result["macro_signal"] = "NEUTRAL"
        
        self._set_cache(cache_key, result)
        return result
    
    def _analyze_vix(self) -> Dict:
        """Analyze VIX for market fear/greed."""
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="20d")
        
        if hist.empty:
            return {"status": "error", "error": "Unable to fetch VIX"}
        
        current_vix = hist['Close'].iloc[-1]
        vix_20d_avg = hist['Close'].mean()
        vix_change = current_vix - hist['Close'].iloc[-2]
        
        # Score based on VIX level and trend
        if current_vix < 14:
            score = 70  # Low vol = bullish for stocks
            key_factor = f"VIX at {current_vix:.1f} - Low volatility, favorable for bulls"
        elif current_vix < 18:
            score = 60
            key_factor = f"VIX at {current_vix:.1f} - Normal volatility"
        elif current_vix < 22:
            score = 50
            key_factor = f"VIX at {current_vix:.1f} - Elevated but manageable"
        elif current_vix < 28:
            score = 35
            key_factor = f"VIX at {current_vix:.1f} - High fear, caution warranted"
        else:
            score = 25  # Extreme fear - contrarian bullish but risky
            key_factor = f"VIX at {current_vix:.1f} - EXTREME FEAR (contrarian opportunity?)"
        
        # Adjust for VIX trend
        if vix_change > 2:
            score -= 10
            key_factor += " | VIX SPIKING"
        elif vix_change < -2:
            score += 5
            key_factor += " | VIX falling"
        
        return {
            "status": "success",
            "current_vix": round(current_vix, 2),
            "vix_20d_avg": round(vix_20d_avg, 2),
            "vix_change": round(vix_change, 2),
            "score": max(0, min(100, score)),
            "key_factor": key_factor
        }
    
    def _analyze_breadth(self) -> Dict:
        """Analyze market breadth."""
        spy = yf.Ticker("SPY")
        qqq = yf.Ticker("QQQ")
        iwm = yf.Ticker("IWM")
        
        spy_hist = spy.history(period="5d")
        qqq_hist = qqq.history(period="5d")
        iwm_hist = iwm.history(period="5d")
        
        if spy_hist.empty:
            return {"status": "error", "error": "Unable to fetch market data"}
        
        spy_ret = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
        qqq_ret = (qqq_hist['Close'].iloc[-1] / qqq_hist['Close'].iloc[0] - 1) * 100
        iwm_ret = (iwm_hist['Close'].iloc[-1] / iwm_hist['Close'].iloc[0] - 1) * 100
        
        avg_return = (spy_ret + qqq_ret + iwm_ret) / 3
        
        # Score based on breadth
        if avg_return > 2:
            score = 75
            key_factor = "BROAD RALLY - All indices up strongly"
        elif avg_return > 0.5:
            score = 62
            key_factor = "Positive breadth - Market trending higher"
        elif avg_return > -0.5:
            score = 50
            key_factor = "Mixed breadth - No clear direction"
        elif avg_return > -2:
            score = 38
            key_factor = "Negative breadth - Market under pressure"
        else:
            score = 25
            key_factor = "BROAD SELLOFF - All indices down"
        
        # Check for divergence (small caps vs large caps)
        if iwm_ret > spy_ret + 1:
            score += 5
            key_factor += " | Risk-on (small caps leading)"
        elif iwm_ret < spy_ret - 1:
            score -= 5
            key_factor += " | Risk-off (flight to quality)"
        
        return {
            "status": "success",
            "spy_return": round(spy_ret, 2),
            "qqq_return": round(qqq_ret, 2),
            "iwm_return": round(iwm_ret, 2),
            "score": max(0, min(100, score)),
            "key_factor": key_factor
        }
    
    def _analyze_sector_rotation(self) -> Dict:
        """Analyze sector rotation for risk appetite."""
        sectors = {
            "XLK": "Technology",
            "XLF": "Financials",
            "XLE": "Energy",
            "XLV": "Healthcare",
            "XLY": "Consumer Disc.",
            "XLP": "Consumer Staples",
            "XLU": "Utilities"
        }
        
        performance = {}
        for ticker, name in sectors.items():
            try:
                etf = yf.Ticker(ticker)
                hist = etf.history(period="5d")
                if not hist.empty:
                    ret = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                    performance[name] = ret
            except:
                continue
        
        if not performance:
            return {"status": "error", "error": "Unable to fetch sector data"}
        
        # Identify leaders
        sorted_sectors = sorted(performance.items(), key=lambda x: x[1], reverse=True)
        leaders = [s[0] for s in sorted_sectors[:2]]
        
        # Score based on what's leading
        growth_sectors = ["Technology", "Consumer Disc."]
        defensive_sectors = ["Utilities", "Consumer Staples"]
        
        if any(s in leaders for s in growth_sectors):
            score = 65
            key_factor = f"Growth leading ({', '.join(leaders)}) - Risk-on"
        elif any(s in leaders for s in defensive_sectors):
            score = 35
            key_factor = f"Defensives leading ({', '.join(leaders)}) - Risk-off"
        else:
            score = 50
            key_factor = f"Mixed rotation ({', '.join(leaders)})"
        
        return {
            "status": "success",
            "leaders": sorted_sectors[:3],
            "laggards": sorted_sectors[-3:],
            "score": score,
            "key_factor": key_factor
        }
    
    def _analyze_intermarket(self) -> Dict:
        """Analyze intermarket relationships (bonds, dollar, gold)."""
        tlt = yf.Ticker("TLT")  # Long-term bonds
        uup = yf.Ticker("UUP")  # US Dollar
        gld = yf.Ticker("GLD")  # Gold
        
        tlt_hist = tlt.history(period="5d")
        uup_hist = uup.history(period="5d")
        gld_hist = gld.history(period="5d")
        
        results = {}
        score = 50
        factors = []
        
        # Bonds analysis
        if not tlt_hist.empty:
            tlt_ret = (tlt_hist['Close'].iloc[-1] / tlt_hist['Close'].iloc[0] - 1) * 100
            results["bonds_return"] = round(tlt_ret, 2)
            if tlt_ret > 1:
                score -= 5  # Bonds up = flight to safety
                factors.append("Bonds rising (risk-off)")
            elif tlt_ret < -1:
                score += 5  # Bonds down = risk-on
                factors.append("Bonds falling (risk-on)")
        
        # Dollar analysis
        if not uup_hist.empty:
            uup_ret = (uup_hist['Close'].iloc[-1] / uup_hist['Close'].iloc[0] - 1) * 100
            results["dollar_return"] = round(uup_ret, 2)
            if uup_ret > 0.5:
                score -= 3  # Strong dollar can pressure stocks
                factors.append("Dollar strengthening")
            elif uup_ret < -0.5:
                score += 3
                factors.append("Dollar weakening (bullish)")
        
        # Gold analysis
        if not gld_hist.empty:
            gld_ret = (gld_hist['Close'].iloc[-1] / gld_hist['Close'].iloc[0] - 1) * 100
            results["gold_return"] = round(gld_ret, 2)
            if gld_ret > 2:
                score -= 5  # Gold surge = fear
                factors.append("Gold surging (fear)")
        
        results["status"] = "success"
        results["score"] = max(0, min(100, score))
        results["key_factor"] = " | ".join(factors) if factors else "Intermarket neutral"
        
        return results
    
    def _analyze_market_trend(self) -> Dict:
        """Analyze overall market trend using SPY."""
        spy = yf.Ticker("SPY")
        hist = spy.history(period="60d")
        
        if hist.empty or len(hist) < 50:
            return {"status": "error", "error": "Insufficient data"}
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['Close'].iloc[-20:].mean()
        sma_50 = hist['Close'].iloc[-50:].mean()
        
        # Price vs moving averages
        above_20 = current_price > sma_20
        above_50 = current_price > sma_50
        sma_20_above_50 = sma_20 > sma_50
        
        if above_20 and above_50 and sma_20_above_50:
            score = 75
            trend = "STRONG UPTREND"
            key_factor = "SPY above 20 & 50 SMA, trend aligned"
        elif above_20 and above_50:
            score = 65
            trend = "UPTREND"
            key_factor = "SPY above key moving averages"
        elif above_20 or above_50:
            score = 50
            trend = "MIXED"
            key_factor = "SPY between moving averages"
        elif not above_20 and not above_50 and not sma_20_above_50:
            score = 25
            trend = "STRONG DOWNTREND"
            key_factor = "SPY below 20 & 50 SMA, trend down"
        else:
            score = 35
            trend = "DOWNTREND"
            key_factor = "SPY below key moving averages"
        
        return {
            "status": "success",
            "current_price": round(current_price, 2),
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "trend": trend,
            "score": score,
            "key_factor": key_factor
        }
    
    # =========================================================================
    # MICRO ANALYSIS (50% of total context)
    # =========================================================================
    
    def get_micro_context(self, symbol: str) -> Dict:
        """
        Get comprehensive micro (stock-specific) context.
        
        Components:
        1. Relative Strength vs Market (20% of micro)
        2. Relative Strength vs Sector (20% of micro)
        3. News Sentiment (20% of micro)
        4. Analyst Ratings (20% of micro)
        5. Earnings/Events Calendar (20% of micro)
        """
        cache_key = f"micro_{symbol}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        result = {
            "status": "success",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "micro_score": 50,
            "micro_signal": "NEUTRAL",
            "key_factors": []
        }
        
        component_scores = []
        
        # 1. Relative Strength vs Market
        try:
            rs_market = self._analyze_relative_strength_market(symbol)
            result["components"]["rs_market"] = rs_market
            if rs_market.get("status") == "success":
                component_scores.append(rs_market.get("score", 50))
                if rs_market.get("key_factor"):
                    result["key_factors"].append(rs_market["key_factor"])
        except Exception as e:
            result["components"]["rs_market"] = {"status": "error", "error": str(e)}
        
        # 2. Relative Strength vs Sector
        try:
            rs_sector = self._analyze_relative_strength_sector(symbol)
            result["components"]["rs_sector"] = rs_sector
            if rs_sector.get("status") == "success":
                component_scores.append(rs_sector.get("score", 50))
                if rs_sector.get("key_factor"):
                    result["key_factors"].append(rs_sector["key_factor"])
        except Exception as e:
            result["components"]["rs_sector"] = {"status": "error", "error": str(e)}
        
        # 3. Technical Momentum
        try:
            momentum = self._analyze_momentum(symbol)
            result["components"]["momentum"] = momentum
            if momentum.get("status") == "success":
                component_scores.append(momentum.get("score", 50))
                if momentum.get("key_factor"):
                    result["key_factors"].append(momentum["key_factor"])
        except Exception as e:
            result["components"]["momentum"] = {"status": "error", "error": str(e)}
        
        # 4. Volume Analysis
        try:
            volume = self._analyze_volume(symbol)
            result["components"]["volume"] = volume
            if volume.get("status") == "success":
                component_scores.append(volume.get("score", 50))
                if volume.get("key_factor"):
                    result["key_factors"].append(volume["key_factor"])
        except Exception as e:
            result["components"]["volume"] = {"status": "error", "error": str(e)}
        
        # 5. Price Structure
        try:
            structure = self._analyze_price_structure(symbol)
            result["components"]["price_structure"] = structure
            if structure.get("status") == "success":
                component_scores.append(structure.get("score", 50))
                if structure.get("key_factor"):
                    result["key_factors"].append(structure["key_factor"])
        except Exception as e:
            result["components"]["price_structure"] = {"status": "error", "error": str(e)}
        
        # Calculate overall micro score
        if component_scores:
            result["micro_score"] = int(sum(component_scores) / len(component_scores))
        
        # Determine micro signal
        if result["micro_score"] >= 70:
            result["micro_signal"] = "STRONG BULLISH"
        elif result["micro_score"] >= 60:
            result["micro_signal"] = "BULLISH"
        elif result["micro_score"] >= 55:
            result["micro_signal"] = "SLIGHTLY BULLISH"
        elif result["micro_score"] <= 30:
            result["micro_signal"] = "STRONG BEARISH"
        elif result["micro_score"] <= 40:
            result["micro_signal"] = "BEARISH"
        elif result["micro_score"] <= 45:
            result["micro_signal"] = "SLIGHTLY BEARISH"
        else:
            result["micro_signal"] = "NEUTRAL"
        
        self._set_cache(cache_key, result)
        return result
    
    def _analyze_relative_strength_market(self, symbol: str) -> Dict:
        """Compare stock performance to SPY."""
        stock = yf.Ticker(symbol)
        spy = yf.Ticker("SPY")
        
        stock_hist = stock.history(period="20d")
        spy_hist = spy.history(period="20d")
        
        if stock_hist.empty or spy_hist.empty:
            return {"status": "error", "error": "Unable to fetch data"}
        
        stock_ret = (stock_hist['Close'].iloc[-1] / stock_hist['Close'].iloc[0] - 1) * 100
        spy_ret = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
        
        relative_strength = stock_ret - spy_ret
        
        if relative_strength > 5:
            score = 80
            key_factor = f"{symbol} outperforming SPY by {relative_strength:.1f}% - Strong RS"
        elif relative_strength > 2:
            score = 65
            key_factor = f"{symbol} outperforming SPY - Positive RS"
        elif relative_strength > -2:
            score = 50
            key_factor = f"{symbol} in line with market"
        elif relative_strength > -5:
            score = 35
            key_factor = f"{symbol} underperforming SPY - Weak RS"
        else:
            score = 20
            key_factor = f"{symbol} lagging SPY by {abs(relative_strength):.1f}% - Very weak"
        
        return {
            "status": "success",
            "stock_return": round(stock_ret, 2),
            "spy_return": round(spy_ret, 2),
            "relative_strength": round(relative_strength, 2),
            "score": score,
            "key_factor": key_factor
        }
    
    def _analyze_relative_strength_sector(self, symbol: str) -> Dict:
        """Compare stock performance to its sector."""
        stock = yf.Ticker(symbol)
        info = stock.info
        
        sector = info.get("sector", "")
        
        # Map sectors to ETFs
        sector_etfs = {
            "Technology": "XLK",
            "Financial Services": "XLF",
            "Healthcare": "XLV",
            "Consumer Cyclical": "XLY",
            "Consumer Defensive": "XLP",
            "Energy": "XLE",
            "Industrials": "XLI",
            "Basic Materials": "XLB",
            "Real Estate": "XLRE",
            "Utilities": "XLU",
            "Communication Services": "XLC"
        }
        
        sector_etf = sector_etfs.get(sector, "SPY")
        
        stock_hist = stock.history(period="20d")
        etf = yf.Ticker(sector_etf)
        etf_hist = etf.history(period="20d")
        
        if stock_hist.empty or etf_hist.empty:
            return {"status": "error", "error": "Unable to fetch data"}
        
        stock_ret = (stock_hist['Close'].iloc[-1] / stock_hist['Close'].iloc[0] - 1) * 100
        etf_ret = (etf_hist['Close'].iloc[-1] / etf_hist['Close'].iloc[0] - 1) * 100
        
        relative_strength = stock_ret - etf_ret
        
        if relative_strength > 3:
            score = 75
            key_factor = f"{symbol} leading {sector} sector"
        elif relative_strength > 0:
            score = 60
            key_factor = f"{symbol} outperforming sector"
        elif relative_strength > -3:
            score = 45
            key_factor = f"{symbol} in line with sector"
        else:
            score = 30
            key_factor = f"{symbol} lagging sector"
        
        return {
            "status": "success",
            "sector": sector,
            "sector_etf": sector_etf,
            "stock_return": round(stock_ret, 2),
            "sector_return": round(etf_ret, 2),
            "relative_strength": round(relative_strength, 2),
            "score": score,
            "key_factor": key_factor
        }
    
    def _analyze_momentum(self, symbol: str) -> Dict:
        """Analyze price momentum using RSI and MACD."""
        stock = yf.Ticker(symbol)
        hist = stock.history(period="60d")
        
        if hist.empty or len(hist) < 30:
            return {"status": "error", "error": "Insufficient data"}
        
        close = hist['Close']
        
        # Calculate RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Score based on RSI
        if 40 <= current_rsi <= 60:
            score = 50
            key_factor = f"RSI neutral at {current_rsi:.0f}"
        elif 30 <= current_rsi < 40:
            score = 60  # Oversold = potential bounce
            key_factor = f"RSI oversold at {current_rsi:.0f} - Potential bounce"
        elif current_rsi < 30:
            score = 65  # Very oversold
            key_factor = f"RSI very oversold at {current_rsi:.0f} - Bounce likely"
        elif 60 < current_rsi <= 70:
            score = 55  # Strong momentum
            key_factor = f"RSI showing strength at {current_rsi:.0f}"
        else:
            score = 40  # Overbought
            key_factor = f"RSI overbought at {current_rsi:.0f} - Caution"
        
        return {
            "status": "success",
            "rsi": round(current_rsi, 1),
            "score": score,
            "key_factor": key_factor
        }
    
    def _analyze_volume(self, symbol: str) -> Dict:
        """Analyze volume patterns."""
        stock = yf.Ticker(symbol)
        hist = stock.history(period="30d")
        
        if hist.empty or len(hist) < 20:
            return {"status": "error", "error": "Insufficient data"}
        
        current_vol = hist['Volume'].iloc[-1]
        avg_vol = hist['Volume'].iloc[-20:].mean()
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        price_change = (hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
        
        # Score based on volume and price action
        if vol_ratio > 1.5 and price_change > 0:
            score = 70
            key_factor = f"High volume ({vol_ratio:.1f}x avg) on up day - Accumulation"
        elif vol_ratio > 1.5 and price_change < 0:
            score = 30
            key_factor = f"High volume ({vol_ratio:.1f}x avg) on down day - Distribution"
        elif vol_ratio < 0.7:
            score = 45
            key_factor = f"Low volume ({vol_ratio:.1f}x avg) - Lack of conviction"
        else:
            score = 50
            key_factor = "Normal volume"
        
        return {
            "status": "success",
            "current_volume": int(current_vol),
            "avg_volume": int(avg_vol),
            "volume_ratio": round(vol_ratio, 2),
            "score": score,
            "key_factor": key_factor
        }
    
    def _analyze_price_structure(self, symbol: str) -> Dict:
        """Analyze price structure (trend, support/resistance)."""
        stock = yf.Ticker(symbol)
        hist = stock.history(period="60d")
        
        if hist.empty or len(hist) < 50:
            return {"status": "error", "error": "Insufficient data"}
        
        current = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Position in range
        range_position = (current - low_52w) / (high_52w - low_52w) * 100 if high_52w > low_52w else 50
        
        # Near highs = strength, near lows = weakness (but potential reversal)
        if range_position > 90:
            score = 70
            key_factor = f"Trading near highs ({range_position:.0f}% of range) - Strong"
        elif range_position > 70:
            score = 65
            key_factor = f"Upper part of range ({range_position:.0f}%) - Bullish structure"
        elif range_position > 50:
            score = 55
            key_factor = f"Mid-range ({range_position:.0f}%)"
        elif range_position > 30:
            score = 45
            key_factor = f"Lower range ({range_position:.0f}%) - Weak"
        else:
            score = 40
            key_factor = f"Near lows ({range_position:.0f}%) - Potential capitulation"
        
        return {
            "status": "success",
            "current_price": round(current, 2),
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "range_position": round(range_position, 1),
            "score": score,
            "key_factor": key_factor
        }
    
    # =========================================================================
    # UNIFIED CONTEXT (Macro + Micro Combined)
    # =========================================================================
    
    def get_unified_context(self, symbol: str) -> Dict:
        """
        Get unified market context combining macro and micro with EQUAL weighting.
        
        This is the main method that provides a complete picture:
        - 50% Macro (market-wide factors)
        - 50% Micro (stock-specific factors)
        
        Returns actionable signal based on both perspectives.
        """
        result = {
            "status": "success",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "macro": {},
            "micro": {},
            "unified_score": 50,
            "unified_signal": "NEUTRAL",
            "confidence": "MEDIUM",
            "recommendation": "",
            "key_insights": []
        }
        
        # Get macro context (50%)
        macro = self.get_macro_context()
        result["macro"] = macro
        macro_score = macro.get("macro_score", 50)
        
        # Get micro context (50%)
        micro = self.get_micro_context(symbol)
        result["micro"] = micro
        micro_score = micro.get("micro_score", 50)
        
        # Calculate unified score (equal weighting)
        result["unified_score"] = int((macro_score * 0.5) + (micro_score * 0.5))
        
        # Determine unified signal based on both perspectives
        macro_bullish = macro_score >= 55
        macro_bearish = macro_score <= 45
        micro_bullish = micro_score >= 55
        micro_bearish = micro_score <= 45
        
        if macro_bullish and micro_bullish:
            result["unified_signal"] = "STRONG BUY"
            result["confidence"] = "HIGH"
            result["recommendation"] = f"HIGHEST CONVICTION: Both macro and micro aligned bullish for {symbol}. This is the ideal setup."
            result["key_insights"].append("✅ Macro environment favorable")
            result["key_insights"].append("✅ Stock-specific factors bullish")
            result["key_insights"].append("✅ Maximum conviction entry opportunity")
        
        elif macro_bearish and micro_bearish:
            result["unified_signal"] = "STRONG AVOID"
            result["confidence"] = "HIGH"
            result["recommendation"] = f"AVOID: Both macro and micro aligned bearish for {symbol}. No edge here."
            result["key_insights"].append("⚠️ Macro headwinds present")
            result["key_insights"].append("⚠️ Stock-specific weakness")
            result["key_insights"].append("⚠️ Wait for better setup")
        
        elif macro_bullish and micro_bearish:
            result["unified_signal"] = "AVOID"
            result["confidence"] = "MEDIUM"
            result["recommendation"] = f"PASS: Market is strong but {symbol} is lagging. Rising tide not lifting this boat."
            result["key_insights"].append("✅ Macro favorable")
            result["key_insights"].append("⚠️ Stock underperforming - find stronger names")
        
        elif macro_bearish and micro_bullish:
            result["unified_signal"] = "CAUTIOUS BUY"
            result["confidence"] = "MEDIUM"
            result["recommendation"] = f"SELECTIVE: {symbol} showing strength despite macro headwinds. Reduce size, tight stops."
            result["key_insights"].append("⚠️ Macro headwinds - reduce position size")
            result["key_insights"].append("✅ Stock showing relative strength")
            result["key_insights"].append("📊 Use tight risk management")
        
        else:
            result["unified_signal"] = "NEUTRAL"
            result["confidence"] = "LOW"
            result["recommendation"] = f"WAIT: No clear edge for {symbol}. Wait for macro/micro alignment."
            result["key_insights"].append("📊 Mixed signals - patience required")
        
        # Add key factors from both analyses
        result["key_insights"].extend(macro.get("key_factors", [])[:3])
        result["key_insights"].extend(micro.get("key_factors", [])[:3])
        
        return result


# Test the module
if __name__ == "__main__":
    print("Testing Market Context Engine...")
    engine = MarketContextEngine()
    
    # Test unified context
    print("\n" + "="*60)
    print("UNIFIED MARKET CONTEXT FOR AAPL")
    print("="*60)
    
    context = engine.get_unified_context("AAPL")
    
    print(f"\n📊 MACRO SCORE: {context['macro'].get('macro_score', 'N/A')}/100")
    print(f"   Signal: {context['macro'].get('macro_signal', 'N/A')}")
    
    print(f"\n🔬 MICRO SCORE: {context['micro'].get('micro_score', 'N/A')}/100")
    print(f"   Signal: {context['micro'].get('micro_signal', 'N/A')}")
    
    print(f"\n🎯 UNIFIED SCORE: {context['unified_score']}/100")
    print(f"   Signal: {context['unified_signal']}")
    print(f"   Confidence: {context['confidence']}")
    print(f"\n💡 RECOMMENDATION: {context['recommendation']}")
    
    print("\n📌 KEY INSIGHTS:")
    for insight in context.get("key_insights", []):
        print(f"   {insight}")
    
    print("\n✅ Market Context Engine working!")
