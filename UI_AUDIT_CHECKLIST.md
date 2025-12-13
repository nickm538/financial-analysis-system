# UI AUDIT CHECKLIST - 100% Accuracy Verification

## FUNDAMENTALS TAB

### Valuation Metrics
- [ ] P/E Ratio - Display as ratio (e.g., "25.3"), not percentage
- [ ] PEG Ratio - Display as ratio (e.g., "1.5"), not percentage
- [ ] EV/EBITDA - Display as ratio (e.g., "12.5"), not percentage
- [ ] Price to Book - Display as ratio (e.g., "3.2"), not percentage
- [ ] Price to Sales - Display as ratio (e.g., "5.1"), not percentage

### Profitability Metrics
- [ ] Net Profit Margin - Display as percentage (e.g., "15.2%")
- [ ] Operating Margin - Display as percentage (e.g., "20.5%")
- [ ] EBITDA Margin - Display as percentage (e.g., "25.3%")
- [ ] ROE - Display as percentage (e.g., "18.5%")
- [ ] ROA - Display as percentage (e.g., "12.3%")
- [ ] ROIC - Display as percentage (e.g., "14.7%")

### Liquidity Metrics
- [ ] Current Ratio - Display as ratio (e.g., "2.5"), interpretation correct
- [ ] Quick Ratio - Display as ratio (e.g., "1.8"), interpretation correct
- [ ] Cash Ratio - Display as ratio (e.g., "0.9"), interpretation correct

### Leverage & Solvency
- [ ] Debt-to-Equity - Display as ratio (e.g., "0.5" or "50%"), consistent
- [ ] Debt-to-Assets - Display as ratio (e.g., "0.3" or "30%"), consistent
- [ ] Interest Coverage - Display as ratio (e.g., "8.5x")

### Growth Metrics
- [ ] Revenue Growth (YoY) - Display as percentage (e.g., "12.5%")
- [ ] EPS Growth (YoY) - Display as percentage (e.g., "15.3%")
- [ ] Projected EPS Growth - Display as percentage (e.g., "18.2%")

### Cash Flow Metrics
- [ ] Operating CF - Display as dollars with proper magnitude (e.g., "$45.2B" or "$45.2M")
- [ ] Free Cash Flow - Display as dollars with proper magnitude
- [ ] Operating CF Ratio - Display as ratio (e.g., "0.85")
- [ ] CF to Debt - Display as ratio (e.g., "0.42")

### Per-Share Metrics
- [ ] EPS - Display as dollars (e.g., "$5.23")
- [ ] Revenue Per Share - Display as dollars (e.g., "$25.50")
- [ ] Cash Flow Per Share - Display as dollars (e.g., "$6.75")
- [ ] Book Value Per Share - Display as dollars (e.g., "$18.25")

---

## TECHNICAL ANALYSIS TAB

### Momentum Indicators
- [ ] RSI - Display as 0-100 value (e.g., "65.3"), interpretation correct (>70 overbought, <30 oversold)
- [ ] MACD - Display with proper decimal places (e.g., "0.52")
- [ ] MACD Signal - Display with proper decimal places
- [ ] MACD Histogram - Display with proper decimal places
- [ ] Stochastic K - Display as 0-100 value (e.g., "75.2")
- [ ] Stochastic D - Display as 0-100 value (e.g., "72.8")
- [ ] CCI - Display as value (e.g., "+125.3" or "-85.2"), interpretation correct (>100 overbought, <-100 oversold)

### Trend Indicators
- [ ] ADX - Display as 0-100 value (e.g., "35.2"), interpretation correct (>25 strong trend)
- [ ] +DI - Display as value (e.g., "25.3")
- [ ] -DI - Display as value (e.g., "18.7")
- [ ] DMI Difference - Display as value (e.g., "+6.6")
- [ ] Williams %R - Display as -100 to 0 value (e.g., "-25.3"), interpretation correct (<-80 oversold, >-20 overbought)
- [ ] ATR - Display with proper decimal places (e.g., "2.35")
- [ ] Bollinger Bands - Display upper/middle/lower with proper decimals

