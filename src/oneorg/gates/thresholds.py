from enum import Enum
from typing import Optional
from pathlib import Path
import yaml
from pydantic import BaseModel, Field

class AutonomyLevel(str, Enum):
    FULLY_AUTONOMOUS = "fully_autonomous"
    AUTONOMOUS_NOTIFY = "autonomous_notify"
    ESCALATE_APPROVAL = "escalate_approval"
    ESCALATE_URGENT = "escalate_urgent"
    
    @classmethod
    def from_confidence(cls, confidence: float) -> "AutonomyLevel":
        if confidence >= 0.85:
            return cls.FULLY_AUTONOMOUS
        if confidence >= 0.70:
            return cls.AUTONOMOUS_NOTIFY
        if confidence >= 0.55:
            return cls.ESCALATE_APPROVAL
        return cls.ESCALATE_URGENT

class DecisionThreshold(BaseModel):
    min_confidence: float = Field(ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    action: str
    notify: bool = False
    override_window_minutes: Optional[int] = None
    escalate_to: Optional[str] = None

DEFAULT_THRESHOLDS = {
    "fully_autonomous": DecisionThreshold(
        min_confidence=0.85,
        action="execute_autonomous",
        notify=False,
    ),
    "autonomous_notify": DecisionThreshold(
        min_confidence=0.70,
        max_confidence=0.85,
        action="execute_notify",
        notify=True,
        override_window_minutes=30,
    ),
    "escalate_approval": DecisionThreshold(
        min_confidence=0.55,
        max_confidence=0.70,
        action="pause_for_approval",
        notify=True,
        escalate_to="headmaster",
    ),
    "escalate_urgent": DecisionThreshold(
        min_confidence=0.0,
        max_confidence=0.55,
        action="pause_urgent_escalation",
        notify=True,
        escalate_to="ceo",
    ),
}

class ThresholdConfig(BaseModel):
    levels: dict[str, DecisionThreshold] = DEFAULT_THRESHOLDS
    config_path: Optional[Path] = None
    
    @classmethod
    def load(cls, path: Optional[Path] = None) -> "ThresholdConfig":
        if path and path.exists():
            with open(path) as f:
                data = yaml.safe_load(f)
                return cls(levels=data.get("levels", DEFAULT_THRESHOLDS), config_path=path)
        return cls()
    
    def get_level(self, confidence: float) -> DecisionThreshold:
        level_name = AutonomyLevel.from_confidence(confidence).value
        return self.levels.get(level_name, self.levels["escalate_approval"])
