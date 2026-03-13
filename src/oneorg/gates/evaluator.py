from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from oneorg.gates.thresholds import ThresholdConfig, AutonomyLevel, DecisionThreshold

class Decision(BaseModel):
    decision_id: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    domain: str
    requester: str
    risk_factors: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

class EvaluationResult(BaseModel):
    decision_id: str
    autonomy_level: AutonomyLevel
    threshold: DecisionThreshold
    can_execute: bool
    notification_required: bool
    effective_confidence: float
    risk_adjustment: float = 0.0
    escalate_to: Optional[str] = None
    override_deadline: Optional[datetime] = None
    evaluated_at: datetime = Field(default_factory=datetime.now)

RISK_PENALTY = {
    "financial_impact": 0.10,
    "policy_change": 0.15,
    "external_communication": 0.20,
    "student_data": 0.25,
    "legal_compliance": 0.30,
}

class DecisionEvaluator:
    def __init__(self, config: ThresholdConfig):
        self.config = config
    
    def evaluate(
        self,
        decision: Decision,
        adjust_for_risk: bool = True,
    ) -> EvaluationResult:
        confidence = decision.confidence
        risk_adjustment = 0.0
        
        if adjust_for_risk and decision.risk_factors:
            for risk in decision.risk_factors:
                risk_adjustment += RISK_PENALTY.get(risk, 0.05)
            confidence = max(0.0, confidence - risk_adjustment)
        
        level = AutonomyLevel.from_confidence(confidence)
        threshold = self.config.get_level(confidence)
        
        can_execute = level in (
            AutonomyLevel.FULLY_AUTONOMOUS,
            AutonomyLevel.AUTONOMOUS_NOTIFY,
        )
        
        override_deadline = None
        if threshold.override_window_minutes:
            from datetime import timedelta
            override_deadline = datetime.now() + timedelta(minutes=threshold.override_window_minutes)
        
        return EvaluationResult(
            decision_id=decision.decision_id,
            autonomy_level=level,
            threshold=threshold,
            can_execute=can_execute,
            notification_required=threshold.notify,
            effective_confidence=confidence,
            risk_adjustment=risk_adjustment,
            escalate_to=threshold.escalate_to,
            override_deadline=override_deadline,
        )
