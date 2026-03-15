from datetime import date, datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field, computed_field

from oneorg.models.gamification import StreakData, LeaderboardVisibility

XP_PER_LEVEL = 500

class Badge(BaseModel):
    badge_id: str
    name: str
    description: str
    icon: str
    earned_at: Optional[datetime] = None

class QuestCompletion(BaseModel):
    quest_id: str
    quest_master: str
    xp_earned: int
    completed_at: datetime
    score: float = Field(ge=0.0, le=1.0)
    feedback: Optional[str] = None

class StudentProgress(BaseModel):
    student_id: str
    name: str
    grade_level: int = Field(ge=1, le=16)
    xp: int = Field(default=0, ge=0)
    quests_completed: list[QuestCompletion] = Field(default_factory=list)
    badges: list[Badge] = Field(default_factory=list)
    current_quest: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Gamification fields
    streak: StreakData = Field(default_factory=StreakData)
    team_id: Optional[str] = None
    leaderboard_settings: LeaderboardVisibility = Field(default_factory=LeaderboardVisibility)
    daily_xp: int = 0
    weekly_xp: int = 0
    title: Optional[str] = None
    
    @computed_field
    @property
    def level(self) -> int:
        return (self.xp // XP_PER_LEVEL) + 1
    
    @computed_field
    @property
    def xp_to_next_level(self) -> int:
        return XP_PER_LEVEL - (self.xp % XP_PER_LEVEL)
    
    def add_quest_completion(self, completion: QuestCompletion) -> None:
        self.quests_completed.append(completion)
        self.add_xp(completion.xp_earned)
        self.updated_at = datetime.now()
    
    def add_xp(self, amount: int) -> int:
        old_level = self.level
        self.xp += amount
        self.updated_at = datetime.now()
        return self.level - old_level
    
    def award_badge(self, badge: Badge) -> bool:
        if self.has_badge(badge.badge_id):
            return False
        badge.earned_at = datetime.now()
        self.badges.append(badge)
        self.updated_at = datetime.now()
        return True
    
    def has_badge(self, badge_id: str) -> bool:
        return any(b.badge_id == badge_id for b in self.badges)
    
    def start_quest(self, quest_id: str) -> None:
        self.current_quest = quest_id
        self.updated_at = datetime.now()
    
    def update_streak(self) -> bool:
        """Update streak on activity. Returns True if streak continued."""
        today = date.today()
        
        if self.streak.last_activity_date == today:
            return False
        
        yesterday = today - timedelta(days=1)
        if self.streak.last_activity_date == yesterday:
            self.streak.current_streak += 1
        elif self.streak.last_activity_date:
            self.streak.current_streak = 1
        
        self.streak.last_activity_date = today
        self.streak.longest_streak = max(self.streak.longest_streak, self.streak.current_streak)
        self.updated_at = datetime.now()
        return True
    
    def get_display_name(self) -> str:
        return self.leaderboard_settings.display_name or self.name
