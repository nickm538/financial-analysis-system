"""
COMPREHENSIVE FUNDAMENTALS MODULE v14.0 - FIXED DATA EXTRACTION
================================================================
✅ Proper field name mappings for all APIs
✅ Multiple fallback sources for each metric
✅ Comprehensive debugging and logging
✅ Guaranteed non-zero values where data exists
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from alphavantage_client import AlphaVantageClient
from typing import Dict, Optional, Union, Any
from datetime import datetime
import time
import json
import yfinance as yf

class ComprehensiveFundamentals:
    """Multi-API comprehensive fundamental analysis with robust data extraction"""

    def __init__(self, massive_api_key: str, finnhub_api_key: str):
        self.massive_api_key = massive_api_key
        self.massive_base_url = "https://api.massive.com/vX/reference"
        self.finnhub_api_key = finnhub_api_key
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        self.session = self._create_session()
        self.alphavantage = AlphaVantageClient()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float, handling nested Massive API structure"""
        if value is None or value == 'None' or value == '': 
            return default
        
        # Handle Massive API nested structure: {'value': 123.45, 'unit': 'USD', ...}
        if isinstance(value, dict):
            if 'value' in value:
                value = value['value']
            else:
                return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _normalize_percentage(self, value: float, is_already_percentage: bool = True) -> float:
        """Normalize percentage values"""
        if value is None or value == 0: 
            return 0.0
        if is_already_percentage: 
            return round(value, 2)
        return round(value * 100, 2)

    def get_fundamentals(self, ticker: str) -> Dict:
        """Get comprehensive metrics from all sources"""
        print(f"\n🔍 Fetching comprehensive fundamentals for {ticker}...")
        
        massive_data = self._fetch_massive_financials(ticker)
        finnhub_data = self._fetch_finnhub_metrics(ticker)
        av_data = self._fetch_alphavantage_data(ticker)
        yf_data = self._fetch_yfinance_data(ticker)  # NEW: yfinance fallback
        
        # Debug: Print what we got from each API
        print(f"\n   📊 API Response Summary:")
        print(f"      Massive API: {len(massive_data) if massive_data else 0} fields")
        print(f"      Finnhub API: {len(finnhub_data) if finnhub_data else 0} fields")
        print(f"      AlphaVantage: {len(av_data) if av_data else 0} fields")
        print(f"      yfinance: {len(yf_data) if yf_data else 0} fields")
        
        metrics = self._calculate_all_metrics(massive_data, finnhub_data, av_data, ticker, yf_data)
        
        print(f"✅ Calculated {len(metrics)} fundamental metrics for {ticker}\n")
        return metrics

    def _fetch_finnhub_metrics(self, ticker: str) -> Dict:
        """Fetch metrics from Finnhub with robust JSON error handling"""
        url = f"{self.finnhub_base_url}/stock/metric"
        params = {'symbol': ticker, 'metric': 'all', 'token': self.finnhub_api_key}
        
        try:
            print(f"   🔍 Finnhub: Fetching metrics for {ticker}...")
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"   ⚠️ Finnhub API Error: HTTP {response.status_code}")
                return {}

            if not response.text or len(response.text.strip()) == 0:
                print(f"   ⚠️ Finnhub API: Empty response received")
                return {}

            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                print(f"   ⚠️ Finnhub API: Invalid content type '{content_type}' (expected JSON)")
                return {}

            try:
                data = response.json()
            except json.JSONDecodeError as je:
                print(f"   ⚠️ Finnhub API: Invalid JSON response - {str(je)}")
                return {}

            if not isinstance(data, dict):
                print(f"   ⚠️ Finnhub API: Response is not a dictionary")
                return {}

            # Extract the 'metric' sub-dictionary which contains all the data
            if 'metric' in data and isinstance(data['metric'], dict):
                finnhub_metrics = data['metric']
                print(f"   ✅ Finnhub: Fetched {len(finnhub_metrics)} metrics successfully")
                return finnhub_metrics
            else:
                print(f"   ⚠️ Finnhub API: No 'metric' field in response")
                return {}

        except requests.exceptions.Timeout:
            print(f"   ⚠️ Finnhub: Request timed out")
            return {}
        except requests.exceptions.RequestException as re:
            print(f"   ⚠️ Finnhub Request Error: {type(re).__name__} - {str(re)}")
            return {}
        except Exception as e:
            print(f"   ⚠️ Finnhub Unexpected Error: {type(e).__name__} - {str(e)}")
            return {}

    def _fetch_massive_financials(self, ticker: str) -> Optional[Dict]:
        """Fetch financial statements from Massive API"""
        try:
            print(f"   🔍 Massive API: Fetching financials for {ticker}...")
            url = f"{self.massive_base_url}/financials"
            params = {'ticker': ticker, 'timeframe': 'ttm', 'limit': 1, 'apiKey': self.massive_api_key}
            res = self.session.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get('results'):
                    financials = data['results'][0]['financials']
                    print(f"   ✅ Massive API: Financials fetched successfully")
                    print(f"   📊 DEBUG: Top-level keys: {list(financials.keys())}")
                    
                    # Massive API returns nested dictionaries:
                    # {'balance_sheet': {...}, 'income_statement': {...}, 'cash_flow_statement': {...}}
                    # We need to flatten these into a single dictionary
                    flattened = {}
                    
                    # Extract from each statement
                    for statement_type in ['balance_sheet', 'income_statement', 'cash_flow_statement', 'comprehensive_income']:
                        if statement_type in financials and isinstance(financials[statement_type], dict):
                            flattened.update(financials[statement_type])
                            print(f"   📊 DEBUG: Extracted {len(financials[statement_type])} fields from {statement_type}")
                    
                    print(f"   ✅ Massive API: Flattened {len(flattened)} total fields")
                    return flattened
            print(f"   ⚠️ Massive API: No data available (HTTP {res.status_code})")
            return {}
        except Exception as e:
            print(f"   ⚠️ Massive API Error: {e}")
            return {}

    def _fetch_alphavantage_data(self, ticker: str) -> Dict:
        """Wrapper for AlphaVantage client"""
        return self.alphavantage.get_comprehensive_data(ticker)

    def _fetch_yfinance_data(self, ticker: str) -> Dict:
        """Fetch comprehensive data from yfinance as fallback - FREE, no rate limits"""
        try:
            print(f"   🔍 yfinance: Fetching data for {ticker}...")
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract key metrics
            data = {
                # Cash Flow
                'free_cash_flow': info.get('freeCashflow', 0),
                'operating_cash_flow': info.get('operatingCashflow', 0),
                'total_cash': info.get('totalCash', 0),
                'total_debt': info.get('totalDebt', 0),
                
                # Valuation
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'trailing_pe': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'ev_to_ebitda': info.get('enterpriseToEbitda', 0),
                'ev_to_revenue': info.get('enterpriseToRevenue', 0),
                
                # Profitability
                'profit_margin': info.get('profitMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'gross_margin': info.get('grossMargins', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'return_on_assets': info.get('returnOnAssets', 0),
                
                # Growth
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 0),
                
                # Per Share
                'eps_trailing': info.get('trailingEps', 0),
                'eps_forward': info.get('forwardEps', 0),
                'book_value': info.get('bookValue', 0),
                'revenue_per_share': info.get('revenuePerShare', 0),
                
                # Balance Sheet
                'total_assets': info.get('totalAssets', 0),
                'total_equity': info.get('totalStockholderEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                
                # Other
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'revenue': info.get('totalRevenue', 0),
                'ebitda': info.get('ebitda', 0),
                'net_income': info.get('netIncomeToCommon', 0),
            }
            
            # Count non-zero values
            non_zero = sum(1 for v in data.values() if v and v != 0)
            print(f"   ✅ yfinance: {non_zero} non-zero metrics fetched")
            return data
            
        except Exception as e:
            print(f"   ⚠️ yfinance Error: {e}")
            return {}

    def _calculate_all_metrics(self, massive_data, finnhub_data, av_data, ticker, yf_data=None) -> Dict:
        """
        Calculate all fundamental metrics with proper formulations.
        Uses multiple fallback sources for each metric.
        """
        metrics = {}
        finnhub_data = finnhub_data or {}
        av_data = av_data or {}
        massive_data = massive_data or {}
        yf_data = yf_data or {}  # NEW: yfinance fallback
        
        # ========== VALUATION METRICS ==========
        
        # P/E Ratio (Price-to-Earnings)
        metrics['pe_ratio'] = self._safe_float(av_data.get('trailing_pe', 0))
        if metrics['pe_ratio'] == 0:
            metrics['pe_ratio'] = self._safe_float(finnhub_data.get('peBasicExclExtraTTM', 0))
        if metrics['pe_ratio'] == 0:
            metrics['pe_ratio'] = self._safe_float(finnhub_data.get('peTTM', 0))
        if metrics['pe_ratio'] == 0:  # yfinance fallback
            metrics['pe_ratio'] = self._safe_float(yf_data.get('trailing_pe', 0))
        
        # Forward P/E
        metrics['forward_pe'] = self._safe_float(av_data.get('forward_pe', 0))
        if metrics['forward_pe'] == 0:  # yfinance fallback
            metrics['forward_pe'] = self._safe_float(yf_data.get('forward_pe', 0))
        if metrics['forward_pe'] == 0:
            metrics['forward_pe'] = self._safe_float(finnhub_data.get('peNormalizedAnnual', 0))
        
        # PEG Ratio (Price/Earnings to Growth)
        metrics['peg_ratio'] = self._safe_float(av_data.get('peg_ratio', 0))
        if metrics['peg_ratio'] == 0:
            metrics['peg_ratio'] = self._safe_float(finnhub_data.get('pegRatio', 0))
        
        # P/S Ratio (Price-to-Sales)
        metrics['ps_ratio'] = self._safe_float(av_data.get('price_to_sales', 0))
        if metrics['ps_ratio'] == 0:
            metrics['ps_ratio'] = self._safe_float(finnhub_data.get('psTTM', 0))
        if metrics['ps_ratio'] == 0:
            metrics['ps_ratio'] = self._safe_float(finnhub_data.get('psAnnual', 0))
        
        # P/B Ratio (Price-to-Book)
        metrics['pb_ratio'] = self._safe_float(av_data.get('price_to_book', 0))
        if metrics['pb_ratio'] == 0:
            metrics['pb_ratio'] = self._safe_float(finnhub_data.get('pbAnnual', 0))
        if metrics['pb_ratio'] == 0:
            metrics['pb_ratio'] = self._safe_float(finnhub_data.get('pbQuarterly', 0))
        
        # ========== EBITDA METRICS ==========
        
        # EBITDA (from AlphaVantage or Massive)
        metrics['ebitda'] = self._safe_float(av_data.get('ebitda', 0))
        if metrics['ebitda'] == 0:
            metrics['ebitda'] = self._safe_float(massive_data.get('ebitda', 0))
        if metrics['ebitda'] == 0:
            # Calculate from operating income if available
            operating_income = self._safe_float(massive_data.get('operating_income', 0))
            depreciation = self._safe_float(massive_data.get('depreciation_and_amortization', 0))
            if operating_income > 0:
                metrics['ebitda'] = operating_income + depreciation
        
        # Revenue (for EBITDA margin calculation)
        metrics['revenue'] = self._safe_float(av_data.get('revenue_ttm', 0))
        if metrics['revenue'] == 0:
            metrics['revenue'] = self._safe_float(massive_data.get('revenues', 0))
        if metrics['revenue'] == 0:
            metrics['revenue'] = self._safe_float(massive_data.get('revenue', 0))
        
        # EBITDA Margin = (EBITDA / Revenue) * 100
        if metrics['revenue'] > 0 and metrics['ebitda'] > 0:
            metrics['ebitda_margin'] = (metrics['ebitda'] / metrics['revenue']) * 100
        else:
            metrics['ebitda_margin'] = 0.0
        
        # EV/EBITDA will be calculated later after debt and cash are known
        
        # ========== PROFITABILITY METRICS ==========
        
        # ROE (Return on Equity) - percentage
        metrics['roe'] = self._safe_float(av_data.get('return_on_equity', 0))
        if metrics['roe'] == 0:
            metrics['roe'] = self._safe_float(finnhub_data.get('roeTTM', 0))
        if metrics['roe'] == 0:
            metrics['roe'] = self._safe_float(finnhub_data.get('roeRfy', 0))
        
        # ROA (Return on Assets) - percentage
        metrics['roa'] = self._safe_float(av_data.get('return_on_assets', 0))
        if metrics['roa'] == 0:
            metrics['roa'] = self._safe_float(finnhub_data.get('roaTTM', 0))
        if metrics['roa'] == 0:
            metrics['roa'] = self._safe_float(finnhub_data.get('roaRfy', 0))
        
        # Net Profit Margin - percentage
        metrics['net_margin'] = self._safe_float(av_data.get('profit_margin', 0))
        if metrics['net_margin'] == 0:
            metrics['net_margin'] = self._safe_float(finnhub_data.get('netProfitMarginTTM', 0))
        if metrics['net_margin'] == 0:
            metrics['net_margin'] = self._safe_float(finnhub_data.get('netProfitMarginAnnual', 0))
        
        # Operating Margin - percentage
        metrics['operating_margin'] = self._safe_float(av_data.get('operating_margin', 0))
        if metrics['operating_margin'] == 0:
            metrics['operating_margin'] = self._safe_float(finnhub_data.get('operatingMarginTTM', 0))
        if metrics['operating_margin'] == 0:
            metrics['operating_margin'] = self._safe_float(finnhub_data.get('operatingMarginAnnual', 0))
        
        # Gross Margin - percentage
        metrics['gross_margin'] = self._safe_float(finnhub_data.get('grossMarginTTM', 0))
        if metrics['gross_margin'] == 0:
            metrics['gross_margin'] = self._safe_float(finnhub_data.get('grossMarginAnnual', 0))
        if metrics['gross_margin'] == 0:  # yfinance fallback (returns as decimal)
            yf_gross = self._safe_float(yf_data.get('gross_margin', 0))
            if yf_gross > 0:
                metrics['gross_margin'] = yf_gross * 100 if yf_gross < 1 else yf_gross
        
        # yfinance fallbacks for other profitability metrics
        if metrics['net_margin'] == 0:
            yf_profit = self._safe_float(yf_data.get('profit_margin', 0))
            if yf_profit > 0:
                metrics['net_margin'] = yf_profit * 100 if yf_profit < 1 else yf_profit
        if metrics['operating_margin'] == 0:
            yf_op = self._safe_float(yf_data.get('operating_margin', 0))
            if yf_op > 0:
                metrics['operating_margin'] = yf_op * 100 if yf_op < 1 else yf_op
        if metrics['roe'] == 0:
            yf_roe = self._safe_float(yf_data.get('return_on_equity', 0))
            if yf_roe > 0:
                metrics['roe'] = yf_roe * 100 if yf_roe < 1 else yf_roe
        if metrics['roa'] == 0:
            yf_roa = self._safe_float(yf_data.get('return_on_assets', 0))
            if yf_roa > 0:
                metrics['roa'] = yf_roa * 100 if yf_roa < 1 else yf_roa
        
        # ========== LIQUIDITY METRICS ==========
        
        # Current Ratio = Current Assets / Current Liabilities
        metrics['current_ratio'] = self._safe_float(finnhub_data.get('currentRatioTTM', 0))
        if metrics['current_ratio'] == 0:
            metrics['current_ratio'] = self._safe_float(finnhub_data.get('currentRatioAnnual', 0))
        if metrics['current_ratio'] == 0:
            metrics['current_ratio'] = self._safe_float(finnhub_data.get('currentRatioQuarterly', 0))
        # Calculate manually if still zero
        if metrics['current_ratio'] == 0:
            current_assets = self._safe_float(massive_data.get('current_assets', 0))
            current_liabilities = self._safe_float(massive_data.get('current_liabilities', 0))
            if current_liabilities > 0:
                metrics['current_ratio'] = current_assets / current_liabilities
        # yfinance fallback
        if metrics['current_ratio'] == 0:
            metrics['current_ratio'] = self._safe_float(yf_data.get('current_ratio', 0))
        
        # Quick Ratio = (Current Assets - Inventory) / Current Liabilities
        metrics['quick_ratio'] = self._safe_float(finnhub_data.get('quickRatioTTM', 0))
        if metrics['quick_ratio'] == 0:
            metrics['quick_ratio'] = self._safe_float(finnhub_data.get('quickRatioAnnual', 0))
        if metrics['quick_ratio'] == 0:
            metrics['quick_ratio'] = self._safe_float(finnhub_data.get('quickRatioQuarterly', 0))
        # Calculate manually if still zero
        if metrics['quick_ratio'] == 0:
            current_assets = self._safe_float(massive_data.get('current_assets', 0))
            inventory = self._safe_float(massive_data.get('inventory', 0))
            current_liabilities = self._safe_float(massive_data.get('current_liabilities', 0))
            if current_liabilities > 0:
                metrics['quick_ratio'] = (current_assets - inventory) / current_liabilities
        # yfinance fallback
        if metrics['quick_ratio'] == 0:
            metrics['quick_ratio'] = self._safe_float(yf_data.get('quick_ratio', 0))
        
        # Cash Ratio = Cash / Current Liabilities
        metrics['cash_ratio'] = self._safe_float(finnhub_data.get('cashRatioTTM', 0))
        if metrics['cash_ratio'] == 0:
            metrics['cash_ratio'] = self._safe_float(finnhub_data.get('cashRatioAnnual', 0))
        if metrics['cash_ratio'] == 0:
            metrics['cash_ratio'] = self._safe_float(finnhub_data.get('cashRatioQuarterly', 0))
        # Calculate manually if still zero
        if metrics['cash_ratio'] == 0:
            # Try multiple field names for cash
            cash = self._safe_float(massive_data.get('cash_and_equivalents', 0))
            if cash == 0:
                cash = self._safe_float(massive_data.get('cash', 0))
            if cash == 0:
                cash = self._safe_float(massive_data.get('cash_and_cash_equivalents', 0))
            if cash == 0:
                cash = self._safe_float(massive_data.get('cash_and_short_term_investments', 0))
            if cash == 0:
                # Try from Finnhub
                cash = self._safe_float(finnhub_data.get('cashAndCashEquivalentsAnnual', 0))
            if cash == 0:
                cash = self._safe_float(finnhub_data.get('cashAndCashEquivalentsQuarterly', 0))
            if cash == 0:
                # Calculate from cash per share × shares outstanding
                cash_per_share = self._safe_float(finnhub_data.get('cashPerSharePerShareAnnual', 0))
                if cash_per_share == 0:
                    cash_per_share = self._safe_float(finnhub_data.get('cashPerSharePerShareQuarterly', 0))
                if cash_per_share == 0:
                    cash_per_share = self._safe_float(finnhub_data.get('cashPerSharePerShareTTM', 0))
                shares_outstanding = self._safe_float(finnhub_data.get('sharesOutstanding', 0))
                if shares_outstanding == 0:
                    shares_outstanding = self._safe_float(av_data.get('shares_outstanding', 0))
                if shares_outstanding == 0:
                    shares_outstanding = self._safe_float(av_data.get('SharesOutstanding', 0))
                if cash_per_share > 0 and shares_outstanding > 0:
                    cash = cash_per_share * shares_outstanding
                    print(f"   📊 CALCULATED: Cash = {cash_per_share:.4f} × {shares_outstanding:,.0f} = ${cash:,.0f}")
            
            current_liabilities = self._safe_float(massive_data.get('current_liabilities', 0))
            if current_liabilities == 0:
                current_liabilities = self._safe_float(finnhub_data.get('currentLiabilitiesAnnual', 0))
            if current_liabilities == 0:
                current_liabilities = self._safe_float(finnhub_data.get('currentLiabilitiesQuarterly', 0))
            
            if current_liabilities > 0 and cash > 0:
                metrics['cash_ratio'] = cash / current_liabilities
                print(f"   ℹ️ INFO: Calculated cash_ratio = {cash:,.0f} / {current_liabilities:,.0f} = {metrics['cash_ratio']:.4f}")
        
        # ========== LEVERAGE & SOLVENCY METRICS ==========
        
        # Debt-to-Equity Ratio
        metrics['debt_to_equity'] = self._safe_float(finnhub_data.get('totalDebt/totalEquityAnnual', 0))
        if metrics['debt_to_equity'] == 0:
            metrics['debt_to_equity'] = self._safe_float(finnhub_data.get('totalDebt/totalEquityTTM', 0))
        if metrics['debt_to_equity'] == 0:
            metrics['debt_to_equity'] = self._safe_float(finnhub_data.get('totalDebt/totalEquityQuarterly', 0))
        # Calculate manually if still zero
        if metrics['debt_to_equity'] == 0:
            total_debt = self._safe_float(massive_data.get('total_debt', 0))
            total_equity = self._safe_float(massive_data.get('total_equity', 0))
            if total_equity > 0:
                metrics['debt_to_equity'] = total_debt / total_equity
        
        # Debt-to-Assets Ratio
        metrics['debt_to_assets'] = self._safe_float(finnhub_data.get('totalDebt/totalAssetsTTM', 0))
        if metrics['debt_to_assets'] == 0:
            metrics['debt_to_assets'] = self._safe_float(finnhub_data.get('totalDebt/totalAssetsAnnual', 0))
        if metrics['debt_to_assets'] == 0:
            metrics['debt_to_assets'] = self._safe_float(finnhub_data.get('totalDebt/totalAssetsQuarterly', 0))
        # Calculate manually if still zero
        if metrics['debt_to_assets'] == 0:
            # Try to get total debt from multiple sources
            total_debt = self._safe_float(massive_data.get('total_debt', 0))
            
            # If not available, calculate from debt-to-equity ratio
            if total_debt == 0 and metrics['debt_to_equity'] > 0:
                total_equity = self._safe_float(massive_data.get('total_equity', 0))
                if total_equity == 0:
                    total_equity = self._safe_float(massive_data.get('stockholders_equity', 0))
                if total_equity == 0:
                    total_equity = self._safe_float(massive_data.get('equity', 0))
                if total_equity > 0:
                    total_debt = metrics['debt_to_equity'] * total_equity
                    print(f"   📊 CALCULATED: Total Debt = D/E ({metrics['debt_to_equity']:.3f}) × Equity (${total_equity:,.0f}) = ${total_debt:,.0f}")
            
            # If still zero, use long-term debt as approximation
            if total_debt == 0:
                total_debt = self._safe_float(massive_data.get('long_term_debt', 0))
                if total_debt > 0:
                    print(f"   ⚠️ WARNING: Using long-term debt (${total_debt:,.0f}) as approximation for total debt")
            
            total_assets = self._safe_float(massive_data.get('total_assets', 0))
            if total_assets == 0:
                total_assets = self._safe_float(massive_data.get('assets', 0))
            
            if total_assets > 0 and total_debt > 0:
                metrics['debt_to_assets'] = (total_debt / total_assets) * 100
                print(f"   ℹ️ INFO: Calculated debt_to_assets = {total_debt:,.0f} / {total_assets:,.0f} = {metrics['debt_to_assets']:.2f}%")
        
        # Interest Coverage Ratio = EBIT / Interest Expense
        metrics['interest_coverage'] = self._safe_float(finnhub_data.get('interestCoverageTTM', 0))
        if metrics['interest_coverage'] == 0:
            metrics['interest_coverage'] = self._safe_float(finnhub_data.get('interestCoverageAnnual', 0))
        
        # Equity Multiplier
        metrics['equity_multiplier'] = self._safe_float(finnhub_data.get('equityMultiplierTTM', 0))
        if metrics['equity_multiplier'] == 0:
            total_assets = self._safe_float(massive_data.get('total_assets', 0))
            total_equity = self._safe_float(massive_data.get('total_equity', 0))
            if total_equity > 0:
                metrics['equity_multiplier'] = total_assets / total_equity
        
        # ========== CASH FLOW METRICS (TTM - Trailing Twelve Months) ==========
        
        # Operating Cash Flow - Multi-source with TTM priority
        # Priority: Finnhub TTM > Massive API > AlphaVantage > Calculated
        
        # Try Finnhub TTM first (most reliable for TTM data)
        metrics['operating_cash_flow'] = self._safe_float(finnhub_data.get('cashFlowPerShareTTM', 0)) * self._safe_float(finnhub_data.get('sharesOutstanding', 0))
        
        # Try Massive API (flattened cash flow statement)
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(massive_data.get('operating_cash_flow', 0))
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(massive_data.get('cash_flow_from_operating_activities', 0))
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(massive_data.get('net_cash_from_operating_activities', 0))
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(massive_data.get('net_cash_provided_by_operating_activities', 0))
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(massive_data.get('net_cash_provided_by_used_in_operating_activities', 0))
        
        # Try AlphaVantage
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(av_data.get('operating_cashflow', 0))
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(av_data.get('operatingCashflow', 0))
        
        # Try yfinance (FREE, reliable for cash flow)
        if metrics['operating_cash_flow'] == 0:
            metrics['operating_cash_flow'] = self._safe_float(yf_data.get('operating_cash_flow', 0))
            if metrics['operating_cash_flow'] != 0:
                print(f"   ✅ yfinance: Operating CF = ${metrics['operating_cash_flow']:,.0f}")
        
        # ACCURATE CALCULATION: Indirect Method (CFA Institute Standard)
        # Operating CF = Net Income + D&A + ΔWorking Capital + Non-Cash Items
        if metrics['operating_cash_flow'] == 0:
            net_income = self._safe_float(massive_data.get('net_income', 0))
            if net_income == 0:
                net_income = self._safe_float(massive_data.get('net_income_loss', 0))
            if net_income == 0:
                net_income = self._safe_float(av_data.get('net_income', 0))
            if net_income == 0:
                net_income = self._safe_float(finnhub_data.get('netIncomeTTM', 0))
            
            # Depreciation & Amortization (non-cash expense, add back)
            depreciation = self._safe_float(massive_data.get('depreciation_and_amortization', 0))
            if depreciation == 0:
                depreciation = self._safe_float(massive_data.get('depreciation_amortization', 0))
            if depreciation == 0:
                depreciation = self._safe_float(massive_data.get('depreciation', 0))
            
            # Changes in Working Capital (simplified)
            change_in_receivables = self._safe_float(massive_data.get('change_in_receivables', 0))
            change_in_inventory = self._safe_float(massive_data.get('change_in_inventory', 0))
            change_in_payables = self._safe_float(massive_data.get('change_in_payables', 0))
            
            # Operating CF = Net Income + D&A - ΔAR - ΔInventory + ΔAP
            if net_income != 0 or depreciation != 0:
                metrics['operating_cash_flow'] = (net_income + depreciation 
                                                - change_in_receivables 
                                                - change_in_inventory 
                                                + change_in_payables)
                print(f"   📊 CALCULATED (Indirect Method): Operating CF = ${metrics['operating_cash_flow']:,.0f}")
                print(f"      Net Income: ${net_income:,.0f}, D&A: ${depreciation:,.0f}")
        
        # Validation: Operating CF should be reasonable relative to Net Income
        if metrics['operating_cash_flow'] != 0:
            net_income_check = self._safe_float(massive_data.get('net_income', 0))
            if net_income_check == 0:
                net_income_check = self._safe_float(av_data.get('net_income', 0))
            
            # Operating CF typically 80-150% of Net Income for healthy companies
            if net_income_check > 0:
                ocf_to_ni_ratio = metrics['operating_cash_flow'] / net_income_check
                if ocf_to_ni_ratio < 0.5 or ocf_to_ni_ratio > 3.0:
                    print(f"   ⚠️ WARNING: OCF/NI ratio = {ocf_to_ni_ratio:.2f} (unusual, verify data)")
                else:
                    print(f"   ✅ Operating CF: ${metrics['operating_cash_flow']:,.0f} (OCF/NI: {ocf_to_ni_ratio:.2f}x)")
            else:
                print(f"   ✅ Operating CF: ${metrics['operating_cash_flow']:,.0f}")
        else:
            print(f"   ⚠️ WARNING: Operating CF = 0 after all attempts")
        
        # Free Cash Flow = Operating Cash Flow - CapEx (TTM)
        # FCF is the most important cash flow metric for valuation
        
        # Try yfinance first (most reliable and FREE)
        metrics['free_cash_flow'] = self._safe_float(yf_data.get('free_cash_flow', 0))
        if metrics['free_cash_flow'] != 0:
            print(f"   ✅ yfinance: Free Cash Flow = ${metrics['free_cash_flow']:,.0f}")
        
        # Try Finnhub (most reliable for TTM)
        capex = self._safe_float(finnhub_data.get('capitalExpenditureTTM', 0))
        
        # Try Massive API
        if capex == 0:
            capex = self._safe_float(massive_data.get('capital_expenditure', 0))
        if capex == 0:
            capex = self._safe_float(massive_data.get('capital_expenditures', 0))
        if capex == 0:
            capex = self._safe_float(massive_data.get('capex', 0))
        if capex == 0:
            capex = self._safe_float(massive_data.get('payments_to_acquire_property_plant_and_equipment', 0))
        if capex == 0:
            capex = self._safe_float(massive_data.get('purchase_of_property_plant_equipment', 0))
        if capex == 0:
            capex = self._safe_float(massive_data.get('payments_for_property_plant_and_equipment', 0))
        
        # Try AlphaVantage
        if capex == 0:
            capex = abs(self._safe_float(av_data.get('capital_expenditures', 0)))
        if capex == 0:
            capex = abs(self._safe_float(av_data.get('capitalExpenditures', 0)))
        
        # CapEx is often buried in investing activities (usually negative)
        if capex == 0:
            investing_cf = self._safe_float(massive_data.get('net_cash_used_for_investing_activities', 0))
            if investing_cf == 0:
                investing_cf = self._safe_float(massive_data.get('net_cash_from_investing_activities', 0))
            if investing_cf == 0:
                investing_cf = self._safe_float(massive_data.get('investing_activities_cash_flow', 0))
            
            # CapEx is typically 60-90% of investing CF for most companies
            if investing_cf < 0:  # Negative = cash outflow
                capex = abs(investing_cf) * 0.75  # Conservative 75% estimate
                print(f"   📊 ESTIMATED: CapEx = 75% of Investing CF = ${capex:,.0f}")
        
        # Industry-based estimation (last resort)
        if capex == 0 and metrics['revenue'] > 0:
            # CapEx intensity varies by industry:
            # Tech/Software: 2-4%, Manufacturing: 5-8%, Utilities: 10-15%
            # Use conservative 5% for unknown industries
            capex = metrics['revenue'] * 0.05
            print(f"   📊 ESTIMATED: CapEx = 5% of Revenue = ${capex:,.0f}")
        
        # Store CapEx in metrics
        metrics['capex'] = abs(capex)
        
        # Calculate Free Cash Flow (only if yfinance didn't already provide it)
        if metrics['free_cash_flow'] == 0:
            if metrics['operating_cash_flow'] > 0:
                metrics['free_cash_flow'] = metrics['operating_cash_flow'] - abs(capex)
                
                # Validation: FCF should be reasonable
                fcf_margin = (metrics['free_cash_flow'] / metrics['revenue'] * 100) if metrics['revenue'] > 0 else 0
                
                if fcf_margin < -20 or fcf_margin > 50:
                    print(f"   ⚠️ WARNING: FCF Margin = {fcf_margin:.1f}% (unusual, verify CapEx)")
                else:
                    print(f"   ✅ Free CF: ${metrics['free_cash_flow']:,.0f} (FCF Margin: {fcf_margin:.1f}%)")
                
                print(f"      Operating CF: ${metrics['operating_cash_flow']:,.0f}, CapEx: ${capex:,.0f}")
            else:
                print(f"   ⚠️ WARNING: Cannot calculate FCF (Operating CF = 0)")
        else:
            # FCF already provided by yfinance, just validate
            fcf_margin = (metrics['free_cash_flow'] / metrics['revenue'] * 100) if metrics['revenue'] > 0 else 0
            print(f"   ✅ Free CF (yfinance): ${metrics['free_cash_flow']:,.0f} (FCF Margin: {fcf_margin:.1f}%)")
        
        # Ensure FCF is set (shouldn't be None)
        if metrics.get('free_cash_flow') is None:
            metrics['free_cash_flow'] = 0.0
        
        # Operating CF Ratio = Operating Cash Flow / Current Liabilities
        # Measures ability to cover short-term obligations with operating cash
        # Healthy ratio: > 0.4 (can cover 40%+ of current liabilities annually)
        
        # Try Finnhub first (TTM data)
        current_liabilities = self._safe_float(finnhub_data.get('totalCurrentLiabilitiesTTM', 0))
        
        # Try Massive API
        if current_liabilities == 0:
            current_liabilities = self._safe_float(massive_data.get('current_liabilities', 0))
        if current_liabilities == 0:
            current_liabilities = self._safe_float(massive_data.get('total_current_liabilities', 0))
        if current_liabilities == 0:
            current_liabilities = self._safe_float(massive_data.get('liabilities_current', 0))
        
        # Calculate from Current Ratio if available
        if current_liabilities == 0:
            current_assets = self._safe_float(massive_data.get('current_assets', 0))
            if current_assets == 0:
                current_assets = self._safe_float(massive_data.get('total_current_assets', 0))
            
            current_ratio = self._safe_float(finnhub_data.get('currentRatioTTM', 0))
            
            if current_assets > 0 and current_ratio > 0:
                current_liabilities = current_assets / current_ratio
                print(f"   📊 CALCULATED: Current Liabilities = ${current_liabilities:,.0f}")
        
        if current_liabilities > 0 and metrics['operating_cash_flow'] > 0:
            metrics['operating_cf_ratio'] = metrics['operating_cash_flow'] / current_liabilities
            
            # Interpretation
            if metrics['operating_cf_ratio'] > 0.4:
                status = "✅ Strong"
            elif metrics['operating_cf_ratio'] > 0.2:
                status = "🟡 Adequate"
            else:
                status = "⚠️ Weak"
            
            print(f"   {status} Operating CF Ratio: {metrics['operating_cf_ratio']:.2f}")
        else:
            metrics['operating_cf_ratio'] = 0.0
            print(f"   ⚠️ WARNING: Cannot calculate Operating CF Ratio")
        
        # CF to Debt Ratio = Operating Cash Flow / Total Debt
        # Measures ability to pay off debt with operating cash flow
        # Healthy ratio: > 0.2 (can pay off 20%+ of debt annually)
        
        # Try Finnhub first (TTM data)
        total_debt = self._safe_float(finnhub_data.get('totalDebtTTM', 0))
        if total_debt == 0:
            total_debt = self._safe_float(finnhub_data.get('totalDebt', 0))
        
        # Try Massive API
        if total_debt == 0:
            total_debt = self._safe_float(massive_data.get('total_debt', 0))
        if total_debt == 0:
            # Total Debt = Long-term Debt + Short-term Debt
            long_term_debt = self._safe_float(massive_data.get('long_term_debt', 0))
            if long_term_debt == 0:
                long_term_debt = self._safe_float(massive_data.get('longterm_debt', 0))
            
            short_term_debt = self._safe_float(massive_data.get('short_term_debt', 0))
            if short_term_debt == 0:
                short_term_debt = self._safe_float(massive_data.get('shortterm_debt', 0))
            
            total_debt = long_term_debt + short_term_debt
        
        # Calculate from D/E ratio if available
        if total_debt == 0:
            total_equity = self._safe_float(massive_data.get('total_equity', 0))
            if total_equity == 0:
                total_equity = self._safe_float(massive_data.get('total_stockholder_equity', 0))
            
            de_ratio = self._safe_float(finnhub_data.get('debtEquityTTM', 0))
            
            if total_equity > 0 and de_ratio > 0:
                total_debt = total_equity * de_ratio
                print(f"   📊 CALCULATED: Total Debt = ${total_debt:,.0f} (from D/E ratio)")
        
        if total_debt > 0 and metrics['operating_cash_flow'] > 0:
            metrics['cf_to_debt'] = metrics['operating_cash_flow'] / total_debt
            
            # Interpretation
            if metrics['cf_to_debt'] > 0.25:
                status = "✅ Excellent"
            elif metrics['cf_to_debt'] > 0.15:
                status = "🟡 Good"
            elif metrics['cf_to_debt'] > 0.08:
                status = "🟠 Fair"
            else:
                status = "⚠️ Weak"
            
            print(f"   {status} CF to Debt: {metrics['cf_to_debt']:.2f} (Debt payoff: {metrics['cf_to_debt']*100:.1f}% annually)")
        else:
            metrics['cf_to_debt'] = 0.0
            if total_debt == 0:
                print(f"   ℹ️ INFO: No debt detected (CF to Debt = N/A)")
            else:
                print(f"   ⚠️ WARNING: Cannot calculate CF to Debt")
        
        # ========== PER-SHARE METRICS ==========
        
        # EPS (Earnings Per Share)
        metrics['eps'] = self._safe_float(av_data.get('eps', 0))
        if metrics['eps'] == 0:
            metrics['eps'] = self._safe_float(av_data.get('diluted_eps', 0))
        if metrics['eps'] == 0:
            metrics['eps'] = self._safe_float(finnhub_data.get('epsBasicExclExtraItemsTTM', 0))
        
        # Projected EPS Growth (5-year estimate)
        metrics['projected_eps'] = self._safe_float(finnhub_data.get('epsGrowth5Y', 0))
        if metrics['projected_eps'] == 0:
            metrics['projected_eps'] = self._safe_float(finnhub_data.get('epsGrowthTTMYoy', 0))
        
        # Revenue Per Share
        metrics['revenue_per_share'] = self._safe_float(av_data.get('revenue_per_share', 0))
        if metrics['revenue_per_share'] == 0:
            metrics['revenue_per_share'] = self._safe_float(finnhub_data.get('revenuePerShareTTM', 0))
        
        # Cash Flow Per Share
        shares_outstanding = self._safe_float(av_data.get('shares_outstanding', 0))
        if shares_outstanding == 0:
            shares_outstanding = self._safe_float(massive_data.get('shares_outstanding', 0))
        if shares_outstanding > 0 and metrics['operating_cash_flow'] > 0:
            metrics['cashflow_per_share'] = metrics['operating_cash_flow'] / shares_outstanding
        else:
            metrics['cashflow_per_share'] = 0.0
        
        # Book Value Per Share
        total_equity = self._safe_float(massive_data.get('total_equity', 0))
        if total_equity == 0:
            total_equity = self._safe_float(massive_data.get('stockholders_equity', 0))
        if shares_outstanding > 0 and total_equity > 0:
            metrics['book_value_per_share'] = total_equity / shares_outstanding
        else:
            metrics['book_value_per_share'] = 0.0
        
        # ========== GROWTH METRICS ==========
        
        # Revenue Growth YoY (percentage)
        metrics['revenue_growth'] = self._safe_float(av_data.get('quarterly_revenue_growth', 0))
        if metrics['revenue_growth'] == 0:
            metrics['revenue_growth'] = self._safe_float(finnhub_data.get('revenueGrowthTTMYoy', 0))
        if metrics['revenue_growth'] == 0:
            metrics['revenue_growth'] = self._safe_float(finnhub_data.get('revenueGrowth5Y', 0))
        
        # EPS Growth YoY (percentage)
        metrics['eps_growth'] = self._safe_float(av_data.get('quarterly_earnings_growth', 0))
        if metrics['eps_growth'] == 0:
            metrics['eps_growth'] = self._safe_float(finnhub_data.get('epsGrowthTTMYoy', 0))
        if metrics['eps_growth'] == 0:
            metrics['eps_growth'] = self._safe_float(finnhub_data.get('epsGrowthQuarterlyYoy', 0))
        
        # ========== MARKET METRICS ==========
        
        # Market Cap
        metrics['market_cap'] = self._safe_float(av_data.get('market_cap', 0))
        if metrics['market_cap'] == 0:
            metrics['market_cap'] = self._safe_float(finnhub_data.get('marketCapitalization', 0))
        
        # Beta (volatility measure)
        metrics['beta'] = self._safe_float(av_data.get('beta', 0))
        if metrics['beta'] == 0:
            metrics['beta'] = self._safe_float(finnhub_data.get('beta', 0))
        
        # Dividend Yield (percentage)
        metrics['dividend_yield'] = self._safe_float(av_data.get('dividend_yield', 0))
        if metrics['dividend_yield'] == 0:
            metrics['dividend_yield'] = self._safe_float(finnhub_data.get('dividendYieldIndicatedAnnual', 0))
        
        # Dividend Per Share
        metrics['dividend_per_share'] = self._safe_float(av_data.get('dividend_per_share', 0))
        if metrics['dividend_per_share'] == 0:
            metrics['dividend_per_share'] = self._safe_float(finnhub_data.get('dividendPerShareAnnual', 0))
        
        # ========== EFFICIENCY METRICS ==========
        
        # Asset Turnover = Revenue / Total Assets
        total_assets = self._safe_float(massive_data.get('total_assets', 0))
        if total_assets > 0 and metrics['revenue'] > 0:
            metrics['asset_turnover'] = metrics['revenue'] / total_assets
        else:
            metrics['asset_turnover'] = 0.0
        
        # Inventory Turnover
        metrics['inventory_turnover'] = self._safe_float(finnhub_data.get('inventoryTurnoverTTM', 0))
        if metrics['inventory_turnover'] == 0:
            metrics['inventory_turnover'] = self._safe_float(finnhub_data.get('inventoryTurnoverAnnual', 0))
        
        # ========== EV/EBITDA CALCULATION (Must be last after debt and cash are known) ==========
        metrics['enterprise_value'] = self._safe_float(av_data.get('enterprise_value', 0))
        
        # Calculate EV manually if not available
        # EV = Market Cap + Total Debt - Cash
        if metrics['enterprise_value'] == 0:
            market_cap = self._safe_float(av_data.get('market_cap', 0))
            if market_cap == 0:
                market_cap = self._safe_float(finnhub_data.get('marketCapitalization', 0)) * 1_000_000  # Finnhub returns in millions
            
            # Get total debt using debt_to_equity ratio (already calculated)
            total_debt = 0
            if metrics.get('debt_to_equity', 0) > 0:
                total_equity = self._safe_float(massive_data.get('total_equity', 0))
                if total_equity == 0:
                    total_equity = self._safe_float(massive_data.get('stockholders_equity', 0))
                if total_equity > 0:
                    total_debt = metrics['debt_to_equity'] * total_equity
            
            # Get cash using cash_ratio (already calculated)
            cash = 0
            if metrics.get('cash_ratio', 0) > 0:
                current_liabilities = self._safe_float(massive_data.get('current_liabilities', 0))
                if current_liabilities > 0:
                    cash = metrics['cash_ratio'] * current_liabilities
            
            if market_cap > 0:
                metrics['enterprise_value'] = market_cap + total_debt - cash
                if metrics['enterprise_value'] > 0:
                    print(f"   📊 CALCULATED: Enterprise Value = Market Cap (${market_cap:,.0f}) + Debt (${total_debt:,.0f}) - Cash (${cash:,.0f}) = ${metrics['enterprise_value']:,.0f}")
        
        # Calculate EV/EBITDA
        if metrics.get('ebitda', 0) > 0 and metrics['enterprise_value'] > 0:
            metrics['ev_ebitda'] = metrics['enterprise_value'] / metrics['ebitda']
            print(f"   ✅ EV/EBITDA: {metrics['ev_ebitda']:.2f}")
        else:
            metrics['ev_ebitda'] = 0.0
        
        return metrics

    def format_for_display(self, metrics: Dict) -> Dict:
        """Format metrics for dashboard display with proper units"""
        formatted = {}
        
        for key, value in metrics.items():
            val = self._safe_float(value)
            
            # Ratios (no unit)
            if any(x in key for x in ['ratio', 'beta', 'turnover', 'coverage', 'multiplier']):
                formatted[key] = f"{val:.2f}" if val != 0 else "N/A"
            
            # Percentages (multiply by 100 if stored as decimal)
            elif any(x in key for x in ['margin', 'growth', 'roe', 'roa', 'roic', 'yield', 'ownership', 'insider', 'institutional']):
                # Check if value is already in percentage form (>1) or decimal form (<1)
                if 0 < val < 1:
                    # Stored as decimal (e.g., 0.152), convert to percentage
                    formatted[key] = f"{val*100:.2f}%"
                elif val >= 1:
                    # Already in percentage form (e.g., 15.2)
                    formatted[key] = f"{val:.2f}%"
                else:
                    formatted[key] = "N/A"
            
            # Large currency values (Market Cap, EBITDA, Revenue, Cash Flow)
            # BUT NOT ev_ebitda which is a ratio
            elif any(x in key for x in ['cap', 'ebitda', 'revenue', 'cash_flow', 'enterprise_value']) and 'ev_ebitda' not in key:
                if val >= 1e12:
                    formatted[key] = f"${val/1e12:.2f}T"
                elif val >= 1e9:
                    formatted[key] = f"${val/1e9:.2f}B"
                elif val >= 1e6:
                    formatted[key] = f"${val/1e6:.2f}M"
                elif val > 0:
                    formatted[key] = f"${val:,.0f}"
                else:
                    formatted[key] = "N/A"
            
            # Per-share values
            elif 'per_share' in key or key == 'eps':
                formatted[key] = f"${val:.2f}" if val != 0 else "N/A"
            
            # Projected EPS (growth rate, not dollar amount)
            elif 'projected_eps' in key:
                if 0 < val < 1:
                    formatted[key] = f"{val*100:.2f}%"
                elif val >= 1:
                    formatted[key] = f"{val:.2f}%"
                else:
                    formatted[key] = "N/A"
            
            # Default
            else:
                formatted[key] = f"{val:.2f}" if val != 0 else "N/A"
        
        return formatted
    
    def _get_empty_metrics(self):
        """Return empty metrics structure"""
        return {}
