# Gamification Refactor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor gamification to remove harmful mechanics (rarity tiers, loss aversion triggers) and implement healthy alternatives (age modes, effort-based badges, positive framing)

**Architecture:** Split into 7 parallel workstreams: AgeMode infrastructure, badge system refactor, streak removal, leaderboard opt-in, XP predictability, effort-based badges, and CLI updates. Each stream is independent with clear interfaces.

**Tech Stack:** Python 3.11+, Pydantic, FastAPI, SQLAlchemy, HTMX, Jinja2, pytest

---

## File Structure

### New Files
- `src/oneorg/models/age_mode.py` - AgeMode enum and configuration
- `src/oneorg/models/calendar.py` - ActivityCalendar model (replaces streak)
- `src/oneorg/models/personal_progress.py` - PersonalProgressView model
- `src/oneorg/gamification/calendar.py` - CalendarManager service
- `src/oneorg/gamification/effort_badges.py` - Effort-based badge definitions

### Modified Files
- `src/oneorg/models/gamification.py` - Remove BadgeRarity, StreakData.longest_streak, Team
- `src/oneorg/models/student.py` - Add age_mode, calendar field, remove team_id
- `src/oneorg/models/leaderboard.py` - Update visibility defaults
- `src/oneorg/db/models.py` - Update database schema
- `src/oneorg/gamification/badges.py` - Remove rarity references, add effort criteria
- `src/oneorg/gamification/leaderboard.py` - Make opt-in default
- `src/oneorg/cli.py` - Replace leaderboard command with personal progress
- `src/oneorg/api/routes/ui.py` - Update dashboard templates
- `tests/` - Update test suite

---

## Chunk 1: AgeMode Infrastructure

**Worker:** Agent 1 (independent, other workers depend on this)

**Goal:** Create AgeMode enum and integrate into StudentProgress

### Files
- Create: `src/oneorg/models/age_mode.py`
- Modify: `src/oneorg/models/student.py:1-98`

### Task 1.1: Create AgeMode model

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_age_mode.py
def test_age_mode_enum_values():
    from oneorg.models.age_mode import AgeMode
    
    assert AgeMode.YOUNG.value == "5-8"
    assert AgeMode.MIDDLE.value == "9-12"
    assert AgeMode.TEEN.value == "13-18"

def test_age_mode_computed_field():
    from oneorg.models.age_mode import AgeMode
    
    student = StudentProgress(
        student_id="stu_test",
        name="Test",
        grade_level=6,
    )
    
    assert student.age_mode == AgeMode.MIDDLE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_age_mode.py::test_age_mode_enum_values -v`
Expected: FAIL with "No module named 'oneorg.models.age_mode'"

- [ ] **Step 3: Write AgeMode enum**

```python
# src/oneorg/models/age_mode.py
from enum import Enum
from typing import Optional

class AgeMode(str, Enum):
    """Age-based display and interaction modes."""
    YOUNG = "5-8"
    MIDDLE = "9-12"
    TEEN = "13-18"
    
    @classmethod
    def from_grade(cls, grade_level: int) -> "AgeMode":
        if grade_level <= 8:
            return cls.YOUNG
        elif grade_level <= 12:
            return cls.MIDDLE
        else:
            return cls.TEEN
    
    @property
    def xp_display_mode(self) -> str:
        """How XP is displayed for this age group."""
        modes = {
            AgeMode.YOUNG: "stars",
            AgeMode.MIDDLE: "points",
            AgeMode.TEEN: "xp",
        }
        return modes[self]
    
    @property
    def description(self) -> str:
        """Age-appropriate description."""
        descriptions = {
            AgeMode.YOUNG: "Young Explorers",
            AgeMode.MIDDLE: "Young Learners",
            AgeMode.TEEN: "Young Scholars",
        }
        return descriptions[self]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models/test_age_mode.py::test_age_mode_enum_values -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models/test_age_mode.py src/oneorg/models/age_mode.py
git commit -m "feat: add AgeMode enum with grade-based mapping

- Add AgeMode enum with YOUNG (5-8), MIDDLE (9-12), TEEN (13-18)
- Add from_grade() factory method
- Add display modes and descriptions per age group"
```

### Task 1.2: Add age_mode to StudentProgress

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_student.py (append)
def test_student_has_computed_age_mode():
    student = StudentProgress(
        student_id="stu_001",
        name="Alice",
        grade_level=5,
    )
    
    from oneorg.models.age_mode import AgeMode
    assert student.age_mode == AgeMode.YOUNG

def test_age_mode_from_grade_10():
    student = StudentProgress(
        student_id="stu_002",
        name="Bob",
        grade_level=10,
    )
    
    from oneorg.models.age_mode import AgeMode
    assert student.age_mode == AgeMode.MIDDLE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_student.py::test_student_has_computed_age_mode -v`
Expected: FAIL with "AttributeError: 'StudentProgress' object has no attribute 'age_mode'"

- [ ] **Step 3: Add age_mode computed field to StudentProgress**

