import pytest
from oneorg.gates.thresholds import DecisionThreshold, AutonomyLevel, ThresholdConfig

def test_autonomy_level_from_confidence():
    assert AutonomyLevel.from_confidence(0.90) == AutonomyLevel.FULLY_AUTONOMOUS
    assert AutonomyLevel.from_confidence(0.75) == AutonomyLevel.AUTONOMOUS_NOTIFY
    assert AutonomyLevel.from_confidence(0.60) == AutonomyLevel.ESCALATE_APPROVAL
    assert AutonomyLevel.from_confidence(0.40) == AutonomyLevel.ESCALATE_URGENT

def test_threshold_config_loads_defaults():
    config = ThresholdConfig.load()
    
    assert "fully_autonomous" in config.levels
    assert config.levels["fully_autonomous"].min_confidence == 0.85

def test_threshold_config_custom():
    config = ThresholdConfig(
        levels={
            "high": DecisionThreshold(min_confidence=0.90, action="auto"),
        }
    )
    
    assert config.levels["high"].min_confidence == 0.90
