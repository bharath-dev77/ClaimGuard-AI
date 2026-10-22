# 🛡️ ClaimGuard AI — Insurance Claim Risk Predictor

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Operational Cost](https://img.shields.io/badge/Operational%20Cost-100%25%20Free-brightgreen.svg)](#zero-cost-tech-stack)

> An open-source AI underwriting and actuarial triage platform that evaluates insurance claims across Auto, Health, Property, and Commercial lines to predict claim risk scores, flag potential fraud anomalies, and estimate net settlement payouts.

---

## 🌟 Key Features

* **🔍 Automated Single-Claim Risk Triage:**
  * Evaluates coverage utilization ratios, early policy tenure anomalies, prior claim frequency, incident severity, and evidentiary documentation (police reports and witness presence).
  * Outputs a standardized **Composite Risk Score (0–100)**, **Approval Probability (%)**, and **Net Estimated Payout**.

* **🚩 SIU Fraud & Anomaly Detection:**
  * Automatically flags high-risk indicators such as coverage exhaustion, early-inception claims (≤ 6 months), and severe/total-loss claims lacking official authority reports.
  * Categorizes claims into four actionable underwriting tiers:
    * `Low Risk (Fast-Track Approval)`
    * `Moderate Risk (Standard Adjuster Review)`
    * `High Risk (Senior Underwriter Audit)`
    * `Critical Risk (SIU Fraud Investigation)`

* **📂 Batch CSV Portfolio Scorer:**
  * Upload multi-claim CSV datasets to score entire claim portfolios in one click and export the scored underwriting report.

* **📋 Embedded SQLite Policy & Claims Ledger:**
  * Stores active policies and historical claim evaluations locally with zero external cloud database dependencies.

---

## 🏗️ System Architecture

```text
       ┌───────────────────────────────┐
       │  Underwriter / Adjuster (Web) │
       └──────────────┬────────────────┘
                      │ Claim Parameters / CSV
                      ▼
       ┌───────────────────────────────┐
       │        ClaimGuard API         │
       │          (FastAPI)            │
       └──────┬───────────────┬────────┘
              │               │
      Risk & Fraud Eval   Audit Logging
              │               │
       ┌──────▼────────┐┌─────▼────────┐
       │ Actuarial AI  ││ SQLite       │
       │ Risk Engine   ││ Database     │
       └───────────────┘└──────────────┘
              ▲               ▲
              │ Analytics     │ Read/Write
       ┌──────┴───────────────┴────────┐
       │   Streamlit Web Dashboard     │
       │ (Predictor, Batch CSV, Stats) │
       └───────────────────────────────┘
```

---

## 🛠️ Zero-Cost Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend API** | FastAPI + Uvicorn | Asynchronous Python REST endpoints for claim evaluation |
| **Database** | SQLite 3 | Embedded, zero-configuration SQL database for policies and claim logs |
| **Frontend UI** | Streamlit + Pandas | Interactive underwriting workbench and batch CSV processor |
| **Risk Engine** | Actuarial Heuristics + Gemini Free-Tier | Deterministic multi-factor risk model + optional LLM synthesis |

---

## 📁 Repository Structure

```text
insurance-claim-risk-predictor/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── database.py       # SQLite database initialization, policy seeding & history
│       ├── predictor.py      # Actuarial risk scoring, fraud flags & AI explanation engine
│       ├── models.py         # Pydantic request/response schemas
│       └── main.py           # FastAPI application routes
├── frontend/
│   └── app.py                # Streamlit interactive underwriting dashboard
├── data/
│   └── sample_claims_data.csv # Pre-loaded sample claims dataset for batch testing
├── .env.example              # Environment configuration template
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/insurance-claim-risk-predictor.git
cd insurance-claim-risk-predictor
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Launch the Streamlit Dashboard
```bash
python -m streamlit run frontend/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 5. (Optional) Run the FastAPI Backend Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Check API and SQLite database status |
| `GET` | `/api/policies` | Retrieve seeded insurance policies |
| `POST` | `/api/predict` | Evaluate a claim and return risk score, tier, flags, and payout |
| `GET` | `/api/history` | Retrieve archived claim risk assessments |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
