from datetime import date, timedelta


def test_calendar_tracks_activity_dates():
    from oneorg.models.calendar import ActivityCalendar
    
    calendar = ActivityCalendar()
    today = date.today()
    
    # Mark activity for today
    calendar.mark_activity(today)
    
    assert calendar.has_activity_on(today)
    assert calendar.activity_count == 1


def test_calendar_shows_recent_week():
    from oneorg.models.calendar import ActivityCalendar
    
    calendar = ActivityCalendar()
    today = date.today()
    
    # Add activities for past week
    for i in range(5):
        calendar.mark_activity(today - timedelta(days=i))
    
    week = calendar.get_recent_week()
    assert len(week) == 7
    assert sum(week.values()) == 5  # 5 active days


def test_calendar_has_no_longest_streak():
    """Ensure we removed the loss aversion trigger."""
    from oneorg.models.calendar import ActivityCalendar
    
    calendar = ActivityCalendar()
    assert not hasattr(calendar, 'longest_streak')
