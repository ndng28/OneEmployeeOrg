import yaml
from pathlib import Path
from pydantic import BaseModel
from oneorg.models.gamification import BadgeCriteria, BadgeCategory, BadgeRarity
from oneorg.models.student import StudentProgress, Badge

class BadgeDefinition(BaseModel):
    version: int
    badges: list[BadgeCriteria]

class BadgeManager:
    def __init__(self, badges_dir: Path = Path("data/badges")):
        self.badges_dir = badges_dir
        self._definitions: dict[str, BadgeCriteria] = {}
        self._load_definitions()
    
    def _load_definitions(self):
        for yaml_file in self.badges_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
                definition = BadgeDefinition(**data)
                for badge in definition.badges:
                    self._definitions[badge.badge_id] = badge
    
    def get_definition(self, badge_id: str) -> BadgeCriteria | None:
        return self._definitions.get(badge_id)
    
    def check_achievements(self, student: StudentProgress) -> list[Badge]:
        """Check all badges and return newly earned ones."""
        earned = []
        
        for badge_id, criteria in self._definitions.items():
            if student.has_badge(badge_id):
                continue
            
            if self._check_criteria(student, criteria):
                badge = Badge(
                    badge_id=badge_id,
                    name=criteria.name,
                    description=criteria.description,
                    icon=criteria.icon,
                )
                earned.append(badge)
        
        return earned
    
    def _check_criteria(self, student: StudentProgress, criteria: BadgeCriteria) -> bool:
        checkers = {
            "quest_count": lambda s, t: len(s.quests_completed) >= t,
            "level": lambda s, t: s.level >= t,
            "streak_days": lambda s, t: s.streak.current_streak >= t,
            "xp_total": lambda s, t: s.xp >= t,
        }
        
        checker = checkers.get(criteria.criteria_type)
        if checker:
            return checker(student, criteria.criteria_threshold)
        return False
    
    def get_progress(self, student: StudentProgress) -> list[dict]:
        """Get progress toward each badge."""
        progress = []
        
        for badge_id, criteria in self._definitions.items():
            if criteria.is_secret and not student.has_badge(badge_id):
                continue
            
            current = self._get_current_value(student, criteria.criteria_type)
            progress.append({
                "badge_id": badge_id,
                "name": criteria.name,
                "icon": criteria.icon,
                "rarity": criteria.rarity.value,
                "earned": student.has_badge(badge_id),
                "current": current,
                "target": criteria.criteria_threshold,
                "percent": min(100, int(current / criteria.criteria_threshold * 100)),
            })
        
        return sorted(progress, key=lambda x: (not x["earned"], -x["percent"]))
    
    def _get_current_value(self, student: StudentProgress, criteria_type: str) -> int:
        values = {
            "quest_count": len(student.quests_completed),
            "level": student.level,
            "streak_days": student.streak.current_streak,
            "xp_total": student.xp,
        }
        return values.get(criteria_type, 0)
