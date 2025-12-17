# Optimized ML Training Pipeline using XGBoost and LightGBM
# Drop-in replacement for RandomForest in your existing training pipeline

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import PowerTransformer, MinMaxScaler, OneHotEncoder, OrdinalEncoder
from sklearn.metrics import roc_auc_score, classification_report

from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

import xgboost as xgb
import lightgbm as lgb

# --------------------------------------------------
# 1. Load Preprocessed Dataset
# --------------------------------------------------

df = pd.read_csv('../output/preprocessed_data.csv')
TARGET = 'is_fraud'

X = df.drop(columns=[TARGET])
y = df[TARGET]

# --------------------------------------------------
# 2. Feature Groups (Same as preprocessing notebook)
# --------------------------------------------------

num_cols_yeo = ['amount_src', 'amount_usd', 'fee', 'exchange_rate_src_to_dest','ip_risk_score', 'chargeback_history_count',
                'risk_score_internal', 'txn_velocity_1h', 'txn_velocity_24h', 'corridor_risk']

num_cols_minmax = ['account_age_days', 'device_age_days']

ordinal_cols = ['kyc_level']

nominal_cols = ['src_country', 'dest_country', 'currency_src', 'currency_dest', 'payment_method', 'device_type']

# --------------------------------------------------
# 3. Preprocessing Pipeline
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        ('yeo', PowerTransformer(method='yeo-johnson'), num_cols_yeo),
        ('minmax', MinMaxScaler(), num_cols_minmax),
        ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), ordinal_cols),
        ('nominal', OneHotEncoder(handle_unknown='ignore', sparse=False), nominal_cols)
    ],
    remainder='drop'
)

# --------------------------------------------------
# 4A. XGBoost Model (Highly Optimized for Fraud)
# --------------------------------------------------

xgb_model = xgb.XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=(y == 0).sum() / (y == 1).sum(),
    tree_method='hist',
    random_state=42,
    n_jobs=-1
)

xgb_pipeline = ImbPipeline(steps=[
    ('preprocessing', preprocessor),
    ('smote', SMOTE(random_state=42)),
    ('model', xgb_model)
])

# --------------------------------------------------
# 4B. LightGBM Model (Faster, Lower Memory)
# --------------------------------------------------

# Train model
lgb_model = lgb.train(
    params,
    train_data,
    num_boost_round=300,
    valid_sets=[test_data],
    callbacks=[
        lgb.early_stopping(stopping_rounds=50),
        lgb.log_evaluation(period=50)  # logs every 50 rounds
    ]
)

lgb_pipeline = ImbPipeline(steps=[
    ('preprocessing', preprocessor),
    ('smote', SMOTE(random_state=42)),
    ('model', lgb_model)
])

# --------------------------------------------------
# 5. Train / Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# --------------------------------------------------
# 6. Train & Evaluate XGBoost
# --------------------------------------------------

xgb_pipeline.fit(X_train, y_train)
xgb_preds = xgb_pipeline.predict(X_test)
xgb_proba = xgb_pipeline.predict_proba(X_test)[:, 1]

print('XGBoost Results')
print(classification_report(y_test, xgb_preds))
print('ROC-AUC:', roc_auc_score(y_test, xgb_proba))

joblib.dump(xgb_pipeline, '../artifacts/model/fraud_xgb_pipeline.pkl')

# --------------------------------------------------
# 7. Train & Evaluate LightGBM
# --------------------------------------------------

lgb_pipeline.fit(X_train, y_train)
lgb_preds = lgb_pipeline.predict(X_test)
lgb_proba = lgb_pipeline.predict_proba(X_test)[:, 1]

print('LightGBM Results')
print(classification_report(y_test, lgb_preds))
print('ROC-AUC:', roc_auc_score(y_test, lgb_proba))

import os
os.makedirs('../artifacts/model', exist_ok=True)

lgb_model.save_model("../artifacts/model/fraud_lgb_pipeline.txt")
print("✅ Model artifacts saved")

# --------------------------------------------------
# 8. Output Artifacts
# --------------------------------------------------
# - fraud_xgb_pipeline.pkl  (highest accuracy)
# - fraud_lgb_pipeline.pkl  (fastest inference)
