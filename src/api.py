from fastapi import FastAPI
from fastapi.responses import FileResponse
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
# Configure joblib for containerized environments
# -----------------------------
# Set joblib temp folder to avoid /dev/shm issues in containers
os.environ['JOBLIB_TEMP_FOLDER'] = '/tmp/joblib_temp'
os.makedirs('/tmp/joblib_temp', exist_ok=True)

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
# Force sequential processing to avoid parallel processing issues in containerized environments
preprocessor.n_jobs = 1
# Also set n_jobs on nested transformers if they exist
if hasattr(preprocessor, 'named_transformers_'):
    for name, transformer in preprocessor.named_transformers_.items():
        if hasattr(transformer, 'n_jobs'):
            transformer.n_jobs = 1

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
    # Binary features
    "new_device": "New or untrusted device detected",
    "location_mismatch": "Unusual location mismatch detected",
    
    # Transaction amounts
    "amount_src": "Unusual source amount",
    "amount_usd": "Unusual transaction amount (USD)",
    "fee": "Unusual fee amount",
    "exchange_rate_src_to_dest": "Suspicious exchange rate",
    
    # Risk scores
    "ip_risk_score": "High-risk IP address",
    "risk_score_internal": "High internal risk score",
    "corridor_risk": "High-risk payment corridor",
    "device_trust_score": "Low device trust score",
    
    # Transaction velocity
    "txn_velocity_1h": "High transaction frequency in last hour",
    "txn_velocity_24h": "High transaction frequency in last 24 hours",
    
    # Account and user features
    "account_age_days": "New or recently created account",
    "chargeback_history_count": "Previous chargeback history",
    "kyc_tier": "Low KYC verification tier",
    
    # Time features
    "hour_sin": "Unusual transaction time",
    "hour_cos": "Unusual transaction time",
    
    # Location and geography (one-hot encoded features)
    "nominal__home_country_UNKNOWN": "Unknown home country",
    "nominal__dest_country_UNKNOWN": "Unknown destination country",
    "nominal__channel_UNKNOWN": "Unknown transaction channel",
    
    # Currency features (one-hot encoded)
    "nominal__source_currency_UNKNOWN": "Unknown source currency",
    "nominal__dest_currency_UNKNOWN": "Unknown destination currency",
    
    # Common one-hot encoded patterns (fallback)
    "nominal__home_country": "Unusual home country",
    "nominal__dest_country": "High-risk destination country",
    "nominal__source_currency": "Unusual source currency",
    "nominal__dest_currency": "High-risk destination currency",
    "nominal__channel": "Unusual transaction channel",
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
# Download logs endpoint
# ======================
@app.get("/logs")
def download_logs():
    """Download the fraud detection API logs"""
    log_file_path = os.path.join(log_dir, "fraud_api.log")
    if os.path.exists(log_file_path):
        return FileResponse(
            log_file_path,
            media_type="text/plain",
            filename="fraud_api.log"
        )
    else:
        return {"error": "Log file not found"}

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

    # Rule-based overrides for obviously risky patterns
    hard_block = False
    # Example: extremely large transaction on a very new account
    if txn.amount_usd >= 1_000_000_000 and txn.account_age_days <= 30:
        hard_block = True

    # Decisioning
    decision = "ALLOW"
    if hard_block:
        decision = "BLOCK"
    elif fraud_score > 0.6:
        decision = "BLOCK"
        # send_email()
    elif fraud_score > 0.4:
        decision = "STEP_UP"
        # send_verification_code()

    # Helper function to get reason code for a feature name
    def get_reason_code(feature_name):
        # Try exact match first
        if feature_name in REASON_MAP:
            return REASON_MAP[feature_name]
        
        # Try partial matches for one-hot encoded features
        # e.g., "nominal__home_country_US" -> try "nominal__home_country" -> try "home_country"
        if "__" in feature_name:
            parts = feature_name.split("__")
            if len(parts) >= 2:
                # Try with prefix (e.g., "nominal__home_country")
                prefix_match = f"{parts[0]}__{parts[1]}"
                if prefix_match in REASON_MAP:
                    return REASON_MAP[prefix_match]
                # Try base feature name (e.g., "home_country")
                base_name = parts[1]
                if base_name in REASON_MAP:
                    return REASON_MAP[base_name]
        
        # Fallback: return a cleaned version of the feature name
        return feature_name.replace("_", " ").title()
    
    # Helper function to get fallback reasons based on transaction features
    def get_fallback_reasons():
        fallback = []
        # Check binary flags first
        if txn.new_device:
            fallback.append(REASON_MAP.get("new_device", "New or untrusted device detected"))
        if txn.location_mismatch:
            fallback.append(REASON_MAP.get("location_mismatch", "Unusual location mismatch detected"))
        
        # Check risk scores
        if txn.ip_risk_score > 0.5:
            fallback.append(REASON_MAP.get("ip_risk_score", "High-risk IP address"))
        if txn.risk_score_internal > 0.5:
            fallback.append(REASON_MAP.get("risk_score_internal", "High internal risk score"))
        if txn.corridor_risk > 0.5:
            fallback.append(REASON_MAP.get("corridor_risk", "High-risk payment corridor"))
        if txn.device_trust_score < 0.3:
            fallback.append(REASON_MAP.get("device_trust_score", "Low device trust score"))
        
        # Check transaction velocity
        if v1 > 10:
            fallback.append(REASON_MAP.get("txn_velocity_1h", "High transaction frequency in last hour"))
        if v24 > 50:
            fallback.append(REASON_MAP.get("txn_velocity_24h", "High transaction frequency in last 24 hours"))
        
        # Check account age
        if txn.account_age_days < 30:
            fallback.append(REASON_MAP.get("account_age_days", "New or recently created account"))
        
        # Check chargeback history
        if txn.chargeback_history_count > 0:
            fallback.append(REASON_MAP.get("chargeback_history_count", "Previous chargeback history"))
        
        # Check transaction amounts
        if txn.amount_usd > 1000:
            fallback.append(REASON_MAP.get("amount_usd", "Unusual transaction amount (USD)"))
        
        # Check KYC tier
        if txn.kyc_tier.upper() in ["LOW", "UNKNOWN"]:
            fallback.append(REASON_MAP.get("kyc_tier", "Low KYC verification tier"))
        
        return fallback
    
    # Compute SHAP reason codes - always return exactly 3 reasons
    reasons = []
    shap_values_dict = {}
    if decision != "ALLOW":
        try:
            shap_vals = explainer.shap_values(X_transformed)[1][0]  # binary classification
            top_idx = np.argsort(np.abs(shap_vals))[-3:]
            reasons = [get_reason_code(FEATURE_NAMES[i]) for i in reversed(top_idx)]

            # Log SHAP values for top features
            shap_values_dict = {FEATURE_NAMES[i]: float(shap_vals[i]) for i in range(len(FEATURE_NAMES))}
        except Exception as e:
            logging.warning(f"SHAP computation failed for user {txn.user_id}: {e}")
        
        # Ensure we have exactly 3 reasons
        if len(reasons) < 3:
            fallback_reasons = get_fallback_reasons()
            # Add fallback reasons that aren't already in the list
            for reason in fallback_reasons:
                if reason not in reasons and len(reasons) < 3:
                    reasons.append(reason)
        
        # If still fewer than 3, pad with generic reasons
        while len(reasons) < 3:
            if decision == "BLOCK":
                reasons.append(f"Fraud score ({fraud_score:.3f}) exceeds block threshold (0.6)")
            elif decision == "STEP_UP":
                reasons.append(f"Fraud score ({fraud_score:.3f}) exceeds step-up threshold (0.4)")
            else:
                reasons.append("Transaction flagged by risk model")
        
        # Take only the first 3 reasons
        reasons = reasons[:3]

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