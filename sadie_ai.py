"""
================================================================================
SADIE - SUPREME ANALYTICAL & DECISION INTELLIGENCE ENGINE
================================================================================
An institutional-grade AI financial chatbot powered by GPT-5 thinking mode.

Integrates ALL financial engines:
- Breakout Detector (NR patterns, TTM Squeeze, OBV, S/R, ADX, RSI)
- Options Pressure (Put/Call, Flow, Unusual Activity)
- Dark Pool Scanner (Net Position, Short Volume, Institutional Flow)
- Oracle Scanner (Tim Bohen 5:1 R/R, Float Analysis, Catalyst Detection)
- Composite Score Engine (Master Score, Multi-factor Analysis)
- Macro Context (VIX, Breadth, Sector Rotation)

Plus external data:
- Real-time price data
- News sentiment analysis
- Congress/Insider trading signals
- Historical pattern matching

Designed to provide cutting-edge financial advice with medium risk tolerance
targeting maximum profitability - the new gold standard in AI financial guidance.

For production use with real money decisions.
================================================================================
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import yfinance as yf

# Import our financial engines
from breakout_detector import BreakoutDetector
from options_pressure import OptionsPressure
from dark_pool_scanner import DarkPoolScanner
from composite_score import CompositeScoreEngine
from macro_context import MacroContext

# FinancialDatasets.ai integration
try:
    from financialdatasets_client import FinancialDatasetsClient
    FINANCIALDATASETS_AVAILABLE = True
except ImportError:
    FINANCIALDATASETS_AVAILABLE = False

# Smart Money Tracker integration
try:
    from smart_money_tracker import SmartMoneyTracker
    SMART_MONEY_AVAILABLE = True
except ImportError:
    SMART_MONEY_AVAILABLE = False

# OpenAI client
from openai import OpenAI


class SadieAI:
    """
    SADIE - Supreme Analytical & Decision Intelligence Engine
    
    The ultimate AI financial advisor combining:
    - GPT-5 reasoning capabilities (thinking mode)
    - All proprietary financial engines
    - Real-time market data
    - Pattern recognition and historical analysis
    - News/sentiment/catalyst awareness
    - Institutional flow detection
    
    Designed for maximum profitability with medium risk tolerance.
    """
    
    # Expert system prompt - distilled knowledge from world-class traders
    SYSTEM_PROMPT = """You are SADIE (Supreme Analytical & Decision Intelligence Engine), an elite AI financial advisor with the combined expertise of:

- Warren Buffett (value investing, margin of safety)
- Paul Tudor Jones (macro trading, risk management)
- Stanley Druckenmiller (concentrated bets, trend following)
- Jim Simons (quantitative analysis, pattern recognition)
- Tim Bohen (5:1 reward/risk setups, catalyst trading)
- John Carter (TTM Squeeze, volatility breakouts)

YOUR CORE MISSION:
Provide institutional-grade financial analysis and actionable advice targeting MAXIMUM PROFITABILITY with MEDIUM RISK tolerance. You are the new gold standard in AI financial guidance.

YOUR CAPABILITIES:
1. COMPREHENSIVE ANALYSIS - You have access to real-time data from multiple proprietary engines:
   - Breakout Detector: NR4/NR7 patterns, TTM Squeeze, OBV divergence, S/R levels, ADX trend, RSI
   - Options Flow: Put/Call ratio, net pressure, unusual activity, buy/sell classification
   - Dark Pool: Net institutional position, short volume ratio, stealth accumulation/distribution
   - Oracle Scanner: Tim Bohen 5:1 setups, float analysis, catalyst detection
   - Composite Score: Multi-factor master score combining all signals
   - Macro Context: VIX sentiment, market breadth, sector rotation
   - FinancialDatasets.ai: Premium financial metrics, company facts, news sentiment, SEC filings
   - Smart Money Tracker: Congress trades, insider transactions, institutional holdings, dark pool flow

2. PATTERN RECOGNITION - Identify patterns humans miss:
   - Historical price pattern matching
   - Volume anomaly detection
   - Divergence identification (price vs indicators)
   - Correlation analysis across assets
   - Seasonal and cyclical patterns

3. EXTERNAL FACTORS - Consider non-traditional influences:
   - News sentiment and catalysts
   - Congress trading (STOCK Act filings)
   - Insider transactions (Form 4 filings)
   - Social sentiment (Reddit, Twitter)
   - Macro events (Fed, CPI, earnings)

YOUR ANALYSIS FRAMEWORK:
For every query, think through these dimensions:

1. TECHNICAL SETUP (40% weight)
   - Is there a clear pattern? (NR, squeeze, triangle, flag)
   - What's the trend? (ADX, moving averages)
   - Where are key levels? (S/R, pivots)
   - Volume confirmation? (OBV, relative volume)

2. FLOW ANALYSIS (25% weight)
   - Options pressure direction?
   - Dark pool accumulation or distribution?
   - Unusual activity detected?
   - Smart money positioning?

