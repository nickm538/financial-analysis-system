"""
ORACLE NEWS CATALYST SCANNER
==============================
Tim Bohen's High-Impact Keyword Detection System.

Scans news for catalysts that historically precede explosive moves:
- FDA approval/breakthrough
- Partnership/acquisition
- Patent/settlement
- Restructuring/debt payoff
- Earnings beat

Each keyword weighted by historical price impact.

For real-money trading - Maximum accuracy.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class OracleNews:
    """
    Oracle News Catalyst Scanner
    
    Scans and scores news based on Tim Bohen's high-impact keywords.
    Identifies catalysts that algorithms react to at 8:00 AM EST.
    """
    
    def __init__(self, finnhub_api_key: str):
        """
        Initialize Oracle News Scanner.
        
        Args:
            finnhub_api_key: Finnhub API key for news data
        """
        self.finnhub_api_key = finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"
        
        # Tim Bohen's High-Impact Keywords (weighted by price impact)
        self.KEYWORDS = {
            # FDA & Regulatory (Highest Impact)
            'FDA approval': 30,
            'FDA': 25,
            'approval': 20,
            'breakthrough': 25,
            'clinical trial': 15,
            'phase 3': 20,
            'phase 2': 15,
            
            # Corporate Actions (High Impact)
            'acquisition': 25,
            'merger': 25,
            'partnership': 20,
            'joint venture': 18,
            'strategic alliance': 15,
            'collaboration': 12,
            
            # Financial (High Impact)
            'earnings beat': 20,
            'revenue beat': 18,
            'guidance raise': 20,
            'debt payoff': 15,
            'restructuring': 10,
            'refinancing': 12,
            
            # Legal & IP (Medium-High Impact)
            'patent': 15,
            'settlement': 15,
            'lawsuit won': 18,
            'patent granted': 18,
            'intellectual property': 12,
            
            # Contracts & Business (Medium Impact)
            'contract': 15,
            'government contract': 20,
            'major contract': 18,
            'supply agreement': 12,
            'distribution agreement': 12,
            
            # Product & Technology (Medium Impact)
            'product launch': 15,
            'new product': 12,
            'innovation': 10,
            'technology': 8,
            'breakthrough technology': 20,
            
            # Analyst Actions (Low-Medium Impact)
            'upgrade': 10,
            'price target raised': 12,
            'analyst upgrade': 10,
            'buy rating': 8,
            
            # Insider Activity (Low-Medium Impact)
            'insider buying': 10,
            'share buyback': 12,
            'stock repurchase': 12
        }
        
        # Negative keywords (reduce score)
        self.NEGATIVE_KEYWORDS = {
            'downgrade': -10,
            'lawsuit': -8,
            'investigation': -12,
            'recall': -15,
            'warning': -8,
            'delay': -10,
            'failure': -12,
            'rejected': -15,
            'denied': -12
        }
    
    def scan_news(self, ticker: str, days_back: int = 7) -> Dict:
        """
        Scan news for high-impact catalysts.
        
        Args:
            ticker: Stock symbol
            days_back: Number of days to look back
        
        Returns:
            Dict with news analysis and catalyst score
        """
        try:
            # Fetch news from Finnhub
            news_items = self._fetch_finnhub_news(ticker, days_back)
            
            if not news_items:
                return self._empty_news_result(ticker)
            
            # Score each news item
            scored_news = []
            for item in news_items:
                score = self._score_news_item(item)
                if score['total_score'] > 0:  # Only include positive catalysts
                    scored_news.append(score)
            
            # Sort by score (descending)
            scored_news.sort(key=lambda x: x['total_score'], reverse=True)
            
            # Calculate aggregate catalyst score
            if scored_news:
                max_score = scored_news[0]['total_score']
                avg_score = sum(item['total_score'] for item in scored_news) / len(scored_news)
                catalyst_count = len(scored_news)
            else:
                max_score = 0
                avg_score = 0
                catalyst_count = 0
            
            # Determine catalyst grade
            grade, quality = self._grade_catalyst(max_score)
            
            return {
                'ticker': ticker,
                'catalyst_score': max_score,
                'average_score': round(avg_score, 1),
                'catalyst_count': catalyst_count,
                'grade': grade,
                'quality': quality,
                'has_catalyst': max_score >= 15,  # Minimum threshold
                'top_catalysts': scored_news[:5],  # Top 5 news items
                'all_news': scored_news,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error scanning news for {ticker}: {e}")
            return self._empty_news_result(ticker, error=str(e))
    
    def _fetch_finnhub_news(self, ticker: str, days_back: int) -> List[Dict]:
        """
        Fetch news from Finnhub API.
        
        Args:
            ticker: Stock symbol
            days_back: Number of days to look back
        
        Returns:
            List of news items
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format dates for API
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Build URL
            url = f"{self.base_url}/company-news"
            params = {
                'symbol': ticker,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_api_key
            }
            
            # Make request
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                news_data = response.json()
                return news_data if isinstance(news_data, list) else []
            else:
                print(f"⚠️ Finnhub news API returned status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"⚠️ Error fetching Finnhub news: {e}")
            return []
    
    def _score_news_item(self, news_item: Dict) -> Dict:
        """
        Score a single news item based on keywords.
        
        Args:
            news_item: News item dict with 'headline' and 'summary'
        
        Returns:
            Dict with scored news item
        """
        headline = str(news_item.get('headline', '')).lower()
        summary = str(news_item.get('summary', '')).lower()
        text = f"{headline} {summary}"
        
        # Score positive keywords
        positive_score = 0
        matched_keywords = []
        
        for keyword, points in self.KEYWORDS.items():
            if keyword.lower() in text:
                positive_score += points
                matched_keywords.append({
                    'keyword': keyword,
                    'points': points
                })
        
        # Score negative keywords
        negative_score = 0
        negative_keywords = []
        
        for keyword, points in self.NEGATIVE_KEYWORDS.items():
            if keyword.lower() in text:
                negative_score += points  # Points are already negative
                negative_keywords.append({
                    'keyword': keyword,
                    'points': points
                })
        
        # Calculate total score
        total_score = positive_score + negative_score
        
        # Determine sentiment
        if total_score >= 20:
            sentiment = "VERY_BULLISH"
        elif total_score >= 10:
            sentiment = "BULLISH"
        elif total_score > 0:
            sentiment = "SLIGHTLY_BULLISH"
        elif total_score == 0:
            sentiment = "NEUTRAL"
        elif total_score >= -10:
            sentiment = "SLIGHTLY_BEARISH"
        else:
            sentiment = "BEARISH"
        
        return {
            'headline': news_item.get('headline', 'N/A'),
            'summary': news_item.get('summary', 'N/A')[:200],  # Truncate
            'datetime': news_item.get('datetime', 0),
            'source': news_item.get('source', 'Unknown'),
            'url': news_item.get('url', ''),
            'total_score': total_score,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'sentiment': sentiment,
            'matched_keywords': matched_keywords,
            'negative_keywords': negative_keywords
        }
    
    def _grade_catalyst(self, score: int) -> Tuple[str, str]:
        """
        Grade catalyst based on score.
        
        Args:
            score: Catalyst score
        
        Returns:
            Tuple of (grade, quality)
        """
        if score >= 50:
            return ("A+", "EXCEPTIONAL")
        elif score >= 35:
            return ("A", "EXCELLENT")
        elif score >= 25:
            return ("A-", "STRONG")
        elif score >= 15:
            return ("B+", "GOOD")
        elif score >= 10:
            return ("B", "FAIR")
        else:
            return ("C", "WEAK")
    
    def _empty_news_result(self, ticker: str, error: Optional[str] = None) -> Dict:
        """Return empty news result"""
        result = {
            'ticker': ticker,
            'catalyst_score': 0,
            'average_score': 0,
            'catalyst_count': 0,
            'grade': 'N/A',
            'quality': 'NO_NEWS',
            'has_catalyst': False,
            'top_catalysts': [],
            'all_news': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if error:
            result['error'] = error
        
        return result
    
    def check_premarket_catalysts(self, ticker: str) -> Dict:
        """
        Check for pre-market catalysts (8:00 AM EST scan).
        
        Tim Bohen's Rule: Algorithmic traders scan press releases at 8 AM
        for keywords. This creates information asymmetry and buying pressure.
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Dict with pre-market catalyst analysis
        """
        try:
            # Scan last 24 hours only (pre-market focus)
            news_result = self.scan_news(ticker, days_back=1)
            
            # Check if news is recent (last 24 hours)
            recent_catalysts = []
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for catalyst in news_result.get('all_news', []):
                news_time = datetime.fromtimestamp(catalyst.get('datetime', 0))
                if news_time >= cutoff_time:
                    recent_catalysts.append(catalyst)
            
            # Determine pre-market status
            has_premarket_catalyst = len(recent_catalysts) > 0
            
            if has_premarket_catalyst:
                max_score = max(c['total_score'] for c in recent_catalysts)
                status = "ACTIVE_CATALYST"
                signal = "🚀 POTENTIAL GAP UP"
            else:
                max_score = 0
                status = "NO_CATALYST"
                signal = "⚪ NO PRE-MARKET NEWS"
            
            return {
                'ticker': ticker,
                'has_premarket_catalyst': has_premarket_catalyst,
                'catalyst_score': max_score,
                'recent_catalyst_count': len(recent_catalysts),
                'status': status,
                'signal': signal,
                'recent_catalysts': recent_catalysts[:3],  # Top 3
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error checking pre-market catalysts for {ticker}: {e}")
            return {
                'ticker': ticker,
                'has_premarket_catalyst': False,
                'error': str(e)
            }
    
    def scan_sector_momentum(self, sector_tickers: List[str]) -> Dict:
        """
        Scan multiple stocks in a sector for catalyst momentum.
        
        Tim Bohen's Rule: Stock must be in a "hot" sector with multiple runners.
        
        Args:
            sector_tickers: List of ticker symbols in the sector
        
        Returns:
            Dict with sector momentum analysis
        """
        try:
            sector_scores = []
            
            for ticker in sector_tickers:
                news_result = self.scan_news(ticker, days_back=3)
                if news_result['has_catalyst']:
                    sector_scores.append({
                        'ticker': ticker,
                        'score': news_result['catalyst_score']
                    })
            
            # Calculate sector momentum
            if sector_scores:
                avg_score = sum(s['score'] for s in sector_scores) / len(sector_scores)
                hot_stock_count = len(sector_scores)
                momentum = min(hot_stock_count / len(sector_tickers), 1.0)  # 0-1 scale
            else:
                avg_score = 0
                hot_stock_count = 0
                momentum = 0.0
            
            # Determine sector status
            if momentum >= 0.7:
                status = "HOT_SECTOR"
                signal = "🔥 MULTIPLE RUNNERS"
            elif momentum >= 0.4:
                status = "WARMING_UP"
                signal = "🟡 SOME ACTIVITY"
            else:
                status = "COLD_SECTOR"
                signal = "❄️ LOW ACTIVITY"
            
            return {
                'sector_momentum': round(momentum, 2),
                'average_catalyst_score': round(avg_score, 1),
                'hot_stock_count': hot_stock_count,
                'total_stocks_scanned': len(sector_tickers),
                'status': status,
                'signal': signal,
                'hot_stocks': sorted(sector_scores, key=lambda x: x['score'], reverse=True),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error scanning sector momentum: {e}")
            return {
                'sector_momentum': 0.0,
                'error': str(e)
            }
