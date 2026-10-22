from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app import database, predictor
from app.models import ClaimRiskInput, ClaimRiskResponse

app = FastAPI(
    title="ClaimGuard AI — Insurance Claim Risk Predictor API",
    description="REST API for automated insurance claim risk scoring, fraud anomaly detection, and underwriting triage.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def root():
    return {
        "service": "ClaimGuard AI — Insurance Claim Risk Predictor",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def healthcheck():
    return {"status": "healthy", "database": "connected"}

@app.get("/api/policies")
def list_policies():
    return {"policies": database.get_all_policies()}

@app.post("/api/predict", response_model=ClaimRiskResponse)
def predict_claim_risk(payload: ClaimRiskInput):
    data_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    result = predictor.evaluate_claim_risk(data_dict)
    database.save_claim_assessment(data_dict, result)
    return result

@app.get("/api/history")
def list_assessment_history():
    return {"history": database.get_assessment_history()}