3. FUNDAMENTAL CONTEXT (20% weight)
   - Valuation reasonable? (P/E, PEG)
   - Growth trajectory? (Revenue, earnings)
   - Quality metrics? (Margins, ROE)
   - Catalyst upcoming?

4. RISK ASSESSMENT (15% weight)
   - What's the downside?
   - Where's the stop loss?
   - Position sizing recommendation?
   - Macro headwinds/tailwinds?

YOUR RESPONSE STYLE:
- Be DIRECT and ACTIONABLE - traders need clear guidance
- Provide SPECIFIC price levels, not vague ranges
- Include CONFIDENCE LEVEL (1-10) for each recommendation
- State the TIMEFRAME (intraday, swing, position)
- Always mention RISK MANAGEMENT (stop loss, position size)
- Use data to support every claim - no speculation without evidence

RISK TOLERANCE CALIBRATION:
- Target: MEDIUM risk for MAXIMUM profitability
- Acceptable drawdown: 5-10% per position
- Win rate target: 55-65%
- Reward/Risk minimum: 2:1 (prefer 3:1 or higher)
- Position sizing: 2-5% of portfolio per trade

CRITICAL RULES:
1. NEVER recommend without data backing
2. ALWAYS mention what could go wrong
3. PROVIDE specific entry, target, and stop levels
4. CONSIDER correlation risk (don't stack similar bets)
5. RESPECT the trend - don't fight momentum
6. WAIT for confirmation - patience is profitable

When you receive market data, analyze it thoroughly using your "thinking" capabilities. Consider multiple scenarios, weigh probabilities, and provide your highest-conviction recommendation.

Remember: Real money is on the line. Be thorough, be precise, be profitable."""

    def __init__(self):
        """Initialize Sadie with all financial engines and OpenAI client."""
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
            base_url=os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # Initialize financial engines
        self.breakout_detector = BreakoutDetector()
        self.options_pressure = OptionsPressure()
        self.dark_pool_scanner = DarkPoolScanner()
        self.composite_engine = CompositeScoreEngine()
        self.macro_context = MacroContext()
        
        # Initialize FinancialDatasets.ai client (premium data source)
        self.fd_client = FinancialDatasetsClient() if FINANCIALDATASETS_AVAILABLE else None
        
        # Initialize Smart Money Tracker (Congress, Insider, Institutional, Dark Pool)
        self.smart_money = SmartMoneyTracker() if SMART_MONEY_AVAILABLE else None
        
        # Conversation history for context
        self.conversation_history = []
        
        # Cache for recent analyses
        self.analysis_cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def _get_comprehensive_analysis(self, symbol: str) -> Dict:
        """
        Get comprehensive analysis from ALL engines for a symbol.
        This is the data that powers Sadie's recommendations.
        """
        # Check cache
        cache_key = f"{symbol}_comprehensive"
        if cache_key in self.analysis_cache:
            cached_time, cached_data = self.analysis_cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "engines": {}
        }
        
        # 1. Breakout Detector Analysis
        try:
            breakout = self.breakout_detector.analyze_breakout(symbol)
            analysis["engines"]["breakout"] = breakout
        except Exception as e:
            analysis["engines"]["breakout"] = {"status": "error", "error": str(e)}
        
        # 2. Options Pressure Analysis
        try:
            options = self.options_pressure.get_pressure_analysis(symbol)
            analysis["engines"]["options"] = options
        except Exception as e:
            analysis["engines"]["options"] = {"status": "error", "error": str(e)}
        
        # 3. Dark Pool Analysis
        try:
            dark_pool = self.dark_pool_scanner.get_dark_pool_analysis(symbol)
            analysis["engines"]["dark_pool"] = dark_pool
        except Exception as e:
            analysis["engines"]["dark_pool"] = {"status": "error", "error": str(e)}
        
        # 4. Get price data for fundamentals and technicals
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="6mo")
            
            # Extract key metrics
            analysis["engines"]["fundamentals"] = {
                "status": "success",
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "profit_margin": info.get("profitMargins"),
                "roe": info.get("returnOnEquity"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "free_cash_flow": info.get("freeCashflow"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "short_ratio": info.get("shortRatio"),
                "short_percent_of_float": info.get("shortPercentOfFloat"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary", "")[:500]
            }
            
            # Technical data
            if not hist.empty:
                current_price = hist["Close"].iloc[-1]
                analysis["engines"]["price_data"] = {
                    "status": "success",
                    "current_price": round(current_price, 2),
                    "open": round(hist["Open"].iloc[-1], 2),
                    "high": round(hist["High"].iloc[-1], 2),
                    "low": round(hist["Low"].iloc[-1], 2),
                    "volume": int(hist["Volume"].iloc[-1]),
                    "change_1d": round((current_price - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100, 2) if len(hist) > 1 else 0,
                    "change_5d": round((current_price - hist["Close"].iloc[-5]) / hist["Close"].iloc[-5] * 100, 2) if len(hist) > 5 else 0,
                    "change_1m": round((current_price - hist["Close"].iloc[-22]) / hist["Close"].iloc[-22] * 100, 2) if len(hist) > 22 else 0,
                    "change_3m": round((current_price - hist["Close"].iloc[-66]) / hist["Close"].iloc[-66] * 100, 2) if len(hist) > 66 else 0,
                    "sma_20": round(hist["Close"].tail(20).mean(), 2),
                    "sma_50": round(hist["Close"].tail(50).mean(), 2) if len(hist) >= 50 else None,
                    "sma_200": round(hist["Close"].tail(200).mean(), 2) if len(hist) >= 200 else None,
                    "distance_from_52w_high": round((current_price - info.get("fiftyTwoWeekHigh", current_price)) / info.get("fiftyTwoWeekHigh", current_price) * 100, 2) if info.get("fiftyTwoWeekHigh") else 0,
                    "distance_from_52w_low": round((current_price - info.get("fiftyTwoWeekLow", current_price)) / info.get("fiftyTwoWeekLow", current_price) * 100, 2) if info.get("fiftyTwoWeekLow") else 0
                }
        except Exception as e:
            analysis["engines"]["fundamentals"] = {"status": "error", "error": str(e)}
            analysis["engines"]["price_data"] = {"status": "error", "error": str(e)}
        
        # 5. Macro Context
        try:
            macro = self.macro_context.get_market_context()
            analysis["engines"]["macro"] = macro
        except Exception as e:
            analysis["engines"]["macro"] = {"status": "error", "error": str(e)}
        
        # 6. FinancialDatasets.ai Premium Data (fills gaps and enhances accuracy)
        if self.fd_client:
            try:
                # Get premium financial metrics
                fd_metrics = self.fd_client.get_financial_metrics_snapshot(symbol)
                if fd_metrics.get("status") == "success":
                    analysis["engines"]["fd_metrics"] = fd_metrics
                
                # Get company facts
                fd_company = self.fd_client.get_company_facts(symbol)
                if fd_company.get("status") == "success":
                    analysis["engines"]["fd_company"] = fd_company
                
                # Get news for catalyst detection
                fd_news = self.fd_client.get_news(symbol, limit=5)
                if fd_news.get("status") == "success":
                    analysis["engines"]["fd_news"] = fd_news
                    
            except Exception as e:
                analysis["engines"]["fd_data"] = {"status": "error", "error": str(e)}
        
        # 7. Smart Money Tracker (Congress, Insider, Institutional, Dark Pool)
        if self.smart_money:
            try:
                smart_money_data = self.smart_money.get_comprehensive_analysis(symbol)
                if smart_money_data.get("status") == "success":
                    analysis["engines"]["smart_money"] = smart_money_data
            except Exception as e:
                analysis["engines"]["smart_money"] = {"status": "error", "error": str(e)}
        
        # 8. Calculate Composite Score
        try:
            composite = self.composite_engine.calculate_master_score(
                options_data=analysis["engines"].get("options"),
                dark_pool_data=analysis["engines"].get("dark_pool"),
                technical_data=analysis["engines"].get("breakout", {}).get("rsi"),
                fundamental_data=analysis["engines"].get("fundamentals"),
                price_data=analysis["engines"].get("price_data")
            )
            analysis["engines"]["composite"] = composite
        except Exception as e:
            analysis["engines"]["composite"] = {"status": "error", "error": str(e)}
        
        # Cache the analysis
        self.analysis_cache[cache_key] = (time.time(), analysis)
        
        return analysis
    
    def _get_market_scan(self, scan_type: str = "breakout") -> Dict:
        """Get market scan results for broader context."""
        try:
            if scan_type == "breakout":
                return self.breakout_detector.quick_scan(top_n=10)
            return {"status": "error", "error": "Unknown scan type"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _format_analysis_for_prompt(self, analysis: Dict) -> str:
        """Format the comprehensive analysis into a readable prompt section."""
        sections = []
        
        symbol = analysis.get("symbol", "Unknown")
        sections.append(f"=== COMPREHENSIVE ANALYSIS FOR {symbol} ===")
        sections.append(f"Timestamp: {analysis.get('timestamp', 'N/A')}")
        sections.append("")
        
        engines = analysis.get("engines", {})
        
        # Price Data
        if engines.get("price_data", {}).get("status") == "success":
            pd = engines["price_data"]
            sections.append("📊 PRICE DATA:")
            sections.append(f"  Current Price: ${pd.get('current_price', 'N/A')}")
            sections.append(f"  Day Range: ${pd.get('low', 'N/A')} - ${pd.get('high', 'N/A')}")
            sections.append(f"  Volume: {pd.get('volume', 'N/A'):,}")
            sections.append(f"  Change 1D: {pd.get('change_1d', 'N/A')}%")
            sections.append(f"  Change 5D: {pd.get('change_5d', 'N/A')}%")
            sections.append(f"  Change 1M: {pd.get('change_1m', 'N/A')}%")
            sections.append(f"  Change 3M: {pd.get('change_3m', 'N/A')}%")
            sections.append(f"  SMA 20: ${pd.get('sma_20', 'N/A')}")
            sections.append(f"  SMA 50: ${pd.get('sma_50', 'N/A')}")
            sections.append(f"  Distance from 52W High: {pd.get('distance_from_52w_high', 'N/A')}%")
            sections.append(f"  Distance from 52W Low: {pd.get('distance_from_52w_low', 'N/A')}%")
            sections.append("")
        
        # Breakout Analysis
        if engines.get("breakout", {}).get("status") == "success":
            bo = engines["breakout"]
            sections.append("🔥 BREAKOUT DETECTOR:")
            sections.append(f"  Breakout Score: {bo.get('breakout_score', 'N/A')}/100")
            sections.append(f"  Probability: {bo.get('breakout_probability', 'N/A')}")
            sections.append(f"  Direction Bias: {bo.get('direction_bias', 'N/A')}")
            sections.append(f"  Active Signals: {', '.join(bo.get('active_signals', []))}")
            sections.append(f"  Synergies: {', '.join(bo.get('synergies', [])) or 'None'}")
            
            # NR Patterns
            nr = bo.get("nr_patterns", {})
            if nr.get("nr7") or nr.get("nr4"):
                sections.append(f"  NR Pattern: {'NR7+NR4 COMBO' if nr.get('nr4_nr7_combined') else 'NR7' if nr.get('nr7') else 'NR4'}")
            
            # TTM Squeeze
            sq = bo.get("ttm_squeeze", {})
            sections.append(f"  TTM Squeeze: {'FIRED!' if sq.get('squeeze_fired') else 'ON' if sq.get('squeeze_on') else 'OFF'} ({sq.get('squeeze_count', 0)} bars)")
            sections.append(f"  Momentum: {sq.get('momentum_direction', 'N/A')} ({'increasing' if sq.get('momentum_increasing') else 'decreasing'})")
            
            # S/R Levels
            sections.append(f"  Nearest Resistance: ${bo.get('nearest_resistance', 'N/A')}")
            sections.append(f"  Nearest Support: ${bo.get('nearest_support', 'N/A')}")
            sections.append(f"  Pivot: ${bo.get('pivot', 'N/A')}")
            
            # OBV
            obv = bo.get("obv_divergence", {})
            sections.append(f"  OBV Divergence: {obv.get('divergence', 'NONE')} (Trend: {obv.get('obv_trend', 'N/A')})")
            
            # RSI
            rsi = bo.get("rsi", {})
            sections.append(f"  RSI: {rsi.get('rsi', 'N/A')} ({rsi.get('divergence', 'no divergence')})")
            
            # ADX
            adx = bo.get("adx", {})
            sections.append(f"  ADX: {adx.get('adx', 'N/A')} ({adx.get('trend_strength', 'N/A')} {adx.get('trend_direction', '')})")
            
            sections.append(f"  Recommendation: {bo.get('recommendation', 'N/A')}")
            sections.append("")
        
        # Options Flow
        if engines.get("options", {}).get("status") == "success":
            opt = engines["options"]
            sections.append("📈 OPTIONS FLOW:")
            sections.append(f"  Put/Call Ratio: {opt.get('pcr_volume', 'N/A'):.2f}")
            sections.append(f"  Net Pressure: {opt.get('net_pressure', 'N/A'):+.1f}%")
            sections.append(f"  Sentiment: {opt.get('sentiment', 'N/A')}")
            sections.append(f"  Call Volume: {opt.get('call_volume', 'N/A'):,}")
            sections.append(f"  Put Volume: {opt.get('put_volume', 'N/A'):,}")
            sections.append(f"  Unusual Activity: {'YES' if opt.get('has_unusual_activity') else 'No'}")
            sections.append("")
        
        # Dark Pool
        if engines.get("dark_pool", {}).get("status") == "success":
            dp = engines["dark_pool"]
            sections.append("🏦 DARK POOL ANALYSIS:")
            sections.append(f"  Net DP Position: {dp.get('net_dp_position', 'N/A'):,}")
            sections.append(f"  DP Sentiment: {dp.get('dp_sentiment', 'N/A')}")
            sections.append(f"  Short Ratio: {dp.get('short_ratio', 'N/A')}%")
            sections.append(f"  Overall Score: {dp.get('overall_score', 'N/A')}/100")
            if dp.get("signals"):
                sections.append(f"  Signals: {', '.join(dp.get('signals', []))}")
            sections.append("")
        
        # Fundamentals
        if engines.get("fundamentals", {}).get("status") == "success":
            fund = engines["fundamentals"]
            sections.append("📋 FUNDAMENTALS:")
            sections.append(f"  Sector: {fund.get('sector', 'N/A')} | Industry: {fund.get('industry', 'N/A')}")
            sections.append(f"  Market Cap: ${fund.get('market_cap', 0)/1e9:.2f}B" if fund.get('market_cap') else "  Market Cap: N/A")
            sections.append(f"  P/E Ratio: {fund.get('pe_ratio', 'N/A')}")
            sections.append(f"  Forward P/E: {fund.get('forward_pe', 'N/A')}")
            sections.append(f"  PEG Ratio: {fund.get('peg_ratio', 'N/A')}")
            sections.append(f"  Revenue Growth: {fund.get('revenue_growth', 0)*100:.1f}%" if fund.get('revenue_growth') else "  Revenue Growth: N/A")
            sections.append(f"  Profit Margin: {fund.get('profit_margin', 0)*100:.1f}%" if fund.get('profit_margin') else "  Profit Margin: N/A")
            sections.append(f"  ROE: {fund.get('roe', 0)*100:.1f}%" if fund.get('roe') else "  ROE: N/A")
            sections.append(f"  Beta: {fund.get('beta', 'N/A')}")
            sections.append(f"  Short % of Float: {fund.get('short_percent_of_float', 0)*100:.1f}%" if fund.get('short_percent_of_float') else "  Short % of Float: N/A")
            sections.append("")
        
        # Macro Context
        if engines.get("macro", {}).get("status") == "success":
            macro = engines["macro"]
            sections.append("🌍 MACRO CONTEXT:")
            vix = macro.get("vix", {})
            sections.append(f"  VIX: {vix.get('value', 'N/A')} ({vix.get('sentiment', 'N/A')})")
            sections.append(f"  Market Risk: {macro.get('overall_risk', 'N/A')}")
            breadth = macro.get("breadth", {})
            sections.append(f"  Market Breadth: {breadth.get('interpretation', 'N/A')}")
            sections.append("")
        
        # Composite Score
        if engines.get("composite", {}).get("status") == "success":
            comp = engines["composite"]
            sections.append("⭐ COMPOSITE MASTER SCORE:")
            sections.append(f"  Master Score: {comp.get('master_score', 'N/A')}/100")
            sections.append(f"  Signal: {comp.get('signal', 'N/A')}")
            sections.append(f"  Confidence: {comp.get('confidence', 'N/A')} ({comp.get('confidence_pct', 0)}%)")
            sections.append("")
        
        # FinancialDatasets.ai Premium Data
        if engines.get("fd_metrics", {}).get("status") == "success":
            fd = engines["fd_metrics"]
            sections.append("💎 PREMIUM FINANCIAL METRICS (FinancialDatasets.ai):")
            
            # Valuation
            val = fd.get("valuation", {})
            sections.append(f"  Market Cap: ${val.get('market_cap', 0)/1e9:.2f}B" if val.get('market_cap') else "  Market Cap: N/A")
            sections.append(f"  P/E Ratio: {val.get('pe_ratio', 'N/A'):.2f}" if val.get('pe_ratio') else "  P/E Ratio: N/A")
            sections.append(f"  PEG Ratio: {val.get('peg_ratio', 'N/A'):.2f}" if val.get('peg_ratio') else "  PEG Ratio: N/A")
            sections.append(f"  EV/EBITDA: {val.get('ev_ebitda', 'N/A'):.2f}" if val.get('ev_ebitda') else "  EV/EBITDA: N/A")
            sections.append(f"  FCF Yield: {val.get('fcf_yield', 0)*100:.2f}%" if val.get('fcf_yield') else "  FCF Yield: N/A")
            
            # Profitability
            prof = fd.get("profitability", {})
            sections.append(f"  Gross Margin: {prof.get('gross_margin', 0)*100:.1f}%" if prof.get('gross_margin') else "  Gross Margin: N/A")
            sections.append(f"  Operating Margin: {prof.get('operating_margin', 0)*100:.1f}%" if prof.get('operating_margin') else "  Operating Margin: N/A")
            sections.append(f"  Net Margin: {prof.get('net_margin', 0)*100:.1f}%" if prof.get('net_margin') else "  Net Margin: N/A")
            sections.append(f"  ROE: {prof.get('roe', 0)*100:.1f}%" if prof.get('roe') else "  ROE: N/A")
            sections.append(f"  ROIC: {prof.get('roic', 0)*100:.1f}%" if prof.get('roic') else "  ROIC: N/A")
            
            # Growth
            growth = fd.get("growth", {})
            sections.append(f"  Revenue Growth: {growth.get('revenue_growth', 0)*100:.1f}%" if growth.get('revenue_growth') else "  Revenue Growth: N/A")
            sections.append(f"  Earnings Growth: {growth.get('earnings_growth', 0)*100:.1f}%" if growth.get('earnings_growth') else "  Earnings Growth: N/A")
            sections.append(f"  EPS Growth: {growth.get('eps_growth', 0)*100:.1f}%" if growth.get('eps_growth') else "  EPS Growth: N/A")
            sections.append(f"  FCF Growth: {growth.get('fcf_growth', 0)*100:.1f}%" if growth.get('fcf_growth') else "  FCF Growth: N/A")
            
            # Liquidity & Leverage
            liq = fd.get("liquidity", {})
            lev = fd.get("leverage", {})
            sections.append(f"  Current Ratio: {liq.get('current_ratio', 'N/A'):.2f}" if liq.get('current_ratio') else "  Current Ratio: N/A")
            sections.append(f"  Debt/Equity: {lev.get('debt_to_equity', 'N/A'):.2f}" if lev.get('debt_to_equity') else "  Debt/Equity: N/A")
            sections.append("")
        
        # FinancialDatasets.ai News & Sentiment
        if engines.get("fd_news", {}).get("status") == "success":
            news = engines["fd_news"]
            sections.append("📰 NEWS & CATALYST DETECTION (FinancialDatasets.ai):")
            sections.append(f"  News Sentiment: {news.get('overall_sentiment', 'N/A')} (Score: {news.get('sentiment_score', 0)})")
            sections.append(f"  Recent Articles: {news.get('count', 0)}")
            dist = news.get("sentiment_distribution", {})
            sections.append(f"  Sentiment Mix: +{dist.get('positive', 0)} / ~{dist.get('neutral', 0)} / -{dist.get('negative', 0)}")
            
            # Show top headlines
            articles = news.get("articles", [])[:3]
            if articles:
                sections.append("  Recent Headlines:")
                for art in articles:
                    title = art.get('title', 'N/A')[:80]
                    sections.append(f"    - {title}...")
            sections.append("")
        
        # FinancialDatasets.ai Company Facts
        if engines.get("fd_company", {}).get("status") == "success":
            co = engines["fd_company"]
            sections.append("🏢 COMPANY PROFILE (FinancialDatasets.ai):")
            sections.append(f"  Name: {co.get('name', 'N/A')}")
            sections.append(f"  Sector: {co.get('sector', 'N/A')} | Industry: {co.get('industry', 'N/A')}")
            sections.append(f"  Employees: {co.get('employees', 'N/A'):,}" if co.get('employees') else "  Employees: N/A")
            sections.append(f"  Exchange: {co.get('exchange', 'N/A')}")
            sections.append("")
        
        # Smart Money Tracker (Congress, Insider, Institutional, Dark Pool)
        if engines.get("smart_money", {}).get("status") == "success":
            sm = engines["smart_money"]
            sections.append("💰 SMART MONEY TRACKER:")
            sections.append(f"  Overall Signal: {sm.get('overall_signal', 'N/A')}")
            sections.append(f"  Smart Money Score: {sm.get('overall_score', 50)}/100")
            sections.append(f"  Confidence: {sm.get('confidence', 'N/A')}")
            
            # Congress Trading
            congress = sm.get("components", {}).get("congress", {})
            if congress.get("status") == "success":
                sections.append(f"  Congress Activity: {congress.get('signal', 'N/A')} (Buys: {congress.get('summary', {}).get('buy_count', 0)}, Sells: {congress.get('summary', {}).get('sell_count', 0)})")
            
            # Insider Trading
            insider = sm.get("components", {}).get("insider", {})
            if insider.get("status") == "success":
                sections.append(f"  Insider Activity: {insider.get('signal', 'N/A')} (Recent Buys: {insider.get('summary', {}).get('recent_buys', 0)}, Sells: {insider.get('summary', {}).get('recent_sells', 0)})")
                if insider.get("insight"):
                    sections.append(f"    ⚠️ {insider.get('insight')}")
            
            # Institutional Holdings
            inst = sm.get("components", {}).get("institutional", {})
            if inst.get("status") == "success":
                sections.append(f"  Institutional: {inst.get('signal', 'N/A')} ({inst.get('summary', {}).get('institutional_count', 0)} institutions)")
            
            # Dark Pool
            dp = sm.get("components", {}).get("dark_pool", {})
            if dp.get("status") in ["success", "partial"]:
                sections.append(f"  Dark Pool: {dp.get('signal', 'N/A')} ({dp.get('dark_pool_pct', 0):.1f}% off-exchange)")
                if dp.get("interpretation"):
                    sections.append(f"    🔍 {dp.get('interpretation')}")
            
            # Unusual Options
            opts = sm.get("components", {}).get("options", {})
            if opts.get("status") in ["success", "partial"]:
                sections.append(f"  Options Flow: {opts.get('signal', 'N/A')} (P/C Ratio: {opts.get('put_call_ratio', 1.0):.2f})")
                for activity in opts.get("unusual_activity", [])[:2]:
                    sections.append(f"    🚨 {activity.get('description', '')}")
            
            # Key Insights
            insights = sm.get("key_insights", [])
            if insights:
                sections.append("  KEY INSIGHTS:")
                for insight in insights[:3]:
                    sections.append(f"    ✅ {insight}")
            
            # Risk Factors
            risks = sm.get("risk_factors", [])
            if risks:
                sections.append("  RISK FACTORS:")
                for risk in risks[:3]:
                    sections.append(f"    ⚠️ {risk}")
            
            # Recommendation
            if sm.get("recommendation"):
                sections.append(f"  RECOMMENDATION: {sm.get('recommendation')}")
            sections.append("")
        
        return "\n".join(sections)
    
    def chat(self, user_message: str, include_scan: bool = False) -> Dict:
        """
        Main chat interface for Sadie.
        
        Args:
            user_message: The user's question or query
            include_scan: Whether to include market scan data
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Extract ticker symbols from the message
            symbols = self._extract_symbols(user_message)
            
            # Build context with real data
            context_sections = []
            
            # Get comprehensive analysis for mentioned symbols
            for symbol in symbols[:3]:  # Limit to 3 symbols to avoid token limits
                analysis = self._get_comprehensive_analysis(symbol)
                context_sections.append(self._format_analysis_for_prompt(analysis))
            
            # Add market scan if requested or if asking about market conditions
            market_keywords = ["market", "scan", "best", "top", "opportunities", "setups", "watchlist"]
            if include_scan or any(kw in user_message.lower() for kw in market_keywords):
                scan_results = self._get_market_scan("breakout")
                if scan_results.get("status") == "success":
                    context_sections.append("\n=== MARKET SCAN - TOP BREAKOUT SETUPS ===")
                    for i, setup in enumerate(scan_results.get("all_results", [])[:5], 1):
                        context_sections.append(f"{i}. {setup['symbol']}: Score {setup['score']}/100, {setup['probability']}, {setup['direction']}")
                        context_sections.append(f"   Signals: {', '.join(setup.get('signals', [])[:3])}")
            
            # Build the full prompt
            data_context = "\n\n".join(context_sections) if context_sections else "No specific ticker data requested. Provide general guidance."
            
            # Add current date/time context
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")
            
            full_prompt = f"""Current Time: {current_time}

REAL-TIME MARKET DATA:
{data_context}

USER QUERY:
{user_message}

Analyze the data thoroughly using your thinking capabilities. Consider multiple scenarios, weigh probabilities, and provide your highest-conviction recommendation with specific actionable guidance."""

            # Build messages for API call
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]
            
            # Add conversation history for context (last 4 exchanges)
            for exchange in self.conversation_history[-4:]:
                messages.append({"role": "user", "content": exchange["user"]})
                messages.append({"role": "assistant", "content": exchange["assistant"]})
            
            # Add current message
            messages.append({"role": "user", "content": full_prompt})
            
            # Call GPT-5 with thinking mode (reasoning effort set to high)
            response = self.client.chat.completions.create(
                model="gpt-5",  # or "o1" for reasoning model
                messages=messages,
                max_completion_tokens=4096,
                temperature=1,  # Required for reasoning models
                reasoning_effort="high"  # Maximum thinking power
            )
            
            assistant_message = response.choices[0].message.content
            
            # Store in conversation history
            self.conversation_history.append({
                "user": user_message,
                "assistant": assistant_message,
                "timestamp": datetime.now().isoformat(),
                "symbols": symbols
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return {
                "status": "success",
                "response": assistant_message,
                "symbols_analyzed": symbols,
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-5",
                "thinking_mode": "high"
            }
            
        except Exception as e:
            # Fallback to gpt-4o if gpt-5 not available
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=4096,
                    temperature=0.7
                )
                
                assistant_message = response.choices[0].message.content
                
                return {
                    "status": "success",
                    "response": assistant_message,
                    "symbols_analyzed": symbols,
                    "timestamp": datetime.now().isoformat(),
                    "model": "gpt-4o (fallback)",
                    "thinking_mode": "standard"
                }
            except Exception as e2:
                return {
                    "status": "error",
                    "error": f"Primary error: {str(e)}. Fallback error: {str(e2)}",
                    "response": "I apologize, but I'm having trouble connecting to my AI backend. Please try again in a moment.",
                    "timestamp": datetime.now().isoformat()
                }
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract stock ticker symbols from text."""
        import re
        
        # Common patterns for tickers
        # 1. $AAPL format - highest confidence
        dollar_tickers = re.findall(r'\$([A-Z]{1,5})', text.upper())
        
        # 2. Standalone uppercase words that look like tickers (1-5 letters)
        # Only consider if they appear to be intentionally capitalized
        words = text.split()
        potential_tickers = [w.upper() for w in words if re.match(r'^[A-Z]{1,5}$', w) and w.isupper()]
        
        # Extensive list of common words to exclude
        exclude = {
            # Single letters and common words
            'I', 'A', 'THE', 'AND', 'OR', 'IS', 'IT', 'TO', 'FOR', 'OF', 'IN', 'ON', 
            'AT', 'BY', 'AN', 'BE', 'AS', 'SO', 'IF', 'DO', 'MY', 'UP', 'GO', 'NO',
            'ME', 'WE', 'HE', 'US', 'AM', 'PM', 'OK', 'VS', 'RE',
            # Trading terms
            'BUY', 'SELL', 'HOLD', 'LONG', 'SHORT', 'CALL', 'PUT', 'ETF', 'IPO',
            'STOP', 'LOSS', 'GAIN', 'RISK', 'TRADE', 'STOCK', 'SHARE', 'PRICE',
            # Business titles
            'CEO', 'CFO', 'COO', 'CTO', 'CIO', 'CMO', 'VP', 'SVP', 'EVP',
            # Financial terms
            'USA', 'GDP', 'CPI', 'FED', 'SEC', 'NYSE', 'NASDAQ', 'DOW', 'SP',
            'PE', 'EPS', 'ROE', 'ROA', 'ROI', 'EBITDA', 'YTD', 'QTD', 'MTD',
            # Tech/AI terms
            'AI', 'ML', 'API', 'LLM', 'GPT', 'AGI', 'NLP', 'IOT',
            # Currencies
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY',
            # Common question words
            'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW', 'WHO', 'WHICH',
            # Common verbs/adjectives
            'THINK', 'ABOUT', 'SHOULD', 'COULD', 'WOULD', 'WILL', 'CAN', 'MAY',
            'GOOD', 'BAD', 'BEST', 'TOP', 'HIGH', 'LOW', 'NEW', 'OLD',
            'GET', 'GIVE', 'TAKE', 'MAKE', 'HAVE', 'HAS', 'HAD', 'WAS', 'WERE',
            'ARE', 'BEEN', 'BEING', 'DOES', 'DID', 'DONE', 'SAY', 'SAID',
            # Time words
            'NOW', 'TODAY', 'WEEK', 'MONTH', 'YEAR', 'DAY', 'TIME',
            # Other common words
            'YOU', 'YOUR', 'THEY', 'THEM', 'THIS', 'THAT', 'THESE', 'THOSE',
            'WITH', 'FROM', 'INTO', 'OVER', 'UNDER', 'AFTER', 'BEFORE',
            'ALL', 'ANY', 'SOME', 'MOST', 'MORE', 'LESS', 'MUCH', 'MANY',
            'OUT', 'OFF', 'DOWN', 'BACK', 'JUST', 'ONLY', 'ALSO', 'VERY',
            'HERE', 'THERE', 'THEN', 'THAN', 'WELL', 'WAY', 'EVEN', 'STILL'
        }
        
        # Combine and deduplicate - prioritize $TICKER format
        all_tickers = list(set(dollar_tickers + [t for t in potential_tickers if t not in exclude]))
        
        # Validate tickers exist (basic check)
        valid_tickers = []
        for ticker in all_tickers[:5]:  # Limit to 5
            try:
                stock = yf.Ticker(ticker)
                if stock.info.get('regularMarketPrice') or stock.info.get('currentPrice'):
                    valid_tickers.append(ticker)
            except:
                continue
        
        return valid_tickers
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        return {"status": "success", "message": "Conversation history cleared"}
    
    def get_quick_analysis(self, symbol: str) -> Dict:
        """Get a quick analysis summary for a symbol."""
        analysis = self._get_comprehensive_analysis(symbol)
        
        # Extract key metrics for quick view
        breakout = analysis.get("engines", {}).get("breakout", {})
        options = analysis.get("engines", {}).get("options", {})
        dark_pool = analysis.get("engines", {}).get("dark_pool", {})
        price = analysis.get("engines", {}).get("price_data", {})
        
        return {
            "symbol": symbol,
            "price": price.get("current_price"),
            "change_1d": price.get("change_1d"),
            "breakout_score": breakout.get("breakout_score"),
            "breakout_probability": breakout.get("breakout_probability"),
            "direction": breakout.get("direction_bias"),
            "options_sentiment": options.get("sentiment"),
            "dark_pool_sentiment": dark_pool.get("dp_sentiment"),
            "signals": breakout.get("active_signals", [])[:5],
            "recommendation": breakout.get("recommendation")
        }


# Test function
if __name__ == "__main__":
    print("Testing Sadie AI...")
    sadie = SadieAI()
    
    # Test symbol extraction
    test_text = "What do you think about $AAPL and NVDA? Should I buy TSLA?"
    symbols = sadie._extract_symbols(test_text)
    print(f"Extracted symbols: {symbols}")
    
    # Test quick analysis
    if symbols:
        quick = sadie.get_quick_analysis(symbols[0])
        print(f"Quick analysis for {symbols[0]}: {quick}")
    
    print("Sadie AI module loaded successfully!")
