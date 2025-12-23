"""
COMPOSITE SCORING ENGINE
=========================
Intelligent multi-factor scoring system that combines:
- Options Flow (pressure, buy/sell classification)
- Dark Pool Activity (short ratio, net position)
- Technical Indicators (RSI, MACD, momentum)
- Fundamental Metrics (valuation, growth, quality)
- Oracle Scanner (float analysis, catalyst detection)

Uses weighted algorithms and AI-driven logic to produce:
1. Category Scores (0-100 each)
2. Master Composite Score (0-100)
3. Trading Signal (STRONG BUY to STRONG SELL)
4. Confidence Level (based on data availability)

For production trading with real money.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class CompositeScoreEngine:
    """
    Intelligent Composite Scoring Engine
    
    Combines multiple data sources using weighted algorithms
    to produce actionable trading signals.
    """
    
    # Category weights (must sum to 1.0)
    CATEGORY_WEIGHTS = {
        'options_flow': 0.25,      # Options pressure and buy/sell flow
        'dark_pool': 0.20,         # Dark pool and short interest
        'technical': 0.25,         # Technical indicators
        'fundamental': 0.15,       # Fundamental metrics
        'momentum': 0.15           # Price momentum and volume
    }
    
    # Signal thresholds
    SIGNAL_THRESHOLDS = {
        'STRONG_BUY': 75,
        'BUY': 60,
        'NEUTRAL': 40,
        'SELL': 25,
        'STRONG_SELL': 0
    }
    
    def __init__(self):
        """Initialize the Composite Score Engine."""
        self.last_calculation = None
        self.debug_mode = False
    
    def calculate_master_score(self, 
                               options_data: Dict = None,
                               dark_pool_data: Dict = None,
                               technical_data: Dict = None,
                               fundamental_data: Dict = None,
                               price_data: Dict = None) -> Dict:
        """
        Calculate the Master Composite Score from all data sources.
        
        Args:
            options_data: Options pressure analysis
            dark_pool_data: Dark pool scanner results
            technical_data: Technical indicators
            fundamental_data: Fundamental metrics
            price_data: Price and volume data
            
        Returns:
            Dict with master score, category scores, signal, and analysis
        """
        try:
            # Calculate individual category scores
            options_score = self._calculate_options_score(options_data)
            dark_pool_score = self._calculate_dark_pool_score(dark_pool_data)
            technical_score = self._calculate_technical_score(technical_data)
            fundamental_score = self._calculate_fundamental_score(fundamental_data)
            momentum_score = self._calculate_momentum_score(price_data, technical_data)
            
            # Calculate weighted master score
            category_scores = {
                'options_flow': options_score,
                'dark_pool': dark_pool_score,
                'technical': technical_score,
                'fundamental': fundamental_score,
                'momentum': momentum_score
            }
            
            # Apply weights and calculate master score
            master_score = 0
            total_weight = 0
            available_categories = 0
            
            for category, score_data in category_scores.items():
                if score_data['available']:
                    weight = self.CATEGORY_WEIGHTS[category]
                    master_score += score_data['score'] * weight
                    total_weight += weight
                    available_categories += 1
            
            # Normalize if not all categories available
            if total_weight > 0 and total_weight < 1.0:
                master_score = master_score / total_weight
            
            # Calculate confidence based on data availability
            confidence = self._calculate_confidence(category_scores)
            
            # Determine trading signal
            signal = self._determine_signal(master_score)
            
            # Generate AI analysis
            analysis = self._generate_analysis(master_score, category_scores, signal)
            
            # Identify key drivers
            drivers = self._identify_key_drivers(category_scores)
            
            # Calculate risk assessment
            risk = self._assess_risk(category_scores, master_score)
            
            result = {
                'ticker': options_data.get('ticker', 'N/A') if options_data else 'N/A',
                'timestamp': datetime.now().isoformat(),
                
                # Master Score
                'master_score': round(master_score, 1),
                'signal': signal['signal'],
                'signal_color': signal['color'],
                'signal_strength': signal['strength'],
                
                # Confidence
                'confidence': confidence['level'],
                'confidence_pct': confidence['percentage'],
                'data_completeness': confidence['completeness'],
                
                # Category Scores
                'category_scores': {
                    'options_flow': {
                        'score': options_score['score'],
                        'available': options_score['available'],
                        'weight': self.CATEGORY_WEIGHTS['options_flow'],
                        'contribution': options_score['score'] * self.CATEGORY_WEIGHTS['options_flow'] if options_score['available'] else 0,
                        'factors': options_score.get('factors', [])
                    },
                    'dark_pool': {
                        'score': dark_pool_score['score'],
                        'available': dark_pool_score['available'],
                        'weight': self.CATEGORY_WEIGHTS['dark_pool'],
                        'contribution': dark_pool_score['score'] * self.CATEGORY_WEIGHTS['dark_pool'] if dark_pool_score['available'] else 0,
                        'factors': dark_pool_score.get('factors', [])
                    },
                    'technical': {
                        'score': technical_score['score'],
                        'available': technical_score['available'],
                        'weight': self.CATEGORY_WEIGHTS['technical'],
                        'contribution': technical_score['score'] * self.CATEGORY_WEIGHTS['technical'] if technical_score['available'] else 0,
                        'factors': technical_score.get('factors', [])
                    },
                    'fundamental': {
                        'score': fundamental_score['score'],
                        'available': fundamental_score['available'],
                        'weight': self.CATEGORY_WEIGHTS['fundamental'],
                        'contribution': fundamental_score['score'] * self.CATEGORY_WEIGHTS['fundamental'] if fundamental_score['available'] else 0,
                        'factors': fundamental_score.get('factors', [])
                    },
                    'momentum': {
                        'score': momentum_score['score'],
                        'available': momentum_score['available'],
                        'weight': self.CATEGORY_WEIGHTS['momentum'],
                        'contribution': momentum_score['score'] * self.CATEGORY_WEIGHTS['momentum'] if momentum_score['available'] else 0,
                        'factors': momentum_score.get('factors', [])
                    }
                },
                
                # Analysis
                'analysis': analysis,
                'key_drivers': drivers,
                'risk_assessment': risk,
                
                # Status
                'status': 'success'
            }
            
            self.last_calculation = result
            return result
            
        except Exception as e:
            return {
                'ticker': 'N/A',
                'timestamp': datetime.now().isoformat(),
                'master_score': 50,
                'signal': 'NEUTRAL',
                'signal_color': '#9E9E9E',
                'confidence': 'LOW',
                'confidence_pct': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def _calculate_options_score(self, data: Dict) -> Dict:
        """
        Calculate Options Flow Score (0-100).
        
        Factors:
        - Put/Call Ratio (inverted - lower is bullish)
        - Net Pressure
        - Buy/Sell Flow
        - Unusual Activity
        """
        if not data or data.get('status') == 'error':
            return {'score': 50, 'available': False, 'factors': []}
        
        score = 50  # Start neutral
        factors = []
        
        # 1. Put/Call Ratio (weight: 25%)
        pcr = data.get('pcr_volume', 1.0)
        if pcr < 0.5:
            pcr_score = 85  # Very bullish
            factors.append(('Put/Call Ratio', pcr, 'BULLISH', '+15'))
        elif pcr < 0.7:
            pcr_score = 70  # Bullish
            factors.append(('Put/Call Ratio', pcr, 'BULLISH', '+10'))
        elif pcr < 1.0:
            pcr_score = 55  # Slightly bullish
            factors.append(('Put/Call Ratio', pcr, 'NEUTRAL', '+2'))
        elif pcr < 1.3:
            pcr_score = 45  # Slightly bearish
            factors.append(('Put/Call Ratio', pcr, 'NEUTRAL', '-2'))
        elif pcr < 1.5:
            pcr_score = 30  # Bearish
            factors.append(('Put/Call Ratio', pcr, 'BEARISH', '-10'))
        else:
            pcr_score = 15  # Very bearish
            factors.append(('Put/Call Ratio', pcr, 'BEARISH', '-15'))
        
        # 2. Net Pressure (weight: 30%)
        net_pressure = data.get('net_pressure', 0)
        pressure_score = 50 + (net_pressure / 2)  # Convert -100/+100 to 0-100
        pressure_score = max(0, min(100, pressure_score))
        
        if net_pressure > 20:
            factors.append(('Net Pressure', f'{net_pressure:+.1f}%', 'BULLISH', '+15'))
        elif net_pressure > 5:
            factors.append(('Net Pressure', f'{net_pressure:+.1f}%', 'BULLISH', '+5'))
        elif net_pressure < -20:
            factors.append(('Net Pressure', f'{net_pressure:+.1f}%', 'BEARISH', '-15'))
        elif net_pressure < -5:
            factors.append(('Net Pressure', f'{net_pressure:+.1f}%', 'BEARISH', '-5'))
        
        # 3. Buy/Sell Flow (weight: 30%)
        buy_pct = data.get('buy_pct', 50)
        flow_score = buy_pct  # Direct mapping
        
        if buy_pct > 60:
            factors.append(('Buy/Sell Flow', f'{buy_pct:.1f}% Buy', 'BULLISH', '+10'))
        elif buy_pct < 40:
            factors.append(('Buy/Sell Flow', f'{buy_pct:.1f}% Buy', 'BEARISH', '-10'))
        
        # 4. Unusual Activity (weight: 15%)
        has_unusual = data.get('has_unusual_activity', False)
        unusual_score = 60 if has_unusual else 50  # Slight bullish bias for unusual activity
        
        if has_unusual:
            factors.append(('Unusual Activity', 'Detected', 'BULLISH', '+5'))
        
        # Weighted combination
        final_score = (
            pcr_score * 0.25 +
            pressure_score * 0.30 +
            flow_score * 0.30 +
            unusual_score * 0.15
        )
        
        return {
            'score': round(final_score, 1),
            'available': True,
            'factors': factors
        }
    
    def _calculate_dark_pool_score(self, data: Dict) -> Dict:
        """
        Calculate Dark Pool Score (0-100).
        
        Factors:
        - Short Ratio (inverted - lower is bullish)
        - Net Dark Pool Position
        - Buy/Sell Estimation
        """
        if not data or data.get('status') == 'error':
            return {'score': 50, 'available': False, 'factors': []}
        
        score = 50
        factors = []
        has_data = False
        
        # 1. Short Ratio (weight: 40%)
        if data.get('has_short_data'):
            has_data = True
            short_ratio = data.get('short_ratio', 50)
            
            # Invert: lower short ratio = more bullish
            if short_ratio < 25:
                short_score = 85
                factors.append(('Short Ratio', f'{short_ratio}%', 'BULLISH', '+20'))
            elif short_ratio < 35:
                short_score = 70
                factors.append(('Short Ratio', f'{short_ratio}%', 'BULLISH', '+10'))
            elif short_ratio < 45:
                short_score = 55
                factors.append(('Short Ratio', f'{short_ratio}%', 'NEUTRAL', '+2'))
            elif short_ratio < 55:
                short_score = 45
                factors.append(('Short Ratio', f'{short_ratio}%', 'NEUTRAL', '-2'))
            elif short_ratio < 65:
                short_score = 30
                factors.append(('Short Ratio', f'{short_ratio}%', 'BEARISH', '-10'))
            else:
                short_score = 15
                factors.append(('Short Ratio', f'{short_ratio}%', 'BEARISH', '-20'))
        else:
            short_score = 50
        
        # 2. Net Dark Pool Position (weight: 35%)
        if data.get('has_dark_pool_data'):
            has_data = True
            net_pos = data.get('net_dp_position', 0)
            
            if net_pos > 1000000:
                dp_score = 85
                factors.append(('DP Net Position', f'{net_pos:,.0f}', 'BULLISH', '+15'))
            elif net_pos > 100000:
                dp_score = 70
                factors.append(('DP Net Position', f'{net_pos:,.0f}', 'BULLISH', '+10'))
            elif net_pos > 0:
                dp_score = 55
                factors.append(('DP Net Position', f'{net_pos:,.0f}', 'NEUTRAL', '+2'))
            elif net_pos > -100000:
                dp_score = 45
                factors.append(('DP Net Position', f'{net_pos:,.0f}', 'NEUTRAL', '-2'))
            elif net_pos > -1000000:
                dp_score = 30
                factors.append(('DP Net Position', f'{net_pos:,.0f}', 'BEARISH', '-10'))
            else:
                dp_score = 15
                factors.append(('DP Net Position', f'{net_pos:,.0f}', 'BEARISH', '-15'))
        else:
            dp_score = 50
        
        # 3. Overall Dark Pool Score from data (weight: 25%)
        overall_dp = data.get('overall_score', 50)
        
        if not has_data:
            return {'score': 50, 'available': False, 'factors': []}
        
        # Weighted combination
        final_score = (
            short_score * 0.40 +
            dp_score * 0.35 +
            overall_dp * 0.25
        )
        
        return {
            'score': round(final_score, 1),
            'available': True,
            'factors': factors
        }
    
    def _calculate_technical_score(self, data: Dict) -> Dict:
        """
        Calculate Technical Score (0-100).
        
        Factors:
        - RSI (oversold/overbought)
        - MACD (signal line crossover)
        - Stochastic (momentum)
        - ADX (trend strength)
        - Moving Averages (trend direction)
        """
        if not data:
            return {'score': 50, 'available': False, 'factors': []}
        
        score = 50
        factors = []
        available_indicators = 0
        total_score = 0
        
        # 1. RSI Analysis
        rsi = data.get('rsi')
        if rsi is not None:
            available_indicators += 1
            if rsi < 30:
                rsi_score = 80  # Oversold - bullish
                factors.append(('RSI', f'{rsi:.1f}', 'BULLISH', 'Oversold'))
            elif rsi < 40:
                rsi_score = 65
                factors.append(('RSI', f'{rsi:.1f}', 'BULLISH', 'Near oversold'))
            elif rsi > 70:
                rsi_score = 20  # Overbought - bearish
                factors.append(('RSI', f'{rsi:.1f}', 'BEARISH', 'Overbought'))
            elif rsi > 60:
                rsi_score = 35
                factors.append(('RSI', f'{rsi:.1f}', 'BEARISH', 'Near overbought'))
            else:
                rsi_score = 50
            total_score += rsi_score
        
        # 2. MACD Analysis
        macd = data.get('macd')
        macd_signal = data.get('macd_signal')
        if macd is not None and macd_signal is not None:
            available_indicators += 1
            macd_diff = macd - macd_signal
            if macd_diff > 0 and macd > 0:
                macd_score = 75  # Bullish crossover above zero
                factors.append(('MACD', f'{macd:.2f}', 'BULLISH', 'Above signal'))
            elif macd_diff > 0:
                macd_score = 60  # Bullish crossover below zero
                factors.append(('MACD', f'{macd:.2f}', 'BULLISH', 'Crossing up'))
            elif macd_diff < 0 and macd < 0:
                macd_score = 25  # Bearish below zero
                factors.append(('MACD', f'{macd:.2f}', 'BEARISH', 'Below signal'))
            elif macd_diff < 0:
                macd_score = 40  # Bearish crossover above zero
                factors.append(('MACD', f'{macd:.2f}', 'BEARISH', 'Crossing down'))
            else:
                macd_score = 50
            total_score += macd_score
        
        # 3. Stochastic Analysis
        stoch_k = data.get('stoch_k')
        stoch_d = data.get('stoch_d')
        if stoch_k is not None:
            available_indicators += 1
            if stoch_k < 20:
                stoch_score = 75  # Oversold
                factors.append(('Stochastic', f'{stoch_k:.1f}', 'BULLISH', 'Oversold'))
            elif stoch_k > 80:
                stoch_score = 25  # Overbought
                factors.append(('Stochastic', f'{stoch_k:.1f}', 'BEARISH', 'Overbought'))
            else:
                stoch_score = 50
            total_score += stoch_score
        
        # 4. ADX (Trend Strength)
        adx = data.get('adx')
        if adx is not None:
            available_indicators += 1
            # ADX doesn't indicate direction, just strength
            # We'll use it as a confidence modifier
            if adx > 25:
                adx_score = 55  # Strong trend (slight positive)
                factors.append(('ADX', f'{adx:.1f}', 'NEUTRAL', 'Strong trend'))
            else:
                adx_score = 50  # Weak trend
            total_score += adx_score
        
        # 5. Moving Average Analysis
        sma_20 = data.get('sma_20')
        sma_50 = data.get('sma_50')
        current_price = data.get('current_price')
        
        if sma_20 is not None and current_price is not None:
            available_indicators += 1
            if current_price > sma_20:
                ma_score = 65  # Above MA - bullish
                factors.append(('Price vs SMA20', f'Above', 'BULLISH', '+'))
            else:
                ma_score = 35  # Below MA - bearish
                factors.append(('Price vs SMA20', f'Below', 'BEARISH', '-'))
            total_score += ma_score
        
        if available_indicators == 0:
            return {'score': 50, 'available': False, 'factors': []}
        
        final_score = total_score / available_indicators
        
        return {
            'score': round(final_score, 1),
            'available': True,
            'factors': factors
        }
    
    def _calculate_fundamental_score(self, data: Dict) -> Dict:
        """
        Calculate Fundamental Score (0-100).
        
        Factors:
        - P/E Ratio (valuation)
        - Revenue Growth
        - Profit Margins
        - ROE (quality)
        - Debt Levels
        """
        if not data:
            return {'score': 50, 'available': False, 'factors': []}
        
        factors = []
        scores = []
        
        # 1. P/E Ratio
        pe = data.get('pe_ratio') or data.get('trailing_pe')
        if pe is not None and pe > 0:
            if pe < 15:
                pe_score = 80  # Undervalued
                factors.append(('P/E Ratio', f'{pe:.1f}', 'BULLISH', 'Undervalued'))
            elif pe < 25:
                pe_score = 60  # Fair value
                factors.append(('P/E Ratio', f'{pe:.1f}', 'NEUTRAL', 'Fair'))
            elif pe < 40:
                pe_score = 40  # Expensive
                factors.append(('P/E Ratio', f'{pe:.1f}', 'BEARISH', 'Expensive'))
            else:
                pe_score = 25  # Very expensive
                factors.append(('P/E Ratio', f'{pe:.1f}', 'BEARISH', 'Very expensive'))
            scores.append(pe_score)
        
        # 2. Revenue Growth
        rev_growth = data.get('revenue_growth')
        if rev_growth is not None:
            if isinstance(rev_growth, str):
                rev_growth = float(rev_growth.replace('%', '')) if '%' in str(rev_growth) else float(rev_growth)
            
            if rev_growth > 20:
                growth_score = 85
                factors.append(('Revenue Growth', f'{rev_growth:.1f}%', 'BULLISH', 'High growth'))
            elif rev_growth > 10:
                growth_score = 70
                factors.append(('Revenue Growth', f'{rev_growth:.1f}%', 'BULLISH', 'Good growth'))
            elif rev_growth > 0:
                growth_score = 55
                factors.append(('Revenue Growth', f'{rev_growth:.1f}%', 'NEUTRAL', 'Positive'))
            else:
                growth_score = 30
                factors.append(('Revenue Growth', f'{rev_growth:.1f}%', 'BEARISH', 'Declining'))
            scores.append(growth_score)
        
        # 3. Profit Margin
        margin = data.get('net_margin') or data.get('profit_margin')
        if margin is not None:
            if isinstance(margin, str):
                margin = float(margin.replace('%', '')) if '%' in str(margin) else float(margin)
            
            if margin > 20:
                margin_score = 80
                factors.append(('Net Margin', f'{margin:.1f}%', 'BULLISH', 'High margin'))
            elif margin > 10:
                margin_score = 65
                factors.append(('Net Margin', f'{margin:.1f}%', 'BULLISH', 'Good margin'))
            elif margin > 0:
                margin_score = 50
                factors.append(('Net Margin', f'{margin:.1f}%', 'NEUTRAL', 'Positive'))
            else:
                margin_score = 25
                factors.append(('Net Margin', f'{margin:.1f}%', 'BEARISH', 'Negative'))
            scores.append(margin_score)
        
        # 4. ROE
        roe = data.get('roe') or data.get('return_on_equity')
        if roe is not None:
            if isinstance(roe, str):
                roe = float(roe.replace('%', '')) if '%' in str(roe) else float(roe)
            
            if roe > 20:
                roe_score = 80
                factors.append(('ROE', f'{roe:.1f}%', 'BULLISH', 'Excellent'))
            elif roe > 10:
                roe_score = 65
                factors.append(('ROE', f'{roe:.1f}%', 'BULLISH', 'Good'))
            elif roe > 0:
                roe_score = 50
                factors.append(('ROE', f'{roe:.1f}%', 'NEUTRAL', 'Positive'))
            else:
                roe_score = 25
                factors.append(('ROE', f'{roe:.1f}%', 'BEARISH', 'Negative'))
            scores.append(roe_score)
        
        # 5. Debt-to-Equity
        de = data.get('debt_to_equity')
        if de is not None:
            if isinstance(de, str):
                de = float(de) if de.replace('.', '').isdigit() else None
            
            if de is not None:
                if de < 0.5:
                    de_score = 75
                    factors.append(('Debt/Equity', f'{de:.2f}', 'BULLISH', 'Low debt'))
                elif de < 1.0:
                    de_score = 60
                    factors.append(('Debt/Equity', f'{de:.2f}', 'NEUTRAL', 'Moderate'))
                elif de < 2.0:
                    de_score = 40
                    factors.append(('Debt/Equity', f'{de:.2f}', 'BEARISH', 'High debt'))
                else:
                    de_score = 25
                    factors.append(('Debt/Equity', f'{de:.2f}', 'BEARISH', 'Very high debt'))
                scores.append(de_score)
        
        if not scores:
            return {'score': 50, 'available': False, 'factors': []}
        
        final_score = sum(scores) / len(scores)
        
        return {
            'score': round(final_score, 1),
            'available': True,
            'factors': factors
        }
    
    def _calculate_momentum_score(self, price_data: Dict, technical_data: Dict) -> Dict:
        """
        Calculate Momentum Score (0-100).
        
        Factors:
        - Price change (1d, 5d, 20d)
        - Volume ratio
        - Relative strength
        """
        factors = []
        scores = []
        
        # Price change
        if price_data:
            price_change = price_data.get('price_change_pct', 0)
            
            if price_change > 5:
                change_score = 80
                factors.append(('Price Change', f'{price_change:+.1f}%', 'BULLISH', 'Strong up'))
            elif price_change > 2:
                change_score = 65
                factors.append(('Price Change', f'{price_change:+.1f}%', 'BULLISH', 'Up'))
            elif price_change > -2:
                change_score = 50
                factors.append(('Price Change', f'{price_change:+.1f}%', 'NEUTRAL', 'Flat'))
            elif price_change > -5:
                change_score = 35
                factors.append(('Price Change', f'{price_change:+.1f}%', 'BEARISH', 'Down'))
            else:
                change_score = 20
                factors.append(('Price Change', f'{price_change:+.1f}%', 'BEARISH', 'Strong down'))
            scores.append(change_score)
            
            # Volume ratio
            vol_ratio = price_data.get('volume_ratio', 1.0)
            if vol_ratio > 2.0:
                vol_score = 70  # High volume = conviction
                factors.append(('Volume Ratio', f'{vol_ratio:.1f}x', 'BULLISH', 'High volume'))
            elif vol_ratio > 1.2:
                vol_score = 60
                factors.append(('Volume Ratio', f'{vol_ratio:.1f}x', 'NEUTRAL', 'Above avg'))
            elif vol_ratio < 0.5:
                vol_score = 40  # Low volume = weak move
                factors.append(('Volume Ratio', f'{vol_ratio:.1f}x', 'BEARISH', 'Low volume'))
            else:
                vol_score = 50
            scores.append(vol_score)
        
        # RSI momentum
        if technical_data:
            rsi = technical_data.get('rsi')
            if rsi is not None:
                # RSI between 40-60 with upward momentum is bullish
                if 45 <= rsi <= 55:
                    rsi_mom_score = 55  # Neutral with room to run
                elif 55 < rsi <= 70:
                    rsi_mom_score = 65  # Bullish momentum
                elif rsi > 70:
                    rsi_mom_score = 40  # Overbought, momentum fading
                elif 30 <= rsi < 45:
                    rsi_mom_score = 45  # Bearish but potential reversal
                else:
                    rsi_mom_score = 60  # Oversold, potential bounce
                scores.append(rsi_mom_score)
        
        if not scores:
            return {'score': 50, 'available': False, 'factors': []}
        
        final_score = sum(scores) / len(scores)
        
        return {
            'score': round(final_score, 1),
            'available': True,
            'factors': factors
        }
    
    def _calculate_confidence(self, category_scores: Dict) -> Dict:
        """Calculate confidence level based on data availability."""
        available_count = sum(1 for cat in category_scores.values() if cat['available'])
        total_categories = len(category_scores)
        
        completeness = available_count / total_categories
        
        if completeness >= 0.8:
            level = 'HIGH'
            percentage = 90
        elif completeness >= 0.6:
            level = 'MEDIUM'
            percentage = 70
        elif completeness >= 0.4:
            level = 'LOW'
            percentage = 50
        else:
            level = 'VERY_LOW'
            percentage = 30
        
        return {
            'level': level,
            'percentage': percentage,
            'completeness': f'{available_count}/{total_categories} categories'
        }
    
    def _determine_signal(self, score: float) -> Dict:
        """Determine trading signal from master score."""
        if score >= 75:
            return {'signal': 'STRONG BUY', 'color': '#00c851', 'strength': 'Very Strong'}
        elif score >= 60:
            return {'signal': 'BUY', 'color': '#4CAF50', 'strength': 'Strong'}
        elif score >= 55:
            return {'signal': 'LEAN BULLISH', 'color': '#8BC34A', 'strength': 'Moderate'}
        elif score >= 45:
            return {'signal': 'NEUTRAL', 'color': '#9E9E9E', 'strength': 'Weak'}
        elif score >= 40:
            return {'signal': 'LEAN BEARISH', 'color': '#FF9800', 'strength': 'Moderate'}
        elif score >= 25:
            return {'signal': 'SELL', 'color': '#FF5722', 'strength': 'Strong'}
        else:
            return {'signal': 'STRONG SELL', 'color': '#F44336', 'strength': 'Very Strong'}
    
    def _generate_analysis(self, score: float, categories: Dict, signal: Dict) -> str:
        """Generate AI-style analysis text."""
        analysis_parts = []
        
        # Overall assessment
        if score >= 70:
            analysis_parts.append(f"Strong bullish setup with multiple confirming signals.")
        elif score >= 55:
            analysis_parts.append(f"Moderately bullish outlook with positive momentum.")
        elif score >= 45:
            analysis_parts.append(f"Mixed signals suggest a neutral stance.")
        elif score >= 30:
            analysis_parts.append(f"Bearish pressure evident across multiple factors.")
        else:
            analysis_parts.append(f"Strong bearish signals warrant caution.")
        
        # Category highlights
        bullish_cats = []
        bearish_cats = []
        
        for cat_name, cat_data in categories.items():
            if cat_data['available']:
                if cat_data['score'] >= 60:
                    bullish_cats.append(cat_name.replace('_', ' ').title())
                elif cat_data['score'] <= 40:
                    bearish_cats.append(cat_name.replace('_', ' ').title())
        
        if bullish_cats:
            analysis_parts.append(f"Bullish factors: {', '.join(bullish_cats)}.")
        if bearish_cats:
            analysis_parts.append(f"Bearish factors: {', '.join(bearish_cats)}.")
        
        return ' '.join(analysis_parts)
    
    def _identify_key_drivers(self, categories: Dict) -> List[Dict]:
        """Identify the key drivers of the score."""
        drivers = []
        
        for cat_name, cat_data in categories.items():
            if cat_data['available'] and cat_data.get('factors'):
                for factor in cat_data['factors']:
                    drivers.append({
                        'category': cat_name.replace('_', ' ').title(),
                        'factor': factor[0],
                        'value': factor[1],
                        'sentiment': factor[2],
                        'impact': factor[3] if len(factor) > 3 else ''
                    })
        
        # Sort by impact (bullish first, then bearish)
        drivers.sort(key=lambda x: (x['sentiment'] != 'BULLISH', x['sentiment'] != 'BEARISH'))
        
        return drivers[:10]  # Top 10 drivers
    
    def _assess_risk(self, categories: Dict, score: float) -> Dict:
        """Assess risk level based on score divergence and volatility."""
        scores = [cat['score'] for cat in categories.values() if cat['available']]
        
        if not scores:
            return {'level': 'UNKNOWN', 'factors': []}
        
        # Calculate standard deviation (divergence)
        std_dev = np.std(scores)
        
        risk_factors = []
        
        if std_dev > 20:
            risk_level = 'HIGH'
            risk_factors.append('High divergence between indicators')
        elif std_dev > 10:
            risk_level = 'MEDIUM'
            risk_factors.append('Moderate indicator divergence')
        else:
            risk_level = 'LOW'
            risk_factors.append('Indicators aligned')
        
        # Check for extreme scores
        if any(s > 80 for s in scores):
            risk_factors.append('Some indicators at extreme levels')
        if any(s < 20 for s in scores):
            risk_factors.append('Some indicators showing strong bearish signals')
        
        return {
            'level': risk_level,
            'divergence': round(std_dev, 1),
            'factors': risk_factors
        }


# Test function
if __name__ == "__main__":
    print("Testing Composite Score Engine...")
    print("=" * 60)
    
    # Mock data for testing
    mock_options = {
        'ticker': 'AAPL',
        'status': 'success',
        'pcr_volume': 0.4,
        'net_pressure': 42.8,
        'buy_pct': 42.4,
        'sell_pct': 57.6,
        'has_unusual_activity': True
    }
    
    mock_dark_pool = {
        'status': 'success',
        'has_short_data': True,
        'short_ratio': 28.55,
        'has_dark_pool_data': False,
        'overall_score': 60
    }
    
    mock_technical = {
        'rsi': 55,
        'macd': 1.5,
        'macd_signal': 1.2,
        'stoch_k': 65,
        'adx': 28,
        'sma_20': 175,
        'current_price': 178
    }
    
    mock_fundamental = {
        'pe_ratio': 28,
        'revenue_growth': 8.5,
        'net_margin': 25.3,
        'roe': 147,
        'debt_to_equity': 1.8
    }
    
    mock_price = {
        'price_change_pct': 1.2,
        'volume_ratio': 1.5
    }
    
    engine = CompositeScoreEngine()
    result = engine.calculate_master_score(
        options_data=mock_options,
        dark_pool_data=mock_dark_pool,
        technical_data=mock_technical,
        fundamental_data=mock_fundamental,
        price_data=mock_price
    )
    
    print(f"\n🎯 MASTER SCORE: {result['master_score']}/100")
    print(f"📊 SIGNAL: {result['signal']} ({result['signal_strength']})")
    print(f"🔒 CONFIDENCE: {result['confidence']} ({result['confidence_pct']}%)")
    
    print(f"\n📈 CATEGORY SCORES:")
    for cat_name, cat_data in result['category_scores'].items():
        status = '✅' if cat_data['available'] else '❌'
        print(f"   {status} {cat_name.replace('_', ' ').title()}: {cat_data['score']}/100 (weight: {cat_data['weight']*100:.0f}%)")
    
    print(f"\n📝 ANALYSIS:")
    print(f"   {result['analysis']}")
    
    print(f"\n⚠️ RISK: {result['risk_assessment']['level']}")
    for factor in result['risk_assessment']['factors']:
        print(f"   - {factor}")
    
    print(f"\n🔑 KEY DRIVERS:")
    for driver in result['key_drivers'][:5]:
        emoji = '🟢' if driver['sentiment'] == 'BULLISH' else '🔴' if driver['sentiment'] == 'BEARISH' else '⚪'
        print(f"   {emoji} {driver['factor']}: {driver['value']} ({driver['impact']})")