```python
# src/oneorg/models/student.py (add imports and computed field)
from oneorg.models.age_mode import AgeMode

# Add after existing imports at top of file

# Add computed field after xp_to_next_level property:
    @computed_field
    @property
    def age_mode(self) -> AgeMode:
        return AgeMode.from_grade(self.grade_level)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models/test_student.py::test_student_has_computed_age_mode -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models/test_student.py src/oneorg/models/student.py
git commit -m "feat: add age_mode computed field to StudentProgress

- Age mode is computed from grade_level
- Supports 3 profiles: YOUNG (5-8), MIDDLE (9-12), TEEN (13-18)"
```

### Task 1.3: Update database model

- [ ] **Step 1: Modify Student DB model**

```python
# src/oneorg/db/models.py
# Add to Student class after grade_level:
    age_mode = Column(String, default="middle")  # young, middle, teen
```

- [ ] **Step 2: Create migration (if using Alembic)**

Run: `alembic revision -m "add age_mode to students"`

Edit migration:
```python
def upgrade():
    op.add_column('students', sa.Column('age_mode', sa.String(), nullable=True))
    op.execute("UPDATE students SET age_mode = CASE WHEN grade_level <= 8 THEN 'young' WHEN grade_level <= 12 THEN 'middle' ELSE 'teen' END")
    op.alter_column('students', 'age_mode', nullable=False)
```

- [ ] **Step 3: Commit**

```bash
git add src/oneorg/db/models.py
git commit -m "db: add age_mode column to students table"
```

---

## Chunk 2: Remove Badge Rarity

**Worker:** Agent 2 (independent, blocks badge updates)

**Goal:** Remove BadgeRarity enum and all rarity references

### Files
- Modify: `src/oneorg/models/gamification.py:1-49`
- Modify: `src/oneorg/gamification/badges.py:1-89`
- Modify: `tests/test_gamification/test_badges.py`

### Task 2.1: Remove BadgeRarity from models

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_gamification.py
def test_badge_criteria_has_no_rarity():
    from oneorg.models.gamification import BadgeCriteria, BadgeCategory
    
    badge = BadgeCriteria(
        badge_id="test_badge",
        name="Test Badge",
        description="A test",
        icon="🌟",
        category=BadgeCategory.MILESTONE,
        criteria_type="quest_count",
        criteria_threshold=5,
    )
    
    # Should NOT have rarity attribute
    assert not hasattr(badge, 'rarity')

def test_no_badge_rarity_enum():
    # BadgeRarity should not exist
    with pytest.raises(ImportError):
        from oneorg.models.gamification import BadgeRarity
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_gamification.py::test_badge_criteria_has_no_rarity -v`
Expected: FAIL - BadgeRarity still exists and BadgeCriteria still has rarity field

- [ ] **Step 3: Remove BadgeRarity and rarity field**

```python
# src/oneorg/models/gamification.py
# REMOVE these lines:
class BadgeRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

# In BadgeCriteria, REMOVE:
    rarity: BadgeRarity = BadgeRarity.COMMON
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models/test_gamification.py::test_badge_criteria_has_no_rarity -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models/test_gamification.py src/oneorg/models/gamification.py
git commit -m "refactor: remove BadgeRarity and variable reward mechanics

- Remove BadgeRarity enum (Common → Legendary tiers)
- Remove rarity field from BadgeCriteria
- Eliminate variable reward scheduling for ethical gamification"
```

### Task 2.2: Update BadgeManager

- [ ] **Step 1: Remove rarity from progress output**

```python
# src/oneorg/gamification/badges.py
# In get_progress method, REMOVE from dict:
# "rarity": criteria.rarity.value,

# Change to:
            progress.append({
                "badge_id": badge_id,
                "name": criteria.name,
                "icon": criteria.icon,
                "earned": student.has_badge(badge_id),
                "current": current,
                "target": criteria.criteria_threshold,
                "percent": min(100, int(current / criteria.criteria_threshold * 100)),
            })
```

- [ ] **Step 2: Update badge YAML files**

Remove rarity from all badge definitions:

```yaml
# data/badges/explorer.yaml
# REMOVE: rarity: common/rare/etc.
version: 1
badges:
  - badge_id: first_quest
    name: "First Quest"
    description: "Complete your first quest"
    icon: 🌟
    category: milestone
    criteria_type: quest_count
    criteria_threshold: 1
    xp_bonus: 0
    # REMOVE: rarity: common
```

- [ ] **Step 3: Commit**

```bash
git add src/oneorg/gamification/badges.py data/badges/
git commit -m "refactor: remove rarity from BadgeManager and badge definitions"
```

---

## Chunk 3: Replace Streaks with Calendar

**Worker:** Agent 3 (independent, other workers depend on this)

**Goal:** Remove longest_streak and streak_freeze, implement ActivityCalendar with positive framing

### Files
- Create: `src/oneorg/models/calendar.py`
- Modify: `src/oneorg/models/student.py` - Replace streak field
- Modify: `src/oneorg/models/gamification.py` - Remove StreakData.longest_streak
- Create: `src/oneorg/gamification/calendar.py`
- Modify: `src/oneorg/cli.py` - Update streak references

### Task 3.1: Create ActivityCalendar model

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_calendar.py
def test_calendar_tracks_activity_dates():
    from datetime import date
    from oneorg.models.calendar import ActivityCalendar
    
    calendar = ActivityCalendar()
    today = date.today()
    
    # Mark activity for today
    calendar.mark_activity(today)
    
    assert calendar.has_activity_on(today)
    assert calendar.activity_count == 1

def test_calendar_shows_recent_week():
    from datetime import date, timedelta
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_calendar.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'oneorg.models.calendar'"

- [ ] **Step 3: Write ActivityCalendar model**

```python
# src/oneorg/models/calendar.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models/test_calendar.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models/test_calendar.py src/oneorg/models/calendar.py
git commit -m "feat: add ActivityCalendar for positive-framed activity tracking

