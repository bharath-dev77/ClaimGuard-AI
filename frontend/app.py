import os
import sys
import pandas as pd
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import database, predictor

database.init_db()

st.set_page_config(
    page_title="ClaimGuard AI — Insurance Claim Risk Predictor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ ClaimGuard AI")
    st.caption("Automated Insurance Claim Risk & Fraud Triage Suite")
    st.markdown("---")
    st.write("**Core Capabilities:**")
    st.write("• Actuarial Claim Risk Scoring (0–100)")
    st.write("• SIU Fraud Anomaly Flagging")
    st.write("• Batch CSV Portfolio Underwriting")
    st.write("• Automated Payout Estimation")
    st.markdown("---")
    st.success("⚡ Engine Status: Online (100% Free Stack)")

st.markdown("<div class='main-title'>🛡️ ClaimGuard AI — Insurance Claim Risk Predictor</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Evaluate insurance claims for fraud anomalies, underwriting risk tiers, and straight-through settlement eligibility.</div>", unsafe_allow_html=True)

tab_predict, tab_batch, tab_ledger, tab_analytics = st.tabs([
    "🔍 Single Claim Risk Predictor",
    "📂 Batch CSV Claim Scorer",
    "📋 Policies & Assessment Ledger",
    "📊 Portfolio Analytics"
])

# -------------------------------------------------------------
# TAB 1: SINGLE CLAIM RISK PREDICTOR
# -------------------------------------------------------------
with tab_predict:
    st.subheader("Evaluate Individual Insurance Claim")
    
    with st.form("claim_risk_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            claim_id = st.text_input("Claim Reference ID", value="CLM-2026-501")
            policy_type = st.selectbox("Policy Category", ["Auto", "Health", "Property", "Commercial"])
            holder_age = st.number_input("Policyholder Age (Years)", min_value=18, max_value=100, value=34)
            tenure_months = st.number_input("Policy Tenure (Months)", min_value=1, max_value=360, value=18)
        with c2:
            coverage_amount = st.number_input("Total Policy Coverage Limit (₹)", min_value=10000.0, value=500000.0, step=25000.0)
            claim_amount = st.number_input("Claimed Amount (₹)", min_value=1000.0, value=120000.0, step=5000.0)
            deductible = st.number_input("Policy Deductible (₹)", min_value=0.0, value=5000.0, step=1000.0)
            prior_claims = st.number_input("Prior Claims Count", min_value=0, max_value=20, value=1)
        with c3:
            incident_severity = st.selectbox("Incident Severity", ["Minor", "Moderate", "Severe", "Total Loss"])
            police_report = st.selectbox("Official Police / Authority Report Filed?", ["Yes", "No"])
            witness_present = st.selectbox("Corroborating Witness Present?", ["Yes", "No"])
            save_to_db = st.checkbox("Archive assessment to SQLite ledger", value=True)
            
        submit_btn = st.form_submit_button("⚡ Run Actuarial Risk Prediction", type="primary")

    if submit_btn:
        payload = {
            "claim_id": claim_id.strip() or "CLM-2026-501",
            "policy_type": policy_type,
            "holder_age": holder_age,
            "tenure_months": tenure_months,
            "coverage_amount": coverage_amount,
            "claim_amount": claim_amount,
            "deductible": deductible,
            "prior_claims": prior_claims,
            "incident_severity": incident_severity,
            "police_report_filed": police_report,
            "witness_present": witness_present
        }
        res = predictor.evaluate_claim_risk(payload)
        if save_to_db:
            database.save_claim_assessment(payload, res)
        st.session_state["last_prediction"] = res

    if "last_prediction" in st.session_state:
        res = st.session_state["last_prediction"]
        st.markdown("---")
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Composite Risk Score", f"{res['risk_score']} / 100")
        k2.metric("Approval Probability", f"{res['approval_probability']}%")
        k3.metric("Estimated Net Payout", f"₹ {res['estimated_payout']:,.2f}")
        k4.metric("Coverage Utilization", f"{res['utilization_ratio_pct']}%")
        
        tier = res["risk_tier"]
        if "Low Risk" in tier:
            st.success(f"✅ **Underwriting Triage Tier:** {tier}")
        elif "Moderate Risk" in tier:
            st.warning(f"⚠️ **Underwriting Triage Tier:** {tier}")
        else:
            st.error(f"🚨 **Underwriting Triage Tier:** {tier}")
            
        col_l, col_r = st.columns([3, 2])
        with col_l:
            st.markdown(res["ai_explanation"])
            st.caption(f"Engine: {res['engine']}")
        with col_r:
            st.markdown("### 🚩 Triggered Anomaly & Audit Flags")
            for flag in res["anomaly_flags"]:
                if "No anomalous" in flag:
                    st.info(f"✓ {flag}")
                else:
                    st.warning(f"• {flag}")

# -------------------------------------------------------------
# TAB 2: BATCH CSV CLAIM SCORER
# -------------------------------------------------------------
with tab_batch:
    st.subheader("Batch Portfolio Claim Risk Scoring")
    st.write("Upload a CSV file containing multiple claims or load the sample portfolio dataset to run bulk underwriting triage.")
    
    sample_csv_path = os.path.join(CURRENT_DIR, "..", "data", "sample_claims_data.csv")
    if os.path.exists(sample_csv_path):
        with open(sample_csv_path, "r") as f:
            sample_csv_content = f.read()
        st.download_button(
            "📥 Download Sample Claims CSV Template",
            sample_csv_content,
            file_name="sample_claims_data.csv",
            mime="text/csv"
        )
        
    use_sample = st.checkbox("Load pre-bundled sample claims dataset (`data/sample_claims_data.csv`)", value=True)
    uploaded_csv = st.file_uploader("Or upload your own Claims CSV", type=["csv"])
    
    df_batch = None
    if uploaded_csv is not None:
        df_batch = pd.read_csv(uploaded_csv)
    elif use_sample and os.path.exists(sample_csv_path):
        df_batch = pd.read_csv(sample_csv_path)
        
    if df_batch is not None and not df_batch.empty:
        if st.button("🚀 Score All Claims in Dataset", type="primary"):
            scored_rows = []
            for _, row in df_batch.iterrows():
                row_dict = row.to_dict()
                out = predictor.evaluate_claim_risk(row_dict)
                scored_rows.append({
                    "claim_id": out["claim_id"],
                    "policy_type": out["policy_type"],
                    "claim_amount": row_dict.get("claim_amount"),
                    "coverage_amount": row_dict.get("coverage_amount"),
                    "risk_score": out["risk_score"],
                    "approval_probability_pct": out["approval_probability"],
                    "risk_tier": out["risk_tier"],
                    "estimated_payout": out["estimated_payout"],
                    "primary_flag": out["anomaly_flags"][0] if out["anomaly_flags"] else "None"
                })
            df_scored = pd.DataFrame(scored_rows)
            st.dataframe(df_scored, use_container_width=True, hide_index=True)
            
            csv_out = df_scored.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Scored Claims Report (CSV)",
                csv_out,
                file_name="scored_insurance_claims.csv",
                mime="text/csv"
            )

