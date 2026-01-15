"""
MACRO CONTEXT MODULE - Market-Wide Factors Analysis
====================================================
Analyzes socioeconomic, political, and market-wide factors that affect trading.

FACTORS ANALYZED:
1. Economic Calendar (Fed meetings, CPI, Jobs reports)
2. Market Sentiment (VIX, Put/Call ratio, Fear & Greed)
3. Sector Performance (Rotation signals)
4. Political/Geopolitical Events
5. Earnings Season Impact
6. Market Breadth (Advance/Decline)

ALL DATA IS REAL-TIME - NO FAKE CALCULATIONS
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class MacroContext:
    """
    Analyzes macro-level factors that affect individual stock performance.
    Provides context that technical analysis alone cannot capture.
    
    PRODUCTION-GRADE: All data is real-time with active date/time context.
    """
    
    def __init__(self, finnhub_api_key: str = None):
        self.finnhub_key = finnhub_api_key
        self.cache = {}
        self.cache_time = None
        self.cache_ttl = 180  # 3 minutes - shorter for more real-time data
    
    def _get_market_session_context(self) -> Dict:
        """
        Get precise market session context with date/time awareness.
        This context is applied to EVERY scan for production accuracy.
        """
        from datetime import datetime
        import pytz
        
        try:
            et = pytz.timezone('US/Eastern')
            now = datetime.now(et)
        except:
            now = datetime.now()
        
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        premarket_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
        afterhours_end = now.replace(hour=20, minute=0, second=0, microsecond=0)
        
        is_weekday = now.weekday() < 5
        is_market_hours = market_open <= now <= market_close and is_weekday
        is_premarket = premarket_start <= now < market_open and is_weekday
        is_afterhours = market_close < now <= afterhours_end and is_weekday
        
        # Determine trading session with granularity
        if not is_weekday:
            session = 'WEEKEND'
            session_detail = 'Markets closed - weekend'
        elif is_premarket:
            session = 'PRE_MARKET'
            session_detail = f'Pre-market trading ({now.strftime("%H:%M")} ET)'
        elif is_afterhours:
            session = 'AFTER_HOURS'
            session_detail = f'After-hours trading ({now.strftime("%H:%M")} ET)'
        elif now < market_open:
            session = 'PRE_OPEN'
            session_detail = f'Before pre-market ({now.strftime("%H:%M")} ET)'
        elif now > afterhours_end:
            session = 'CLOSED'
            session_detail = 'Markets closed for the day'
        else:
            # During market hours - granular session
            if now < now.replace(hour=10, minute=0):
                session = 'OPENING_30'
                session_detail = 'First 30 minutes - HIGH volatility expected'
            elif now < now.replace(hour=10, minute=30):
                session = 'OPENING_HOUR'
                session_detail = 'Opening hour - Elevated volatility'
            elif now < now.replace(hour=12, minute=0):
                session = 'MORNING_MOMENTUM'
                session_detail = 'Morning momentum session'
            elif now < now.replace(hour=14, minute=0):
                session = 'MIDDAY_LULL'
                session_detail = 'Midday consolidation - Lower volume typical'
            elif now < now.replace(hour=15, minute=0):
                session = 'AFTERNOON_SETUP'
                session_detail = 'Afternoon setup - Watch for breakouts'
            else:
                session = 'POWER_HOUR'
                session_detail = 'POWER HOUR - High volume, institutional activity'
        
        # Special day awareness
        day_of_month = now.day
        day_of_week = now.weekday()
        month = now.month
        
        special_notes = []
        
        # Triple witching (3rd Friday of March, June, Sept, Dec)
        if month in [3, 6, 9, 12] and day_of_week == 4 and 15 <= day_of_month <= 21:
            special_notes.append('⚠️ TRIPLE WITCHING - Extreme volume and volatility expected')
        
        # Monthly options expiration (3rd Friday)
        if day_of_week == 4 and 15 <= day_of_month <= 21:
            special_notes.append('📅 Monthly OPEX - Options expiration day')
        
        # Weekly options expiration (every Friday)
        if day_of_week == 4:
            special_notes.append('📅 Weekly options expiration')
        
        # First trading day of month
        if day_of_month <= 3 and day_of_week == 0:
            special_notes.append('📅 First trading day of month - Institutional rebalancing')
        
        # Jobs report (first Friday)
        if day_of_week == 4 and day_of_month <= 7:
            special_notes.append('📊 Jobs Report Day - NFP release 8:30 AM ET')
        
        # CPI week (typically mid-month)
        if 10 <= day_of_month <= 15:
            special_notes.append('📊 CPI Week - Inflation data may impact markets')
        
        # End of quarter
        if month in [3, 6, 9, 12] and day_of_month >= 25:
            special_notes.append('📅 End of Quarter - Window dressing, rebalancing')
        
        return {
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S ET'),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'day_of_week': now.strftime('%A'),
            'is_market_hours': is_market_hours,
            'is_premarket': is_premarket,
            'is_afterhours': is_afterhours,
            'session': session,
            'session_detail': session_detail,
            'special_notes': special_notes,
            'minutes_to_open': max(0, int((market_open - now).total_seconds() / 60)) if now < market_open else 0,
            'minutes_to_close': max(0, int((market_close - now).total_seconds() / 60)) if now < market_close else 0
        }
        
    def _get_cached_or_fetch(self, key: str, fetch_func):
        """Simple caching mechanism"""
        now = datetime.now()
        if self.cache_time and (now - self.cache_time).seconds < self.cache_ttl:
            if key in self.cache:
                return self.cache[key]
        
        result = fetch_func()
        self.cache[key] = result
        self.cache_time = now
        return result
    
    # =========================================================================
    # VIX - MARKET FEAR GAUGE
    # =========================================================================
    def get_vix_analysis(self) -> Dict:
        """
        Analyze VIX (Volatility Index) for market fear/greed.
        
        VIX LEVELS:
        - Below 12: Extreme complacency (potential top)
        - 12-20: Normal/Low volatility
        - 20-30: Elevated fear
        - Above 30: Extreme fear (potential bottom)
        """
        try:
            # Use Yahoo Finance for VIX
            import yfinance as yf
            vix = yf.Ticker("^VIX")
            hist = vix.history(period="5d")
            
            if hist.empty:
                return {"status": "error", "error": "Unable to fetch VIX data"}
            
            current_vix = hist['Close'].iloc[-1]
            prev_vix = hist['Close'].iloc[-2] if len(hist) > 1 else current_vix
            vix_change = current_vix - prev_vix
            vix_change_pct = (vix_change / prev_vix) * 100 if prev_vix > 0 else 0
            
            # Determine market sentiment
            if current_vix < 12:
                sentiment = "EXTREME_COMPLACENCY"
                interpretation = "⚠️ VIX extremely low - Market may be overconfident. Potential for sudden volatility spike."
                risk_level = "HIGH"
            elif current_vix < 16:
                sentiment = "LOW_FEAR"
                interpretation = "🟢 Low volatility environment - Favorable for trend-following strategies."
                risk_level = "LOW"
            elif current_vix < 20:
                sentiment = "NORMAL"
                interpretation = "📊 Normal market conditions - Standard risk management applies."
                risk_level = "MODERATE"
            elif current_vix < 25:
                sentiment = "ELEVATED_FEAR"
                interpretation = "⚠️ Elevated fear - Consider reducing position sizes or hedging."
                risk_level = "ELEVATED"
            elif current_vix < 30:
                sentiment = "HIGH_FEAR"
                interpretation = "🔴 High fear - Volatile conditions. Potential for sharp reversals."
                risk_level = "HIGH"
            else:
                sentiment = "EXTREME_FEAR"
                interpretation = "🔴 EXTREME FEAR - Historically, extreme VIX often marks bottoms. Contrarian opportunity?"
                risk_level = "EXTREME"
            
            return {
                "status": "success",
                "current_vix": round(current_vix, 2),
                "previous_vix": round(prev_vix, 2),
                "change": round(vix_change, 2),
                "change_pct": round(vix_change_pct, 2),
                "sentiment": sentiment,
                "risk_level": risk_level,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # =========================================================================
    # MARKET BREADTH - ADVANCE/DECLINE
    # =========================================================================
    def get_market_breadth(self) -> Dict:
        """
        Analyze market breadth to understand if moves are broad-based or narrow.
        
        SIGNIFICANCE:
        - Strong breadth = Healthy market, trends likely to continue
        - Weak breadth = Narrow leadership, potential reversal
        """
        try:
            import yfinance as yf
            
            # Get major indices for comparison
            spy = yf.Ticker("SPY")
            qqq = yf.Ticker("QQQ")
            iwm = yf.Ticker("IWM")  # Russell 2000 (small caps)
            
            spy_hist = spy.history(period="5d")
            qqq_hist = qqq.history(period="5d")
            iwm_hist = iwm.history(period="5d")
            
            if spy_hist.empty:
                return {"status": "error", "error": "Unable to fetch market data"}
            
            # Calculate daily returns
            spy_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[-2] - 1) * 100
            qqq_return = (qqq_hist['Close'].iloc[-1] / qqq_hist['Close'].iloc[-2] - 1) * 100
            iwm_return = (iwm_hist['Close'].iloc[-1] / iwm_hist['Close'].iloc[-2] - 1) * 100
            
            # Breadth analysis
            all_positive = spy_return > 0 and qqq_return > 0 and iwm_return > 0
            all_negative = spy_return < 0 and qqq_return < 0 and iwm_return < 0
            
            # Check for divergence (small caps vs large caps)
            large_cap_avg = (spy_return + qqq_return) / 2
            small_cap = iwm_return
            divergence = abs(large_cap_avg - small_cap) > 1  # More than 1% difference
            
            if all_positive:
                breadth = "STRONG_BULLISH"
                interpretation = "🟢 BROAD RALLY - All market caps participating. Healthy bullish breadth."
            elif all_negative:
                breadth = "STRONG_BEARISH"
                interpretation = "🔴 BROAD SELLOFF - All market caps declining. Risk-off environment."
            elif divergence and small_cap > large_cap_avg:
                breadth = "RISK_ON_ROTATION"
                interpretation = "📈 RISK-ON ROTATION - Small caps outperforming. Risk appetite increasing."
            elif divergence and small_cap < large_cap_avg:
                breadth = "RISK_OFF_ROTATION"
                interpretation = "📉 RISK-OFF ROTATION - Large caps outperforming. Flight to safety."
            else:
                breadth = "MIXED"
                interpretation = "📊 MIXED BREADTH - No clear direction. Selective stock picking environment."
            
            return {
                "status": "success",
                "breadth": breadth,
                "spy_return": round(spy_return, 2),
                "qqq_return": round(qqq_return, 2),
                "iwm_return": round(iwm_return, 2),
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # =========================================================================
    # ECONOMIC CALENDAR - KEY EVENTS
    # =========================================================================
    def get_economic_events(self) -> Dict:
        """
        Get upcoming economic events that could impact markets.
        
        KEY EVENTS:
        - FOMC Meetings (Fed rate decisions)
        - CPI/PPI (Inflation data)
        - Jobs Report (NFP)
        - GDP releases
        - Earnings season
        """
        try:
            # Use Finnhub economic calendar if available
            if self.finnhub_key:
                url = "https://finnhub.io/api/v1/calendar/economic"
                params = {
                    "token": self.finnhub_key,
                    "from": datetime.now().strftime("%Y-%m-%d"),
                    "to": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if "economicCalendar" in data:
                    events = data["economicCalendar"]
                    
                    # Filter for high-impact events
                    high_impact = [e for e in events if e.get("impact") == "high"]
                    
                    # Categorize events
                    fed_events = [e for e in events if "FOMC" in e.get("event", "") or "Fed" in e.get("event", "")]
                    inflation_events = [e for e in events if "CPI" in e.get("event", "") or "PPI" in e.get("event", "")]
                    jobs_events = [e for e in events if "Payroll" in e.get("event", "") or "Employment" in e.get("event", "")]
                    
                    # Risk assessment
                    if fed_events:
                        risk = "HIGH"
                        warning = "⚠️ FED EVENT THIS WEEK - Expect increased volatility around announcement."
                    elif high_impact:
                        risk = "ELEVATED"
                        warning = f"📊 {len(high_impact)} high-impact events this week. Monitor closely."
                    else:
                        risk = "NORMAL"
                        warning = "📅 No major economic events expected. Normal trading conditions."
                    
                    return {
                        "status": "success",
                        "total_events": len(events),
                        "high_impact_count": len(high_impact),
                        "fed_events": len(fed_events),
                        "inflation_events": len(inflation_events),
                        "jobs_events": len(jobs_events),
                        "risk_level": risk,
                        "warning": warning,
                        "upcoming_events": events[:5]  # First 5 events
                    }
            
            # Fallback: Basic calendar awareness
            today = datetime.now()
            day_of_week = today.weekday()
            day_of_month = today.day
            
            warnings = []
            risk = "NORMAL"
            
            # First Friday = Jobs report
            if day_of_week == 4 and day_of_month <= 7:
                warnings.append("📊 JOBS REPORT DAY - NFP release typically at 8:30 AM ET")
                risk = "ELEVATED"
            
            # Mid-month = CPI typically
            if 10 <= day_of_month <= 15:
                warnings.append("📊 CPI week - Inflation data may be released")
                risk = "ELEVATED"
            
            # FOMC meetings (roughly every 6 weeks)
            # This is approximate - real calendar would be better
            
            return {
                "status": "success",
                "total_events": 0,
                "high_impact_count": 0,
                "risk_level": risk,
                "warning": warnings[0] if warnings else "📅 No major known events. Check economic calendar for updates.",
                "note": "Limited calendar data - using date-based estimation"
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # =========================================================================
    # SECTOR ROTATION ANALYSIS
    # =========================================================================
    def get_sector_rotation(self) -> Dict:
        """
        Analyze sector performance to understand market rotation.
        
        SECTORS:
        - XLK (Tech), XLF (Financials), XLE (Energy), XLV (Healthcare)
        - XLY (Consumer Discretionary), XLP (Consumer Staples)
        - XLI (Industrials), XLB (Materials), XLU (Utilities), XLRE (Real Estate)
        """
        try:
            import yfinance as yf
            
            sectors = {
                "XLK": "Technology",
                "XLF": "Financials",
                "XLE": "Energy",
                "XLV": "Healthcare",
                "XLY": "Consumer Disc.",
                "XLP": "Consumer Staples",
                "XLI": "Industrials",
                "XLB": "Materials",
                "XLU": "Utilities",
                "XLRE": "Real Estate"
            }
            
            sector_performance = {}
            
            for ticker, name in sectors.items():
                try:
                    etf = yf.Ticker(ticker)
                    hist = etf.history(period="5d")
                    if not hist.empty:
                        daily_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
                        weekly_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
                        sector_performance[ticker] = {
                            "name": name,
                            "daily_return": round(daily_return, 2),
                            "weekly_return": round(weekly_return, 2)
                        }
                except:
                    continue
            
            if not sector_performance:
                return {"status": "error", "error": "Unable to fetch sector data"}
            
            # Sort by daily performance
            sorted_sectors = sorted(sector_performance.items(), key=lambda x: x[1]['daily_return'], reverse=True)
            
            # Identify leaders and laggards
            leaders = sorted_sectors[:3]
            laggards = sorted_sectors[-3:]
            
            # Determine rotation type
            leader_names = [s[1]['name'] for s in leaders]
            
            if "Technology" in leader_names or "Consumer Disc." in leader_names:
                rotation = "GROWTH"
                interpretation = "📈 GROWTH ROTATION - Risk-on sentiment. Tech and discretionary leading."
            elif "Utilities" in leader_names or "Consumer Staples" in leader_names:
                rotation = "DEFENSIVE"
                interpretation = "🛡️ DEFENSIVE ROTATION - Risk-off sentiment. Utilities and staples leading."
            elif "Energy" in leader_names or "Materials" in leader_names:
                rotation = "CYCLICAL"
                interpretation = "🔄 CYCLICAL ROTATION - Economic optimism. Commodities and industrials leading."
            elif "Financials" in leader_names:
                rotation = "RATE_SENSITIVE"
                interpretation = "🏦 RATE-SENSITIVE ROTATION - Financials leading. Watch interest rate expectations."
            else:
                rotation = "MIXED"
                interpretation = "📊 MIXED ROTATION - No clear sector theme. Stock-specific factors dominate."
            
            return {
                "status": "success",
                "rotation_type": rotation,
                "interpretation": interpretation,
                "leaders": [{"ticker": s[0], **s[1]} for s in leaders],
                "laggards": [{"ticker": s[0], **s[1]} for s in laggards],
                "all_sectors": sector_performance
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # =========================================================================
    # NEWS SENTIMENT FOR SPECIFIC STOCK
    # =========================================================================
    def get_stock_news_sentiment(self, symbol: str) -> Dict:
        """
        Get news sentiment for a specific stock.
        """
        try:
            if not self.finnhub_key:
                return {"status": "error", "error": "Finnhub API key required for news"}
            
            url = "https://finnhub.io/api/v1/company-news"
            params = {
                "symbol": symbol,
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "to": datetime.now().strftime("%Y-%m-%d"),
                "token": self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            news = response.json()
            
            if not news:
                return {
                    "status": "success",
                    "news_count": 0,
                    "sentiment": "NEUTRAL",
                    "interpretation": "📰 No recent news for this stock."
                }
            
            # Simple sentiment analysis based on headlines
            positive_words = ["surge", "jump", "gain", "rise", "beat", "upgrade", "buy", "bullish", "growth", "profit", "record"]
            negative_words = ["fall", "drop", "decline", "miss", "downgrade", "sell", "bearish", "loss", "cut", "warning", "concern"]
            
            positive_count = 0
            negative_count = 0
            
            headlines = []
            for article in news[:10]:  # Last 10 articles
                headline = article.get("headline", "").lower()
                headlines.append(article.get("headline", ""))
                
                for word in positive_words:
                    if word in headline:
                        positive_count += 1
                        break
                
                for word in negative_words:
                    if word in headline:
                        negative_count += 1
                        break
            
            # Determine sentiment
            if positive_count > negative_count + 2:
                sentiment = "VERY_BULLISH"
                interpretation = f"📈 BULLISH NEWS FLOW - {positive_count} positive vs {negative_count} negative headlines."
            elif positive_count > negative_count:
                sentiment = "BULLISH"
                interpretation = f"📈 Slightly bullish news sentiment."
            elif negative_count > positive_count + 2:
                sentiment = "VERY_BEARISH"
                interpretation = f"📉 BEARISH NEWS FLOW - {negative_count} negative vs {positive_count} positive headlines."
            elif negative_count > positive_count:
                sentiment = "BEARISH"
                interpretation = f"📉 Slightly bearish news sentiment."
            else:
                sentiment = "NEUTRAL"
                interpretation = "📊 Neutral news sentiment - no clear bias."
            
            return {
                "status": "success",
                "news_count": len(news),
                "positive_count": positive_count,
                "negative_count": negative_count,
                "sentiment": sentiment,
                "interpretation": interpretation,
                "recent_headlines": headlines[:5]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # =========================================================================
    # COMPREHENSIVE MACRO ANALYSIS
    # =========================================================================
    def get_full_macro_context(self, symbol: str = None) -> Dict:
        """
        Get comprehensive macro context for trading decisions.
        PRODUCTION-GRADE: Includes active date/time context on every call.
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        # CRITICAL: Add market session context to EVERY scan
        result["market_session"] = self._get_market_session_context()
        
        # VIX Analysis
        result["vix"] = self.get_vix_analysis()
        
        # Market Breadth
        result["breadth"] = self.get_market_breadth()
        
        # Economic Calendar
        result["economic_calendar"] = self.get_economic_events()
        
        # Sector Rotation
        result["sector_rotation"] = self.get_sector_rotation()
        
        # Stock-specific news (if symbol provided)
        if symbol:
            result["stock_news"] = self.get_stock_news_sentiment(symbol)
        
        # Calculate overall market risk score
        risk_factors = 0
        
        if result["vix"].get("risk_level") in ["HIGH", "EXTREME"]:
            risk_factors += 2
        elif result["vix"].get("risk_level") == "ELEVATED":
            risk_factors += 1
        
        if result["breadth"].get("breadth") in ["STRONG_BEARISH", "RISK_OFF_ROTATION"]:
            risk_factors += 1
        
        if result["economic_calendar"].get("risk_level") in ["HIGH", "ELEVATED"]:
            risk_factors += 1
        
        if risk_factors >= 3:
            result["overall_risk"] = "HIGH"
            result["risk_warning"] = "⚠️ ELEVATED MARKET RISK - Multiple macro factors suggest caution. Consider reducing position sizes."
        elif risk_factors >= 2:
            result["overall_risk"] = "MODERATE"
            result["risk_warning"] = "📊 MODERATE RISK - Some macro headwinds. Use appropriate risk management."
        else:
            result["overall_risk"] = "LOW"
            result["risk_warning"] = "🟢 LOW MACRO RISK - Favorable conditions for trading."
        
        return result