- Track activity dates without streak pressure
- Show visual week view of recent activity
- Provide month summaries with positive messaging
- Remove longest_streak to eliminate loss aversion"
```

### Task 3.2: Update StudentProgress to use ActivityCalendar

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_student.py (append)
def test_student_has_activity_calendar():
    from oneorg.models.calendar import ActivityCalendar
    
    student = StudentProgress(
        student_id="stu_001",
        name="Alice",
        grade_level=5,
    )
    
    assert isinstance(student.calendar, ActivityCalendar)

def test_student_no_longest_streak():
    student = StudentProgress(
        student_id="stu_001",
        name="Alice",
        grade_level=5,
    )
    
    # Should not have longest_streak attribute
    assert not hasattr(student, 'longest_streak')
    
    # Calendar should not have it either
    assert not hasattr(student.calendar, 'longest_streak')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_student.py::test_student_has_activity_calendar -v`
Expected: FAIL

- [ ] **Step 3: Replace streak with calendar in StudentProgress**

```python
# src/oneorg/models/student.py

# REMOVE StreakData import and field:
# from oneorg.models.gamification import StreakData, LeaderboardVisibility

# CHANGE to:
from oneorg.models.gamification import LeaderboardVisibility
from oneorg.models.calendar import ActivityCalendar

# In StudentProgress class, REPLACE:
# streak: StreakData = Field(default_factory=StreakData)

# WITH:
    calendar: ActivityCalendar = Field(default_factory=ActivityCalendar)
    
    # Legacy compatibility - computed property for current streak
    @computed_field
    @property
    def current_streak(self) -> int:
        """Current consecutive days (for backward compatibility)."""
        return self.calendar.get_consecutive_days()
    
    @computed_field  
    @property
    def last_activity_date(self) -> Optional[date]:
        """Last activity date for display."""
        from datetime import date as dt_date
        # Find most recent date
        if not self.calendar.activity_dates:
            return None
        return max(dt_date.fromisoformat(d) for d in self.calendar.activity_dates)

# REMOVE update_streak method, REPLACE with:
    def mark_activity(self, activity_date: Optional[date] = None) -> bool:
        """Mark activity on a date (defaults to today)."""
        if activity_date is None:
            activity_date = date.today()
        
        was_new = self.calendar.mark_activity(activity_date)
        if was_new:
            self.updated_at = datetime.now()
        return was_new
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models/test_student.py::test_student_has_activity_calendar -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models/test_student.py src/oneorg/models/student.py
git commit -m "refactor: replace StreakData with ActivityCalendar in StudentProgress

- Remove StreakData.longest_streak (loss aversion trigger)
- Add ActivityCalendar for positive-framed tracking
- Maintain backward compatibility with current_streak property
- Add mark_activity() method for activity tracking"
```

### Task 3.3: Update StreakData model

- [ ] **Step 1: Remove longest_streak from StreakData**

```python
# src/oneorg/models/gamification.py
# In StreakData class, REMOVE:
# longest_streak: int = 0

# Also REMOVE:
# streak_freeze_remaining: int = 3

# Keep only:
class StreakData(BaseModel):
    current_streak: int = 0
    last_activity_date: Optional[date] = None
```

- [ ] **Step 2: Create CalendarManager service**

```python
# src/oneorg/gamification/calendar.py
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
```

- [ ] **Step 3: Commit**

```bash
git add src/oneorg/models/gamification.py src/oneorg/gamification/calendar.py
git commit -m "refactor: remove longest_streak and streak_freeze from gamification

- Remove loss aversion triggers from StreakData
- Add CalendarManager for positive activity management"
```

---

## Chunk 4: Make Leaderboard Opt-In

**Worker:** Agent 4 (independent)

**Goal:** Change leaderboard default to opt-out (private), update CLI

### Files
- Modify: `src/oneorg/models/gamification.py:46-49`
- Modify: `src/oneorg/gamification/leaderboard.py`
- Modify: `src/oneorg/cli.py:183-208`

### Task 4.1: Update visibility default

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gamification/test_leaderboard.py
def test_leaderboard_is_opt_out_by_default():
    from oneorg.models.gamification import LeaderboardVisibility
    
    settings = LeaderboardVisibility()
    
    # Should be opt-out (private) by default
    assert settings.show_on_leaderboard == False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gamification/test_leaderboard.py::test_leaderboard_is_opt_out_by_default -v`
Expected: FAIL - current default is True

- [ ] **Step 3: Change default to False**

```python
# src/oneorg/models/gamification.py
# In LeaderboardVisibility class, CHANGE:
# show_on_leaderboard: bool = True

