import pytest
from oneorg.gates.evaluator import DecisionEvaluator, Decision, EvaluationResult
from oneorg.gates.thresholds import ThresholdConfig

def test_evaluator_high_confidence_decision():
    config = ThresholdConfig.load()
    evaluator = DecisionEvaluator(config)
    
    decision = Decision(
        decision_id="dec_001",
        description="Start frontend basics quest for student Alex",
        confidence=0.92,
        domain="operations",
        requester="operations-dept-head",
    )
    
    result = evaluator.evaluate(decision)
    
    assert result.autonomy_level.value == "fully_autonomous"
    assert result.can_execute is True
    assert result.notification_required is False

def test_evaluator_medium_confidence_decision():
    config = ThresholdConfig.load()
    evaluator = DecisionEvaluator(config)
    
    decision = Decision(
        decision_id="dec_002",
        description="Award premium quest without sufficient XP",
        confidence=0.65,
        domain="finance",
        requester="finance-dept-head",
    )
    
    result = evaluator.evaluate(decision)
    
    assert result.autonomy_level.value == "escalate_approval"
    assert result.can_execute is False
    assert result.notification_required is True

def test_evaluator_with_risk_factors():
    config = ThresholdConfig.load()
    evaluator = DecisionEvaluator(config)
    
    decision = Decision(
        decision_id="dec_003",
        description="Unlock all premium content for student",
        confidence=0.80,
        domain="finance",
        requester="finance-dept-head",
        risk_factors=["financial_impact", "policy_change"],
    )
    
    result = evaluator.evaluate(decision, adjust_for_risk=True)
    
    assert result.effective_confidence < decision.confidence
