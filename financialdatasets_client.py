"""
================================================================================
FINANCIAL DATASETS CLIENT - MCP Integration
================================================================================
Premium financial data provider via FinancialDatasets.ai MCP server.

Provides:
- Real-time stock prices and snapshots
- Financial statements (Income, Balance Sheet, Cash Flow)
- Financial metrics (P/E, ROE, margins, growth rates)
- Company facts and segmented revenues
- News and sentiment for catalyst detection
- SEC filings for deep analysis

Designed to enhance predictions and fill data gaps across all modules.
================================================================================
"""

import subprocess
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


class FinancialDatasetsClient:
    """
    Client for FinancialDatasets.ai via MCP server.
    
    Provides institutional-grade financial data to enhance:
    - Sadie AI recommendations
    - Fundamental analysis
    - News/catalyst detection
    - Comprehensive scoring
    """
    
    def __init__(self):
        """Initialize the client."""
        self.server_name = "financialdatasets"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def _call_mcp(self, tool_name: str, params: Dict) -> Optional[Dict]:
        """
        Call an MCP tool and return the result.
        
        Args:
            tool_name: Name of the MCP tool to call
            params: Dictionary of parameters
            
        Returns:
            Parsed JSON response or None on error
        """
        try:
            # Build the command
            params_json = json.dumps(params)
            cmd = f"manus-mcp-cli tool call {tool_name} --server {self.server_name} --input '{params_json}'"
            
            # Execute
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output - find JSON in the response
            output = result.stdout
            
            # Find the JSON part (after "Tool execution result:")
            if "Tool execution result:" in output:
                json_start = output.find("Tool execution result:") + len("Tool execution result:")
                json_str = output[json_start:].strip()
                return json.loads(json_str)
            
            return None
            
        except subprocess.TimeoutExpired:
            print(f"MCP call timeout: {tool_name}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parse error for {tool_name}: {e}")
            return None
        except Exception as e:
            print(f"MCP call error for {tool_name}: {e}")
            return None
    
    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Get cached data if still valid."""
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        return None
    
    def _set_cache(self, cache_key: str, data: Dict):
        """Cache data with timestamp."""
        self.cache[cache_key] = (time.time(), data)
    
    # ==================== PRICE DATA ====================
    
    def get_price_snapshot(self, ticker: str) -> Dict:
        """
        Get the latest price snapshot for a stock.
        
        Returns: OHLC, volume, and latest price data
        """
        cache_key = f"price_snapshot_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        result = self._call_mcp("getStockPriceSnapshot", {"ticker": ticker})
        
        if result:
            self._set_cache(cache_key, result)
            return {
                "status": "success",
                "ticker": ticker,
                "price": result.get("close"),
                "open": result.get("open"),
                "high": result.get("high"),
                "low": result.get("low"),
                "volume": result.get("volume"),
                "date": result.get("date"),
                "source": "FinancialDatasets.ai"
            }
        
        return {"status": "error", "error": "Failed to fetch price snapshot"}
    
    def get_historical_prices(self, ticker: str, days: int = 90) -> Dict:
        """
        Get historical price data.
        
        Args:
            ticker: Stock symbol
            days: Number of days of history
            
        Returns: List of OHLCV data
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        result = self._call_mcp("getStockPrices", {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "interval": "day"
        })
        
        if result and isinstance(result, list):
            return {
                "status": "success",
                "ticker": ticker,
                "prices": result,
                "count": len(result),
                "source": "FinancialDatasets.ai"
            }
        
        return {"status": "error", "error": "Failed to fetch historical prices"}
    
    # ==================== FINANCIAL METRICS ====================
    
    def get_financial_metrics_snapshot(self, ticker: str) -> Dict:
        """
        Get current financial metrics snapshot.
        
        Returns comprehensive metrics including:
        - Valuation: P/E, P/B, P/S, EV/EBITDA, PEG
        - Profitability: Gross margin, operating margin, net margin, ROE, ROA, ROIC
        - Liquidity: Current ratio, quick ratio, cash ratio
        - Leverage: Debt/equity, debt/assets
        - Growth: Revenue, earnings, EPS, FCF growth
        - Per-share: EPS, book value, FCF per share
        """
        cache_key = f"metrics_snapshot_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        result = self._call_mcp("getFinancialMetricsSnapshot", {"ticker": ticker})
        
        if result:
            # Structure the data for easy consumption
            metrics = {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                
                # Valuation
                "valuation": {
                    "market_cap": result.get("market_cap"),
                    "enterprise_value": result.get("enterprise_value"),
                    "pe_ratio": result.get("price_to_earnings_ratio"),
                    "pb_ratio": result.get("price_to_book_ratio"),
                    "ps_ratio": result.get("price_to_sales_ratio"),
                    "ev_ebitda": result.get("enterprise_value_to_ebitda_ratio"),
                    "ev_revenue": result.get("enterprise_value_to_revenue_ratio"),
                    "peg_ratio": result.get("peg_ratio"),
                    "fcf_yield": result.get("free_cash_flow_yield")
                },
                
                # Profitability
                "profitability": {
                    "gross_margin": result.get("gross_margin"),
                    "operating_margin": result.get("operating_margin"),
                    "net_margin": result.get("net_margin"),
                    "roe": result.get("return_on_equity"),
                    "roa": result.get("return_on_assets"),
                    "roic": result.get("return_on_invested_capital")
                },
                
                # Efficiency
                "efficiency": {
                    "asset_turnover": result.get("asset_turnover"),
                    "inventory_turnover": result.get("inventory_turnover"),
                    "receivables_turnover": result.get("receivables_turnover"),
                    "working_capital_turnover": result.get("working_capital_turnover")
                },
                
                # Liquidity
                "liquidity": {
                    "current_ratio": result.get("current_ratio"),
                    "quick_ratio": result.get("quick_ratio"),
                    "cash_ratio": result.get("cash_ratio"),
                    "ocf_ratio": result.get("operating_cash_flow_ratio")
                },
                
                # Leverage
                "leverage": {
                    "debt_to_equity": result.get("debt_to_equity"),
                    "debt_to_assets": result.get("debt_to_assets"),
                    "interest_coverage": result.get("interest_coverage")
                },
                
                # Growth
                "growth": {
                    "revenue_growth": result.get("revenue_growth"),
                    "earnings_growth": result.get("earnings_growth"),
                    "eps_growth": result.get("earnings_per_share_growth"),
                    "fcf_growth": result.get("free_cash_flow_growth"),
                    "operating_income_growth": result.get("operating_income_growth"),
                    "ebitda_growth": result.get("ebitda_growth"),
                    "book_value_growth": result.get("book_value_growth")
                },
                
                # Per Share
                "per_share": {
                    "eps": result.get("earnings_per_share"),
                    "book_value": result.get("book_value_per_share"),
                    "fcf": result.get("free_cash_flow_per_share")
                },
                
                # Dividend
                "dividend": {
                    "payout_ratio": result.get("payout_ratio")
                }
            }
            
            self._set_cache(cache_key, metrics)
            return metrics
        
        return {"status": "error", "error": "Failed to fetch financial metrics"}
    
    # ==================== COMPANY INFO ====================
    
    def get_company_facts(self, ticker: str) -> Dict:
        """
        Get comprehensive company facts.
        
        Returns: Market cap, employees, sector, industry, exchange, location, etc.
        """
        cache_key = f"company_facts_{ticker}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        result = self._call_mcp("getCompanyFacts", {"ticker": ticker})
        
        if result:
            facts = {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                "name": result.get("name"),
                "market_cap": result.get("market_cap"),
                "employees": result.get("employees"),
                "sector": result.get("sector"),
                "industry": result.get("industry"),
                "exchange": result.get("exchange"),
                "city": result.get("city"),
                "state": result.get("state"),
                "country": result.get("country"),
                "website": result.get("website"),
                "description": result.get("description"),
                "sic_code": result.get("sic_code"),
                "sic_description": result.get("sic_description")
            }
            self._set_cache(cache_key, facts)
            return facts
        
        return {"status": "error", "error": "Failed to fetch company facts"}
    
    # ==================== NEWS & CATALYSTS ====================
    
    def get_news(self, ticker: str, limit: int = 10) -> Dict:
        """
        Get recent news for a stock.
        
        Returns: List of news articles with sentiment
        """
        result = self._call_mcp("getNews", {"ticker": ticker, "limit": limit})
        
        if result and isinstance(result, list):
            # Analyze sentiment distribution
            sentiments = {"positive": 0, "negative": 0, "neutral": 0}
            for article in result:
                sentiment = article.get("sentiment", "neutral").lower()
                if sentiment in sentiments:
                    sentiments[sentiment] += 1
            
            # Calculate overall sentiment score (-1 to +1)
            total = len(result) if result else 1
            sentiment_score = (sentiments["positive"] - sentiments["negative"]) / total
            
            return {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                "articles": result,
                "count": len(result),
                "sentiment_distribution": sentiments,
                "sentiment_score": round(sentiment_score, 2),
                "overall_sentiment": "BULLISH" if sentiment_score > 0.2 else "BEARISH" if sentiment_score < -0.2 else "NEUTRAL"
            }
        
        return {"status": "error", "error": "Failed to fetch news"}
    
    # ==================== FINANCIAL STATEMENTS ====================
    
    def get_income_statement(self, ticker: str, period: str = "ttm", limit: int = 4) -> Dict:
        """
        Get income statement data.
        
        Args:
            ticker: Stock symbol
            period: 'annual', 'quarterly', or 'ttm'
            limit: Number of periods
        """
        result = self._call_mcp("getIncomeStatement", {
            "ticker": ticker,
            "period": period,
            "limit": limit
        })
        
        if result:
            return {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                "period": period,
                "statements": result if isinstance(result, list) else [result]
            }
        
        return {"status": "error", "error": "Failed to fetch income statement"}
    
    def get_balance_sheet(self, ticker: str, period: str = "ttm", limit: int = 4) -> Dict:
        """
        Get balance sheet data.
        """
        result = self._call_mcp("getBalanceSheet", {
            "ticker": ticker,
            "period": period,
            "limit": limit
        })
        
        if result:
            return {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                "period": period,
                "statements": result if isinstance(result, list) else [result]
            }
        
        return {"status": "error", "error": "Failed to fetch balance sheet"}
    
    def get_cash_flow(self, ticker: str, period: str = "ttm", limit: int = 4) -> Dict:
        """
        Get cash flow statement data.
        """
        result = self._call_mcp("getCashFlowStatement", {
            "ticker": ticker,
            "period": period,
            "limit": limit
        })
        
        if result:
            return {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                "period": period,
                "statements": result if isinstance(result, list) else [result]
            }
        
        return {"status": "error", "error": "Failed to fetch cash flow statement"}
    
    # ==================== SEC FILINGS ====================
    
    def get_sec_filings(self, ticker: str, filing_type: str = None, limit: int = 10) -> Dict:
        """
        Get SEC filings for a company.
        
        Args:
            ticker: Stock symbol
            filing_type: '10-K', '10-Q', '8-K', etc.
            limit: Number of filings
        """
        params = {"ticker": ticker, "limit": limit}
        if filing_type:
            params["filing_type"] = filing_type
        
        result = self._call_mcp("getFilings", params)
        
        if result and isinstance(result, list):
            return {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                "filings": result,
                "count": len(result)
            }
        
        return {"status": "error", "error": "Failed to fetch SEC filings"}
    
    # ==================== SEGMENTED REVENUE ====================
    
    def get_segmented_revenue(self, ticker: str, limit: int = 4) -> Dict:
        """
        Get revenue breakdown by segment.
        
        Useful for understanding business composition and diversification.
        """
        result = self._call_mcp("getSegmentedRevenues", {
            "ticker": ticker,
            "limit": limit
        })
        
        if result:
            return {
                "status": "success",
                "ticker": ticker,
                "source": "FinancialDatasets.ai",
                "segments": result if isinstance(result, list) else [result]
            }
        
        return {"status": "error", "error": "Failed to fetch segmented revenue"}
    
    # ==================== COMPREHENSIVE ANALYSIS ====================
    
    def get_comprehensive_data(self, ticker: str) -> Dict:
        """
        Get all available data for a stock in one call.
        
        This is the main method for enhancing Sadie AI and other modules.
        Combines: metrics, company facts, news, and recent price.
        """
        comprehensive = {
            "status": "success",
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "source": "FinancialDatasets.ai"
        }
        
        # Get financial metrics
        metrics = self.get_financial_metrics_snapshot(ticker)
        if metrics.get("status") == "success":
            comprehensive["metrics"] = metrics
        
        # Get company facts
        facts = self.get_company_facts(ticker)
        if facts.get("status") == "success":
            comprehensive["company"] = facts
        
        # Get news
        news = self.get_news(ticker, limit=5)
        if news.get("status") == "success":
            comprehensive["news"] = news
        
        # Get price snapshot
        price = self.get_price_snapshot(ticker)
        if price.get("status") == "success":
            comprehensive["price"] = price
        
        return comprehensive


# Test function
if __name__ == "__main__":
    print("Testing FinancialDatasets Client...")
    client = FinancialDatasetsClient()
    
    # Test metrics
    print("\n1. Testing Financial Metrics Snapshot...")
    metrics = client.get_financial_metrics_snapshot("AAPL")
    if metrics.get("status") == "success":
        print(f"   P/E: {metrics['valuation']['pe_ratio']:.2f}")
        print(f"   ROE: {metrics['profitability']['roe']*100:.1f}%")
        print(f"   Revenue Growth: {metrics['growth']['revenue_growth']*100:.1f}%")
    
    # Test news
    print("\n2. Testing News...")
    news = client.get_news("AAPL", limit=3)
    if news.get("status") == "success":
        print(f"   Found {news['count']} articles")
        print(f"   Sentiment: {news['overall_sentiment']} ({news['sentiment_score']})")
    
    # Test comprehensive
    print("\n3. Testing Comprehensive Data...")
    comp = client.get_comprehensive_data("NVDA")
    print(f"   Sections: {list(comp.keys())}")
    
    print("\n✅ FinancialDatasets Client working!")