# TO:
show_on_leaderboard: bool = False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_gamification/test_leaderboard.py::test_leaderboard_is_opt_out_by_default -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_gamification/test_leaderboard.py src/oneorg/models/gamification.py
git commit -m "refactor: make leaderboard opt-in (default to private)

- Change show_on_leaderboard default from True to False
- Students must explicitly opt-in to appear on leaderboard
- Protects privacy and reduces social pressure"
```

### Task 4.2: Replace leaderboard CLI command

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
def test_progress_command_shows_personal_stats():
    """Test that 'oneorg progress' shows personal progress instead of leaderboard."""
    from click.testing import CliRunner
    from oneorg.cli import main
    
    runner = CliRunner()
    result = runner.invoke(main, ['progress', 'stu_test'])
    
    # Should show personal progress, not leaderboard
    assert 'Personal Progress' in result.output or 'Level' in result.output
    assert 'Leaderboard' not in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_progress_command_shows_personal_stats -v`
Expected: FAIL - command doesn't exist yet

- [ ] **Step 3: Replace leaderboard command with progress command**

```python
# src/oneorg/cli.py

# REMOVE leaderboard command (lines 183-208), REPLACE with:

@main.command()
@click.argument("student_id")
def progress(student_id):
    """Show personal progress and achievements (replaces leaderboard)."""
    tracker = StateTracker(DEFAULT_STATE_DIR)
    
    if not tracker.exists(student_id):
        console.print(f"[red]Error:[/red] Student {student_id} not found")
        return
    
    student = tracker.load(student_id)
    
    # Personal progress display
    console.print(f"\n[bold]{student.name}[/bold]'s Personal Progress")
    console.print("=" * 50)
    
    console.print(f"\n📊 [bold]Level {student.level}[/bold]")
    console.print(f"   XP: {student.xp} ({student.xp_to_next_level} to next level)")
    console.print(f"   Grade: {student.grade_level}")
    
    # Calendar summary
    if student.calendar:
        month_data = student.calendar.get_recent_month_summary()
        console.print(f"\n📅 {month_data['message']}")
    
    console.print(f"\n🎯 Quests Completed: {len(student.quests_completed)}")
    
    if student.badges:
        console.print(f"\n🏅 Badges Earned ({len(student.badges)}):")
        for badge in student.badges[-5:]:  # Show last 5
            console.print(f"   {badge.icon} {badge.name}")

# If you want to keep leaderboard as opt-in command:
@main.command()
@click.option("--limit", "-l", default=10)
@click.option("--include-me", "-m", is_flag=True, help="Include me even if opted out")
def leaderboard(limit, include_me):
    """Show leaderboard (opt-in only)."""
    tracker = StateTracker(DEFAULT_STATE_DIR)
    manager = LeaderboardManager(tracker)
    
    entries = manager.get_leaderboard(limit=limit, include_opted_out=include_me)
    
    if not entries:
        console.print("[yellow]No students have opted in to the leaderboard yet.[/yellow]")
        console.print("Use 'oneorg opt-in' to share your progress!")
        return
    
    # ... rest of leaderboard display
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_progress_command_shows_personal_stats -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/oneorg/cli.py
git commit -m "refactor: replace leaderboard command with personal progress

- New 'oneorg progress <student_id>' shows personal stats
- Leaderboard is now opt-in only
- Promotes intrinsic motivation over competition"
```

---

## Chunk 5: Implement Predictable XP System

**Worker:** Agent 5 (depends on AgeMode from Chunk 1)

**Goal:** Remove XP randomness, make rewards predictable and transparent

### Files
- Create: `src/oneorg/models/xp_system.py`
- Modify: `src/oneorg/services/quest_engine.py`
- Modify: `src/oneorg/gamification/badges.py`

### Task 5.1: Create predictable XP calculator

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_xp_system.py
def test_xp_is_predictable():
    """XP rewards should be deterministic, not random."""
    from oneorg.models.xp_system import XPConfig, XPCalculator
    
    config = XPConfig()
    calc = XPCalculator(config)
    
    # Same quest should always give same XP
    xp1 = calc.calculate_quest_xp(difficulty=2, accuracy=0.8, time_spent=300)
    xp2 = calc.calculate_quest_xp(difficulty=2, accuracy=0.8, time_spent=300)
    
    assert xp1 == xp2
    assert xp1 > 0

