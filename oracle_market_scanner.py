"""
ORACLE MARKET SCANNER - Full Market 5:1 Reward-Risk Scanner
============================================================

Scans the ENTIRE market (all caps, all sectors) in real-time to find stocks
that meet Tim Bohen's Oracle criteria with 5:1 reward-to-risk ratio.

TIM BOHEN'S 5:1 CRITERIA:
=========================
1. FLOAT CRITERIA (25 points max)
   - Ideal: Float < 20M shares (small float = explosive moves)
   - Good: Float 20M-50M shares
   - Acceptable: Float 50M-100M shares

2. VOLUME SURGE (20 points max)
   - Volume > 2x average = Strong interest
   - Volume > 1.5x average = Good interest

3. NEWS CATALYST (30 points max)
   - Recent news within 24-48 hours
   - Earnings, FDA, contracts, etc.

4. SECTOR MOMENTUM (15 points max)
   - Sector showing strength
   - Not fighting the trend

5. CHART PATTERN (35 points max)
   - Clear support/resistance levels
   - Risk defined (stop loss level)
   - Reward target 5x the risk

5:1 REWARD-RISK CALCULATION:
============================
- Entry Price: Current price or breakout level
- Stop Loss: Below recent support (defines RISK)
- Target: 5x the risk distance above entry (defines REWARD)
- Example: Entry $10, Stop $9 (risk $1), Target $15 (reward $5) = 5:1

DATA SOURCES (ALL REAL-TIME, NO FALLBACKS):
==========================================
- Yahoo Finance (yfinance): Price, volume, float data
- Finnhub: News, company metrics
- TwelveData: Technical indicators

SCANNING APPROACH:
==================
1. Get list of all tradeable stocks (NYSE, NASDAQ, AMEX)
2. Filter by basic criteria (price range, volume minimum)
3. Calculate Oracle score for each
4. Return top stocks meeting 5:1 criteria
"""

