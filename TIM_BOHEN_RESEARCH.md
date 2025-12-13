# Tim Bohen Oracle Algorithm - Research Findings

## Source: StocksToTrade Official Platform

### Key Facts from Official Source

**Oracle Algorithm Specifications:**
- Scans 15,000 stocks every second
- Searches for 5-to-1 risk ratios (minimum)
- Generates approximately 15 trading opportunities per day
- 2,642 winning Oracle picks (historical performance)

**Tim Bohen's Trading Focus:**
- Multi-day runners (primary pattern)
- Afternoon breakouts
- Fundamental analysis integration
- Hot sector focus
- Disciplined, repeatable profits

### Critical Insights

1. **5:1 Risk/Reward is MANDATORY** - Not a guideline, but a hard filter
2. **15 opportunities/day** - This means VERY selective (out of 15,000 stocks scanned)
3. **Multi-day runners are primary pattern** - Not day-one runners
4. **Hot sectors are critical** - Stocks must be in current hot sectors
5. **Fundamental analysis matters** - Not just technical patterns

### Pattern Criteria (from research)

**Multi-Day Runner Requirements:**
1. Must be in a hot sector (current momentum)
2. First green day closes in top 10-20% of range
3. Volume surge 2-3x average minimum
4. Float <20M shares (smaller is better)
5. News catalyst present
6. 5:1 risk/reward ratio minimum
7. NOT a "one-and-done" - must have staying power

**Red-to-Green Reversal:**
1. Opens below previous close (red)
2. Wait for first red 5-minute candle after early spike
3. Use that candle's range (top and bottom) for entry and stop
4. Entry when price crosses above previous close
5. Stop below morning low
6. Target at previous day high or resistance

### Scoring Weight Insights

Based on "15 opportunities out of 15,000 stocks" (0.1% pass rate):

**Critical Factors (Must-Have):**
- 5:1 Risk/Reward: BINARY (pass/fail, not scored)
- Float <20M: BINARY (pass/fail)
- Volume Surge 2-3x: BINARY (pass/fail)

**Weighted Factors:**
- News Catalyst: HIGH weight (drives multi-day moves)
- Sector Momentum: HIGH weight (hot sector required)
- Chart Pattern: MODERATE weight (confirms setup)
- Float Size: MODERATE weight (smaller = better within <20M)

### Execution Rules

**Entry:**
- Wait for confirmation (not anticipation)
- Red-to-green: Enter when crosses above previous close
- Multi-day: Enter on first green day close in top 10-20% of range

**Stop Loss:**
- Always set BEFORE entry
- Red-to-green: Below morning low
- Multi-day: Below first green day low
- Never move stop loss down

**Exit:**
- Scale out at resistance levels
- Take profits at 5:1 (minimum target)
- Trail stop on runners
- Exit if pattern breaks

### Key Differences from My Initial Implementation

1. **5:1 is MANDATORY** - I had it as 40 points max, should be BINARY filter
2. **15 setups/day target** - Need much stricter filtering
3. **Hot sector is CRITICAL** - I had it as 15 points, needs to be higher
4. **Volume surge is 2-3x** - I had 3x, but 2x is acceptable
5. **Fundamental analysis matters** - Need to integrate earnings, revenue growth

### Recalibrated Scoring System

**New Approach: Two-Stage Filtering**

**Stage 1: BINARY Filters (Must Pass ALL)**
- 5:1 Risk/Reward: YES/NO
- Float <20M: YES/NO
- Volume >2x average: YES/NO
- News catalyst present: YES/NO

**Stage 2: Scoring (0-100 scale)**
- Float Size (0-25): Smaller is better within <20M
  - <5M: 25 pts
  - 5-10M: 20 pts
  - 10-15M: 15 pts
  - 15-20M: 10 pts
- Volume Surge (0-20): Higher is better
  - >5x: 20 pts
  - 4-5x: 18 pts
  - 3-4x: 15 pts
  - 2-3x: 10 pts
- News Catalyst (0-30): Impact matters
  - FDA/Acquisition/Major: 30 pts
  - Earnings beat/Partnership: 20 pts
  - Minor positive: 10 pts
- Sector Momentum (0-15): Hot sector required
  - Multiple runners in sector: 15 pts
  - Some activity: 10 pts
  - Weak: 5 pts
- Chart Pattern (0-10): Confirmation only
  - Perfect multi-day setup: 10 pts
  - Good setup: 7 pts
  - Acceptable: 5 pts

**Total: 100 points max**
**Threshold: 70+ = A+ Setup (top 0.1% of stocks)**

### Implementation Changes Needed

1. **Add BINARY filters before scoring**
2. **Reduce scoring weights** (was 0-165, now 0-100)
3. **Make 5:1 R/R a hard requirement**
4. **Increase news catalyst weight** (was 30/165, now 30/100)
5. **Add sector momentum detection** (scan for multiple runners)
6. **Integrate fundamental filters** (earnings, revenue growth)
7. **Stricter thresholds** (70+ instead of 75+)

