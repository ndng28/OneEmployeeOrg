from datetime import date
from oneorg.models.calendar import ActivityCalendar


class CalendarManager:
    """Manages activity calendars with positive framing."""
    
    def mark_quest_completion(self, calendar: ActivityCalendar) -> bool:
        """Mark today's activity from quest completion."""
        return calendar.mark_activity(date.today())
    
    def get_display_data(self, calendar: ActivityCalendar) -> dict:
        """Get age-appropriate display data."""
        week = calendar.get_recent_week()
        month = calendar.get_recent_month_summary()
        
        return {
            "recent_week": week,
            "month_summary": month,
            "total_days": calendar.activity_count,
        }
