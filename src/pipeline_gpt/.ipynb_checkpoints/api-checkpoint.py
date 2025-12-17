# FastAPI Inference Service for Fraud Detection
# Hybrid: /predict returns optional SHAP explanations with explain=True
# Added /predict/batch_csv endpoint for CSV batch uploads

from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from pydantic import BaseModel
import joblib
import pandas as pd
import shap
import io

# --------------------------------------------------
# 1. App Initialization
# --------------------------------------------------

app = FastAPI(
    title="Fraud Detection Inference API",
    description="Real-time fraud scoring service with optional SHAP explanations and CSV batch upload",
    version="1.3.0"
)

# --------------------------------------------------
# 2. Load Inference Pipeline
# --------------------------------------------------

MODEL_PATH = "model/fraud_inference_pipeline.pkl"

pipeline = joblib.load(MODEL_PATH)
preprocessor = pipeline.named_steps['preprocessing']
model = pipeline.named_steps['model']

explainer = shap.TreeExplainer(model)

# --------------------------------------------------
# 3. Request Schema
# --------------------------------------------------

class Transaction(BaseModel):
    amount_src: float
    amount_usd: float
    fee: float
    exchange_rate_src_to_dest: float
    ip_risk_score: float
    chargeback_history_count: int
    risk_score_internal: float
    txn_velocity_1h: int
    txn_velocity_24h: int
    corridor_risk: float
    account_age_days: int
    device_age_days: int
    kyc_level: int
    src_country: str
    dest_country: str
    currency_src: str
    currency_dest: str
    payment_method: str
    device_type: str

# --------------------------------------------------
# 4. Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# --------------------------------------------------
# 5. Prediction Endpoint (Optional SHAP)
# --------------------------------------------------

@app.post("/predict")
def predict(transaction: Transaction, explain: bool = Query(False), threshold: float = Query(0.7)):
    try:
        df = pd.DataFrame([transaction.dict()])
        proba = pipeline.predict_proba(df)[:, 1][0]
        prediction = int(proba >= threshold)
        response = {
            "fraud_probability": round(float(proba), 6),
            "fraud_prediction": prediction,
            "threshold": threshold
        }

        if explain:
            X_transformed = preprocessor.transform(df)
            shap_values = explainer.shap_values(X_transformed)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            feature_names = preprocessor.get_feature_names_out()
            response["shap"] = {name: float(val) for name, val in zip(feature_names, shap_values[0])}

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------
# 6. Batch Prediction Endpoint (JSON)
# --------------------------------------------------

@app.post("/predict/batch")
def predict_batch(transactions: list[Transaction], explain: bool = Query(False), threshold: float = Query(0.7)):
    try:
        df = pd.DataFrame([t.dict() for t in transactions])
        probas = pipeline.predict_proba(df)[:, 1]
        preds = (probas >= threshold).astype(int)
        responses = []

        for i in range(len(df)):
            resp = {
                "fraud_probability": round(float(probas[i]), 6),
                "fraud_prediction": int(preds[i]),
                "threshold": threshold
            }

            if explain:
                X_transformed = preprocessor.transform(df.iloc[[i]])
                shap_values = explainer.shap_values(X_transformed)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]
                feature_names = preprocessor.get_feature_names_out()
                resp["shap"] = {name: float(val) for name, val in zip(feature_names, shap_values[0])}

            responses.append(resp)

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------
# 7. Batch Prediction Endpoint (CSV)
# --------------------------------------------------

@app.post("/predict/batch_csv")
async def predict_batch_csv(file: UploadFile = File(...), explain: bool = Query(False), threshold: float = Query(0.7)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # Ensure all required columns are present
        missing_cols = set(preprocessor.feature_names_in_) - set(df.columns)
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing_cols}")

        probas = pipeline.predict_proba(df)[:, 1]
        preds = (probas >= threshold).astype(int)
        responses = []

        for i in range(len(df)):
            resp = {
                "fraud_probability": round(float(probas[i]), 6),
                "fraud_prediction": int(preds[i]),
                "threshold": threshold
            }

            if explain:
                X_transformed = preprocessor.transform(df.iloc[[i]])
                shap_values = explainer.shap_values(X_transformed)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]
                feature_names = preprocessor.get_feature_names_out()
                resp["shap"] = {name: float(val) for name, val in zip(feature_names, shap_values[0])}

            responses.append(resp)

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------------------
# Run Locally
# uvicorn app:app --host 0.0.0.0 --port 8000