### Volume Indicators
- [ ] OBV - Display as volume value (e.g., "1.2B" or "450M")
- [ ] VWAP - Display as price (e.g., "$278.37")

### Composite Indicators
- [ ] Ultimate Oscillator - Display as 0-100 value (e.g., "55.3")
- [ ] Awesome Oscillator - Display with proper decimals (e.g., "0.0234" or "-0.0156")
- [ ] Chaikin Oscillator - Display with proper decimals

---

## ORACLE SCANNER TAB

### Oracle Score & Grade
- [ ] Oracle Score - Display as 0-165 value (e.g., "125")
- [ ] Grade - Display as letter grade (e.g., "A+", "A", "A-", "B+", "C")
- [ ] Color coding - Correct colors for each grade

### Score Breakdown
- [ ] Float Score - Display as 0-20 value (e.g., "18")
- [ ] Volume Score - Display as 0-15 value (e.g., "12")
- [ ] News Score - Display as 0-25 value (e.g., "20")
- [ ] Sector Score - Display as 0-20 value (e.g., "15")
- [ ] Chart Score - Display as 0-15 value (e.g., "12")
- [ ] Intraday Score - Display as 0-5 value (e.g., "4")
- [ ] Risk/Reward Score - Display as 0-5 value (e.g., "5")

### Float Analysis
- [ ] Float - Display with proper magnitude (e.g., "14.76B", "2.39B", "450M")
- [ ] Float Size Category - Display as text (e.g., "Micro Cap", "Small Cap", "Mid Cap")
- [ ] Float Rotation - Display as percentage (e.g., "25.3%")
- [ ] Institutional Ownership - Display as percentage (e.g., "64.89%")
- [ ] Expected Move - Display as percentage (e.g., "+15.2%")

### News Catalysts
- [ ] Catalyst Grade - Display as letter grade (e.g., "A+", "A", "A-", "B+")
- [ ] Catalyst Score - Display as 0-100 value (e.g., "75")
- [ ] Sentiment - Display as text (e.g., "VERY_BULLISH", "BULLISH", "NEUTRAL")
- [ ] News headline - Display full headline
- [ ] News date - Display in readable format (e.g., "Dec 13, 2025 8:00 AM")

### Support/Resistance Levels
- [ ] Level Price - Display as price with proper decimals (e.g., "$278.37")
- [ ] Level Type - Display as text (e.g., "Resistance", "Support", "Pivot")
- [ ] Strength - Display as text with emoji (e.g., "Very Strong 🔴", "Strong 🟠", "Moderate 🟡")
- [ ] Distance - Display as percentage (e.g., "+0.5%" or "-1.2%")

### Position Analysis
- [ ] Current Price - Display as price (e.g., "$278.37")
- [ ] VWAP - Display as price (e.g., "$278.40")
- [ ] Position - Display as text (e.g., "AT_SUPPORT", "AT_RESISTANCE", "BETWEEN_LEVELS")
- [ ] VWAP Position - Display as text (e.g., "Above VWAP ✅", "Below VWAP ⚠️")

### Risk/Reward
- [ ] Entry Price - Display as price (e.g., "$278.50")
- [ ] Stop Loss - Display as price (e.g., "$275.00")
- [ ] Target Price - Display as price (e.g., "$296.00")
- [ ] Risk Amount - Display as dollars (e.g., "$3.50")
- [ ] Reward Amount - Display as dollars (e.g., "$17.50")
- [ ] Risk/Reward Ratio - Display as ratio (e.g., "5.0:1")
- [ ] Meets 5:1 - Display as Yes/No with color coding