def test_effort_bonus_is_calculated_not_random():
    from oneorg.models.xp_system import XPCalculator
    
    calc = XPCalculator(XPConfig())
    
    # Effort bonus based on time/attempts, not luck
    bonus = calc.calculate_effort_bonus(
        time_spent=600,  # 10 minutes
        attempts=3,
        hints_used=1,
    )
    
    # Should be deterministic formula
    assert bonus == calc.calculate_effort_bonus(
        time_spent=600,
        attempts=3,
        hints_used=1,
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_xp_system.py -v`
Expected: FAIL - module doesn't exist

- [ ] **Step 3: Write XP system models**

```python
# src/oneorg/models/xp_system.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class XPConfig:
    """Configuration for XP calculations.
    
    All formulas are transparent and deterministic:
    - Students can see exactly how XP is calculated
    - No randomness, no gambling mechanics
    """
    # Base XP per difficulty level
    base_xp_per_difficulty: int = 50
    
    # Accuracy bonus (linear, not random)
    accuracy_multiplier_min: float = 0.5  # 50% accuracy
    accuracy_multiplier_max: float = 1.5  # 100% accuracy
    
    # Effort bonuses (recognizes persistence)
    time_bonus_per_minute: int = 2  # +2 XP per minute spent
    time_bonus_cap_minutes: int = 30  # Cap at 30 min
    attempt_bonus_per_retry: int = 5  # +5 XP per retry (learning from mistakes)
    attempt_bonus_cap: int = 25  # Cap at 5 retries
    
    # Streak bonus (gentle encouragement, not pressure)
    streak_bonus_per_day: int = 2  # +2 XP per consecutive day
    streak_bonus_cap_days: int = 5  # Cap at 5 days

@dataclass
class QuestAttempt:
    """Data from a quest attempt for XP calculation."""
    difficulty: int  # 1-5
    accuracy: float  # 0.0-1.0
    time_spent_seconds: int
    attempt_number: int = 1  # 1 = first try
    hints_used: int = 0
    current_streak_days: int = 0

class XPCalculator:
    """Deterministic XP calculator with transparent formulas."""
    
    def __init__(self, config: Optional[XPConfig] = None):
        self.config = config or XPConfig()
    
    def calculate_quest_xp(self, attempt: QuestAttempt) -> dict:
        """Calculate total XP with full breakdown.
        
        Returns breakdown so students can see exactly how XP is earned:
        {
            "total": 145,
            "breakdown": {
                "base": 100,
                "accuracy_bonus": 25,
                "effort_bonus": 15,
                "streak_bonus": 5,
            },
            "formula": "base (50×2) + accuracy (25) + effort (15) + streak (5)"
        }
        """
        base = self._calculate_base(attempt.difficulty)
        accuracy = self._calculate_accuracy_bonus(base, attempt.accuracy)
        effort = self._calculate_effort_bonus(attempt)
        streak = self._calculate_streak_bonus(attempt.current_streak_days)
        
        total = base + accuracy + effort + streak
        
        return {
            "total": total,
            "breakdown": {
                "base": base,
                "accuracy_bonus": accuracy,
                "effort_bonus": effort,
                "streak_bonus": streak,
            },
            "formula": self._format_formula(base, accuracy, effort, streak),
        }
    
    def _calculate_base(self, difficulty: int) -> int:
        return difficulty * self.config.base_xp_per_difficulty
    
    def _calculate_accuracy_bonus(self, base_xp: int, accuracy: float) -> int:
        """Linear accuracy bonus - better performance = more XP."""
        # Map accuracy 0.0-1.0 to multiplier 0.5-1.5
        multiplier = self.config.accuracy_multiplier_min + \
                     (accuracy * (self.config.accuracy_multiplier_max - 
                                 self.config.accuracy_multiplier_min))
        return int(base_xp * (multiplier - 1))  # Bonus only, not total
    
    def _calculate_effort_bonus(self, attempt: QuestAttempt) -> int:
        """Reward effort and persistence."""
        # Time bonus (up to cap)
        minutes = min(attempt.time_spent_seconds // 60, 
                     self.config.time_bonus_cap_minutes)
        time_bonus = minutes * self.config.time_bonus_per_minute
        
        # Retry bonus (learning from mistakes)
        retries = max(0, attempt.attempt_number - 1)
        retry_bonus = min(retries * self.config.attempt_bonus_per_retry,
                         self.config.attempt_bonus_cap)
        
        return time_bonus + retry_bonus
    
    def _calculate_streak_bonus(self, streak_days: int) -> int:
        """Gentle streak bonus (capped to avoid pressure)."""
        capped_days = min(streak_days, self.config.streak_bonus_cap_days)
        return capped_days * self.config.streak_bonus_per_day
    
    def _format_formula(self, base: int, accuracy: int, effort: int, streak: int) -> str:
        parts = [f"base ({base})"]
        if accuracy > 0:
            parts.append(f"accuracy (+{accuracy})")
        if effort > 0:
            parts.append(f"effort (+{effort})")
        if streak > 0:
            parts.append(f"streak (+{streak})")
        return " + ".join(parts)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models/test_xp_system.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models/test_xp_system.py src/oneorg/models/xp_system.py
git commit -m "feat: implement predictable XP system with transparent formulas

- Deterministic XP calculations (no randomness)
- Breakdown shown to students so they understand rewards
- Effort bonuses for persistence and time spent
- Gentle streak bonuses (capped to avoid pressure)"
```

### Task 5.2: Integrate XP calculator into quest engine

- [ ] **Step 1: Update quest engine to use XPCalculator**

```python
# src/oneorg/services/quest_engine.py

# Add imports:
from oneorg.models.xp_system import XPCalculator, XPConfig, QuestAttempt

# Modify complete_quest method to use predictable XP:
def complete_quest(
    self,
    student: Student,
    quest: Quest,
    score: float,
    time_spent_seconds: int = 300,
    attempt_number: int = 1,
) -> QuestCompletion:
    """Complete a quest and award predictable XP."""
    
    # Calculate XP deterministically
    calculator = XPCalculator(XPConfig())
    attempt = QuestAttempt(
        difficulty=quest.difficulty,
        accuracy=score,
        time_spent_seconds=time_spent_seconds,
        attempt_number=attempt_number,
        current_streak_days=student.current_streak,
    )
    
    xp_result = calculator.calculate_quest_xp(attempt)
    
    completion = QuestCompletion(
        student=student,
        quest=quest,
        score=score,
        xp_earned=xp_result["total"],
        xp_breakdown=xp_result["breakdown"],  # Store for display
        completed_at=datetime.utcnow(),
    )
    
    # Update student
    student.xp += xp_result["total"]
    student.current_streak += 1  # Or use calendar.mark_activity()
    
    return completion
```

- [ ] **Step 2: Update tests**

```python
# tests/test_services/test_quest_engine.py
def test_quest_completion_uses_predictable_xp():
    """Quest completion should use deterministic XP."""
    # Mock student and quest
    # Call complete_quest with same params twice
    # Verify XP is identical both times
```

- [ ] **Step 3: Commit**

```bash
git add src/oneorg/services/quest_engine.py tests/test_services/
git commit -m "feat: integrate predictable XP into quest completion

- Replace random XP with deterministic calculations
- Store XP breakdown for transparency
- Students see exactly how XP is earned"
```

---

## Chunk 6: Create Effort-Based Badge System

**Worker:** Agent 6 (depends on Chunk 2 - badge rarity removal)

**Goal:** Replace achievement-only badges with effort-based criteria

### Files
- Create: `src/oneorg/gamification/effort_badges.py`
- Modify: `src/oneorg/gamification/badges.py`
- Create: `data/badges/effort.yaml`

### Task 6.1: Define effort-based badge criteria

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gamification/test_effort_badges.py
def test_effort_badges_recognize_persistence():
    """Badges should reward effort, not just achievements."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress
    
    checker = EffortBadgeChecker()
    
    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )
    
    # Simulate multiple attempts (persistence)
    # Should earn "Persistent" badge
    badge = checker.check_effort_badges(student)
    
    assert any(b.badge_id == "persistent" for b in badge)

def test_time_spent_badges():
    """Badges for time spent learning (not speed)."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress
    
    checker = EffortBadgeChecker()
    
    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )
    
    # Simulate significant time spent
    # Should earn time-based badge
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gamification/test_effort_badges.py -v`
Expected: FAIL - module doesn't exist

- [ ] **Step 3: Write effort badge checker**

```python
# src/oneorg/gamification/effort_badges.py
from datetime import datetime
from oneorg.models.student import StudentProgress, Badge
from oneorg.models.gamification import BadgeCategory

class EffortBadgeCriteria:
    """Criteria for effort-based badges (not achievement-only)."""
    
    PERSISTENT = "persistent"
    THOROUGH = "thorough"
    CURIOUS = "curious"
    REFLECTIVE = "reflective"
    COLLABORATIVE = "collaborative"

class EffortBadgeChecker:
    """Checks for effort-based badges that recognize the learning process."""
    
    EFFORT_BADGES = {
        "persistent": {
            "name": "Persistence Pays",
            "description": "Tried a quest multiple times before succeeding",
            "icon": "🌱",
            "category": BadgeCategory.MASTERY,
            "check": lambda s: s.total_attempts >= 10,  # Total retries across quests
        },
        "thorough": {
            "name": "Thorough Explorer",
            "description": "Spent significant time on quests",
            "icon": "🔍",
            "category": BadgeCategory.MASTERY,
            "check": lambda s: s.total_time_spent >= 3600,  # 1 hour total
        },
        "curious": {
            "name": "Curious Mind",
            "description": "Tried quests from different categories",
            "icon": "🤔",
            "category": BadgeCategory.EXPLORATION,
            "check": lambda s: len(s.categories_attempted) >= 3,
        },
        "reflective": {
            "name": "Reflective Learner",
            "description": "Revisited completed quests to improve",
            "icon": "💭",
            "category": BadgeCategory.MASTERY,
            "check": lambda s: s.revisits >= 3,
        },
        "collaborative": {
            "name": "Team Player",
            "description": "Helped others or participated in group quests",
            "icon": "🤝",
            "category": BadgeCategory.SOCIAL,
            "check": lambda s: s.collaborations >= 5,
        },
    }
    
    def check_effort_badges(self, student: StudentProgress) -> list[Badge]:
        """Check and return newly earned effort badges."""
        earned = []
        
        for badge_id, config in self.EFFORT_BADGES.items():
            if student.has_badge(badge_id):
                continue
            
            if config["check"](student):
                badge = Badge(
                    badge_id=badge_id,
                    name=config["name"],
                    description=config["description"],
                    icon=config["icon"],
                )
                earned.append(badge)
        
        return earned
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_gamification/test_effort_badges.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_gamification/test_effort_badges.py src/oneorg/gamification/effort_badges.py
git commit -m "feat: add effort-based badge system

- Recognize persistence (multiple attempts)
- Reward thoroughness (time spent)
- Encourage curiosity (category exploration)
- Value reflection (revisiting content)
- Promote collaboration (helping others)"
```

### Task 6.2: Create effort badge YAML definitions

- [ ] **Step 1: Create effort badges YAML**

```yaml
# data/badges/effort.yaml
version: 1
badges:
  - badge_id: first_try
    name: "First Step"
    description: "Completed your first quest"
    icon: 👣
    category: milestone
    criteria_type: quest_count
    criteria_threshold: 1
    xp_bonus: 0
    
  - badge_id: persistent_learner
    name: "Persistent Learner"
    description: "Completed a quest after multiple attempts"
    icon: 🎯
    category: mastery
    criteria_type: quest_with_retries
    criteria_threshold: 1
    xp_bonus: 0
    
  - badge_id: deep_diver
    name: "Deep Diver"
    description: "Spent 15+ minutes on a single quest"
    icon: 🌊
    category: mastery
    criteria_type: time_on_quest
    criteria_threshold: 900  # 15 minutes in seconds
    xp_bonus: 0
    
  - badge_id: explorer
    name: "Quest Explorer"
    description: "Tried quests from 3 different categories"
    icon: 🗺️
    category: exploration
    criteria_type: categories_attempted
    criteria_threshold: 3
    xp_bonus: 0
    
  - badge_id: reflective
    name: "Reflective Learner"
    description: "Revisited a quest to improve your score"
    icon: 🪞
    category: mastery
    criteria_type: quest_revisits
    criteria_threshold: 1
    xp_bonus: 0
    
  - badge_id: tenacious
    name: "Tenacious Spirit"
    description: "Kept trying even when it was challenging"
    icon: 🧗
    category: mastery
    criteria_type: low_accuracy_completion
    criteria_threshold: 1  # Completed with < 70% accuracy but kept trying
    xp_bonus: 0
    
  - badge_id: consistent
    name: "Consistent Learner"
    description: "Active on 5 different days"
    icon: 📅
    category: milestone
    criteria_type: active_days
    criteria_threshold: 5
    xp_bonus: 0
```

- [ ] **Step 2: Update BadgeManager to load effort badges**

```python
# src/oneorg/gamification/badges.py

# Add new criteria types to _check_criteria:
def _check_criteria(self, student: StudentProgress, criteria: BadgeCriteria) -> bool:
    checkers = {
        "quest_count": lambda s, t: len(s.quests_completed) >= t,
        "level": lambda s, t: s.level >= t,
        "xp_total": lambda s, t: s.xp >= t,
        # New effort-based criteria
        "quest_with_retries": lambda s, t: s.completions_with_retries >= t,
        "time_on_quest": lambda s, t: s.max_time_on_quest >= t,
        "categories_attempted": lambda s, t: len(s.categories_attempted) >= t,
        "quest_revisits": lambda s, t: s.quest_revisits >= t,
        "low_accuracy_completion": lambda s, t: s.persistent_completions >= t,
        "active_days": lambda s, t: s.calendar.activity_count >= t,
    }
    
    # ... rest of method
```

- [ ] **Step 3: Commit**

```bash
git add data/badges/effort.yaml src/oneorg/gamification/badges.py
git commit -m "feat: add effort badge definitions and criteria

- 7 effort-based badges rewarding process over outcomes
- New criteria types: retries, time, exploration, revisits
- Active days criteria using ActivityCalendar"
```

---

## Chunk 7: Update Dashboard Templates

**Worker:** Agent 7 (depends on Chunks 1, 3, 4, 5, 6)

**Goal:** Update UI to show new gamification system (age-appropriate, positive framing)

### Files
- Modify: `src/oneorg/api/templates/dashboard.html`
- Modify: `src/oneorg/api/templates/base.html`
- Modify: `src/oneorg/api/routes/ui.py`

### Task 7.1: Create age-appropriate dashboard components

- [ ] **Step 1: Update dashboard to show calendar instead of streak**

```html
<!-- src/oneorg/api/templates/dashboard.html -->
<!-- REPLACE streak display section -->

<!-- OLD (streak with pressure): -->
<!-- <div class="streak-display">
  <span class="streak-count">{{ student.streak.current_streak }}</span>
  <span>day streak!</span>
  <span class="longest">(Longest: {{ student.streak.longest_streak }})</span>
</div> -->

<!-- NEW (calendar with positive framing): -->
<div class="calendar-display">
  <h3>📅 {{ student.calendar.get_recent_month_summary().message }}</h3>
  <div class="week-view">
    {% for date_str, active in student.calendar.get_recent_week().items() %}
      <div class="day {% if active %}active{% endif %}">
        {{ date_str[-2:] }}
      </div>
    {% endfor %}
  </div>
</div>
```

- [ ] **Step 2: Add age-specific display modes**

```html
<!-- In dashboard.html, add age-conditional display -->
{% if student.age_mode.value == "5-8" %}
  <!-- Young: Stars, simple progress -->
  <div class="young-mode">
    <h2>⭐ {{ student.xp // 10 }} Stars!</h2>
    <p>You've completed {{ student.quests_completed|length }} quests!</p>
  </div>
{% elif student.age_mode.value == "9-12" %}
  <!-- Middle: Points, more detail -->
  <div class="middle-mode">
    <h2>🎯 {{ student.xp }} Points</h2>
    <p>Level {{ student.level }} • {{ student.xp_to_next_level }} points to next level</p>
  </div>
{% else %}
  <!-- Teen: XP, full stats -->
  <div class="teen-mode">
    <h2>🎓 {{ student.xp }} XP</h2>
    <p>Level {{ student.level }} ({{ student.xp_to_next_level }} XP to level {{ student.level + 1 }})</p>
  </div>
{% endif %}
```

- [ ] **Step 3: Update badges display (no rarity)

```html
<!-- Replace badge grid with simple earned list -->
<div class="badges-section">
  <h3>🏅 Your Badges</h3>
  <div class="badge-list">
    {% for badge in student.badges %}
      <div class="badge earned">
        <span class="badge-icon">{{ badge.icon }}</span>
        <span class="badge-name">{{ badge.name }}</span>
        <span class="badge-desc">{{ badge.description }}</span>
      </div>
    {% endfor %}
  </div>
</div>
```

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/api/templates/dashboard.html
git commit -m "feat: update dashboard with age-appropriate, positive-framed display

- Replace streak pressure with ActivityCalendar visualization
- Add age-specific display modes (stars/points/XP)
- Remove rarity indicators from badges
- Positive messaging throughout"
```

### Task 7.2: Update UI routes

- [ ] **Step 1: Update student data in UI routes**

```python
# src/oneorg/api/routes/ui.py

# In get_student_dashboard or similar, add:
@app.get("/dashboard")
async def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    student = await get_student_for_user(current_user.id)
    
    # Prepare age-appropriate data
    dashboard_data = {
        "student": student,
        "age_mode": student.age_mode,
        "calendar_summary": student.calendar.get_recent_month_summary(),
        "week_view": student.calendar.get_recent_week(),
        "badges": student.badges,
        # Don't include leaderboard data unless opted in
        "show_leaderboard_prompt": not student.leaderboard_settings.show_on_leaderboard,
    }
    
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, **dashboard_data}
    )
