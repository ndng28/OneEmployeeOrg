from pathlib import Path
from datetime import datetime
from oneorg.state.tracker import StateTracker
from oneorg.models.leaderboard import LeaderboardEntry, LeaderboardScope

class LeaderboardManager:
    def __init__(self, tracker: StateTracker):
        self.tracker = tracker
    
    def get_leaderboard(
        self,
        scope: LeaderboardScope = LeaderboardScope.GLOBAL,
        limit: int = 100,
        class_code: str | None = None,
    ) -> list[LeaderboardEntry]:
        students = []
        
        for student_id in self.tracker.list_all():
            student = self.tracker.load(student_id)
            if student and student.leaderboard_settings.show_on_leaderboard:
                students.append(student)
        
        students.sort(key=lambda s: s.xp, reverse=True)
        
        entries = []
        prev_xp = None
        prev_rank = 0
        
        for i, student in enumerate(students[:limit]):
            rank = prev_rank if student.xp == prev_xp else i + 1
            entries.append(LeaderboardEntry(
                rank=rank,
                student_id=student.student_id,
                display_name=student.get_display_name(),
                xp=student.xp,
                level=student.level,
                quests_completed=len(student.quests_completed),
                current_streak=student.streak.current_streak,
                team_id=student.team_id,
            ))
            prev_xp = student.xp
            prev_rank = rank
        
        return entries
    
    def get_student_rank(self, student_id: str) -> int | None:
        leaderboard = self.get_leaderboard(limit=10000)
        for entry in leaderboard:
            if entry.student_id == student_id:
                return entry.rank
        return None