### Position Sizing
- [ ] Account Size - Input as dollars (e.g., "$10,000")
- [ ] Risk Percentage - Input as percentage (e.g., "2%")
- [ ] Risk Amount - Display as dollars (e.g., "$200")
- [ ] Shares to Buy - Display as integer (e.g., "57")
- [ ] Position Value - Display as dollars (e.g., "$15,874.50")
- [ ] Position % of Account - Display as percentage (e.g., "15.87%")
- [ ] Warning if >25% - Display warning message

---

## UNIT CONVERSION RULES

### Percentages
- **Display as percentage when:** Margins, Growth rates, Ownership %, Returns (ROE, ROA, ROIC)
- **Format:** "15.2%" (one decimal place)
- **Backend:** Store as decimal (0.152) or percentage (15.2), convert for display

### Ratios
- **Display as ratio when:** P/E, PEG, Current Ratio, Quick Ratio, D/E, Interest Coverage
- **Format:** "25.3" or "25.3x" (one decimal place)
- **Backend:** Store as decimal, display as-is

### Dollars
- **Display with magnitude when:** Revenue, Market Cap, Cash Flow, Operating CF
- **Format:** "$45.2B", "$1.3M", "$450K" (one decimal place + magnitude)
- **Backend:** Store as full number, convert to B/M/K for display
- **Conversion:** Billions (≥1B), Millions (≥1M), Thousands (≥1K), Dollars (<1K)

### Prices
- **Display with 2 decimals:** Stock prices, VWAP, Support/Resistance levels
- **Format:** "$278.37" (two decimal places)
- **Backend:** Store as decimal, display with $ and 2 decimals

### Indicators (0-100 scale)
- **Display with 1 decimal:** RSI, Stochastic, ADX, CCI, Ultimate Oscillator
- **Format:** "65.3" (one decimal place)
- **Backend:** Store as decimal, display with 1 decimal

### Indicators (other scales)
- **MACD:** Display with 2-4 decimals (e.g., "0.5234")
- **Williams %R:** Display with 1 decimal (e.g., "-25.3")
- **Awesome Oscillator:** Display with 4 decimals (e.g., "0.0234")
- **ATR:** Display with 2 decimals (e.g., "2.35")

---

## INTERPRETATION RULES

### RSI
- **>70:** "⚠️ Overbought - Potential reversal"
- **50-70:** "✅ Bullish momentum"
- **30-50:** "📊 Neutral"
- **<30:** "🟢 Oversold - Potential bounce"

### ADX
- **>40:** "🔥 Very strong trend"
- **25-40:** "✅ Strong trend"
- **20-25:** "📊 Developing trend"
- **<20:** "⚠️ Weak trend / Ranging"

### Current Ratio
- **>3.0:** "✅ Excellent liquidity"
- **2.0-3.0:** "✅ Strong liquidity"
- **1.5-2.0:** "📊 Adequate liquidity"
- **1.0-1.5:** "⚠️ Moderate concerns"
- **<1.0:** "🔴 Critical liquidity crisis"

### Debt-to-Equity
- **<0.3:** "✅ Conservative leverage"
- **0.3-0.5:** "✅ Moderate leverage"
- **0.5-1.0:** "📊 Average leverage"
- **1.0-2.0:** "⚠️ High leverage"
- **>2.0:** "🔴 Very high leverage risk"

### Oracle Score
- **120-165:** "A+ 🚀 Maximum conviction"
- **100-119:** "A ✅ High conviction"
- **75-99:** "A- 🔥 Moderate conviction"
- **60-74:** "B+ 🟡 Watch closely"
- **<60:** "C 🔴 Avoid"

---

## DATA FLOW VERIFICATION

### Fundamentals Flow
1. **Backend:** `comprehensive_fundamentals_FIXED.py` → `calculate_all_metrics()`
2. **Returns:** Dictionary with all metrics
3. **Frontend:** `streamlit_dashboard_PRODUCTION_FIXED.py` → Tab 1
4. **Display:** `st.metric()` with proper formatting

