from pydantic import BaseModel, Field
from typing import Optional, List

class ClaimRiskInput(BaseModel):
    claim_id: Optional[str] = Field("CLM-2026-900", example="CLM-2026-900")
    policy_type: str = Field(..., example="Auto")
    holder_age: int = Field(..., example=34)
    tenure_months: int = Field(..., example=24)
    coverage_amount: float = Field(..., example=500000.0)
    claim_amount: float = Field(..., example=65000.0)
    deductible: float = Field(5000.0, example=5000.0)
    prior_claims: int = Field(0, example=0)
    incident_severity: str = Field("Moderate", example="Moderate")
    police_report_filed: str = Field("Yes", example="Yes")
    witness_present: str = Field("Yes", example="Yes")

class ClaimRiskResponse(BaseModel):
    claim_id: str
    policy_type: str
    risk_score: float
    approval_probability: float
    risk_tier: str
    estimated_payout: float
    utilization_ratio_pct: float
    anomaly_flags: List[str]
    recommended_action: str
    ai_explanation: str
    engine: str
