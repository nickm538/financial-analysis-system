"""
ORACLE FLOAT ANALYSIS & ROTATION CALCULATOR
============================================
Tim Bohen's Float-Based Movement Prediction System.

Key Metrics:
- Float Size: <10M ideal, 20M maximum
- Float Rotation: (Daily Volume / Float) × 100
- Days to Cover: Float / Average Volume
- Institutional Ownership: Lower is better for volatility

Formula: Expected_Move% = (Float_Rotation × Catalyst_Score) / 100

For real-money trading - Maximum precision.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import math

class OracleFloat:
    """
    Oracle Float Analysis & Rotation Calculator
    
    Predicts explosive moves based on float size and volume rotation.
    Tim Bohen's proven methodology for small-cap momentum.
    """
    
    def __init__(self, finnhub_api_key: str):
        """
        Initialize Oracle Float Analyzer.
        
        Args:
            finnhub_api_key: Finnhub API key for float data
        """
        self.finnhub_api_key = finnhub_api_key
        self.base_url = "https://finnhub.io/api/v1"
        
        # Tim Bohen's Float Criteria
        self.FLOAT_IDEAL = 10_000_000  # <10M shares (best)
        self.FLOAT_ACCEPTABLE = 20_000_000  # 20M shares (max)
        self.FLOAT_TOO_HIGH = 50_000_000  # >50M (avoid)
        
        self.ROTATION_EXPLOSIVE = 50  # >50% rotation = explosive
        self.ROTATION_STRONG = 30  # 30-50% = strong
        self.ROTATION_MODERATE = 15  # 15-30% = moderate
        self.ROTATION_WEAK = 5  # <5% = weak
        
        self.INSTITUTIONAL_LOW = 20  # <20% institutional = ideal
        self.INSTITUTIONAL_MODERATE = 40  # 20-40% = acceptable
        self.INSTITUTIONAL_HIGH = 60  # >60% = avoid
    
    def analyze_float(self, ticker: str, current_volume: float, 
                     avg_volume: float) -> Dict:
        """
        Comprehensive float analysis for a stock.
        
        Args:
            ticker: Stock symbol
            current_volume: Today's volume
            avg_volume: Average daily volume
        
        Returns:
            Dict with complete float analysis
        """
        try:
            # Fetch float data from Finnhub
            float_data = self._fetch_float_data(ticker)
            
            if not float_data:
                return self._empty_float_result(ticker)
            
            # Extract key metrics
            float_size = float_data.get('float', 0)
            shares_outstanding = float_data.get('shares_outstanding', 0)
            institutional_ownership = float_data.get('institutional_ownership', 0)
            insider_ownership = float_data.get('insider_ownership', 0)
            
            # Calculate float rotation
            rotation = self._calculate_float_rotation(float_size, current_volume)
            
            # Calculate days to cover
            days_to_cover = self._calculate_days_to_cover(float_size, avg_volume)
            
            # Calculate expected move
            expected_move = self._calculate_expected_move(rotation, float_size)
            
            # Grade float quality
            float_grade = self._grade_float_size(float_size)
            rotation_grade = self._grade_rotation(rotation)
            institutional_grade = self._grade_institutional(institutional_ownership)
            
            # Calculate overall float score (0-100)
            float_score = self._calculate_float_score(
                float_size, rotation, institutional_ownership
            )
            
            # Determine if stock meets Tim Bohen's criteria
            meets_criteria = self._check_bohen_criteria(
                float_size, rotation, institutional_ownership
            )
            
            return {
                'ticker': ticker,
                'float_size': float_size,
                'shares_outstanding': shares_outstanding,
                'float_rotation': round(rotation, 2),
                'days_to_cover': round(days_to_cover, 2),
                'institutional_ownership': round(institutional_ownership, 2),
                'insider_ownership': round(insider_ownership, 2),
                'expected_move_percent': round(expected_move, 2),
                'float_grade': float_grade,
                'rotation_grade': rotation_grade,
                'institutional_grade': institutional_grade,
                'float_score': float_score,
                'meets_bohen_criteria': meets_criteria,
                'analysis': self._generate_analysis(
                    float_size, rotation, institutional_ownership, expected_move
                ),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error analyzing float for {ticker}: {e}")
            return self._empty_float_result(ticker, error=str(e))
    
    def _fetch_float_data(self, ticker: str) -> Optional[Dict]:
        """
        Fetch float data from Finnhub.
        
        Args:
            ticker: Stock symbol
        
        Returns:
            Dict with float data or None
        """
        try:
            # Fetch basic financials (includes float)
            url = f"{self.base_url}/stock/metric"
            params = {
                'symbol': ticker,
                'metric': 'all',
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract metrics from nested structure
                if 'metric' in data and isinstance(data['metric'], dict):
                    metrics = data['metric']
                    
                    return {
                        'float': metrics.get('sharesFloat', 0),
                        'shares_outstanding': metrics.get('sharesOutstanding', 0),
                        'institutional_ownership': metrics.get('institutionalHoldingPercent', 0),
                        'insider_ownership': metrics.get('insiderHoldingPercent', 0)
                    }
                else:
                    print(f"⚠️ Unexpected Finnhub data structure for {ticker}")
                    return None
            else:
                print(f"⚠️ Finnhub API returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error fetching float data: {e}")
            return None
    
    def _calculate_float_rotation(self, float_size: float, 
                                  current_volume: float) -> float:
        """
        Calculate float rotation percentage.
        
        Formula: (Daily Volume / Float) × 100
        
        Args:
            float_size: Number of shares in float
            current_volume: Today's volume
        
        Returns:
            Float rotation percentage
        """
        if float_size > 0:
            return (current_volume / float_size) * 100
        else:
            return 0.0
    
    def _calculate_days_to_cover(self, float_size: float, 
                                 avg_volume: float) -> float:
        """
        Calculate days to cover (float / average volume).
        
        Lower is better - indicates how quickly float can be absorbed.
        
        Args:
            float_size: Number of shares in float
            avg_volume: Average daily volume
        
        Returns:
            Days to cover
        """
        if avg_volume > 0:
            return float_size / avg_volume
        else:
            return 999.0  # Effectively infinite
    
    def _calculate_expected_move(self, rotation: float, 
                                 float_size: float) -> float:
        """
        Calculate expected price move based on rotation and float.
        
        Tim Bohen's Formula (simplified):
        Expected_Move% = (Rotation × Float_Multiplier) / 10
        
        Where Float_Multiplier:
        - <5M float: 3.0x
        - 5-10M float: 2.0x
        - 10-20M float: 1.5x
        - >20M float: 1.0x
        
        Args:
            rotation: Float rotation percentage
            float_size: Number of shares in float
        
        Returns:
            Expected move percentage
        """
        # Determine float multiplier
        if float_size < 5_000_000:
            multiplier = 3.0
        elif float_size < self.FLOAT_IDEAL:
            multiplier = 2.0
        elif float_size < self.FLOAT_ACCEPTABLE:
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        # Calculate expected move
        expected_move = (rotation * multiplier) / 10
        
        return min(expected_move, 100.0)  # Cap at 100%
    
    def _grade_float_size(self, float_size: float) -> Dict:
        """Grade float size quality"""
        if float_size == 0:
            return {'grade': 'N/A', 'quality': 'UNKNOWN', 'description': 'No float data'}
        elif float_size < 5_000_000:
            return {
                'grade': 'A+',
                'quality': 'EXCEPTIONAL',
                'description': 'Ultra-low float - Explosive potential'
            }
        elif float_size < self.FLOAT_IDEAL:
            return {
                'grade': 'A',
                'quality': 'EXCELLENT',
                'description': 'Low float - Strong potential'
            }
        elif float_size < self.FLOAT_ACCEPTABLE:
            return {
                'grade': 'B+',
                'quality': 'GOOD',
                'description': 'Acceptable float - Moderate potential'
            }
        elif float_size < self.FLOAT_TOO_HIGH:
            return {
                'grade': 'C',
                'quality': 'FAIR',
                'description': 'High float - Limited potential'
            }
        else:
            return {
                'grade': 'F',
                'quality': 'POOR',
                'description': 'Float too high - Avoid'
            }
    
    def _grade_rotation(self, rotation: float) -> Dict:
        """Grade float rotation quality"""
        if rotation >= self.ROTATION_EXPLOSIVE:
            return {
                'grade': 'A+',
                'quality': 'EXPLOSIVE',
                'description': f'{rotation:.1f}% rotation - Extreme volume'
            }
        elif rotation >= self.ROTATION_STRONG:
            return {
                'grade': 'A',
                'quality': 'STRONG',
                'description': f'{rotation:.1f}% rotation - High volume'
            }
        elif rotation >= self.ROTATION_MODERATE:
            return {
                'grade': 'B',
                'quality': 'MODERATE',
                'description': f'{rotation:.1f}% rotation - Good volume'
            }
        elif rotation >= self.ROTATION_WEAK:
            return {
                'grade': 'C',
                'quality': 'WEAK',
                'description': f'{rotation:.1f}% rotation - Low volume'
            }
        else:
            return {
                'grade': 'F',
                'quality': 'VERY_WEAK',
                'description': f'{rotation:.1f}% rotation - Minimal volume'
            }
    
    def _grade_institutional(self, institutional_percent: float) -> Dict:
        """Grade institutional ownership"""
        if institutional_percent < self.INSTITUTIONAL_LOW:
            return {
                'grade': 'A+',
                'quality': 'IDEAL',
                'description': f'{institutional_percent:.1f}% institutional - High volatility potential'
            }
        elif institutional_percent < self.INSTITUTIONAL_MODERATE:
            return {
                'grade': 'A',
                'quality': 'GOOD',
                'description': f'{institutional_percent:.1f}% institutional - Acceptable'
            }
        elif institutional_percent < self.INSTITUTIONAL_HIGH:
            return {
                'grade': 'B',
                'quality': 'MODERATE',
                'description': f'{institutional_percent:.1f}% institutional - Some resistance'
            }
        else:
            return {
                'grade': 'C',
                'quality': 'HIGH',
                'description': f'{institutional_percent:.1f}% institutional - Limited volatility'
            }
    
    def _calculate_float_score(self, float_size: float, rotation: float, 
                               institutional: float) -> int:
        """
        Calculate overall float score (0-100).
        
        Weighting:
        - Float size: 40%
        - Rotation: 40%
        - Institutional: 20%
        
        Args:
            float_size: Number of shares in float
            rotation: Float rotation percentage
            institutional: Institutional ownership percentage
        
        Returns:
            Score from 0-100
        """
        # Float size score (0-40)
        if float_size == 0:
            float_score = 0
        elif float_size < 5_000_000:
            float_score = 40
        elif float_size < self.FLOAT_IDEAL:
            float_score = 35
        elif float_size < self.FLOAT_ACCEPTABLE:
            float_score = 25
        elif float_size < self.FLOAT_TOO_HIGH:
            float_score = 10
        else:
            float_score = 0
        
        # Rotation score (0-40)
        if rotation >= self.ROTATION_EXPLOSIVE:
            rotation_score = 40
        elif rotation >= self.ROTATION_STRONG:
            rotation_score = 35
        elif rotation >= self.ROTATION_MODERATE:
            rotation_score = 25
        elif rotation >= self.ROTATION_WEAK:
            rotation_score = 10
        else:
            rotation_score = 0
        
        # Institutional score (0-20)
        if institutional < self.INSTITUTIONAL_LOW:
            institutional_score = 20
        elif institutional < self.INSTITUTIONAL_MODERATE:
            institutional_score = 15
        elif institutional < self.INSTITUTIONAL_HIGH:
            institutional_score = 8
        else:
            institutional_score = 0
        
        return float_score + rotation_score + institutional_score
    
    def _check_bohen_criteria(self, float_size: float, rotation: float, 
                             institutional: float) -> Dict:
        """
        Check if stock meets Tim Bohen's float criteria.
        
        Criteria:
        1. Float <20M shares
        2. Rotation >15%
        3. Institutional <60%
        
        Args:
            float_size: Number of shares in float
            rotation: Float rotation percentage
            institutional: Institutional ownership percentage
        
        Returns:
            Dict with criteria check results
        """
        criteria = {
            'float_acceptable': 0 < float_size <= self.FLOAT_ACCEPTABLE,
            'float_ideal': 0 < float_size <= self.FLOAT_IDEAL,
            'rotation_strong': rotation >= self.ROTATION_MODERATE,
            'rotation_explosive': rotation >= self.ROTATION_EXPLOSIVE,
            'institutional_acceptable': institutional < self.INSTITUTIONAL_HIGH,
            'institutional_ideal': institutional < self.INSTITUTIONAL_LOW
        }
        
        # All critical criteria must be met
        meets_all = (
            criteria['float_acceptable'] and
            criteria['rotation_strong'] and
            criteria['institutional_acceptable']
        )
        
        # Ideal setup
        is_ideal = (
            criteria['float_ideal'] and
            criteria['rotation_explosive'] and
            criteria['institutional_ideal']
        )
        
        return {
            'meets_minimum': meets_all,
            'is_ideal_setup': is_ideal,
            'criteria': criteria
        }
    
    def _generate_analysis(self, float_size: float, rotation: float, 
                          institutional: float, expected_move: float) -> str:
        """Generate human-readable analysis"""
        if float_size == 0:
            return "⚠️ No float data available"
        
        # Float analysis
        if float_size < self.FLOAT_IDEAL:
            float_text = f"✅ Excellent float ({float_size/1_000_000:.1f}M shares)"
        elif float_size < self.FLOAT_ACCEPTABLE:
            float_text = f"🟡 Acceptable float ({float_size/1_000_000:.1f}M shares)"
        else:
            float_text = f"🔴 Float too high ({float_size/1_000_000:.1f}M shares)"
        
        # Rotation analysis
        if rotation >= self.ROTATION_EXPLOSIVE:
            rotation_text = f"🚀 Explosive rotation ({rotation:.1f}%)"
        elif rotation >= self.ROTATION_STRONG:
            rotation_text = f"✅ Strong rotation ({rotation:.1f}%)"
        elif rotation >= self.ROTATION_MODERATE:
            rotation_text = f"🟡 Moderate rotation ({rotation:.1f}%)"
        else:
            rotation_text = f"🔴 Weak rotation ({rotation:.1f}%)"
        
        # Institutional analysis
        if institutional < self.INSTITUTIONAL_LOW:
            inst_text = f"✅ Low institutional ({institutional:.1f}%)"
        elif institutional < self.INSTITUTIONAL_MODERATE:
            inst_text = f"🟡 Moderate institutional ({institutional:.1f}%)"
        else:
            inst_text = f"🔴 High institutional ({institutional:.1f}%)"
        
        # Expected move
        move_text = f"📈 Expected move: {expected_move:.1f}%"
        
        return f"{float_text} | {rotation_text} | {inst_text} | {move_text}"
    
    def _empty_float_result(self, ticker: str, error: Optional[str] = None) -> Dict:
        """Return empty float result"""
        result = {
            'ticker': ticker,
            'float_size': 0,
            'shares_outstanding': 0,
            'float_rotation': 0,
            'days_to_cover': 0,
            'institutional_ownership': 0,
            'insider_ownership': 0,
            'expected_move_percent': 0,
            'float_grade': {'grade': 'N/A', 'quality': 'UNKNOWN'},
            'rotation_grade': {'grade': 'N/A', 'quality': 'UNKNOWN'},
            'institutional_grade': {'grade': 'N/A', 'quality': 'UNKNOWN'},
            'float_score': 0,
            'meets_bohen_criteria': {
                'meets_minimum': False,
                'is_ideal_setup': False,
                'criteria': {}
            },
            'analysis': '⚠️ No float data available',
            'timestamp': datetime.now().isoformat()
        }
        
        if error:
            result['error'] = error
        
        return result
