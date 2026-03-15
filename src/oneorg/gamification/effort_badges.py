"""Effort-based badge system that rewards the learning process."""
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
                badge.earned_at = datetime.now()
                earned.append(badge)

        return earned