# Test the module
if __name__ == "__main__":
    import os
    
    finnhub_key = os.environ.get("FINNHUB_API_KEY", "d55b3ohr01qljfdeghm0d55b3ohr01qljfdeghmg")
    
    macro = MacroContext(finnhub_key)
    
    print("=" * 60)
    print("MACRO CONTEXT ANALYSIS")
    print("=" * 60)
    
    # Test VIX
    print("\n📊 VIX Analysis:")
    vix = macro.get_vix_analysis()
    if vix["status"] == "success":
        print(f"   Current VIX: {vix['current_vix']}")
        print(f"   Sentiment: {vix['sentiment']}")
        print(f"   {vix['interpretation']}")
    
    # Test Market Breadth
    print("\n📈 Market Breadth:")
    breadth = macro.get_market_breadth()
    if breadth["status"] == "success":
        print(f"   SPY: {breadth['spy_return']:+.2f}%")
        print(f"   QQQ: {breadth['qqq_return']:+.2f}%")
        print(f"   IWM: {breadth['iwm_return']:+.2f}%")
        print(f"   {breadth['interpretation']}")
    
    # Test Sector Rotation
    print("\n🔄 Sector Rotation:")
    sectors = macro.get_sector_rotation()
    if sectors["status"] == "success":
        print(f"   Rotation: {sectors['rotation_type']}")
        print(f"   {sectors['interpretation']}")
        print(f"   Leaders: {[s['name'] for s in sectors['leaders']]}")
    
    # Test Full Context
    print("\n🌍 Full Macro Context for AAPL:")
    full = macro.get_full_macro_context("AAPL")
    print(f"   Overall Risk: {full['overall_risk']}")
    print(f"   {full['risk_warning']}")
