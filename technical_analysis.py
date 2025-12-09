"""
TECHNICAL ANALYSIS MODULE v4.0 - COMPLETE NORMALIZATION
========================================================
✅ Integrates TwelveData API for all indicators
✅ Proper normalization of all indicator values
✅ Handles nested and flat data structures
✅ Ensures no null values in output
✅ World-class technical analysis formulations
"""

from twelvedata_client import TwelveDataClient
from typing import Dict, Any, Optional
import numpy as np

class TechnicalAnalysis:
    """
    Professional technical analysis using TwelveData API.
    Provides normalized, dashboard-ready indicator data.
    """
    
    def __init__(self):
        self.td_client = TwelveDataClient()
        self.use_twelvedata = True
    
    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        if value is None or value == '' or value == 'None':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_all_indicators(self, symbol: str, interval: str = "1day") -> Dict:
        """
        Primary method - Fetch all indicators from TwelveData and normalize.
        Returns dashboard-compatible format with no null values.
        """
        if self.use_twelvedata:
            result = self.td_client.get_all_for_dashboard(symbol, interval)
            return self._normalize_twelvedata_response(result)
        else:
            # Fallback to local calculation (not recommended)
            return self._local_calculation_fallback(symbol)
    
    def _normalize_twelvedata_response(self, result: Dict) -> Dict:
        """
        Normalize TwelveData response to ensure consistent structure.
        Handles nested values and ensures no nulls.
        """
        indicators = result.get('indicators', {})
        patterns = result.get('patterns', {})
        
        normalized = {
            'indicators': {},
            'patterns': patterns
        }
        
        # ========== MOMENTUM INDICATORS ==========
        
        # RSI - Direct float value
        normalized['indicators']['rsi'] = self._safe_float(indicators.get('rsi', 50.0))
        
        # Stochastic RSI - Nested structure
        stochrsi = indicators.get('stochrsi', {})
        if isinstance(stochrsi, dict):
            normalized['indicators']['stochrsi'] = {
                'valueK': self._safe_float(stochrsi.get('valueK', 50.0)),
                'valueD': self._safe_float(stochrsi.get('valueD', 50.0))
            }
        else:
            normalized['indicators']['stochrsi'] = {'valueK': 50.0, 'valueD': 50.0}
        
        # MACD - Nested structure with MACD, Signal, and Histogram
        macd = indicators.get('macd', {})
        if isinstance(macd, dict):
            normalized['indicators']['macd'] = {
                'valueMACD': self._safe_float(macd.get('valueMACD', 0.0)),
                'valueMACDSignal': self._safe_float(macd.get('valueMACDSignal', 0.0)),
                'valueMACDHist': self._safe_float(macd.get('valueMACDHist', 0.0))
            }
        else:
            normalized['indicators']['macd'] = {
                'valueMACD': 0.0,
                'valueMACDSignal': 0.0,
                'valueMACDHist': 0.0
            }
        
        # CCI - Direct float value
        normalized['indicators']['cci'] = self._safe_float(indicators.get('cci', 0.0))
        
        # Stochastic Oscillator - Nested structure
        stoch = indicators.get('stoch', {})
        if isinstance(stoch, dict):
            normalized['indicators']['stoch'] = {
                'valueK': self._safe_float(stoch.get('valueK', 50.0)),
                'valueD': self._safe_float(stoch.get('valueD', 50.0))
            }
        else:
            normalized['indicators']['stoch'] = {'valueK': 50.0, 'valueD': 50.0}
        
        # Williams %R - Direct float value (typically -100 to 0)
        normalized['indicators']['williams_r'] = self._safe_float(indicators.get('williams_r', -50.0))
        
        # ========== TREND INDICATORS ==========
        
        # ADX - Nested structure with single value
        adx = indicators.get('adx', {})
        if isinstance(adx, dict):
            normalized['indicators']['adx'] = {
                'value': self._safe_float(adx.get('value', 0.0))
            }
        else:
            normalized['indicators']['adx'] = {'value': self._safe_float(adx, 0.0)}
        
        # DMI - Nested structure with Plus DI, Minus DI, and net value
        dmi = indicators.get('dmi', {})
        if isinstance(dmi, dict):
            normalized['indicators']['dmi'] = {
                'plus_di': self._safe_float(dmi.get('plus_di', 0.0)),
                'minus_di': self._safe_float(dmi.get('minus_di', 0.0)),
                'value': self._safe_float(dmi.get('value', 0.0))
            }
        else:
            normalized['indicators']['dmi'] = {
                'plus_di': 0.0,
                'minus_di': 0.0,
                'value': 0.0
            }
        
        # Bollinger Bands - Nested structure with upper, middle, lower
        bbands = indicators.get('bbands', {})
        if isinstance(bbands, dict):
            normalized['indicators']['bbands'] = {
                'upper': self._safe_float(bbands.get('upper', 0.0)),
                'middle': self._safe_float(bbands.get('middle', 0.0)),
                'lower': self._safe_float(bbands.get('lower', 0.0))
            }
        else:
            normalized['indicators']['bbands'] = {
                'upper': 0.0,
                'middle': 0.0,
                'lower': 0.0
            }
        
        # ATR - Direct float value
        normalized['indicators']['atr'] = self._safe_float(indicators.get('atr', 0.0))
        
        # EMA - Direct float value
        normalized['indicators']['ema'] = self._safe_float(indicators.get('ema', 0.0))
        
        # SMA - Direct float value
        normalized['indicators']['sma'] = self._safe_float(indicators.get('sma', 0.0))
        
        # ========== VOLUME INDICATORS ==========
        
        # OBV - Direct float value
        normalized['indicators']['obv'] = self._safe_float(indicators.get('obv', 0.0))
        
        # ========== COMPOSITE INDICATORS ==========
        
        # Ultimate Oscillator - Direct float value (0-100)
        normalized['indicators']['ultimate_oscillator'] = self._safe_float(
            indicators.get('ultimate_oscillator', 50.0)
        )
        
        # Awesome Oscillator - Direct float value
        normalized['indicators']['awesome_oscillator'] = self._safe_float(
            indicators.get('awesome_oscillator', 0.0)
        )
        
        # Chaikin Oscillator - Direct float value
        normalized['indicators']['chaikin_oscillator'] = self._safe_float(
            indicators.get('chaikin_oscillator', 0.0)
        )
        
        # ========== PRICE INDICATORS ==========
        
        # VWAP - Direct float value
        normalized['indicators']['vwap'] = self._safe_float(indicators.get('vwap', 0.0))
        
        return normalized
    
    def _local_calculation_fallback(self, symbol: str) -> Dict:
        """
        Fallback method for local calculation if TwelveData unavailable.
        Returns minimal structure with default values.
        """
        print(f"⚠️ Using local calculation fallback for {symbol}")
        return {
            'indicators': {
                'rsi': 50.0,
                'macd': {'valueMACD': 0.0, 'valueMACDSignal': 0.0, 'valueMACDHist': 0.0},
                'adx': {'value': 0.0},
                'stoch': {'valueK': 50.0, 'valueD': 50.0},
                'stochrsi': {'valueK': 50.0, 'valueD': 50.0},
                'williams_r': -50.0,
                'cci': 0.0,
                'bbands': {'upper': 0.0, 'middle': 0.0, 'lower': 0.0},
                'atr': 0.0,
                'obv': 0.0,
                'ema': 0.0,
                'sma': 0.0,
                'dmi': {'plus_di': 0.0, 'minus_di': 0.0, 'value': 0.0},
                'ultimate_oscillator': 50.0,
                'awesome_oscillator': 0.0,
                'chaikin_oscillator': 0.0
            },
            'patterns': {}
        }
    
    def interpret_rsi(self, rsi: float) -> tuple:
        """Interpret RSI value"""
        if rsi <= 30:
            return ("OVERSOLD", "🟢", "Strong buy signal - RSI indicates oversold conditions")
        elif rsi <= 40:
            return ("WEAK", "🟡", "Potential buy - RSI showing weakness")
        elif rsi >= 70:
            return ("OVERBOUGHT", "🔴", "Caution - RSI indicates overbought conditions")
        elif rsi >= 60:
            return ("STRONG", "🟡", "Strong momentum - RSI elevated")
        else:
            return ("NEUTRAL", "⚪", "RSI in neutral range")
    
    def interpret_macd(self, macd: float, signal: float) -> tuple:
        """Interpret MACD crossover"""
        if macd > signal and macd > 0:
            return ("BULLISH", "🟢", "Bullish crossover - MACD above signal and zero")
        elif macd > signal:
            return ("BULLISH_WEAK", "🟡", "Bullish crossover - MACD above signal")
        elif macd < signal and macd < 0:
            return ("BEARISH", "🔴", "Bearish crossover - MACD below signal and zero")
        elif macd < signal:
            return ("BEARISH_WEAK", "🟡", "Bearish crossover - MACD below signal")
        else:
            return ("NEUTRAL", "⚪", "MACD and signal converging")
    
    def interpret_adx(self, adx: float) -> tuple:
        """Interpret ADX trend strength"""
        if adx > 40:
            return ("VERY_STRONG", "🟢", "Very strong trend - ADX above 40")
        elif adx > 25:
            return ("STRONG", "🟢", "Strong trend - ADX above 25")
        elif adx > 20:
            return ("MODERATE", "🟡", "Moderate trend - ADX above 20")
        else:
            return ("WEAK", "🔴", "Weak trend - ADX below 20")
    
    def interpret_stochastic(self, k: float, d: float) -> tuple:
        """Interpret Stochastic Oscillator"""
        if k < 20 and d < 20:
            return ("OVERSOLD", "🟢", "Oversold - Both K and D below 20")
        elif k > 80 and d > 80:
            return ("OVERBOUGHT", "🔴", "Overbought - Both K and D above 80")
        elif k > d:
            return ("BULLISH", "🟡", "Bullish - K crossing above D")
        elif k < d:
            return ("BEARISH", "🟡", "Bearish - K crossing below D")
        else:
            return ("NEUTRAL", "⚪", "Neutral stochastic position")
    
    def interpret_williams_r(self, williams: float) -> tuple:
        """Interpret Williams %R"""
        if williams < -80:
            return ("OVERSOLD", "🟢", "Oversold - Williams %R below -80")
        elif williams > -20:
            return ("OVERBOUGHT", "🔴", "Overbought - Williams %R above -20")
        else:
            return ("NEUTRAL", "⚪", "Neutral Williams %R range")
    
    def interpret_dmi(self, plus_di: float, minus_di: float) -> tuple:
        """Interpret DMI (Directional Movement Index)"""
        if plus_di > minus_di and plus_di > 25:
            return ("STRONG_BULLISH", "🟢", "Strong uptrend - +DI dominates")
        elif plus_di > minus_di:
            return ("BULLISH", "🟡", "Uptrend - +DI above -DI")
        elif minus_di > plus_di and minus_di > 25:
            return ("STRONG_BEARISH", "🔴", "Strong downtrend - -DI dominates")
        elif minus_di > plus_di:
            return ("BEARISH", "🟡", "Downtrend - -DI above +DI")
        else:
            return ("NEUTRAL", "⚪", "No clear directional movement")
    
    def interpret_composite_oscillator(self, value: float, indicator_name: str) -> tuple:
        """Interpret composite oscillators (Ultimate, Awesome, Chaikin)"""
        if indicator_name == "ultimate_oscillator":
            # Ultimate Oscillator: 0-100 scale
            if value < 30:
                return ("OVERSOLD", "🟢", "Oversold - Below 30")
            elif value > 70:
                return ("OVERBOUGHT", "🔴", "Overbought - Above 70")
            else:
                return ("NEUTRAL", "⚪", "Neutral range")
        else:
            # Awesome and Chaikin: Centered around zero
            if value > 0:
                return ("BULLISH", "🟢", "Positive momentum")
            elif value < 0:
                return ("BEARISH", "🔴", "Negative momentum")
            else:
                return ("NEUTRAL", "⚪", "Zero momentum")
    
    def get_technical_summary(self, indicators: Dict) -> Dict:
        """Generate comprehensive technical summary"""
        summary = {
            'momentum': 'NEUTRAL',
            'trend': 'NEUTRAL',
            'volume': 'NEUTRAL',
            'overall': 'NEUTRAL',
            'score': 50
        }
        
        # Analyze momentum
        rsi = self._safe_float(indicators.get('rsi', 50))
        if rsi < 30:
            summary['momentum'] = 'BULLISH'
        elif rsi > 70:
            summary['momentum'] = 'BEARISH'
        
        # Analyze trend
        adx_data = indicators.get('adx', {})
        if isinstance(adx_data, dict):
            adx = self._safe_float(adx_data.get('value', 0))
            if adx > 25:
                summary['trend'] = 'STRONG'
        
        # Analyze volume
        obv = self._safe_float(indicators.get('obv', 0))
        if obv > 0:
            summary['volume'] = 'BULLISH'
        
        # Calculate overall score (simplified)
        score = 50
        if summary['momentum'] == 'BULLISH':
            score += 15
        elif summary['momentum'] == 'BEARISH':
            score -= 15
        
        if summary['trend'] == 'STRONG':
            score += 10
        
        if summary['volume'] == 'BULLISH':
            score += 10
        
        summary['score'] = max(0, min(100, score))
        
        if summary['score'] >= 70:
            summary['overall'] = 'BULLISH'
        elif summary['score'] <= 30:
            summary['overall'] = 'BEARISH'
        
        return summary
