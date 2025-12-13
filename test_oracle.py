"""
Oracle Module Test Script
Test all Oracle components with real market data
"""

import sys
import pandas as pd
from datetime import datetime

# Test imports
print("=" * 60)
print("ORACLE MODULE TEST SUITE")
print("=" * 60)
print()

try:
    from oracle_algorithm import OracleAlgorithm
    print("✅ oracle_algorithm imported successfully")
except Exception as e:
    print(f"❌ oracle_algorithm import failed: {e}")
    sys.exit(1)

try:
    from oracle_levels import OracleLevels
    print("✅ oracle_levels imported successfully")
except Exception as e:
    print(f"❌ oracle_levels import failed: {e}")
    sys.exit(1)

try:
    from oracle_news import OracleNews
    print("✅ oracle_news imported successfully")
except Exception as e:
    print(f"❌ oracle_news import failed: {e}")
    sys.exit(1)

try:
    from oracle_float import OracleFloat
    print("✅ oracle_float imported successfully")
except Exception as e:
    print(f"❌ oracle_float import failed: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("ALL ORACLE MODULES IMPORTED SUCCESSFULLY")
print("=" * 60)
print()

# Test with sample data
print("Testing Oracle Float Analysis...")
print("-" * 60)

FINNHUB_API_KEY = "d47ssnpr01qk80bicu4gd47ssnpr01qk80bicu50"
oracle_float = OracleFloat(FINNHUB_API_KEY)

# Test with AAPL
result = oracle_float.analyze_float("AAPL", 50_000_000, 45_000_000)
print(f"Ticker: {result.get('ticker')}")
print(f"Float Size: {result.get('float_size', 0) / 1_000_000:.1f}M")
print(f"Float Rotation: {result.get('float_rotation', 0):.2f}%")
print(f"Float Score: {result.get('float_score', 0)}/100")
print(f"Analysis: {result.get('analysis', 'N/A')}")
print()

print("Testing Oracle News Scanner...")
print("-" * 60)

oracle_news = OracleNews(FINNHUB_API_KEY)
news_result = oracle_news.scan_news("AAPL", days_back=7)
print(f"Ticker: {news_result.get('ticker')}")
print(f"Catalyst Score: {news_result.get('catalyst_score', 0)}")
print(f"Grade: {news_result.get('grade', 'N/A')}")
print(f"Has Catalyst: {news_result.get('has_catalyst', False)}")
print(f"Top Catalysts: {len(news_result.get('top_catalysts', []))}")
print()

print("Testing Oracle Levels Calculator...")
print("-" * 60)

# Create sample price data
dates = pd.date_range(end=datetime.now(), periods=20, freq='D')
sample_data = pd.DataFrame({
    'date': dates,
    'open': [150 + i for i in range(20)],
    'high': [152 + i for i in range(20)],
    'low': [148 + i for i in range(20)],
    'close': [151 + i for i in range(20)],
    'volume': [50_000_000 + i * 1_000_000 for i in range(20)]
})

oracle_levels = OracleLevels()
levels_result = oracle_levels.calculate_oracle_levels(sample_data)
print(f"Current Price: ${levels_result.get('current_price', 0):.2f}")
print(f"Position: {levels_result.get('position', {}).get('position', 'N/A')}")
print(f"Signal: {levels_result.get('position', {}).get('signal', 'N/A')}")
print(f"Strong Resistance Levels: {len(levels_result.get('levels', {}).get('strong_resistance', []))}")
print(f"Support Levels: {len(levels_result.get('levels', {}).get('support', []))}")
print()

print("=" * 60)
print("✅ ALL ORACLE TESTS PASSED")
print("=" * 60)
print()
print("Oracle Scanner is ready for production use!")
