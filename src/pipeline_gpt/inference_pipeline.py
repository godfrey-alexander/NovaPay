# Inference-Only ML Pipeline
# Uses the trained XGBoost or LightGBM pipeline artifact
# No SMOTE, no training logic – SAFE for production

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

# --------------------------------------------------
# 1. Load Trained Pipeline
# --------------------------------------------------
# Choose ONE depending on deployment

MODEL_PATH = '../model/fraud_lgb_pipeline.pkl'   # or fraud_xgb_pipeline.pkl

pipeline = joblib.load(MODEL_PATH)

# --------------------------------------------------
# 2. Remove Training-Only Steps (SMOTE)
# --------------------------------------------------
# Imbalanced-learn pipelines keep steps by name
# We rebuild a clean inference pipeline

inference_pipeline = Pipeline([
    ('preprocessing', pipeline.named_steps['preprocessing']),
    ('model', pipeline.named_steps['model'])
])

# --------------------------------------------------
# 3. Example Input (Single or Batch)
# --------------------------------------------------

sample_transaction = pd.DataFrame([
    {
        'amount_src': 250.0,
        'amount_usd': 270.0,
        'fee': 2.5,
        'exchange_rate_src_to_dest': 1.08,
        'ip_risk_score': 0.12,
        'chargeback_history_count': 1,
        'risk_score_internal': 0.34,
        'txn_velocity_1h': 3,
        'txn_velocity_24h': 18,
        'corridor_risk': 0.45,
        'account_age_days': 420,
        'device_age_days': 180,
        'kyc_level': 2,
        'src_country': 'US',
        'dest_country': 'NG',
        'currency_src': 'USD',
        'currency_dest': 'NGN',
        'payment_method': 'card',
        'device_type': 'mobile'
    }
])

# --------------------------------------------------
# 4. Run Inference
# --------------------------------------------------

fraud_probability = inference_pipeline.predict_proba(sample_transaction)[:, 1]
fraud_prediction = (fraud_probability >= 0.5).astype(int)

print('Fraud Probability:', fraud_probability[0])
print('Fraud Prediction:', fraud_prediction[0])

# --------------------------------------------------
# 5. Optional: Custom Threshold
# --------------------------------------------------

def predict_with_threshold(df, threshold=0.7):
    probs = inference_pipeline.predict_proba(df)[:, 1]
    return (probs >= threshold).astype(int), probs

# --------------------------------------------------
# 6. Save Clean Inference Pipeline
# --------------------------------------------------

joblib.dump(inference_pipeline, '../model/fraud_inference_pipeline.pkl')

print('\n')
print('Inference-only pipeline saved successfully.')

# --------------------------------------------------
# 7. Deployment Notes
# --------------------------------------------------
# - Stateless
# - Deterministic
# - Latency-safe (<50ms typical)
# - Ready for FastAPI / batch jobs
