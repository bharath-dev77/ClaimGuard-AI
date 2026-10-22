import sqlite3
import os
import tempfile
import json
from typing import List, Dict, Any, Optional

def get_default_db_path() -> str:
    """
    Determines optimal SQLite path. Prefers local project directory,
    falling back to temp directory if filesystem locks are restricted.
    """
    if os.environ.get("CLAIMS_DB_PATH"):
        return os.environ["CLAIMS_DB_PATH"]
    
    preferred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "claims.db")
    try:
        test_conn = sqlite3.connect(preferred_path)
        test_conn.cursor().execute("CREATE TABLE IF NOT EXISTS _fs_test (x INT);")
        test_conn.commit()
        test_conn.cursor().execute("DROP TABLE _fs_test;")
        test_conn.commit()
        test_conn.close()
        return os.path.abspath(preferred_path)
    except Exception:
        return os.path.join(tempfile.gettempdir(), "insurance_claims.db")

DB_FILE = get_default_db_path()

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes SQLite tables and seeds default insurance policies and sample claim assessments."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_number TEXT UNIQUE NOT NULL,
                policy_type TEXT NOT NULL,
                holder_name TEXT NOT NULL,
                holder_age INTEGER NOT NULL,
                tenure_months INTEGER NOT NULL,
                coverage_amount REAL NOT NULL,
                deductible REAL NOT NULL,
                annual_premium REAL NOT NULL,
                prior_claims INTEGER NOT NULL DEFAULT 0,
                status TEXT DEFAULT 'Active'
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                policy_type TEXT NOT NULL,
                holder_age INTEGER NOT NULL,
                tenure_months INTEGER NOT NULL,
                coverage_amount REAL NOT NULL,
                claim_amount REAL NOT NULL,
                deductible REAL NOT NULL,
                prior_claims INTEGER NOT NULL,
                incident_severity TEXT NOT NULL,
                police_report_filed TEXT NOT NULL,
                witness_present TEXT NOT NULL,
                risk_score REAL NOT NULL,
                approval_probability REAL NOT NULL,
                risk_tier TEXT NOT NULL,
                estimated_payout REAL NOT NULL,
                anomaly_flags TEXT NOT NULL,
                ai_explanation TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

    seed_default_data()

def seed_default_data() -> None:
    sample_policies = [
        ("POL-AUTO-1001", "Auto", "Arjun Mehta", 34, 48, 500000.0, 5000.0, 14500.0, 0, "Active"),
        ("POL-AUTO-1002", "Auto", "Karthik Rajan", 22, 3, 600000.0, 5000.0, 21000.0, 3, "Under Review"),
        ("POL-HLTH-2001", "Health", "Divya Krishnan", 45, 36, 1000000.0, 10000.0, 28000.0, 1, "Active"),
        ("POL-PROP-3001", "Property", "Suresh Nair", 52, 84, 2500000.0, 25000.0, 32000.0, 0, "Active"),
        ("POL-COMM-4001", "Commercial", "Apex Logistics Pvt Ltd", 39, 5, 5000000.0, 50000.0, 95000.0, 2, "Flagged"),
        ("POL-HLTH-2002", "Health", "Meera Sundaram", 29, 24, 500000.0, 5000.0, 12000.0, 0, "Active")
    ]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM policies;")
        if cursor.fetchone()[0] == 0:
            for p in sample_policies:
                cursor.execute("""
                    INSERT INTO policies (
                        policy_number, policy_type, holder_name, holder_age,
                        tenure_months, coverage_amount, deductible, annual_premium,
                        prior_claims, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, p)
            conn.commit()

def get_all_policies() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM policies ORDER BY id ASC;")
        return [dict(row) for row in cursor.fetchall()]

def save_claim_assessment(data: Dict[str, Any], result: Dict[str, Any]) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO claim_assessments (
                claim_id, policy_type, holder_age, tenure_months,
                coverage_amount, claim_amount, deductible, prior_claims,
                incident_severity, police_report_filed, witness_present,
                risk_score, approval_probability, risk_tier, estimated_payout,
                anomaly_flags, ai_explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            data.get("claim_id", "CLM-MANUAL"),
            data.get("policy_type", "Auto"),
            int(data.get("holder_age", 30)),
            int(data.get("tenure_months", 12)),
            float(data.get("coverage_amount", 500000.0)),
            float(data.get("claim_amount", 50000.0)),
            float(data.get("deductible", 5000.0)),
            int(data.get("prior_claims", 0)),
            data.get("incident_severity", "Minor"),
            data.get("police_report_filed", "Yes"),
            data.get("witness_present", "Yes"),
            float(result["risk_score"]),
            float(result["approval_probability"]),
            result["risk_tier"],
            float(result["estimated_payout"]),
            json.dumps(result["anomaly_flags"]),
            result["ai_explanation"]
        ))
        conn.commit()
        return cursor.lastrowid

def get_assessment_history(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM claim_assessments ORDER BY created_at DESC LIMIT ?;", (limit,))
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            try:
                d["anomaly_flags"] = json.loads(d["anomaly_flags"])
            except Exception:
                d["anomaly_flags"] = []
            rows.append(d)
        return rows