# -------------------------------------------------------------
# TAB 3: POLICIES & ASSESSMENT LEDGER
# -------------------------------------------------------------
with tab_ledger:
    st.subheader("Active Policy Catalog")
    policies = database.get_all_policies()
    if policies:
        st.dataframe(pd.DataFrame(policies), use_container_width=True, hide_index=True)
        
    st.markdown("---")
    st.subheader("Historical Claim Risk Assessments")
    history = database.get_assessment_history()
    if history:
        df_h = pd.DataFrame(history)
        cols = ["id", "claim_id", "policy_type", "claim_amount", "risk_score", "approval_probability", "risk_tier", "estimated_payout", "created_at"]
        st.dataframe(df_h[cols], use_container_width=True, hide_index=True)
    else:
        st.info("No claim assessments archived yet. Evaluate a claim in Tab 1 to populate the ledger.")

# -------------------------------------------------------------
# TAB 4: PORTFOLIO ANALYTICS
# -------------------------------------------------------------
with tab_analytics:
    st.subheader("Actuarial Portfolio Risk Distribution")
    if os.path.exists(sample_csv_path):
        df_port = pd.read_csv(sample_csv_path)
        results = [predictor.evaluate_claim_risk(r.to_dict()) for _, r in df_port.iterrows()]
        df_res = pd.DataFrame(results)
        
        a1, a2, a3 = st.columns(3)
        a1.metric("Sample Portfolio Claims", len(df_res))
        a2.metric("Average Risk Score", f"{df_res['risk_score'].mean():.1f} / 100")
        high_risk_cnt = sum(1 for r in results if r["risk_score"] >= 55.0)
        a3.metric("High / Critical Risk Claims", high_risk_cnt)
        
        st.markdown("### 📊 Risk Score by Policy Type")
        chart_df = df_res.groupby("policy_type")[["risk_score", "approval_probability"]].mean()
        st.bar_chart(chart_df)
