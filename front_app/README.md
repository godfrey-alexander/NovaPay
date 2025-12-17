# Fraud Detection Frontend Application

A professional Streamlit-based web application for real-time fraud detection predictions.

## Features

- 🎨 **Professional UI**: Modern, stylish interface designed for stakeholders
- 🔍 **Real-time Predictions**: Instant fraud risk assessment
- 📊 **Visual Analytics**: Interactive charts and gauges for risk scores
- 🎯 **Risk Factors**: Detailed explanation of risk indicators
- 📥 **Export Results**: Download prediction results as JSON

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your Fraud Detection API is running (default: `http://localhost:8000`)

2. Start the Streamlit application:
```bash
streamlit run app.py
```

3. The application will open in your default web browser at `http://localhost:8501`

4. Configure the API URL in the sidebar if your API is running on a different address

5. Fill out the transaction form and click "Analyze Transaction" to get fraud predictions

## Configuration

- **API Base URL**: Configure in the sidebar (default: `http://localhost:8000`)
- The application will automatically check API health on load

## Features Overview

### Transaction Input Form
- User Information (User ID, Account Age, KYC Tier)
- Transaction Amounts (Source Amount, USD Amount, Fee, Exchange Rate)
- Location & Geography (Countries, Currencies, Channel)
- Risk Indicators (IP Risk, Internal Risk, Corridor Risk, Device Trust)
- Additional Information (Chargeback History, Device Status, Location Mismatch)
- Time Information (Transaction Hour)

### Results Display
- **Fraud Risk Score Gauge**: Visual representation of risk level
- **Decision Card**: Clear indication of transaction decision (ALLOW/STEP_UP/BLOCK)
- **Risk Factors**: Top contributing factors to the risk assessment
- **Transaction Summary**: Complete overview of transaction and prediction
- **Export Functionality**: Download results as JSON

## Decision Thresholds

- **ALLOW**: Fraud score ≤ 0.5 (Low risk)
- **STEP_UP**: Fraud score 0.5 - 0.6 (Medium risk - requires additional verification)
- **BLOCK**: Fraud score > 0.6 (High risk - transaction blocked)

## Support

For issues or questions, please contact the development team.

