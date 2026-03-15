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
