import os
from typing import Dict, Any, List

def evaluate_claim_risk(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actuarial and heuristic ML risk scoring engine for insurance claims.
    Calculates a 0-100 risk score, approval probability, fraud anomaly flags,
    estimated payout, and structured underwriting explanation.
    """
    claim_id = str(data.get("claim_id", "CLM-2026-001"))
    policy_type = str(data.get("policy_type", "Auto"))
    holder_age = int(data.get("holder_age", 35))
    tenure_months = int(data.get("tenure_months", 24))
    coverage_amount = max(1.0, float(data.get("coverage_amount", 500000.0)))
    claim_amount = max(0.0, float(data.get("claim_amount", 50000.0)))
    deductible = max(0.0, float(data.get("deductible", 5000.0)))
    prior_claims = int(data.get("prior_claims", 0))
    incident_severity = str(data.get("incident_severity", "Minor"))
    police_report = str(data.get("police_report_filed", "Yes"))
    witness_present = str(data.get("witness_present", "Yes"))

    score = 10.0  # Baseline risk
    flags: List[str] = []

    # 1. Claim-to-Coverage Ratio
    utilization_ratio = claim_amount / coverage_amount
    if utilization_ratio > 1.0:
        score += 35.0
        flags.append(f"Claim amount exceeds total policy coverage ({utilization_ratio*100:.1f}% of limit)")
    elif utilization_ratio >= 0.75:
        score += 25.0
        flags.append(f"High coverage exhaustion ({utilization_ratio*100:.1f}% of policy limit claimed)")
    elif utilization_ratio >= 0.40:
        score += 12.0

    # 2. Policy Tenure Factor (Early claim indicator)
    if tenure_months <= 6:
        score += 22.0
        flags.append(f"Early-tenure claim filed within {tenure_months} months of policy inception")
    elif tenure_months <= 12:
        score += 10.0
    elif tenure_months >= 36:
        score -= 6.0  # Loyalty discount on risk

    # 3. Prior Claims Frequency
    if prior_claims >= 3:
        score += 24.0
        flags.append(f"High historical claim frequency ({prior_claims} prior claims on record)")
    elif prior_claims == 2:
        score += 14.0
        flags.append("Multiple prior claims (2 previous claims logged)")
    elif prior_claims == 1:
        score += 5.0

    # 4. Incident Severity & Evidentiary Documentation
    severity_weights = {
        "Minor": 2.0,
        "Moderate": 10.0,
        "Severe": 18.0,
        "Total Loss": 25.0
    }
    score += severity_weights.get(incident_severity, 10.0)

    if incident_severity in ["Severe", "Total Loss"] and police_report == "No":
        score += 18.0
        flags.append(f"Missing official police/authority report for {incident_severity} incident")

    if incident_severity in ["Severe", "Total Loss"] and witness_present == "No":
        score += 8.0
        flags.append("No corroborating witness statement for high-severity claim")

    # 5. Age & Actuarial Bracket
    if policy_type == "Auto" and holder_age < 25:
        score += 8.0
    elif holder_age > 70 and policy_type == "Health":
        score += 6.0

    # Bound risk score between 2.0 and 99.0
    risk_score = round(max(2.0, min(99.0, score)), 1)
    approval_prob = round(max(1.0, min(98.0, 100.0 - risk_score)), 1)

    # Determine Risk Tier & Underwriting Action
    if risk_score < 30.0:
        risk_tier = "Low Risk (Fast-Track Approval)"
        recommended_action = "Auto-approve claim and initiate direct settlement transfer."
    elif risk_score < 55.0:
        risk_tier = "Moderate Risk (Standard Adjuster Review)"
        recommended_action = "Verify itemized invoices and standard surveyor documentation before payout."
    elif risk_score < 75.0:
        risk_tier = "High Risk (Senior Underwriter Audit)"
        recommended_action = "Hold automated payout; assign field adjuster for physical/medical verification."
    else:
        risk_tier = "Critical Risk (SIU Fraud Investigation)"
        recommended_action = "Escalate to Special Investigations Unit (SIU) for forensic audit and claimant interview."

    # Calculate Estimated Payout
    capped_claim = min(claim_amount, coverage_amount)
    estimated_payout = round(max(0.0, capped_claim - deductible), 2)

    if not flags:
        flags.append("No anomalous fraud or underwriting flags detected")

    ai_explanation = generate_underwriting_summary(
        claim_id, policy_type, claim_amount, coverage_amount,
        risk_score, approval_prob, risk_tier, recommended_action, flags
    )

    return {
        "claim_id": claim_id,
        "policy_type": policy_type,
        "risk_score": risk_score,
        "approval_probability": approval_prob,
        "risk_tier": risk_tier,
        "estimated_payout": estimated_payout,
        "utilization_ratio_pct": round(utilization_ratio * 100, 1),
        "anomaly_flags": flags,
        "recommended_action": recommended_action,
        "ai_explanation": ai_explanation["text"],
        "engine": ai_explanation["engine"]
    }

def generate_underwriting_summary(
    claim_id: str, policy_type: str, claim_amount: float, coverage_amount: float,
    risk_score: float, approval_prob: float, risk_tier: str,
    recommended_action: str, flags: List[str]
) -> Dict[str, str]:
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"Act as a senior insurance underwriting analyst. Summarize this claim assessment:
"
                f"Claim ID: {claim_id} ({policy_type} Policy)
"
                f"Claimed: Rs.{claim_amount:,.2f} / Coverage: Rs.{coverage_amount:,.2f}
"
                f"Risk Score: {risk_score}/100 ({risk_tier}), Approval Probability: {approval_prob}%
"
                f"Flags: {'; '.join(flags)}
"
                f"Write a concise 2-paragraph underwriting report with actionable next steps."
            )
            resp = model.generate_content(prompt)
            if resp and resp.text:
                return {"text": resp.text.strip(), "engine": "Google Gemini Free-Tier"}
        except Exception:
            pass

    flags_formatted = "; ".join(flags)
    text = (
        f"### 🛡️ Actuarial Risk Assessment — `{claim_id}` ({policy_type})

"
        f"**1. Risk Profile & Scoring Summary:**
"
        f"This claim achieved a composite risk score of **{risk_score}/100**, placing it in the **{risk_tier}** category "
        f"with an estimated straight-through approval probability of **{approval_prob}%**. "
        f"The claimed amount of **₹ {claim_amount:,.2f}** represents **{(claim_amount/max(1.0, coverage_amount))*100:.1f}%** of the active policy limit (**₹ {coverage_amount:,.2f}**).

"
        f"**2. Key Underwriting Signals:**
"
        f"Primary risk indicators identified during automated screening: *{flags_formatted}*.

"
        f"**3. Recommended Settlement Protocol:**
"
        f"{recommended_action}"
    )
    return {"text": text, "engine": "Offline Actuarial Heuristic Engine (Zero-Cost)"}
