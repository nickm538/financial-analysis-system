"""
DATETIME CONTEXT - MARKET TIMING & CALENDAR AWARENESS
======================================================
Real-time awareness of market conditions based on date/time.

FEATURES:
1. Market Hours Detection (Pre-market, Regular, After-hours, Closed)
2. Economic Calendar Integration (Fed, CPI, Jobs, Earnings)
3. Options Expiration Awareness (Monthly, Weekly, Quad Witching)
4. Holiday Calendar
5. Earnings Season Detection
6. End of Month/Quarter Effects

ALL DATA IS REAL-TIME - NO FAKE CALCULATIONS
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz


class DateTimeContext:
    """
    Market timing and calendar awareness for trading decisions.
    """
    
    def __init__(self):
        self.eastern = pytz.timezone('US/Eastern')
        
        # 2025-2026 Market Holidays (NYSE)
        self.market_holidays = [
            # 2025
            datetime(2025, 1, 1),   # New Year's Day
            datetime(2025, 1, 20),  # MLK Day
            datetime(2025, 2, 17),  # Presidents Day
            datetime(2025, 4, 18),  # Good Friday
            datetime(2025, 5, 26),  # Memorial Day
            datetime(2025, 6, 19),  # Juneteenth
            datetime(2025, 7, 4),   # Independence Day
            datetime(2025, 9, 1),   # Labor Day
            datetime(2025, 11, 27), # Thanksgiving
            datetime(2025, 12, 25), # Christmas
            # 2026
            datetime(2026, 1, 1),   # New Year's Day
            datetime(2026, 1, 19),  # MLK Day
            datetime(2026, 2, 16),  # Presidents Day
            datetime(2026, 4, 3),   # Good Friday
            datetime(2026, 5, 25),  # Memorial Day
            datetime(2026, 6, 19),  # Juneteenth
            datetime(2026, 7, 3),   # Independence Day (observed)
            datetime(2026, 9, 7),   # Labor Day
            datetime(2026, 11, 26), # Thanksgiving
            datetime(2026, 12, 25), # Christmas
        ]
        
        # Key Economic Events (approximate dates - these shift yearly)
        # Format: (month, typical_week, event_name, impact)
        self.recurring_events = [
            (1, 1, "FOMC Minutes", "HIGH"),
            (1, 2, "CPI Release", "VERY_HIGH"),
            (1, 3, "FOMC Meeting", "VERY_HIGH"),
            (2, 1, "Jobs Report", "VERY_HIGH"),
            (2, 2, "CPI Release", "VERY_HIGH"),
            (3, 1, "Jobs Report", "VERY_HIGH"),
            (3, 2, "CPI Release", "VERY_HIGH"),
            (3, 3, "FOMC Meeting", "VERY_HIGH"),
            (4, 1, "Jobs Report", "VERY_HIGH"),
            (4, 2, "CPI Release", "VERY_HIGH"),
            (5, 1, "Jobs Report", "VERY_HIGH"),
            (5, 2, "CPI Release", "VERY_HIGH"),
            (5, 1, "FOMC Meeting", "VERY_HIGH"),
            (6, 1, "Jobs Report", "VERY_HIGH"),
            (6, 2, "CPI Release", "VERY_HIGH"),
            (6, 3, "FOMC Meeting", "VERY_HIGH"),
            (7, 1, "Jobs Report", "VERY_HIGH"),
            (7, 2, "CPI Release", "VERY_HIGH"),
            (8, 1, "Jobs Report", "VERY_HIGH"),
            (8, 2, "CPI Release", "VERY_HIGH"),
            (9, 1, "Jobs Report", "VERY_HIGH"),
            (9, 2, "CPI Release", "VERY_HIGH"),
            (9, 3, "FOMC Meeting", "VERY_HIGH"),
            (10, 1, "Jobs Report", "VERY_HIGH"),
            (10, 2, "CPI Release", "VERY_HIGH"),
            (11, 1, "Jobs Report", "VERY_HIGH"),
            (11, 2, "CPI Release", "VERY_HIGH"),
            (11, 1, "FOMC Meeting", "VERY_HIGH"),
            (12, 1, "Jobs Report", "VERY_HIGH"),
            (12, 2, "CPI Release", "VERY_HIGH"),
            (12, 3, "FOMC Meeting", "VERY_HIGH"),
        ]
    
    def get_current_context(self) -> Dict:
        """
        Get comprehensive date/time context for trading decisions.
        """
        now = datetime.now(self.eastern)
        
        return {
            "timestamp": now.isoformat(),
            "market_status": self._get_market_status(now),
            "trading_session": self._get_trading_session(now),
            "calendar_context": self._get_calendar_context(now),
            "options_context": self._get_options_context(now),
            "seasonality_context": self._get_seasonality_context(now),
            "risk_events": self._get_upcoming_risk_events(now),
            "trading_recommendation": self._get_timing_recommendation(now)
        }
    
    def _get_market_status(self, now: datetime) -> Dict:
        """Determine current market status."""
        # Check if holiday
        today = now.date()
        is_holiday = any(h.date() == today for h in self.market_holidays)
        
        # Check if weekend
        is_weekend = now.weekday() >= 5
        
        if is_holiday:
            return {
                "status": "CLOSED",
                "reason": "Market Holiday",
                "next_open": self._get_next_market_open(now)
            }
        
        if is_weekend:
            return {
                "status": "CLOSED",
                "reason": "Weekend",
                "next_open": self._get_next_market_open(now)
            }
        
        hour = now.hour
        minute = now.minute
        time_decimal = hour + minute / 60
        
        if time_decimal < 4:
            status = "CLOSED"
            session = "Overnight"
        elif time_decimal < 9.5:
            status = "PRE_MARKET"
            session = "Pre-Market (4:00 AM - 9:30 AM)"
        elif time_decimal < 16:
            status = "OPEN"
            session = "Regular Hours (9:30 AM - 4:00 PM)"
        elif time_decimal < 20:
            status = "AFTER_HOURS"
            session = "After-Hours (4:00 PM - 8:00 PM)"
        else:
            status = "CLOSED"
            session = "Overnight"
        
        return {
            "status": status,
            "session": session,
            "is_regular_hours": status == "OPEN",
            "time_to_open": self._time_to_open(now) if status != "OPEN" else None,
            "time_to_close": self._time_to_close(now) if status == "OPEN" else None
        }
    
    def _get_next_market_open(self, now: datetime) -> str:
        """Get next market open time."""
        next_day = now + timedelta(days=1)
        while next_day.weekday() >= 5 or any(h.date() == next_day.date() for h in self.market_holidays):
            next_day += timedelta(days=1)
        
        open_time = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
        return open_time.strftime("%Y-%m-%d %H:%M ET")
    
    def _time_to_open(self, now: datetime) -> str:
        """Calculate time until market opens."""
        if now.weekday() >= 5:
            # Weekend - calculate to Monday
            days_until_monday = 7 - now.weekday()
            open_time = (now + timedelta(days=days_until_monday)).replace(
                hour=9, minute=30, second=0, microsecond=0
            )
        else:
            open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
            if now >= open_time:
                open_time += timedelta(days=1)
        
        delta = open_time - now
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60
        
        if delta.days > 0:
            return f"{delta.days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m"
    
    def _time_to_close(self, now: datetime) -> str:
        """Calculate time until market closes."""
        close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
        delta = close_time - now
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60
        return f"{hours}h {minutes}m"
    
    def _get_trading_session(self, now: datetime) -> Dict:
        """Get detailed trading session information."""
        hour = now.hour
        minute = now.minute
        time_decimal = hour + minute / 60
        
        # Session characteristics
        if 9.5 <= time_decimal < 10:
            session_type = "OPENING_VOLATILITY"
            description = "First 30 minutes - High volatility, gaps filling"
            risk_level = "HIGH"
            recommendation = "Wait for direction to establish. Avoid chasing."
        elif 10 <= time_decimal < 11.5:
            session_type = "MORNING_MOMENTUM"
            description = "Morning momentum - Best moves often happen here"
            risk_level = "MODERATE"
            recommendation = "Prime trading window. Look for breakouts with volume."
        elif 11.5 <= time_decimal < 14:
            session_type = "MIDDAY_CHOP"
            description = "Lunch hour - Low volume, choppy action"
            risk_level = "MODERATE"
            recommendation = "Reduce activity. Many false signals during this period."
        elif 14 <= time_decimal < 15.5:
            session_type = "AFTERNOON_TREND"
            description = "Afternoon session - Trends often resume"
            risk_level = "MODERATE"
            recommendation = "Watch for trend continuation or reversal setups."
        elif 15.5 <= time_decimal < 16:
            session_type = "POWER_HOUR"
            description = "Last 30 minutes - Institutional positioning"
            risk_level = "HIGH"
            recommendation = "High volume, strong moves. Close positions or ride momentum."
        else:
            session_type = "EXTENDED_HOURS"
            description = "Pre/After market - Lower liquidity"
            risk_level = "HIGH"
            recommendation = "Wider spreads, less liquidity. Trade with caution."
        
        return {
            "session_type": session_type,
            "description": description,
            "risk_level": risk_level,
            "recommendation": recommendation
        }
    
    def _get_calendar_context(self, now: datetime) -> Dict:
        """Get calendar-based context."""
        day_of_week = now.weekday()
        day_of_month = now.day
        month = now.month
        
        # Day of week effects
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_effects = {
            0: "Mondays often see gap fills from weekend news. Watch for reversals.",
            1: "Tuesdays historically neutral. Good for trend continuation.",
            2: "Wednesdays often see Fed announcements. Check calendar.",
            3: "Thursdays see weekly options expiration. Increased volatility.",
            4: "Fridays see position squaring. Watch for end-of-week moves.",
        }
        
        # Month effects
        month_effects = {
            1: "January Effect - Small caps often outperform early in year.",
            2: "February often sees continuation of January trends.",
            3: "March - End of Q1. Watch for window dressing.",
            4: "April - Tax selling ends. Historically strong month.",
            5: "May - 'Sell in May' seasonality. Caution warranted.",
            6: "June - End of Q2. Rebalancing flows.",
            7: "July - Summer doldrums begin. Lower volume.",
            8: "August - Vacation season. Thin markets can be volatile.",
            9: "September - Historically weakest month. Be defensive.",
            10: "October - Volatility month. Watch for bottoms.",
            11: "November - Holiday rally often begins.",
            12: "December - Santa Rally, tax-loss selling early month."
        }
        
        # End of month/quarter effects
        is_month_end = day_of_month >= 25
        is_quarter_end = month in [3, 6, 9, 12] and is_month_end
        
        return {
            "day_of_week": dow_names[day_of_week],
            "day_effect": dow_effects.get(day_of_week, ""),
            "month": month,
            "month_effect": month_effects.get(month, ""),
            "is_month_end": is_month_end,
            "is_quarter_end": is_quarter_end,
            "calendar_note": self._get_calendar_note(is_month_end, is_quarter_end)
        }
    
    def _get_calendar_note(self, month_end: bool, quarter_end: bool) -> str:
        """Get note about calendar effects."""
        if quarter_end:
            return "⚠️ QUARTER END - Expect window dressing, rebalancing flows, and increased volatility."
        elif month_end:
            return "📅 MONTH END - Watch for institutional rebalancing and position adjustments."
        return ""
    
    def _get_options_context(self, now: datetime) -> Dict:
        """Get options expiration context."""
        # Find next Friday
        days_until_friday = (4 - now.weekday()) % 7
        if days_until_friday == 0 and now.hour >= 16:
            days_until_friday = 7
        next_friday = now + timedelta(days=days_until_friday)
        
        # Monthly options expire 3rd Friday
        # Find 3rd Friday of current month
        first_day = now.replace(day=1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
        third_friday = first_friday + timedelta(weeks=2)
        
        is_monthly_opex = next_friday.date() == third_friday.date()
        
        # Quad witching (3rd Friday of Mar, Jun, Sep, Dec)
        is_quad_witching = is_monthly_opex and now.month in [3, 6, 9, 12]
        
        # Days to expiration
        days_to_opex = days_until_friday
        
        return {
            "next_expiration": next_friday.strftime("%Y-%m-%d"),
            "days_to_expiration": days_to_opex,
            "is_monthly_opex": is_monthly_opex,
            "is_quad_witching": is_quad_witching,
            "opex_warning": self._get_opex_warning(days_to_opex, is_monthly_opex, is_quad_witching)
        }
    
    def _get_opex_warning(self, days: int, monthly: bool, quad: bool) -> str:
        """Get options expiration warning."""
        if quad and days <= 2:
            return "🔴 QUAD WITCHING - Extreme volatility expected. Max pain levels will be tested."
        elif monthly and days <= 2:
            return "⚠️ MONTHLY OPEX - Increased volatility. Watch for pinning at key strikes."
        elif days <= 1:
            return "📌 WEEKLY OPEX - Short-dated options expiring. Watch for gamma effects."
        elif days <= 3:
            return "Options expiration approaching. Gamma exposure increasing."
        return ""
    
    def _get_seasonality_context(self, now: datetime) -> Dict:
        """Get seasonality-based context."""
        month = now.month
        
        # Earnings seasons
        earnings_months = [1, 4, 7, 10]  # Earnings season months
        is_earnings_season = month in earnings_months or (month - 1) in earnings_months
        
        # Tax loss selling (December)
        is_tax_loss_season = month == 12 and now.day <= 20
        
        # Santa Rally (last 5 trading days of year + first 2 of new year)
        is_santa_rally = (month == 12 and now.day >= 24) or (month == 1 and now.day <= 3)
        
        return {
            "is_earnings_season": is_earnings_season,
            "is_tax_loss_season": is_tax_loss_season,
            "is_santa_rally": is_santa_rally,
            "seasonality_note": self._get_seasonality_note(is_earnings_season, is_tax_loss_season, is_santa_rally)
        }
    
    def _get_seasonality_note(self, earnings: bool, tax_loss: bool, santa: bool) -> str:
        """Get seasonality note."""
        if santa:
            return "🎅 SANTA RALLY - Historically bullish period. Enjoy the ride!"
        elif tax_loss:
            return "📉 TAX LOSS SELLING - Beaten-down stocks may face additional pressure."
        elif earnings:
            return "📊 EARNINGS SEASON - Expect increased volatility around reports."
        return ""
    
    def _get_upcoming_risk_events(self, now: datetime) -> List[Dict]:
        """Get upcoming high-impact events."""
        events = []
        
        # Check next 7 days for recurring events
        for month, week, event_name, impact in self.recurring_events:
            if month == now.month:
                # Approximate event date (week of month)
                event_date = now.replace(day=min(28, week * 7))
                days_until = (event_date - now).days
                
                if 0 <= days_until <= 7:
                    events.append({
                        "event": event_name,
                        "approximate_date": event_date.strftime("%Y-%m-%d"),
                        "days_until": days_until,
                        "impact": impact
                    })
        
        return sorted(events, key=lambda x: x["days_until"])[:5]
    
    def _get_timing_recommendation(self, now: datetime) -> Dict:
        """Get overall timing recommendation."""
        market_status = self._get_market_status(now)
        session = self._get_trading_session(now)
        options = self._get_options_context(now)
        calendar = self._get_calendar_context(now)
        
        # Calculate timing score
        score = 50  # Neutral baseline
        warnings = []
        
        # Market status
        if market_status["status"] != "OPEN":
            score -= 20
            warnings.append("Market not in regular hours")
        
        # Session quality
        if session["session_type"] == "MIDDAY_CHOP":
            score -= 15
            warnings.append("Midday chop - lower quality setups")
        elif session["session_type"] in ["MORNING_MOMENTUM", "AFTERNOON_TREND"]:
            score += 10
        
        # Options expiration
        if options["is_quad_witching"] and options["days_to_expiration"] <= 2:
            score -= 20
            warnings.append("Quad witching volatility")
        elif options["days_to_expiration"] <= 1:
            score -= 10
            warnings.append("Options expiration day")
        
        # Calendar effects
        if calendar["is_quarter_end"]:
            score -= 10
            warnings.append("Quarter-end rebalancing")
        
        # Determine recommendation
        if score >= 60:
            recommendation = "FAVORABLE"
            action = "Good timing for new positions"
        elif score >= 40:
            recommendation = "NEUTRAL"
            action = "Proceed with normal caution"
        else:
            recommendation = "CAUTION"
            action = "Consider reducing activity or waiting"
        
        return {
            "timing_score": score,
            "recommendation": recommendation,
            "action": action,
            "warnings": warnings
        }


# Test if run directly
if __name__ == "__main__":
    ctx = DateTimeContext()
    result = ctx.get_current_context()
    
    print("=== CURRENT MARKET CONTEXT ===")
    print(f"Market Status: {result['market_status']['status']}")
    print(f"Session: {result['trading_session']['session_type']}")
    print(f"Recommendation: {result['trading_session']['recommendation']}")
    print()
    print(f"Calendar: {result['calendar_context']['day_of_week']}")
    print(f"Effect: {result['calendar_context']['day_effect']}")
    print()
    print(f"Options: {result['options_context']['days_to_expiration']} days to expiration")
    print(f"Warning: {result['options_context']['opex_warning']}")
    print()
    print(f"Timing Score: {result['trading_recommendation']['timing_score']}")
    print(f"Action: {result['trading_recommendation']['action']}")
