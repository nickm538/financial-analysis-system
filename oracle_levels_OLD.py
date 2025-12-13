"""
ORACLE SUPPORT/RESISTANCE CALCULATOR
=====================================
Tim Bohen's Volume-Weighted Level Calculation with Time Decay.

Formula:
Level_Strength = (Volume_at_Level × Touch_Count × e^(-0.1 × Days_Since_Touch))

Color Coding:
- 🔴 Strong Resistance (Dark Red) - Top 3 levels
- 🟠 Moderate Resistance (Light Red) - Levels 4-6
- 🟡 Weak Resistance (Pink) - Levels 7-8
- 🟢 Support (Green shades) - Levels 9+

For real-money trading - Maximum precision.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math

class OracleLevels:
    """
    Oracle Support/Resistance Calculator
    
    Implements Tim Bohen's volume-weighted level calculation
    with exponential time decay for recency weighting.
    """
    
    def __init__(self):
        """Initialize Oracle Levels calculator"""
        self.TIME_DECAY_FACTOR = 0.1  # Exponential decay rate
        self.PRICE_PRECISION = 2  # Round to cents
        self.MIN_TOUCHES = 2  # Minimum touches to qualify as level
        self.LOOKBACK_DAYS = 20  # Days to analyze
    
    def calculate_oracle_levels(self, price_data: pd.DataFrame, 
                                 timeframe: str = '1day') -> Dict:
        """
        Calculate Oracle support/resistance levels.
        
        Uses volume profile + time decay + touch count to identify
        high-probability price levels where stock will react.
        
        Args:
            price_data: DataFrame with OHLCV data
            timeframe: '1min', '5min', '1day', etc.
        
        Returns:
            Dict with color-coded levels by strength
        """
        try:
            if price_data.empty:
                return self._empty_levels()
            
            # Step 1: Build Volume Profile
            volume_profile = self._build_volume_profile(price_data)
            
            # Step 2: Identify High-Volume Nodes (HVN)
            hvn_levels = self._identify_hvn_levels(volume_profile)
            
            # Step 3: Calculate Touch Counts
            touch_counts = self._calculate_touch_counts(price_data, hvn_levels)
            
            # Step 4: Apply Time Decay Weighting
            weighted_levels = self._apply_time_decay(price_data, hvn_levels, touch_counts)
            
            # Step 5: Sort by Strength and Color Code
            color_coded_levels = self._color_code_levels(weighted_levels)
            
            # Step 6: Identify Current Price Position
            current_price = float(price_data.iloc[-1]['close'])
            position_analysis = self._analyze_price_position(current_price, color_coded_levels)
            
            return {
                'levels': color_coded_levels,
                'current_price': current_price,
                'position': position_analysis,
                'nearest_support': self._find_nearest_support(current_price, color_coded_levels),
                'nearest_resistance': self._find_nearest_resistance(current_price, color_coded_levels),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error calculating Oracle levels: {e}")
            return self._empty_levels()
    
    def _build_volume_profile(self, price_data: pd.DataFrame) -> Dict[float, float]:
        """
        Build volume profile - volume accumulated at each price level.
        
        Args:
            price_data: DataFrame with OHLCV data
        
        Returns:
            Dict mapping price level to total volume
        """
        volume_profile = {}
        
        for idx, row in price_data.iterrows():
            # Use close price as representative level
            price_level = round(float(row['close']), self.PRICE_PRECISION)
            volume = float(row['volume'])
            
            if price_level in volume_profile:
                volume_profile[price_level] += volume
            else:
                volume_profile[price_level] = volume
        
        return volume_profile
    
    def _identify_hvn_levels(self, volume_profile: Dict[float, float], 
                             top_n: int = 15) -> List[Tuple[float, float]]:
        """
        Identify High-Volume Nodes (HVN) - price levels with most volume.
        
        Args:
            volume_profile: Dict mapping price to volume
            top_n: Number of top levels to return
        
        Returns:
            List of (price, volume) tuples sorted by volume
        """
        # Sort by volume (descending)
        sorted_levels = sorted(volume_profile.items(), 
                              key=lambda x: x[1], 
                              reverse=True)
        
        return sorted_levels[:top_n]
    
    def _calculate_touch_counts(self, price_data: pd.DataFrame, 
                                hvn_levels: List[Tuple[float, float]]) -> Dict[float, int]:
        """
        Calculate how many times price touched each level.
        
        A "touch" is when price comes within 1% of the level.
        
        Args:
            price_data: DataFrame with OHLCV data
            hvn_levels: List of (price, volume) tuples
        
        Returns:
            Dict mapping price level to touch count
        """
        touch_counts = {}
        tolerance = 0.01  # 1% tolerance
        
        for price_level, _ in hvn_levels:
            touches = 0
            
            for idx, row in price_data.iterrows():
                high = float(row['high'])
                low = float(row['low'])
                
                # Check if price touched this level
                if low <= price_level * (1 + tolerance) and high >= price_level * (1 - tolerance):
                    touches += 1
            
            touch_counts[price_level] = touches
        
        return touch_counts
    
    def _apply_time_decay(self, price_data: pd.DataFrame, 
                         hvn_levels: List[Tuple[float, float]], 
                         touch_counts: Dict[float, int]) -> List[Dict]:
        """
        Apply exponential time decay to weight recent touches more heavily.
        
        Formula: Level_Strength = Volume × Touch_Count × e^(-0.1 × Days_Since_Touch)
        
        Args:
            price_data: DataFrame with OHLCV data
            hvn_levels: List of (price, volume) tuples
            touch_counts: Dict mapping price to touch count
        
        Returns:
            List of dicts with weighted level data
        """
        weighted_levels = []
        
        # Get latest date
        if 'date' in price_data.columns:
            latest_date = pd.to_datetime(price_data['date']).max()
        else:
            latest_date = datetime.now()
        
        for price_level, volume in hvn_levels:
            touches = touch_counts.get(price_level, 0)
            
            if touches < self.MIN_TOUCHES:
                continue  # Skip levels with too few touches
            
            # Find most recent touch
            days_since_touch = self._calculate_days_since_touch(
                price_data, price_level, latest_date
            )
            
            # Calculate time decay weight
            time_weight = math.exp(-self.TIME_DECAY_FACTOR * days_since_touch)
            
            # Calculate final strength
            strength = volume * touches * time_weight
            
            weighted_levels.append({
                'price': price_level,
                'volume': volume,
                'touches': touches,
                'days_since_touch': days_since_touch,
                'time_weight': time_weight,
                'strength': strength
            })
        
        # Sort by strength (descending)
        weighted_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        return weighted_levels
    
    def _calculate_days_since_touch(self, price_data: pd.DataFrame, 
                                    price_level: float, 
                                    latest_date: datetime) -> float:
        """
        Calculate days since price last touched this level.
        
        Args:
            price_data: DataFrame with OHLCV data
            price_level: Price level to check
            latest_date: Most recent date in data
        
        Returns:
            Days since last touch
        """
        tolerance = 0.01  # 1% tolerance
        last_touch_date = None
        
        for idx, row in price_data.iterrows():
            high = float(row['high'])
            low = float(row['low'])
            
            # Check if price touched this level
            if low <= price_level * (1 + tolerance) and high >= price_level * (1 - tolerance):
                if 'date' in row:
                    touch_date = pd.to_datetime(row['date'])
                    if last_touch_date is None or touch_date > last_touch_date:
                        last_touch_date = touch_date
        
        if last_touch_date:
            days_since = (latest_date - last_touch_date).days
            return max(days_since, 0)
        else:
            return self.LOOKBACK_DAYS  # Default to max lookback
    
    def _color_code_levels(self, weighted_levels: List[Dict]) -> Dict:
        """
        Color code levels by strength (Tim Bohen's system).
        
        Color Coding:
        - Strong Resistance (Dark Red): Top 3 levels
        - Moderate Resistance (Light Red): Levels 4-6
        - Weak Resistance (Pink): Levels 7-8
        - Pivot (Yellow): Level 9
        - Support (Green shades): Levels 10+
        
        Args:
            weighted_levels: List of level dicts sorted by strength
        
        Returns:
            Dict with color-coded levels
        """
        color_coded = {
            'strong_resistance': [],
            'moderate_resistance': [],
            'weak_resistance': [],
            'pivot': [],
            'support': []
        }
        
        for i, level in enumerate(weighted_levels):
            level_data = {
                'price': level['price'],
                'strength': round(level['strength'], 2),
                'touches': level['touches'],
                'days_since_touch': level['days_since_touch'],
                'volume': level['volume']
            }
            
            if i < 3:
                color_coded['strong_resistance'].append(level_data)
            elif i < 6:
                color_coded['moderate_resistance'].append(level_data)
            elif i < 8:
                color_coded['weak_resistance'].append(level_data)
            elif i < 9:
                color_coded['pivot'].append(level_data)
            else:
                color_coded['support'].append(level_data)
        
        return color_coded
    
    def _analyze_price_position(self, current_price: float, 
                                color_coded_levels: Dict) -> Dict:
        """
        Analyze current price position relative to key levels.
        
        Args:
            current_price: Current stock price
            color_coded_levels: Color-coded support/resistance levels
        
        Returns:
            Dict with position analysis
        """
        # Find nearest levels above and below
        all_levels = []
        for category in color_coded_levels.values():
            all_levels.extend([level['price'] for level in category])
        
        all_levels.sort()
        
        levels_below = [l for l in all_levels if l < current_price]
        levels_above = [l for l in all_levels if l > current_price]
        
        nearest_support = levels_below[-1] if levels_below else None
        nearest_resistance = levels_above[0] if levels_above else None
        
        # Calculate distance to levels
        if nearest_support:
            support_distance = ((current_price - nearest_support) / current_price) * 100
        else:
            support_distance = None
        
        if nearest_resistance:
            resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
        else:
            resistance_distance = None
        
        # Determine position
        if support_distance and resistance_distance:
            if support_distance < 2:
                position = "AT_SUPPORT"
                signal = "🟢 POTENTIAL BOUNCE"
            elif resistance_distance < 2:
                position = "AT_RESISTANCE"
                signal = "🔴 POTENTIAL REJECTION"
            elif support_distance < resistance_distance:
                position = "NEAR_SUPPORT"
                signal = "🟡 WATCH FOR SUPPORT TEST"
            else:
                position = "NEAR_RESISTANCE"
                signal = "🟠 WATCH FOR RESISTANCE TEST"
        else:
            position = "NO_CLEAR_LEVEL"
            signal = "⚪ NO NEARBY LEVELS"
        
        return {
            'position': position,
            'signal': signal,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'support_distance_percent': round(support_distance, 2) if support_distance else None,
            'resistance_distance_percent': round(resistance_distance, 2) if resistance_distance else None
        }
    
    def _find_nearest_support(self, current_price: float, 
                             color_coded_levels: Dict) -> Optional[Dict]:
        """Find nearest support level below current price"""
        all_support = []
        
        for category in ['support', 'pivot', 'weak_resistance', 
                        'moderate_resistance', 'strong_resistance']:
            if category in color_coded_levels:
                all_support.extend(color_coded_levels[category])
        
        # Filter levels below current price
        below = [l for l in all_support if l['price'] < current_price]
        
        if below:
            # Return closest level
            return min(below, key=lambda x: current_price - x['price'])
        else:
            return None
    
    def _find_nearest_resistance(self, current_price: float, 
                                 color_coded_levels: Dict) -> Optional[Dict]:
        """Find nearest resistance level above current price"""
        all_resistance = []
        
        for category in ['strong_resistance', 'moderate_resistance', 
                        'weak_resistance', 'pivot', 'support']:
            if category in color_coded_levels:
                all_resistance.extend(color_coded_levels[category])
        
        # Filter levels above current price
        above = [l for l in all_resistance if l['price'] > current_price]
        
        if above:
            # Return closest level
            return min(above, key=lambda x: x['price'] - current_price)
        else:
            return None
    
    def _empty_levels(self) -> Dict:
        """Return empty levels structure"""
        return {
            'levels': {
                'strong_resistance': [],
                'moderate_resistance': [],
                'weak_resistance': [],
                'pivot': [],
                'support': []
            },
            'current_price': 0.0,
            'position': {
                'position': 'UNKNOWN',
                'signal': '⚪ NO DATA',
                'nearest_support': None,
                'nearest_resistance': None
            },
            'nearest_support': None,
            'nearest_resistance': None,
            'error': 'No price data available'
        }
    
    def calculate_risk_reward(self, entry_price: float, 
                             support_level: float, 
                             resistance_level: float) -> Dict:
        """
        Calculate risk/reward ratio for a trade setup.
        
        Tim Bohen's Rule: Minimum 5:1 risk/reward for A+ setups.
        
        Args:
            entry_price: Proposed entry price
            support_level: Stop loss level (support)
            resistance_level: Target level (resistance)
        
        Returns:
            Dict with risk/reward analysis
        """
        try:
            # Calculate risk and reward
            risk = entry_price - support_level
            reward = resistance_level - entry_price
            
            if risk <= 0:
                return {'error': 'Invalid stop loss (must be below entry)'}
            
            if reward <= 0:
                return {'error': 'Invalid target (must be above entry)'}
            
            # Calculate ratio
            rr_ratio = reward / risk
            
            # Determine grade
            if rr_ratio >= 10:
                grade = "A+"
                quality = "EXCEPTIONAL"
            elif rr_ratio >= 7:
                grade = "A"
                quality = "EXCELLENT"
            elif rr_ratio >= 5:
                grade = "A-"
                quality = "STRONG"
            elif rr_ratio >= 3:
                grade = "B+"
                quality = "GOOD"
            elif rr_ratio >= 2:
                grade = "B"
                quality = "FAIR"
            else:
                grade = "C"
                quality = "WEAK"
            
            # Calculate percentages
            risk_percent = (risk / entry_price) * 100
            reward_percent = (reward / entry_price) * 100
            
            return {
                'risk_reward_ratio': round(rr_ratio, 2),
                'grade': grade,
                'quality': quality,
                'meets_bohen_criteria': rr_ratio >= 5.0,
                'entry_price': entry_price,
                'stop_loss': support_level,
                'target': resistance_level,
                'risk_dollars': round(risk, 2),
                'reward_dollars': round(reward, 2),
                'risk_percent': round(risk_percent, 2),
                'reward_percent': round(reward_percent, 2)
            }
            
        except Exception as e:
            print(f"❌ Error calculating risk/reward: {e}")
            return {'error': str(e)}
