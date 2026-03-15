from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class LeaderboardScope(str, Enum):
    GLOBAL = "global"
    CLASS = "class"
    TEAM = "team"
    WEEKLY = "weekly"

class LeaderboardEntry(BaseModel):
    rank: int
    student_id: str
    display_name: str
    xp: int
    level: int
    quests_completed: int
    current_streak: int
    trend: int = 0
    team_id: str | None = None
