"""
COMPREHENSIVE SCORING MODULE v3.0 - TWELVEDATA SUPPORT
Precise scoring algorithms adapted for TwelveData API structure.
"""

from typing import Dict, Any

class ComprehensiveScoring:
    def __init__(self):
        self.name = "Comprehensive Scoring v3.0 (TwelveData)"

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        if value is None: return default
        try: return float(value)
        except: return default

    def calculate_technical_score(self, indicators: Dict, patterns: Dict, current_price: float) -> Dict:
        """
        Calculate technical score based on TwelveData indicators.
        Handles both raw TwelveData format and normalized dashboard format.
        """
        score = 0.0
        details = []
        max_score = 100.0
        
        # 1. RSI (0-100) - Weight: 25%
        rsi = self._safe_float(indicators.get('rsi', 50.0))
        
        if rsi <= 30:
            score += 25
            details.append(f"🟢 RSI Oversold ({rsi:.1f}) - Strong Buy Signal")
        elif rsi <= 40:
            score += 20
            details.append(f"🟢 RSI Low ({rsi:.1f}) - Buy Signal")
        elif rsi >= 70:
            score += 5
            details.append(f"🔴 RSI Overbought ({rsi:.1f}) - Sell Signal")
        elif rsi >= 60:
            score += 10
            details.append(f"🟡 RSI High ({rsi:.1f}) - Caution")
        elif 45 <= rsi <= 55:
            score += 15
            details.append(f"🟡 RSI Neutral ({rsi:.1f})")
        else:
            score += 12
            details.append(f"🟡 RSI Moderate ({rsi:.1f})")
            
        # 2. MACD - Weight: 25%
        # Handle both normalized format (valueMACD, valueMACDSignal) and raw format (macd, signal)
        macd_data = indicators.get('macd', {})
        if isinstance(macd_data, dict):
            macd_val = self._safe_float(macd_data.get('valueMACD', macd_data.get('macd', 0)))
            macd_sig = self._safe_float(macd_data.get('valueMACDSignal', macd_data.get('signal', 0)))
            macd_hist = self._safe_float(macd_data.get('valueMACDHist', macd_data.get('hist', 0)))
            
            if macd_hist > 0 and macd_val > macd_sig:
                score += 25
                details.append(f"🟢 MACD Bullish Crossover (Hist: {macd_hist:.3f})")
            elif macd_hist > 0:
                score += 20
                details.append(f"🟢 MACD Positive Momentum")
            elif macd_hist < 0 and macd_val < macd_sig:
                score += 5
                details.append(f"🔴 MACD Bearish Crossover")
            else:
                score += 10
                details.append(f"🟡 MACD Neutral")
        else:
            score += 12
            details.append("⚪ MACD Data Unavailable")
        
        # 3. ADX (Trend Strength) - Weight: 20%
        # Handle both nested format {'value': x} and direct value
        adx_data = indicators.get('adx', {})
        if isinstance(adx_data, dict):
            adx = self._safe_float(adx_data.get('value', 0))
        else:
            adx = self._safe_float(adx_data)
            
        if adx > 40:
            score += 20
            details.append(f"🟢 Very Strong Trend (ADX {adx:.1f})")
        elif adx > 25:
            score += 18
            details.append(f"🟢 Strong Trend (ADX {adx:.1f})")
        elif adx > 20:
            score += 12
            details.append(f"🟡 Moderate Trend (ADX {adx:.1f})")
        else:
            score += 8
            details.append(f"🔴 Weak Trend (ADX {adx:.1f})")
            
        # 4. Stochastic - Weight: 15%
        # Handle both normalized format (valueK, valueD) and raw format (k, d)
        stoch_data = indicators.get('stoch', {})
        if isinstance(stoch_data, dict):
            k = self._safe_float(stoch_data.get('valueK', stoch_data.get('k', 50)))
            d = self._safe_float(stoch_data.get('valueD', stoch_data.get('d', 50)))
            
            if k < 20:
                score += 15
                details.append(f"🟢 Stochastic Oversold (K: {k:.1f}) - Buy Signal")
            elif k < 30:
                score += 12
                details.append(f"🟢 Stochastic Low (K: {k:.1f})")
            elif k > 80:
                score += 3
                details.append(f"🔴 Stochastic Overbought (K: {k:.1f}) - Sell Signal")
            elif k > 70:
                score += 6
                details.append(f"🟡 Stochastic High (K: {k:.1f})")
            else:
                score += 10
                details.append(f"🟡 Stochastic Neutral (K: {k:.1f})")
        else:
            score += 8
            details.append("⚪ Stochastic Data Unavailable")
        
        # 5. CCI (Commodity Channel Index) - Weight: 10%
        cci = self._safe_float(indicators.get('cci', 0))
        if cci != 0:
            if cci < -100:
                score += 10
                details.append(f"🟢 CCI Oversold ({cci:.1f})")
            elif cci > 100:
                score += 3
                details.append(f"🔴 CCI Overbought ({cci:.1f})")
            else:
                score += 7
                details.append(f"🟡 CCI Neutral ({cci:.1f})")
        
        # 6. Bollinger Bands - Weight: 5%
        bbands = indicators.get('bbands', {})
        if isinstance(bbands, dict) and current_price > 0:
            upper = self._safe_float(bbands.get('upper', 0))
            lower = self._safe_float(bbands.get('lower', 0))
            middle = self._safe_float(bbands.get('middle', 0))
            
            if lower > 0 and current_price < lower:
                score += 5
                details.append(f"🟢 Price Below Lower BB - Oversold")
            elif upper > 0 and current_price > upper:
                score += 1
                details.append(f"🔴 Price Above Upper BB - Overbought")
            else:
                score += 3
                details.append(f"🟡 Price Within BB Range")

        # Normalize score to 0-100
        final_score = min(100, max(0, score))
        
        # Signal determination with more granular levels
        if final_score >= 80:
            signal = "STRONG BUY"
            confidence = "HIGH"
        elif final_score >= 65:
            signal = "BUY"
            confidence = "MEDIUM-HIGH"
        elif final_score >= 50:
            signal = "HOLD"
            confidence = "MEDIUM"
        elif final_score >= 35:
            signal = "WEAK HOLD"
            confidence = "MEDIUM-LOW"
        else:
            signal = "SELL"
            confidence = "HIGH"

        return {
            'score': final_score,
            'signal': signal,
            'confidence': confidence,
            'details': details
        }

    def calculate_fundamental_score(self, fundamentals: Dict) -> float:
        # (Standard fundamental logic here - kept simple for this update)
        score = 50
        pe = self._safe_float(fundamentals.get('pe_ratio', 0))
        if 0 < pe < 20: score += 20
        
        roe = self._safe_float(fundamentals.get('roe', 0))
        if roe > 15: score += 20
        
        return min(100, score)

    def calculate_momentum_score(self, indicators: Dict) -> Dict:
        """Calculate momentum-specific score from indicators"""
        score = 0.0
        details = []
        
        # RSI
        rsi = self._safe_float(indicators.get('rsi', 50.0))
        if rsi <= 30:
            score += 50
            details.append(f"RSI Oversold: {rsi:.1f}")
        elif rsi >= 70:
            score += 10
            details.append(f"RSI Overbought: {rsi:.1f}")
        else:
            score += 30
            details.append(f"RSI Neutral: {rsi:.1f}")
        
        # Stochastic
        stoch_data = indicators.get('stoch', {})
        if isinstance(stoch_data, dict):
            k = self._safe_float(stoch_data.get('valueK', stoch_data.get('k', 50)))
            if k < 20:
                score += 50
                details.append(f"Stoch Oversold: {k:.1f}")
            elif k > 80:
                score += 10
                details.append(f"Stoch Overbought: {k:.1f}")
            else:
                score += 30
        
        final_score = min(100, score)
        signal = "BUY" if final_score >= 60 else "HOLD" if final_score >= 40 else "SELL"
        
        return {'score': final_score, 'signal': signal, 'details': details}
    
    def calculate_trend_score(self, indicators: Dict) -> Dict:
        """Calculate trend-specific score from indicators"""
        score = 0.0
        details = []
        
        # ADX
        adx_data = indicators.get('adx', {})
        if isinstance(adx_data, dict):
            adx = self._safe_float(adx_data.get('value', 0))
        else:
            adx = self._safe_float(adx_data)
        
        if adx > 25:
            score += 50
            details.append(f"Strong Trend: ADX {adx:.1f}")
        else:
            score += 20
            details.append(f"Weak Trend: ADX {adx:.1f}")
        
        # MACD
        macd_data = indicators.get('macd', {})
        if isinstance(macd_data, dict):
            macd_hist = self._safe_float(macd_data.get('valueMACDHist', macd_data.get('hist', 0)))
            if macd_hist > 0:
                score += 50
                details.append("MACD Bullish")
            else:
                score += 20
                details.append("MACD Bearish")
        
        final_score = min(100, score)
        signal = "BUY" if final_score >= 60 else "HOLD" if final_score >= 40 else "SELL"
        
        return {'score': final_score, 'signal': signal, 'details': details}
    
    def calculate_volume_score(self, indicators: Dict) -> Dict:
        """Calculate volume-specific score from indicators"""
        score = 50.0  # Default neutral
        details = []
        
        # OBV
        obv_data = indicators.get('obv', {})
        if isinstance(obv_data, dict):
            obv = self._safe_float(obv_data.get('value', 0))
            if obv > 0:
                score += 25
                details.append("OBV Positive")
            else:
                details.append("OBV Neutral")
        
        # MFI if available
        mfi_data = indicators.get('mfi', {})
        if isinstance(mfi_data, dict):
            mfi = self._safe_float(mfi_data.get('value', 50))
            if mfi < 20:
                score += 25
                details.append(f"MFI Oversold: {mfi:.1f}")
            elif mfi > 80:
                details.append(f"MFI Overbought: {mfi:.1f}")
            else:
                details.append(f"MFI Neutral: {mfi:.1f}")
        
        final_score = min(100, score)
        signal = "BUY" if final_score >= 60 else "HOLD" if final_score >= 40 else "SELL"
        
        return {'score': final_score, 'signal': signal, 'details': details}
    
    def calculate_pattern_score(self, patterns: Dict) -> Dict:
        """Calculate pattern-specific score"""
        score = 50.0  # Default neutral
        details = []
        
        if not patterns:
            return {'score': score, 'signal': 'HOLD', 'details': ['No patterns detected']}
        
        # Count bullish vs bearish patterns
        bullish_count = 0
        bearish_count = 0
        
        for pattern_name, pattern_value in patterns.items():
            if isinstance(pattern_value, (int, float)):
                if pattern_value > 0:
                    bullish_count += 1
                    details.append(f"Bullish: {pattern_name}")
                elif pattern_value < 0:
                    bearish_count += 1
                    details.append(f"Bearish: {pattern_name}")
        
        if bullish_count > bearish_count:
            score = 70
            signal = "BUY"
        elif bearish_count > bullish_count:
            score = 30
            signal = "SELL"
        else:
            score = 50
            signal = "HOLD"
        
        return {'score': score, 'signal': signal, 'details': details}
    
    def calculate_composite_score(self, fund_score: float, tech_score: Dict) -> Dict:
        raw_score = (fund_score * 0.5) + (tech_score['score'] * 0.5)
        
        if raw_score >= 75: 
            rec = "Strong Buy - High Confluence"
            signal = "STRONG BUY"
            grade = "A"
        elif raw_score >= 60: 
            rec = "Buy - Positive Outlook"
            signal = "BUY"
            grade = "B"
        elif raw_score >= 40: 
            rec = "Hold - Mixed Signals"
            signal = "HOLD"
            grade = "C"
        else: 
            rec = "Sell - Negative Outlook"
            signal = "SELL"
            grade = "D"
            
        return {
            'score': raw_score,
            'signal': signal,
            'grade': grade,
            'recommendation': rec,
            'confidence': "HIGH"
        }