```

- [ ] **Step 2: Add opt-in endpoint**

```python
@app.post("/leaderboard/opt-in")
async def opt_in_leaderboard(current_user: User = Depends(get_current_user)):
    """Allow students to opt-in to leaderboard."""
    student = await get_student_for_user(current_user.id)
    student.leaderboard_settings.show_on_leaderboard = True
    await save_student(student)
    
    return {"message": "You're now visible on the leaderboard!"}
```

- [ ] **Step 3: Commit**

```bash
git add src/oneorg/api/routes/ui.py
git commit -m "feat: update UI routes for new gamification system

- Add age-appropriate dashboard data preparation
- Add leaderboard opt-in endpoint
- Remove public leaderboard by default"
```

---

## Integration Checklist

Before merging all chunks, verify these cross-cutting concerns:

- [ ] **Database migrations** - All schema changes applied
- [ ] **API compatibility** - Frontend receives expected data structures
- [ ] **Tests pass** - All new and existing tests pass
- [ ] **CLI works** - `oneorg progress` command functional
- [ ] **Templates render** - Dashboard displays without errors

### Final Integration Test

```bash
# Run full test suite
pytest tests/ -v

# Test CLI commands
oneorg student test_student --name "Test" --grade 5
oneorg complete test_student quest_001 "Test Master"
oneorg progress test_student

