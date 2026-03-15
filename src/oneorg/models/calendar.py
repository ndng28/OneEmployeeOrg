from datetime import date, timedelta
from typing import Optional
from pydantic import BaseModel, Field


class ActivityCalendar(BaseModel):
    """Tracks activity dates without streak pressure.
    
    Shows a visual calendar of recent activity with positive framing:
    "You've been active 12 days this month!" instead of streak counting.
    """
    activity_dates: set[str] = Field(default_factory=set)
    
    def mark_activity(self, activity_date: date) -> bool:
        """Mark a date as having activity. Returns True if newly added."""
        date_str = activity_date.isoformat()
        if date_str not in self.activity_dates:
            self.activity_dates.add(date_str)
            return True
        return False
    
    def has_activity_on(self, check_date: date) -> bool:
        return check_date.isoformat() in self.activity_dates
    
    @property
    def activity_count(self) -> int:
        return len(self.activity_dates)
    
    def get_recent_week(self) -> dict[str, bool]:
        """Get activity status for the past 7 days (oldest to newest)."""
        today = date.today()
        result = {}
        for i in range(6, -1, -1):
            check_date = today - timedelta(days=i)
            result[check_date.isoformat()] = self.has_activity_on(check_date)
        return result
    
    def get_recent_month_summary(self) -> dict:
        """Get positive-framed summary for display."""
        today = date.today()
        month_start = today.replace(day=1)
        
        active_days = sum(
            1 for d in self.activity_dates
            if date.fromisoformat(d) >= month_start
        )
        
        return {
            "active_days": active_days,
            "month_name": today.strftime("%B"),
            "message": f"You've been active {active_days} days this month!",
        }
    
    def get_consecutive_days(self, check_date: Optional[date] = None) -> int:
        """Count consecutive days UP TO check_date (for gentle encouragement, not pressure)."""
        if check_date is None:
            check_date = date.today()
        
        consecutive = 0
        current = check_date
        
        while self.has_activity_on(current):
            consecutive += 1
            current -= timedelta(days=1)
        
        return consecutive
