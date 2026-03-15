"""Predictable XP system with transparent formulas.

This module provides deterministic XP calculations with no randomness.
Students can see exactly how XP is earned, and effort is rewarded.
"""
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
            "formula": "base (100) + accuracy (+25) + effort (+15) + streak (+5)"
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
        """Calculate base XP from difficulty."""
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
        """Format the formula string showing how XP was calculated."""
        parts = [f"base ({base})"]
        if accuracy > 0:
            parts.append(f"accuracy (+{accuracy})")
        elif accuracy < 0:
            parts.append(f"accuracy ({accuracy})")
        if effort > 0:
            parts.append(f"effort (+{effort})")
        if streak > 0:
            parts.append(f"streak (+{streak})")
        return " + ".join(parts)
