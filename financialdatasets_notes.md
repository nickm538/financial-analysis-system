# FinancialDatasets.ai MCP Integration Notes

## Available Tools (16 total)

### Price Data
- `getStockPriceSnapshot` - Latest price, volume, OHLC
- `getStockPrices` - Historical price data with date range
- `getCryptoPriceSnapshot` - Latest crypto price
- `getCryptoPrices` - Historical crypto prices

### Financial Statements
- `getBalanceSheet` - Assets, liabilities, equity
- `getIncomeStatement` - Revenue, expenses, net income
- `getCashFlowStatement` - Operating, investing, financing cash flows

### Financial Metrics
- `getFinancialMetrics` - Historical P/E, EV, revenue per share
- `getFinancialMetricsSnapshot` - Current metrics snapshot

### Company Info
- `getCompanyFacts` - Market cap, employees, sector, industry
- `getSegmentedRevenues` - Revenue by segment/geography

### News & Filings
- `getNews` - Company-specific news articles
- `getFilings` - SEC filings (10-K, 10-Q, 8-K)
- `getFilingItems` - Extract specific sections from filings
- `getAvailableFilingItems` - List available filing sections

### Crypto
- `getAvailableCryptoTickers` - List supported crypto symbols

## Key Use Cases for Our System

1. **Enhance Sadie AI** - Real-time news, financial metrics, company facts
2. **Improve Fundamentals** - Balance sheet, income statement, cash flow
3. **News Sentiment** - getNews for catalyst detection
4. **SEC Filings** - Risk factors, business description for deeper analysis
5. **Segmented Revenue** - Understand business composition
