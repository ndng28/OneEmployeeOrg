from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class BadgeRarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class BadgeCategory(str, Enum):
    MILESTONE = "milestone"
    STREAK = "streak"
    MASTERY = "mastery"
    SOCIAL = "social"
    EXPLORATION = "exploration"

class StreakData(BaseModel):
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    streak_freeze_remaining: int = 3

class BadgeCriteria(BaseModel):
    badge_id: str
    name: str
    description: str
    icon: str
    category: BadgeCategory
    criteria_type: str
    criteria_threshold: int
    xp_bonus: int = 0
    rarity: BadgeRarity = BadgeRarity.COMMON
    is_secret: bool = False

class Team(BaseModel):
    team_id: str
    name: str
    description: str = ""
    members: list[str] = Field(default_factory=list)
    team_xp: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

class LeaderboardVisibility(BaseModel):
    show_on_leaderboard: bool = True
    display_name: Optional[str] = None
    show_achievements: bool = True