### Data Sources Needed

**Real-Time:**
- TwelveData websocket for live prices
- Finnhub for news (real-time)
- Web scraping for float data (Yahoo Finance, Finviz)

**Fundamental:**
- Earnings surprises (AlphaVantage, Finnhub)
- Revenue growth (AlphaVantage)
- Sector performance (need to calculate from multiple stocks)

### Next Steps

1. Implement two-stage filtering (binary + scoring)
2. Add TwelveData websocket for real-time data
3. Web scrape float data from Yahoo Finance/Finviz
4. Build sector momentum scanner
5. Validate support/resistance with real charts
6. Remove all placeholders (sector_momentum = 0.7)
7. Test with live market data


## CRITICAL FINDINGS - Multi-Day Runner Article (Dec 13, 2024)

### VWAP Hold Scan - The Core Strategy

**Tim Bohen's Go-To Scan:**
"The VWAP hold scan identifies stocks closing strong—above VWAP, with good volume, news catalysts, and clean chart patterns."

**Key Criteria:**
1. **Closing above VWAP** - MANDATORY
2. **Good volume** - Must be unusual/elevated
3. **News catalysts** - Present and relevant
4. **Clean chart patterns** - No messy, choppy action

**Setup Prediction:**
"If a stock closes strong, holding VWAP, get ready for a textbook weak-open, red-to-green setup tomorrow."

### The Checklist (Tim's Exact Words)

**"When you check all your boxes:"**
1. Strong intraday action
2. Daily chart breakouts
3. Sector strength
4. Unusual volume

**"You're stacking the odds in your favor."**

### One-and-Dones vs Multi-Day Runners

**One-and-Done (AVOID):**
- Pops on news or catalyst
- Looks solid at first glance
- Good volume initially
- But chart history shows: Big spike, big fail
- "The only thing reliable about them is that they'll do what they did before and create a lot of bag holders"

**Multi-Day Runners (FOCUS):**
- About confirmation and simplicity
- May chop around and pull back
- When they retest resistance, they can really take off
- About discipline and proven staying power
- NOT chasing random moves

### Real Example: RGTI (Dec 2024)

**Oracle Signal:**
- Entry: $6.95
- Return: 13.52% (quick)
- Pattern: Multi-day runner in hot quantum computing sector
- Retested resistance and took off

### Implementation Changes Needed

1. **Add VWAP to criteria** - MANDATORY for multi-day runners
2. **Check chart history** - Avoid one-and-done patterns
3. **Sector strength is CRITICAL** - Not just "hot sector" but multiple runners
4. **Intraday action matters** - Strong closes, not just EOD price
5. **Daily chart breakouts** - Must be breaking out on daily timeframe
6. **Unusual volume** - Not just 2-3x, but UNUSUAL for that stock

### Revised Binary Filters

**MUST PASS ALL:**
1. Closes above VWAP ✓
2. 5:1 Risk/Reward ✓
3. Float <20M ✓
4. Volume >2x average (and UNUSUAL) ✓
5. News catalyst present ✓
6. NOT a one-and-done (check chart history) ✓
7. Sector has multiple runners (sector strength) ✓

### Revised Scoring (After Binary Filters Pass)

**Float Size (0-20):**
- <5M: 20 pts
- 5-10M: 16 pts
- 10-15M: 12 pts
- 15-20M: 8 pts

**Volume Surge (0-15):**
- >5x AND unusual: 15 pts
- 4-5x AND unusual: 12 pts
- 3-4x AND unusual: 10 pts
- 2-3x AND unusual: 7 pts

**News Catalyst Impact (0-25):**
- FDA/Acquisition/Major: 25 pts
- Earnings beat/Partnership: 18 pts
- Minor positive: 10 pts

**Sector Strength (0-20):** - INCREASED WEIGHT
- 3+ runners in sector today: 20 pts
- 2 runners in sector: 15 pts
- 1 runner in sector: 10 pts
- Weak sector: 5 pts

**Chart Pattern (0-15):**
- Perfect multi-day setup + VWAP hold: 15 pts
- Good setup + VWAP hold: 12 pts
- Acceptable setup: 8 pts
- Clean daily breakout: +5 bonus pts

**Intraday Action (0-5):** - NEW CATEGORY
- Strong close in top 20% of range: 5 pts
- Moderate close: 3 pts
- Weak close: 0 pts

**Total: 100 points max**
**Threshold: 75+ = A+ Setup**

### Critical Quote

"Multi-day runners aren't just about finding hot stocks—they're about discipline. They keep you from chasing random one-and-dones that fizzle out so you can focus your energy on setups with proven staying power."

### Action Items

1. Add VWAP calculation and hold detection
2. Implement chart history check (avoid one-and-dones)
3. Build sector strength scanner (count runners in same sector)
4. Add intraday action scoring (close position in range)
5. Validate daily chart breakout detection
6. Increase sector strength weight from 15 to 20 points
7. Add bonus points for clean daily breakouts
