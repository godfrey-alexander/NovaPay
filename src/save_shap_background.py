import numpy as np
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer

# Load data & artifacts
df = pd.read_csv("../output/preprocessed_data.csv")

# preprocessor = joblib.load("../artifacts/preprocessor.pkl")

# # Feature definitions
# num_cols_yeo = [
#     'amount_src', 'amount_usd', 'fee', 'exchange_rate_src_to_dest',
#     'ip_risk_score', 'chargeback_history_count', 'risk_score_internal',
#     'txn_velocity_1h', 'txn_velocity_24h', 'corridor_risk'
# ]

# num_cols_minmax = ['account_age_days', 'device_trust_score']

# ordinal_cols = ['kyc_tier']

# nominal_cols = ['home_country', 'dest_country', 'source_currency', 'dest_currency','channel']

# bin_cols = ["new_device", "location_mismatch"]

# time_cols = ["hour_sin", "hour_cos"]

# Make sure passthrough includes bin_cols + time_cols
# X = preprocessor.transform(df)

# Safe sampling
n = min(300, len(df))
background = df[np.random.choice(len(df), n, replace=False)]

# Save
np.save("../artifacts/shap_background.npy", background)

print(f"✅ SHAP background saved ({n} rows)")