# Verify database
python -c "from oneorg.db.models import Student; print('Schema OK')"
```

---

## Summary

This plan refactors OneEmployeeOrg's gamification to be healthy and age-appropriate:

1. **AgeMode** - 3 profiles (5-8, 9-12, 13-18) with appropriate displays
2. **No rarity tiers** - Remove variable reward mechanics
3. **ActivityCalendar** - Replace streaks with positive-framed tracking
4. **Opt-in leaderboard** - Privacy-first, reduce social pressure
5. **Predictable XP** - Transparent formulas, no randomness
6. **Effort badges** - Reward process and persistence over outcomes
7. **Updated UI** - Age-appropriate dashboards with positive messaging

**Dependencies:**
- Chunk 1 (AgeMode) blocks Chunks 5, 7
- Chunk 2 (rarity removal) blocks Chunk 6
- Chunk 3 (calendar) blocks Chunks 5, 7
- Chunk 7 requires Chunks 1, 3, 4, 5, 6

**Workers can run in parallel:**
- Agents 1, 2, 3, 4 start immediately
- Agent 5 waits for Agent 1
- Agent 6 waits for Agent 2
- Agent 7 waits for Agents 1, 3, 4, 5, 6

Plan saved to `docs/superpowers/plans/2026-03-15-gamification-refactor.md`

Ready to execute with subagents?
