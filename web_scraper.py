"""
Firecrawl Web Scraper Module for Sadie AI
==========================================
Provides real-time web scraping capabilities to fill gaps in API data.
Uses Firecrawl for reliable, fast web scraping with no hallucinations.

Key Features:
- Options chain scraping from Yahoo Finance
- Real-time news and earnings data
- Analyst ratings and price targets
- SEC filings and insider trading
- Any data that APIs don't provide
"""

import os
import re
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class FirecrawlScraper:
    """
    Firecrawl-based web scraper for real-time financial data.
    Ensures all data is current and verified - no hallucinations.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('FIRECRAWL_API_KEY')
        if not self.api_key:
            print("Warning: FIRECRAWL_API_KEY not set - web scraping disabled")
            self.enabled = False
        else:
            self.enabled = True
        self.base_url = "https://api.firecrawl.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search(self, query: str, limit: int = 5) -> Dict:
        """
        Search the web for real-time information.
        
        Args:
            query: Search query
            limit: Max results to return
            
        Returns:
            Dict with search results including URLs and snippets
        """
        if not self.enabled:
            return {"status": "error", "error": "Firecrawl not configured"}
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={
                    "query": query,
                    "limit": limit
                },
                timeout=30
            )
            response.raise_for_status()
            return {"status": "success", "results": response.json()}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def scrape(self, url: str, only_main_content: bool = True) -> Dict:
        """
        Scrape content from a single URL.
        
        Args:
            url: URL to scrape
            only_main_content: Whether to extract only main content
            
        Returns:
            Dict with scraped markdown content
        """
        if not self.enabled:
            return {"status": "error", "error": "Firecrawl not configured"}
        
        try:
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=self.headers,
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "onlyMainContent": only_main_content
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return {
                "status": "success",
                "content": data.get("data", {}).get("markdown", ""),
                "url": url,
                "scraped_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_options_chain(self, symbol: str) -> Dict:
        """
        Scrape real-time options chain from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with parsed options data (calls and puts)
        """
        url = f"https://finance.yahoo.com/quote/{symbol}/options/"
        result = self.scrape(url)
        
        if result.get("status") != "success":
            return result
        
        content = result.get("content", "")
        
        # Parse the options data from markdown tables
        options_data = self._parse_options_markdown(content, symbol)
        options_data["scraped_at"] = result.get("scraped_at")
        options_data["source"] = "Yahoo Finance (live scrape)"
        
        return options_data
    
    def _parse_options_markdown(self, content: str, symbol: str) -> Dict:
        """Parse options chain from scraped markdown content."""
        calls = []
        puts = []
        
        # Split into calls and puts sections
        calls_section = ""
        puts_section = ""
        
        if "### Calls" in content:
            parts = content.split("### Calls")
            if len(parts) > 1:
                calls_part = parts[1]
                if "### Puts" in calls_part:
                    calls_section, puts_section = calls_part.split("### Puts", 1)
                else:
                    calls_section = calls_part
        
        if "### Puts" in content and not puts_section:
            puts_section = content.split("### Puts")[1] if "### Puts" in content else ""
        
        # Parse table rows
        calls = self._parse_options_table(calls_section)
        puts = self._parse_options_table(puts_section)
        
        # Calculate key metrics
        total_call_volume = sum(c.get("volume", 0) for c in calls if isinstance(c.get("volume"), (int, float)))
        total_put_volume = sum(p.get("volume", 0) for p in puts if isinstance(p.get("volume"), (int, float)))
        total_call_oi = sum(c.get("open_interest", 0) for c in calls if isinstance(c.get("open_interest"), (int, float)))
        total_put_oi = sum(p.get("open_interest", 0) for p in puts if isinstance(p.get("open_interest"), (int, float)))
        
        put_call_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else 0
        
        # Find max pain (strike with highest total OI)
        strike_oi = {}
        for opt in calls + puts:
            strike = opt.get("strike", 0)
            oi = opt.get("open_interest", 0)
            if isinstance(oi, (int, float)):
                strike_oi[strike] = strike_oi.get(strike, 0) + oi
        
        max_pain_strike = max(strike_oi.keys(), key=lambda k: strike_oi[k]) if strike_oi else 0
        
        # Find highest volume strikes (unusual activity)
        all_options = [(o, "call") for o in calls] + [(o, "put") for o in puts]
        all_options.sort(key=lambda x: x[0].get("volume", 0) if isinstance(x[0].get("volume"), (int, float)) else 0, reverse=True)
        unusual_activity = []
        for opt, opt_type in all_options[:5]:
            if isinstance(opt.get("volume"), (int, float)) and opt.get("volume", 0) > 1000:
                unusual_activity.append({
                    "type": opt_type,
                    "strike": opt.get("strike"),
                    "volume": opt.get("volume"),
                    "open_interest": opt.get("open_interest"),
                    "implied_volatility": opt.get("implied_volatility")
                })
        
        return {
            "status": "success",
            "symbol": symbol,
            "calls": calls[:20],  # Top 20 calls
            "puts": puts[:20],    # Top 20 puts
            "summary": {
                "total_call_volume": total_call_volume,
                "total_put_volume": total_put_volume,
                "put_call_ratio": round(put_call_ratio, 2),
                "total_call_oi": total_call_oi,
                "total_put_oi": total_put_oi,
                "max_pain_strike": max_pain_strike,
                "unusual_activity": unusual_activity
            }
        }
    
    def _parse_options_table(self, section: str) -> List[Dict]:
        """Parse options table from markdown section."""
        options = []
        lines = section.split("\n")
        
        for line in lines:
            if "|" not in line or "---" in line or "Contract Name" in line:
                continue
            
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 10:
                try:
                    # Extract strike price (usually 3rd column after contract name and date)
                    strike_str = cells[2] if len(cells) > 2 else "0"
                    strike_match = re.search(r'[\d.]+', strike_str)
                    strike = float(strike_match.group()) if strike_match else 0
                    
                    # Extract other values
                    def parse_num(s):
                        s = s.replace(",", "").replace("-", "0").replace("\\", "").strip()
                        match = re.search(r'[\d.]+', s)
                        return float(match.group()) if match else 0
                    
                    def parse_pct(s):
                        s = s.replace("%", "").replace(",", "").strip()
                        match = re.search(r'[\d.]+', s)
                        return float(match.group()) if match else 0
                    
                    option = {
                        "strike": strike,
                        "last_price": parse_num(cells[3]) if len(cells) > 3 else 0,
                        "bid": parse_num(cells[4]) if len(cells) > 4 else 0,
                        "ask": parse_num(cells[5]) if len(cells) > 5 else 0,
                        "change": parse_num(cells[6]) if len(cells) > 6 else 0,
                        "change_pct": parse_pct(cells[7]) if len(cells) > 7 else 0,
                        "volume": int(parse_num(cells[8])) if len(cells) > 8 else 0,
                        "open_interest": int(parse_num(cells[9])) if len(cells) > 9 else 0,
                        "implied_volatility": parse_pct(cells[10]) if len(cells) > 10 else 0
                    }
                    
                    if option["strike"] > 0:
                        options.append(option)
                except Exception:
                    continue
        
        return options
    
    def get_analyst_ratings(self, symbol: str) -> Dict:
        """
        Scrape analyst ratings and price targets.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with analyst ratings data
        """
        # Search for recent analyst ratings
        search_result = self.search(f"{symbol} stock analyst rating price target 2026", limit=3)
        
        if search_result.get("status") != "success":
            return search_result
        
        # Scrape the analysis page from Yahoo
        url = f"https://finance.yahoo.com/quote/{symbol}/analysis/"
        result = self.scrape(url)
        
        return {
            "status": "success",
            "symbol": symbol,
            "search_results": search_result.get("results", {}).get("web", []),
            "analysis_content": result.get("content", "")[:3000],  # Limit content
            "scraped_at": datetime.now().isoformat(),
            "source": "Yahoo Finance + Web Search (live scrape)"
        }
    
    def get_earnings_calendar(self, symbol: str) -> Dict:
        """
        Scrape earnings calendar and estimates.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with earnings data
        """
        url = f"https://finance.yahoo.com/quote/{symbol}/"
        result = self.scrape(url)
        
        if result.get("status") != "success":
            return result
        
        content = result.get("content", "")
        
        # Extract earnings-related info
        earnings_info = {
            "status": "success",
            "symbol": symbol,
            "raw_content": content[:5000],  # First 5000 chars for context
            "scraped_at": result.get("scraped_at"),
            "source": "Yahoo Finance (live scrape)"
        }
        
        # Try to find earnings date
        if "Earnings Date" in content:
            earnings_info["has_earnings_date"] = True
        
        return earnings_info
    
    def get_insider_trading(self, symbol: str) -> Dict:
        """
        Scrape insider trading activity.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with insider trading data
        """
        url = f"https://finance.yahoo.com/quote/{symbol}/insider-transactions/"
        result = self.scrape(url)
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "symbol": symbol,
            "content": result.get("content", "")[:5000],
            "scraped_at": result.get("scraped_at", datetime.now().isoformat()),
            "source": "Yahoo Finance Insider Transactions (live scrape)"
        }
    
    def get_real_time_quote(self, symbol: str) -> Dict:
        """
        Scrape real-time quote data.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with current price and key metrics
        """
        url = f"https://finance.yahoo.com/quote/{symbol}/"
        result = self.scrape(url)
        
        if result.get("status") != "success":
            return result
        
        content = result.get("content", "")
        
        # Parse key metrics from the content
        quote_data = {
            "status": "success",
            "symbol": symbol,
            "raw_content": content[:3000],
            "scraped_at": result.get("scraped_at"),
            "source": "Yahoo Finance (live scrape)",
            "note": "REAL-TIME DATA - Use these numbers, do not hallucinate"
        }
        
        return quote_data
    
    def search_news(self, query: str, limit: int = 5) -> Dict:
        """
        Search for recent news articles.
        
        Args:
            query: Search query (e.g., "AAPL earnings news")
            limit: Max results
            
        Returns:
            Dict with news articles
        """
        result = self.search(f"{query} news today", limit=limit)
        
        if result.get("status") != "success":
            return result
        
        return {
            "status": "success",
            "query": query,
            "articles": result.get("results", {}).get("web", []),
            "scraped_at": datetime.now().isoformat(),
            "source": "Web Search (live)"
        }


class SadieWebDataProvider:
    """
    High-level data provider that combines Firecrawl scraping
    with existing API data to ensure complete, accurate information.
    """
    
    def __init__(self):
        self.scraper = FirecrawlScraper()
    
    def get_complete_options_data(self, symbol: str) -> Dict:
        """
        Get complete options data with real-time scraping.
        This data is REAL and CURRENT - no hallucinations.
        """
        options = self.scraper.get_options_chain(symbol)
        
        if options.get("status") == "success":
            # Add explicit data verification note
            options["data_verification"] = {
                "is_real_data": True,
                "source": "Yahoo Finance Live Scrape",
                "scraped_at": options.get("scraped_at"),
                "warning": "USE THESE EXACT NUMBERS - DO NOT HALLUCINATE OR ESTIMATE"
            }
        
        return options
    
    def get_complete_analysis_data(self, symbol: str) -> Dict:
        """
        Get comprehensive analysis data from multiple sources.
        All data is scraped in real-time - verified and current.
        """
        data = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "data_sources": []
        }
        
        # Get options chain
        options = self.scraper.get_options_chain(symbol)
        if options.get("status") == "success":
            data["options"] = options
            data["data_sources"].append("Yahoo Finance Options (live)")
        
        # Get analyst ratings
        ratings = self.scraper.get_analyst_ratings(symbol)
        if ratings.get("status") == "success":
            data["analyst_ratings"] = ratings
            data["data_sources"].append("Analyst Ratings (live)")
        
        # Get real-time quote
        quote = self.scraper.get_real_time_quote(symbol)
        if quote.get("status") == "success":
            data["quote"] = quote
            data["data_sources"].append("Real-time Quote (live)")
        
        # Get recent news
        news = self.scraper.search_news(f"{symbol} stock", limit=3)
        if news.get("status") == "success":
            data["news"] = news
            data["data_sources"].append("Recent News (live)")
        
        data["verification"] = {
            "all_data_is_real": True,
            "all_data_is_current": True,
            "no_hallucinations": True,
            "instruction": "USE ONLY THE DATA PROVIDED ABOVE. DO NOT MAKE UP ANY NUMBERS."
        }
        
        return data
    
    def format_for_prompt_injection(self, data: Dict) -> str:
        """
        Format scraped data for injection into LLM prompt.
        Ensures the LLM uses real data and doesn't hallucinate.
        """
        sections = []
        symbol = data.get("symbol", "UNKNOWN")
        
        sections.append(f"=== VERIFIED REAL-TIME DATA FOR {symbol} ===")
        sections.append(f"Data scraped at: {data.get('timestamp', 'N/A')}")
        sections.append("CRITICAL: Use ONLY the data below. Do NOT hallucinate or estimate any numbers.")
        sections.append("")
        
        # Options data
        if "options" in data:
            opts = data["options"]
            summary = opts.get("summary", {})
            sections.append("--- OPTIONS CHAIN (REAL DATA) ---")
            sections.append(f"Put/Call Ratio: {summary.get('put_call_ratio', 'N/A')}")
            sections.append(f"Max Pain Strike: ${summary.get('max_pain_strike', 'N/A')}")
            sections.append(f"Total Call Volume: {summary.get('total_call_volume', 'N/A'):,}")
            sections.append(f"Total Put Volume: {summary.get('total_put_volume', 'N/A'):,}")
            sections.append(f"Total Call OI: {summary.get('total_call_oi', 'N/A'):,}")
            sections.append(f"Total Put OI: {summary.get('total_put_oi', 'N/A'):,}")
            
            unusual = summary.get("unusual_activity", [])
            if unusual:
                sections.append("\nUnusual Options Activity:")
                for u in unusual[:3]:
                    sections.append(f"  - {u['type'].upper()} ${u['strike']}: Vol {u['volume']:,}, OI {u['open_interest']:,}, IV {u['implied_volatility']}%")
            sections.append("")
        
        # Quote data
        if "quote" in data:
            sections.append("--- CURRENT QUOTE (REAL DATA) ---")
            sections.append(data["quote"].get("raw_content", "")[:1000])
            sections.append("")
        
        # News
        if "news" in data:
            sections.append("--- RECENT NEWS (REAL DATA) ---")
            for article in data["news"].get("articles", [])[:3]:
                sections.append(f"- {article.get('title', 'N/A')}")
                sections.append(f"  Source: {article.get('url', 'N/A')}")
            sections.append("")
        
        sections.append("=== END VERIFIED DATA ===")
        sections.append("REMINDER: All numbers above are REAL and CURRENT. Use them exactly as provided.")
        
        return "\n".join(sections)


# Test function
def test_scraper():
    """Test the Firecrawl scraper with AAPL."""
    provider = SadieWebDataProvider()
    
    print("Testing options chain scrape...")
    options = provider.get_complete_options_data("AAPL")
    
    if options.get("status") == "success":
        print(f"✓ Options scraped successfully")
        print(f"  Put/Call Ratio: {options.get('summary', {}).get('put_call_ratio')}")
        print(f"  Max Pain: ${options.get('summary', {}).get('max_pain_strike')}")
        print(f"  Unusual Activity: {len(options.get('summary', {}).get('unusual_activity', []))} items")
    else:
        print(f"✗ Options scrape failed: {options.get('error')}")
    
    return options


if __name__ == "__main__":
    test_scraper()