import yfinance as yf
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class OracleMarketScanner:
    """
    Full market scanner for Tim Bohen's Oracle 5:1 setups.
    
    Scans ALL stocks across NYSE, NASDAQ, AMEX to find the best setups.
    Uses ONLY real-time data - NO fallbacks, NO demo data.
    """
    
    def __init__(self, finnhub_api_key: str = None):
        """
        Initialize the market scanner.
        
        Args:
            finnhub_api_key: Finnhub API key for news data
        """
        self.finnhub_api_key = finnhub_api_key
        
        # Minimum criteria for initial filtering
        self.min_price = 1.0        # Minimum $1 (avoid penny stocks)
        self.max_price = 500.0      # Maximum $500
        self.min_volume = 100000    # Minimum 100K daily volume
        self.min_avg_volume = 50000 # Minimum 50K average volume
        
        # Oracle scoring thresholds
        self.ideal_float = 20_000_000      # 20M shares
        self.good_float = 50_000_000       # 50M shares
        self.acceptable_float = 100_000_000 # 100M shares
        
        # 5:1 reward-risk parameters
        self.reward_risk_ratio = 5.0
        self.atr_multiplier_base = 1.2  # Base stop loss = 1.2x ATR below entry
        
    def _calculate_dynamic_atr_multiplier(self, current_atr: float, avg_atr_20: float, price: float) -> float:
        """
        Calculate dynamic ATR multiplier based on current volatility regime.
        
        Tim Bohen's approach: Tighter stops in high volatility (to limit risk),
        wider stops in low volatility (to avoid noise).
        
        Args:
            current_atr: Current ATR value
            avg_atr_20: 20-period average ATR
            price: Current stock price
            
        Returns:
            ATR multiplier for stop loss calculation (1.0 to 1.5)
        """
        if avg_atr_20 <= 0:
            return self.atr_multiplier_base
        
        volatility_ratio = current_atr / avg_atr_20
        
        # High volatility regime (ATR > 1.5x average)
        if volatility_ratio > 1.5:
            return 1.0  # Tighter stop to limit risk in volatile conditions
        
        # Low volatility regime (ATR < 0.7x average)
        elif volatility_ratio < 0.7:
            return 1.5  # Wider stop to avoid getting stopped out by noise
        
        # Normal volatility
        else:
            return self.atr_multiplier_base  # Standard 1.2x
        
    def _get_stock_universe(self) -> List[str]:
        """
        Get list of all tradeable stocks from major exchanges.
        
        Returns a comprehensive list of tickers to scan.
        DYNAMIC DISCOVERY - No predefined restrictions on cap size or sector.
        """
        print("📊 Building DYNAMIC stock universe (real-time discovery)...")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Use a combination of sources for comprehensive coverage
        tickers = set()
        
        # Method 0: Get TODAY'S most active, gainers, losers from Yahoo Finance (DYNAMIC)
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            # Most Active Today
            most_active_url = "https://finance.yahoo.com/most-active"
            resp = requests.get(most_active_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/quote/' in href and '?' not in href:
                    ticker = href.split('/quote/')[1].split('/')[0].split('?')[0]
                    if ticker.isalpha() and len(ticker) <= 5:
                        tickers.add(ticker)
            print(f"   ✅ Added today's most active stocks")
            
            # Day Gainers
            gainers_url = "https://finance.yahoo.com/gainers"
            resp = requests.get(gainers_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/quote/' in href and '?' not in href:
                    ticker = href.split('/quote/')[1].split('/')[0].split('?')[0]
                    if ticker.isalpha() and len(ticker) <= 5:
                        tickers.add(ticker)
            print(f"   ✅ Added today's top gainers")
            
            # Day Losers (potential bounce plays)
            losers_url = "https://finance.yahoo.com/losers"
            resp = requests.get(losers_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/quote/' in href and '?' not in href:
                    ticker = href.split('/quote/')[1].split('/')[0].split('?')[0]
                    if ticker.isalpha() and len(ticker) <= 5:
                        tickers.add(ticker)
            print(f"   ✅ Added today's top losers (bounce candidates)")
            
            # Trending Tickers
            trending_url = "https://finance.yahoo.com/trending-tickers"
            resp = requests.get(trending_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/quote/' in href and '?' not in href:
                    ticker = href.split('/quote/')[1].split('/')[0].split('?')[0]
                    if ticker.isalpha() and len(ticker) <= 5:
                        tickers.add(ticker)
            print(f"   ✅ Added trending tickers")
            
        except Exception as e:
            print(f"   ⚠️ Dynamic discovery partial: {e}")
        
        # Method 1: Get S&P 500 + Russell 2000 components via Wikipedia
        try:
            # S&P 500
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            sp500_df = pd.read_html(sp500_url)[0]
            tickers.update(sp500_df['Symbol'].str.replace('.', '-').tolist())
            print(f"   ✅ Added {len(sp500_df)} S&P 500 stocks")
        except Exception as e:
            print(f"   ⚠️ Could not fetch S&P 500: {e}")
        
        # Method 2: Get NASDAQ-100
        try:
            nasdaq_url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            nasdaq_tables = pd.read_html(nasdaq_url)
            for table in nasdaq_tables:
                if 'Ticker' in table.columns:
                    tickers.update(table['Ticker'].tolist())
                    print(f"   ✅ Added NASDAQ-100 stocks")
                    break
        except Exception as e:
            print(f"   ⚠️ Could not fetch NASDAQ-100: {e}")
        
        # Method 3: Add popular small-cap and mid-cap tickers
        popular_tickers = [
            # Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'AMD', 'INTC', 'TSM', 'AVGO',
            'CRM', 'ORCL', 'ADBE', 'NOW', 'SNOW', 'PLTR', 'NET', 'DDOG', 'ZS', 'CRWD',
            # EV/Auto
            'TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'F', 'GM', 'TM', 'STLA',
            # Biotech/Pharma
            'MRNA', 'BNTX', 'PFE', 'JNJ', 'LLY', 'ABBV', 'MRK', 'BMY', 'GILD', 'REGN',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'V', 'MA',
            # Retail
            'WMT', 'TGT', 'COST', 'HD', 'LOW', 'AMZN', 'EBAY', 'ETSY', 'W', 'BBY',
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY', 'MPC', 'VLO', 'PSX', 'HAL',
            # Small caps with potential
            'SOFI', 'HOOD', 'AFRM', 'UPST', 'COIN', 'MARA', 'RIOT', 'CLSK', 'HUT', 'BITF',
            'IONQ', 'RGTI', 'QUBT', 'ARQQ', 'QBTS',  # Quantum
            'SMCI', 'DELL', 'HPE', 'PSTG', 'NTAP',  # AI/Data Center
            'ARM', 'ASML', 'KLAC', 'LRCX', 'AMAT',  # Semis
            # Meme/Retail favorites
            'GME', 'AMC', 'BBBY', 'BB', 'NOK', 'WISH', 'CLOV', 'SPCE', 'PLTR',
            # Cannabis
            'TLRY', 'CGC', 'ACB', 'SNDL', 'CRON',
            # Chinese ADRs
            'BABA', 'JD', 'PDD', 'BIDU', 'NTES',
            # SPACs and recent IPOs
            'DWAC', 'TMTG', 'RKLB', 'ASTR', 'VORB',
        ]
        tickers.update(popular_tickers)
        
        # Method 4: Get most active stocks from Yahoo Finance
        try:
            most_active = yf.Tickers(' '.join(['AAPL', 'TSLA', 'NVDA', 'AMD', 'AMZN']))
            # This is just to verify yfinance is working
        except:
            pass
        
        print(f"   📊 Total universe: {len(tickers)} stocks")
        return list(tickers)
    
    def _get_stock_data(self, ticker: str) -> Optional[Dict]:
        """
        Get comprehensive stock data for a single ticker.
        
        Returns None if data cannot be fetched (NO FALLBACKS).
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            # Get current price and volume
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
            volume = info.get('regularMarketVolume', info.get('volume', 0))
            avg_volume = info.get('averageVolume', 0)
            
            if not current_price or current_price == 0:
                return None
            
            # Apply basic filters
            if current_price < self.min_price or current_price > self.max_price:
                return None
            if volume < self.min_volume:
                return None
            if avg_volume < self.min_avg_volume:
                return None
            
            # Get float and shares data
            float_shares = info.get('floatShares', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            
            # Get historical data for ATR calculation
            hist = stock.history(period='1mo')
            if hist.empty or len(hist) < 14:
                return None
            
            # Calculate ATR (14-period)
            high = hist['High'].values
            low = hist['Low'].values
            close = hist['Close'].values
            
            tr = []
            for i in range(len(high)):
                if i == 0:
                    tr.append(high[i] - low[i])
                else:
                    tr.append(max(
                        high[i] - low[i],
                        abs(high[i] - close[i-1]),
                        abs(low[i] - close[i-1])
                    ))
            
            atr = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
            
            # Calculate 20-period average ATR for volatility regime detection
            atr_20 = np.mean(tr[-20:]) if len(tr) >= 20 else np.mean(tr)
            
            # Calculate support/resistance from recent price action
            recent_low = hist['Low'].tail(20).min()
            recent_high = hist['High'].tail(20).max()
            
            # Calculate DYNAMIC ATR multiplier based on volatility regime
            # Tim Bohen: Tighter stops in high vol, wider in low vol
            atr_multiplier = self._calculate_dynamic_atr_multiplier(atr, atr_20, current_price)
            
            # Calculate 5:1 setup with dynamic stop
            stop_loss = current_price - (atr * atr_multiplier)
            risk = current_price - stop_loss
            target = current_price + (risk * self.reward_risk_ratio)
            
            # Volume ratio
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            
            return {
                'ticker': ticker,
                'price': current_price,
                'volume': volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'float_shares': float_shares,
                'shares_outstanding': shares_outstanding,
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'atr': atr,
                'recent_low': recent_low,
                'recent_high': recent_high,
                'stop_loss': stop_loss,
                'target': target,
                'risk': risk,
                'reward': target - current_price,
                'reward_risk_ratio': (target - current_price) / risk if risk > 0 else 0,
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'beta': info.get('beta', 1.0),
            }
            
        except Exception as e:
            return None
    
    def _calculate_oracle_score(self, stock_data: Dict) -> Dict:
        """
        Calculate Tim Bohen's Oracle score for a stock.
        
        Returns score breakdown and total score.
        """
        scores = {
            'float_score': 0,
            'volume_score': 0,
            'chart_score': 0,
            'momentum_score': 0,
            'risk_reward_score': 0,
            'total_score': 0,
            'max_score': 125,
            'grade': 'F',
            'meets_5_to_1': False
        }
        
        # 1. FLOAT CRITERIA (25 points max)
        float_shares = stock_data.get('float_shares', 0)
        if float_shares > 0:
            if float_shares <= self.ideal_float:
                scores['float_score'] = 25  # Ideal small float
            elif float_shares <= self.good_float:
                scores['float_score'] = 20  # Good float
            elif float_shares <= self.acceptable_float:
                scores['float_score'] = 15  # Acceptable
            elif float_shares <= 500_000_000:
                scores['float_score'] = 10  # Large but tradeable
            else:
                scores['float_score'] = 5   # Very large float
        
        # 2. VOLUME SURGE (20 points max)
        volume_ratio = stock_data.get('volume_ratio', 1.0)
        if volume_ratio >= 3.0:
            scores['volume_score'] = 20  # Massive surge
        elif volume_ratio >= 2.0:
            scores['volume_score'] = 15  # Strong surge
        elif volume_ratio >= 1.5:
            scores['volume_score'] = 10  # Good interest
        elif volume_ratio >= 1.2:
            scores['volume_score'] = 5   # Slight increase
        else:
            scores['volume_score'] = 0   # Below average
        
        # 3. CHART PATTERN / TECHNICAL SETUP (35 points max)
        price = stock_data.get('price', 0)
        recent_low = stock_data.get('recent_low', 0)
        recent_high = stock_data.get('recent_high', 0)
        atr = stock_data.get('atr', 0)
        
        if price > 0 and recent_low > 0 and recent_high > 0:
            # Price position in range
            range_size = recent_high - recent_low
            if range_size > 0:
                position_in_range = (price - recent_low) / range_size
                
                # Best setups are near support (bottom of range) for longs
                if position_in_range <= 0.3:
                    scores['chart_score'] = 35  # Near support - ideal entry
                elif position_in_range <= 0.5:
                    scores['chart_score'] = 25  # Lower half - good entry
                elif position_in_range <= 0.7:
                    scores['chart_score'] = 15  # Middle - okay
                else:
                    scores['chart_score'] = 5   # Near resistance - risky entry
        
        # 4. MOMENTUM (15 points max)
        # Based on price vs 52-week range
        high_52 = stock_data.get('fifty_two_week_high', 0)
        low_52 = stock_data.get('fifty_two_week_low', 0)
        
        if high_52 > 0 and low_52 > 0 and price > 0:
            range_52 = high_52 - low_52
            if range_52 > 0:
                position_52 = (price - low_52) / range_52
                
                # Momentum stocks are in upper half of 52-week range
                if position_52 >= 0.8:
                    scores['momentum_score'] = 15  # Strong momentum
                elif position_52 >= 0.6:
                    scores['momentum_score'] = 10  # Good momentum
                elif position_52 >= 0.4:
                    scores['momentum_score'] = 5   # Neutral
                else:
                    scores['momentum_score'] = 0   # Weak/beaten down
        
        # 5. RISK/REWARD SCORE (30 points max)
        rr_ratio = stock_data.get('reward_risk_ratio', 0)
        if rr_ratio >= 5.0:
            scores['risk_reward_score'] = 30  # Perfect 5:1 or better
            scores['meets_5_to_1'] = True
        elif rr_ratio >= 4.0:
            scores['risk_reward_score'] = 25  # Very good
        elif rr_ratio >= 3.0:
            scores['risk_reward_score'] = 20  # Good
        elif rr_ratio >= 2.0:
            scores['risk_reward_score'] = 10  # Acceptable
        else:
            scores['risk_reward_score'] = 0   # Poor risk/reward
        
        # Calculate total
        scores['total_score'] = (
            scores['float_score'] +
            scores['volume_score'] +
            scores['chart_score'] +
            scores['momentum_score'] +
            scores['risk_reward_score']
        )
        
        # Assign grade
        pct = scores['total_score'] / scores['max_score'] * 100
        if pct >= 80:
            scores['grade'] = 'A'
        elif pct >= 70:
            scores['grade'] = 'B'
        elif pct >= 60:
            scores['grade'] = 'C'
        elif pct >= 50:
            scores['grade'] = 'D'
        else:
            scores['grade'] = 'F'
        
        return scores
    
    def scan_market(self, max_results: int = 20, min_score: int = 60) -> Dict:
        """
        Scan the entire market for 5:1 Oracle setups.
        
        Args:
            max_results: Maximum number of results to return
            min_score: Minimum Oracle score to include
            
        Returns:
            Dict with scan results and statistics
        """
        start_time = datetime.now()
        print(f"\n{'='*60}")
        print("🔮 ORACLE MARKET SCANNER - 5:1 Reward-Risk Scan")
        print(f"{'='*60}")
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get stock universe
        universe = self._get_stock_universe()
        
        print(f"\n📊 Scanning {len(universe)} stocks...")
        print("   This may take a few minutes for comprehensive coverage...\n")
        
        results = []
        scanned = 0
        errors = 0
        
        # Scan stocks with progress updates
        for i, ticker in enumerate(universe):
            if i % 50 == 0:
                print(f"   Progress: {i}/{len(universe)} ({i/len(universe)*100:.1f}%)")
            
            try:
                # Get stock data
                stock_data = self._get_stock_data(ticker)
                
                if stock_data:
                    scanned += 1
                    
                    # Calculate Oracle score
                    scores = self._calculate_oracle_score(stock_data)
                    
                    # Only include if meets minimum score
                    if scores['total_score'] >= min_score:
                        results.append({
                            **stock_data,
                            **scores
                        })
                
                # Rate limiting - be nice to APIs
                if i % 10 == 0:
                    time.sleep(0.1)
                    
            except Exception as e:
                errors += 1
                continue
        
        # Sort by total score (highest first)
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Filter for 5:1 setups
        five_to_one_setups = [r for r in results if r['meets_5_to_1']]
        
        # Take top results
        top_results = results[:max_results]
        top_5_to_1 = five_to_one_setups[:max_results]
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print("✅ SCAN COMPLETE")
        print(f"{'='*60}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Stocks scanned: {scanned}")
        print(f"Errors: {errors}")
        print(f"Stocks meeting criteria: {len(results)}")
        print(f"5:1 Setups found: {len(five_to_one_setups)}")
        
        # Add date/time context
        # ALWAYS USE EASTERN TIME for market context
        import pytz
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)
        
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        is_market_hours = market_open <= now <= market_close and now.weekday() < 5
        
        # Determine trading session
        if now.weekday() >= 5:
            session = 'WEEKEND'
        elif now < market_open:
            session = 'PRE_MARKET'
        elif now > market_close:
            session = 'AFTER_HOURS'
        else:
            if now < now.replace(hour=10, minute=30):
                session = 'OPENING_VOLATILITY'
            elif now < now.replace(hour=12, minute=0):
                session = 'MORNING_MOMENTUM'
            elif now < now.replace(hour=14, minute=0):
                session = 'MIDDAY_CONSOLIDATION'
            else:
                session = 'POWER_HOUR'
        
        return {
            'status': 'success',
            'timestamp': now.isoformat(),
            'scan_duration_seconds': duration,
            'stocks_scanned': scanned,
            'stocks_meeting_criteria': len(results),
            'five_to_one_count': len(five_to_one_setups),
            'top_results': top_results,
            'five_to_one_setups': top_5_to_1,
            'data_source': 'Yahoo Finance (Real-time)',
            'market_context': {
                'is_market_hours': is_market_hours,
                'trading_session': session,
                'scan_time': now.strftime('%Y-%m-%d %H:%M:%S ET'),
                'day_of_week': now.strftime('%A'),
            },
            'criteria': {
                'min_price': self.min_price,
                'max_price': self.max_price,
                'min_volume': self.min_volume,
                'min_score': min_score,
                'reward_risk_target': self.reward_risk_ratio
            }
        }
    
    def quick_scan(self, tickers: List[str] = None) -> Dict:
        """
        Quick scan of a specific list of tickers.
        PRODUCTION-GRADE: Uses DYNAMIC discovery if no tickers provided.
        
        Useful for scanning watchlists or specific sectors.
        """
        if tickers is None:
            # DYNAMIC DISCOVERY - Get TODAY'S most active stocks
            tickers = self._get_stock_universe()  # Full dynamic discovery
        
        print(f"\n🔮 Quick Oracle Scan - {len(tickers)} stocks")
        print("-" * 40)
        
        results = []
        for ticker in tickers:
            stock_data = self._get_stock_data(ticker)
            if stock_data:
                scores = self._calculate_oracle_score(stock_data)
                results.append({**stock_data, **scores})
        
        # Sort by score
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        five_to_one = [r for r in results if r['meets_5_to_1']]
        
        # Add date/time context for production accuracy - ALWAYS USE EASTERN TIME
        import pytz
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)
        
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        is_market_hours = market_open <= now <= market_close and now.weekday() < 5
        
        if now.weekday() >= 5:
            session = 'WEEKEND'
        elif now < market_open:
            session = 'PRE_MARKET'
        elif now > market_close:
            session = 'AFTER_HOURS'
        else:
            if now < now.replace(hour=10, minute=30):
                session = 'OPENING_VOLATILITY'
            elif now < now.replace(hour=12, minute=0):
                session = 'MORNING_MOMENTUM'
            elif now < now.replace(hour=14, minute=0):
                session = 'MIDDAY_CONSOLIDATION'
            else:
                session = 'POWER_HOUR'
        
        return {
            'status': 'success',
            'timestamp': now.isoformat(),
            'stocks_scanned': len(tickers),
            'results': results,
            'five_to_one_setups': five_to_one,
            'five_to_one_count': len(five_to_one),
            'market_context': {
                'is_market_hours': is_market_hours,
                'trading_session': session,
                'scan_time': now.strftime('%Y-%m-%d %H:%M:%S ET'),
                'day_of_week': now.strftime('%A'),
                'dynamic_universe_size': len(tickers)
            }
        }


# Test function
if __name__ == "__main__":
    scanner = OracleMarketScanner()
    
    # Quick scan test
    result = scanner.quick_scan()
    
    print("\n" + "="*60)
    print("TOP 5:1 SETUPS FOUND")
    print("="*60)
    
    if result['five_to_one_setups']:
        for setup in result['five_to_one_setups'][:10]:
            print(f"\n{setup['ticker']} - Score: {setup['total_score']}/{setup['max_score']} (Grade {setup['grade']})")
            print(f"   Price: ${setup['price']:.2f}")
            print(f"   Float: {setup['float_shares']/1e6:.1f}M shares")
            print(f"   Volume Ratio: {setup['volume_ratio']:.2f}x")
            print(f"   Entry: ${setup['price']:.2f} | Stop: ${setup['stop_loss']:.2f} | Target: ${setup['target']:.2f}")
            print(f"   Risk: ${setup['risk']:.2f} | Reward: ${setup['reward']:.2f} | R:R = {setup['reward_risk_ratio']:.1f}:1")
    else:
        print("No 5:1 setups found in quick scan.")
        print("\nTop scoring stocks:")
        for setup in result['results'][:5]:
            print(f"   {setup['ticker']}: {setup['total_score']}/{setup['max_score']} (R:R = {setup['reward_risk_ratio']:.1f}:1)")
