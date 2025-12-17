from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
import shap
import os
from redis_store import get_velocity, update_velocity

import logging
import json

# -----------------------------
# Ensure logs folder exists
# -----------------------------
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # creates 'logs' folder if it doesn't exist

# -----------------------------
# Configure logging
# -----------------------------
log_file = os.path.join(log_dir, "fraud_api.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("✅ Logging initialized")


# ======================
# App
# ======================
app = FastAPI(  
                title="Fraud Detection API",
                description="Real-time fraud scoring service using ML pipeline",
                version="1.0.0"
            )

# ======================
# Load artifacts ONCE
# ======================
model_lgb  = joblib.load("../artifacts/model/fraud_model.pkl")

preprocessor = joblib.load("../artifacts/preprocessor.pkl")

shap_background = np.load("../artifacts/shap_background.npy", allow_pickle=True)

explainer = shap.TreeExplainer(model_lgb)

# ======================
# Feature definitions
# ======================
num_cols_yeo = [
    'amount_src', 'amount_usd', 'fee', 'exchange_rate_src_to_dest',
    'ip_risk_score', 'chargeback_history_count', 'risk_score_internal',
    'txn_velocity_1h', 'txn_velocity_24h', 'corridor_risk'
]

num_cols_minmax = ['account_age_days', 'device_trust_score']

ordinal_cols = ['kyc_tier']

nominal_cols = ['home_country', 'dest_country', 'source_currency', 'dest_currency', 'channel']

bin_cols = ["new_device", "location_mismatch"]

time_cols = ["hour_sin", "hour_cos"]


FEATURE_NAMES = (
    num_cols_yeo + num_cols_minmax + ordinal_cols +
    list(preprocessor.named_transformers_['nominal'].get_feature_names_out()) +
    bin_cols + time_cols
)


REASON_MAP = {
    "new_device": "New or untrusted device",
    "ip_risk_score": "High-risk IP",
    "location_mismatch": "Unusual location",
    "txn_velocity_1h": "High transaction frequency",
    "amount_usd": "Unusual transaction amount",
}

# ======================
# Input schema
# ======================
class Transaction(BaseModel):
    user_id: str
    amount_src: float
    amount_usd: float
    fee: float
    exchange_rate_src_to_dest: float
    ip_risk_score: float
    chargeback_history_count: int
    risk_score_internal: float
    account_age_days: int
    device_trust_score: float
    corridor_risk: float
    home_country: str
    source_currency: str
    dest_currency: str
    channel: str
    ip_country: str
    kyc_tier: str
    new_device: int
    location_mismatch: int
    hour: int

# ======================
# Health check
# ======================
@app.get("/health")
def health():
    return {"status": "ok"}

# ======================
# Prediction endpoint
# ======================
@app.post("/predict")
def predict(txn: Transaction):
    # Redis velocity
    v1, v24 = get_velocity(txn.user_id)
    update_velocity(txn.user_id)

    # Time encoding
    hour_sin = np.sin(2 * np.pi * txn.hour / 24)
    hour_cos = np.cos(2 * np.pi * txn.hour / 24)

    data = {
        "amount_src": txn.amount_src,
        "amount_usd": txn.amount_usd,
        "fee": txn.fee,
        "exchange_rate_src_to_dest": txn.exchange_rate_src_to_dest,
        "ip_risk_score": txn.ip_risk_score,
        "chargeback_history_count": txn.chargeback_history_count,
        "risk_score_internal": txn.risk_score_internal,
        "account_age_days": txn.account_age_days,
        "device_trust_score": txn.device_trust_score,
        "txn_velocity_1h": v1,
        "txn_velocity_24h": v24,
        "corridor_risk": txn.corridor_risk,
        "new_device": txn.new_device,
        "location_mismatch": txn.location_mismatch,
        "hour_sin": hour_sin,
        "hour_cos": hour_cos,
        "home_country": txn.home_country,
        "source_currency": txn.source_currency,
        "dest_currency": txn.dest_currency,
        "channel": txn.channel,
        "ip_country": txn.ip_country,
        "kyc_tier": txn.kyc_tier
    }

    X = pd.DataFrame([data])

    X_transformed = preprocessor.transform(X)
    
    # Prediction
    fraud_score = model_lgb.predict(X_transformed)[0]

    # Decisioning
    decision = "ALLOW"
    if fraud_score > 0.6:
        decision = "BLOCK"
        # send_email()
    elif fraud_score > 0.4:
        decision = "STEP_UP"
        # send_verification_code()

    # Compute SHAP reason codes
    reasons = []
    shap_values_dict = {}
    if decision != "ALLOW":
        try:
            shap_vals = explainer.shap_values(X_transformed)[1][0]  # binary classification
            top_idx = np.argsort(np.abs(shap_vals))[-3:]
            reasons = [REASON_MAP.get(FEATURE_NAMES[i], FEATURE_NAMES[i]) for i in reversed(top_idx)]

            # Log SHAP values for top features
            shap_values_dict = {FEATURE_NAMES[i]: float(shap_vals[i]) for i in range(len(FEATURE_NAMES))}
        except Exception as e:
            logging.warning(f"SHAP computation failed for user {txn.user_id}: {e}")

    # Prepare result
    result = {
        "fraud_score": round(float(fraud_score), 4),
        "decision": decision,
        "reason_codes": reasons
    }

    # Convert SHAP values to native Python floats
    shap_values_dict = {k: float(v) for k, v in shap_values_dict.items()}
    
    # Convert features to floats
    features_list = X_transformed.astype(float).tolist()
    
    log_entry = {
        "user_id": txn.user_id,
        "fraud_score": float(fraud_score),
        "decision": decision,
        "reason_codes": reasons,
        "features": features_list,
        "shap_values": shap_values_dict
    }
    
    logging.info(json.dumps(log_entry))

    return result