### Technical Analysis Flow
1. **Backend:** `technical_analysis.py` → `analyze()`
2. **Uses:** `twelvedata_client.py` for indicators
3. **Returns:** Dictionary with normalized indicators
4. **Frontend:** `streamlit_dashboard_PRODUCTION_FIXED.py` → Tab 3
5. **Display:** `st.metric()` with proper formatting

### Oracle Scanner Flow
1. **Backend:** `oracle_algorithm.py` → `calculate_oracle_score()`
2. **Uses:** `oracle_levels.py`, `oracle_news.py`, `oracle_float.py`
3. **Returns:** Dictionary with score, grade, breakdown
4. **Frontend:** `streamlit_dashboard_PRODUCTION_FIXED.py` → Tab 6
5. **Display:** Custom layout with metrics and tables

---

## COMMON ISSUES TO FIX

### Issue 1: Percentage vs Decimal Confusion
- **Problem:** Backend returns 0.152, frontend displays "0.152" instead of "15.2%"
- **Fix:** Multiply by 100 and add "%" in frontend

### Issue 2: Magnitude Not Applied
- **Problem:** Backend returns 45200000000, frontend displays "$45200000000"
- **Fix:** Convert to "$45.2B" using magnitude function

### Issue 3: Wrong Decimal Places
- **Problem:** Price displays as "$278.3" instead of "$278.37"
- **Fix:** Use `.2f` format for prices

### Issue 4: Missing Interpretation
- **Problem:** RSI displays "75.3" with no context
- **Fix:** Add interpretation text based on value ranges

### Issue 5: Incorrect Color Coding
- **Problem:** Negative values show in green, positive in red
- **Fix:** Reverse color logic for proper interpretation

### Issue 6: N/A vs 0 Confusion
- **Problem:** Missing data displays as "0" instead of "N/A"
- **Fix:** Check for None/0 and display "N/A" for missing data

### Issue 7: Unit Mismatch
- **Problem:** Backend calculates in millions, frontend assumes billions
- **Fix:** Ensure consistent units throughout data flow

---

## TESTING CHECKLIST

### Test with AAPL
- [ ] All fundamentals display correctly
- [ ] All technical indicators display correctly
- [ ] Oracle Scanner displays correctly
- [ ] Units are consistent
- [ ] Interpretations are accurate

### Test with TSLA
- [ ] All fundamentals display correctly
- [ ] All technical indicators display correctly
- [ ] Oracle Scanner displays correctly
- [ ] Units are consistent
- [ ] Interpretations are accurate

### Test with Small Cap (<$1B)
- [ ] Magnitude displays correctly (M instead of B)
- [ ] Float analysis works
- [ ] Oracle Scanner works

### Test with Penny Stock (<$5)
- [ ] Price displays correctly (e.g., "$2.35" not "$2.3")
- [ ] Percentage moves display correctly
- [ ] Support/resistance levels accurate

---

## VALIDATION CRITERIA

### ✅ PASS Criteria
- All metrics display with correct units
- All percentages show "%" symbol
- All dollars show "$" symbol with proper magnitude
- All ratios display correctly (no % when shouldn't be)
- All interpretations are accurate and helpful
- All color coding is correct (green=good, red=bad)
- All N/A values display as "N/A" not "0"
- All data flows from backend to frontend correctly

### ❌ FAIL Criteria
- Any metric displays wrong units
- Any percentage missing "%" or shown as decimal
- Any dollar amount missing "$" or wrong magnitude
- Any ratio shown as percentage when it shouldn't be
- Any interpretation is incorrect or misleading
- Any color coding is reversed
- Any missing data shows as "0" instead of "N/A"
- Any data flow breaks or displays incorrect values

---

**AUDIT STATUS:** 🔄 IN PROGRESS
**NEXT STEP:** Systematically check each tab and fix issues
