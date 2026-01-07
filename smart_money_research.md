# Smart Money Data Sources Research

## QuiverQuant API (api.quiverquant.com)
**FREE PUBLIC ENDPOINTS:**

### Congress Trading
- `GET /beta/live/congresstrading` - Recent Congress trades
- `GET /beta/historical/congresstrading/{ticker}` - Historical by ticker
- `GET /beta/live/housetrading` - Recent House trades
- `GET /beta/live/senatetrading` - Recent Senate trades
- `GET /beta/bulk/congresstrading` - Bulk download

**Response Fields:**
- Representative, ReportDate, TransactionDate
- Ticker, Transaction (Purchase/Sale), Range
- District, House, Amount, Party
- ExcessReturn, PriceChange, SPYChange

### Insider Trading
- `GET /beta/live/insidertrading` - Recent insider trades

### Institutional Holdings
- `GET /beta/live/sec13f` - Live SEC 13F filings
- `GET /beta/live/sec13fchanges` - Recent changes

### Dark Pool / Off-Exchange
- `GET /beta/live/offexchange` - Live off-exchange data
- `GET /beta/historical/offexchange/{ticker}` - Historical

### Other Useful
- `GET /beta/live/lobbying` - Corporate lobbying
- `GET /beta/live/govcontracts` - Government contracts

**Auth:** Bearer token required

---

## Yahoo Finance API (via Manus data_api)
- `YahooFinance/get_stock_holders` - Insider holdings, institutional, mutual funds
- `YahooFinance/get_stock_sec_filing` - SEC filings

---

## Data to Track for Each Stock:
1. **Congress Trades** - Recent buys/sells by politicians
2. **Insider Trades** - Form 4 filings (CEO, CFO, directors)
3. **Institutional Holdings** - 13F changes (hedge funds)
4. **Dark Pool Activity** - Off-exchange volume
5. **Unusual Options** - Large sweeps, unusual volume
6. **Short Interest** - Changes in short positions
