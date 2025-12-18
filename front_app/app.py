import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import json
import turtle


# ======================
# Page Configuration
# ======================
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# Custom CSS Styling
# ======================
# st.markdown("""
#     <style>
#     .main-header {
#         font-size: 3rem;
#         font-weight: 700;
#         background: linear-gradient(90deg, #1f77b4, #ff7f0e);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         text-align: center;
#         margin-bottom: 0.5rem;
#     }
#     .sub-header {
#         text-align: center;
#         color: #666;
#         font-size: 1.2rem;
#         margin-bottom: 2rem;
#     }
#     .metric-card {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1.5rem;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#     }
#     .decision-block {
#         background: #ff4444;
#         padding: 1rem;
#         border-radius: 8px;
#         color: white;
#         text-align: center;
#         font-weight: bold;
#         font-size: 1.5rem;
#     }
#     .decision-step {
#         background: #ffaa00;
#         padding: 1rem;
#         border-radius: 8px;
#         color: white;
#         text-align: center;
#         font-weight: bold;
#         font-size: 1.5rem;
#     }
#     .decision-allow {
#         background: #00cc66;
#         padding: 1rem;
#         border-radius: 8px;
#         color: white;
#         text-align: center;
#         font-weight: bold;
#         font-size: 1.5rem;
#     }
#     .stButton>button {
#         width: 100%;
#         background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         font-weight: bold;
#         border: none;
#         border-radius: 8px;
#         padding: 0.75rem;
#         font-size: 1.1rem;
#         transition: all 0.3s;
#     }
#     .stButton>button:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
#     }
#     .info-box {
#         background: #f0f2f6;
#         padding: 1rem;
#         border-radius: 8px;
#         border-left: 4px solid #667eea;
#         margin: 1rem 0;
#     }
#     </style>
# """, unsafe_allow_html=True)


# Custom CSS for ultra-stylish professional dark theme design with larger fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800&display=swap');
    
    /* Dark theme base with enhanced gradient */
    .stApp {
        background: linear-gradient(180deg, #0a0d14 0%, #0e1117 30%, #1a1d29 70%, #0e1117 100%);
        font-size: 18px;
    }
    
    .main .block-container {
        background: transparent;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    * {
        font-family: 'Poppins', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Base font size increase */
    body, p, div, span {
        font-size: 18px !important;
        line-height: 1.7 !important;
    }
    
    /* Main header with reduced brightness and original font sizes */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 1.6rem 1.4rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 1.2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3),
                    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.4; }
        50% { transform: scale(1.1); opacity: 0.6; }
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.2rem !important;
        font-weight: 800;
        margin-bottom: 0.3rem;
        text-shadow: 0 2px 20px rgba(0, 0, 0, 0.2);
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1rem !important;
        margin: 0;
        font-weight: 300;
        position: relative;
        z-index: 1;
        text-shadow: 0 1px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced section headers - Dark theme */
    .section-header {
        background: linear-gradient(135deg, rgba(38, 39, 48, 0.98) 0%, rgba(30, 33, 43, 0.98) 100%);
        padding: 1.8rem 2.5rem;
        border-left: 6px solid;
        border-image: linear-gradient(135deg, #667eea, #764ba2, #f093fb) 1;
        border-radius: 16px;
        margin: 2.5rem 0 2rem 0;
        font-size: 1.8rem !important;
        font-weight: 800;
        color: #fafafa;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(102, 126, 234, 0.3) inset;
        letter-spacing: -0.5px;
    }
    
    /* Section headers (h3, h4) - Larger fonts */
    h3 {
        color: #fafafa !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    h4 {
        color: #fafafa !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Premium metric cards with glassmorphism - Dark theme */
    .metric-card {
        background: linear-gradient(135deg, rgba(38, 39, 48, 0.95) 0%, rgba(30, 33, 43, 0.95) 100%);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(102, 126, 234, 0.2) inset;
        border: 1px solid rgba(102, 126, 234, 0.2);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        color: #fafafa;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3),
                    0 0 0 1px rgba(102, 126, 234, 0.4) inset;
    }
    
    /* Decision cards - Dark theme with larger fonts */
    .decision-block {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 50%, #c92a2a 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 800;
        font-size: 1.6rem !important;
        box-shadow: 0 15px 40px rgba(238, 90, 111, 0.5),
                    0 0 0 2px rgba(255, 255, 255, 0.15) inset;
        margin: 1rem 0;
        border: 2px solid rgba(255, 255, 255, 0.25);
        letter-spacing: 0.5px;
    }
    
    .decision-step {
        background: linear-gradient(135deg, #ffd43b 0%, #ffa94d 50%, #f08c00 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 800;
        font-size: 1.6rem !important;
        box-shadow: 0 15px 40px rgba(255, 168, 77, 0.5),
                    0 0 0 2px rgba(255, 255, 255, 0.15) inset;
        margin: 1rem 0;
        border: 2px solid rgba(255, 255, 255, 0.25);
        letter-spacing: 0.5px;
    }
    
    .decision-allow {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 50%, #2b8a3e 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 800;
        font-size: 1.6rem !important;
        box-shadow: 0 15px 40px rgba(64, 192, 87, 0.5),
                    0 0 0 2px rgba(255, 255, 255, 0.15) inset;
        margin: 1rem 0;
        border: 2px solid rgba(255, 255, 255, 0.25);
        letter-spacing: 0.5px;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    /* Stunning prediction cards */
    .fraud-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 50%, #c92a2a 100%);
        color: white;
        padding: 1.6rem 1.4rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 14px 40px rgba(238, 90, 111, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
                    0 0 100px rgba(255, 107, 107, 0.2);
        position: relative;
        overflow: hidden;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 20px 60px rgba(238, 90, 111, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1) inset, 0 0 100px rgba(255, 107, 107, 0.2); }
        to { box-shadow: 0 20px 60px rgba(238, 90, 111, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.15) inset, 0 0 120px rgba(255, 107, 107, 0.3); }
    }
    
    .legitimate-card {
        background: linear-gradient(135deg, #51cf66 0%, #40c057 50%, #2b8a3e 100%);
        color: white;
        padding: 1.6rem 1.4rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 14px 40px rgba(64, 192, 87, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
                    0 0 100px rgba(81, 207, 102, 0.2);
        position: relative;
        overflow: hidden;
        animation: glow-green 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow-green {
        from { box-shadow: 0 20px 60px rgba(64, 192, 87, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.1) inset, 0 0 100px rgba(81, 207, 102, 0.2); }
        to { box-shadow: 0 20px 60px rgba(64, 192, 87, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.15) inset, 0 0 120px rgba(81, 207, 102, 0.3); }
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1f3a 0%, #2c3e50 50%, #34495e 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #2c3e50 50%, #34495e 100%);
    }
    
    /* Premium button styling - Larger fonts */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        font-weight: 700;
        padding: 1.2rem 3.5rem;
        border-radius: 16px;
        border: none;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4),
                    0 0 0 2px rgba(255, 255, 255, 0.15) inset;
        font-size: 1.3rem !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
    }
    
    .stButton>button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    /* Enhanced input fields - Dark theme with larger fonts */
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stTextInput>div>div>input {
        border-radius: 14px;
        border: 2px solid rgba(102, 126, 234, 0.4);
        background: rgba(38, 39, 48, 0.9);
        color: #fafafa;
        transition: all 0.3s ease;
        padding: 1rem 1.3rem;
        font-size: 1.1rem !important;
        font-weight: 500;
    }
    
    .stNumberInput>div>div>input:focus, 
    .stSelectbox>div>div>select:focus,
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.3),
                    0 6px 20px rgba(102, 126, 234, 0.25);
        background: rgba(38, 39, 48, 1);
        outline: none;
        color: #fafafa;
        transform: scale(1.02);
    }
    
    /* Selectbox options */
    .stSelectbox>div>div>select option {
        background: #262730;
        color: #fafafa;
        font-size: 1.1rem;
        padding: 0.8rem;
    }
    
    /* Labels - Larger fonts */
    label {
        color: #e0e0e0 !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Enhanced expanders - Dark theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(38, 39, 48, 0.8) 0%, rgba(30, 33, 43, 0.8) 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-weight: 600;
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        color: #fafafa;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border-color: rgba(102, 126, 234, 0.5);
        transform: translateX(4px);
    }
    
    /* Expander content */
    .streamlit-expanderContent {
        background: rgba(38, 39, 48, 0.6);
        color: #fafafa;
    }
    
    /* Enhanced tabs - Dark theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(38, 39, 48, 0.5);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(38, 39, 48, 0.8);
        color: #e0e0e0;
        border-radius: 12px 12px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes with gradient - Dark theme */
    .info-box {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(33, 150, 243, 0.08) 100%);
        border-left: 4px solid #2196F3;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
        color: #fafafa;
    }
    
    /* Premium footer - Dark theme */
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        color: #b0b0b0;
        font-size: 0.95rem;
        margin-top: 4rem;
        background: linear-gradient(135deg, rgba(38, 39, 48, 0.8) 0%, rgba(30, 33, 43, 0.8) 100%);
        border-radius: 20px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 10px;
    }
    
    /* Metrics styling - Larger fonts */
    [data-testid="stMetricValue"] {
        font-weight: 800;
        font-size: 2.8rem !important;
        color: #fafafa !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #b0b0b0;
        font-size: 1.2rem !important;
    }
    
    /* Hide some Streamlit default elements but keep header (for sidebar toggle button) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Scrollbar styling - Dark theme */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(38, 39, 48, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #f093fb);
    }
    
    /* Success/Error messages - Dark theme */
    .stSuccess {
        background: linear-gradient(135deg, rgba(81, 207, 102, 0.15) 0%, rgba(64, 192, 87, 0.08) 100%);
        border-left: 4px solid #51cf66;
        border-radius: 12px;
        padding: 1rem;
        color: #fafafa;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15) 0%, rgba(238, 90, 111, 0.08) 100%);
        border-left: 4px solid #ff6b6b;
        border-radius: 12px;
        padding: 1rem;
        color: #fafafa;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(33, 150, 243, 0.08) 100%);
        border-left: 4px solid #2196F3;
        border-radius: 12px;
        padding: 1rem;
        color: #fafafa;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 168, 77, 0.15) 0%, rgba(255, 168, 77, 0.08) 100%);
        border-left: 4px solid #ffa94d;
        border-radius: 12px;
        padding: 1rem;
        color: #fafafa;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(38, 39, 48, 0.8) !important;
        color: #fafafa !important;
    }
    
    /* Text colors - Larger fonts */
    p, div, span {
        color: #e0e0e0;
        font-size: 1.1rem !important;
        line-height: 1.8 !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #e0e0e0;
        font-size: 1.1rem !important;
        line-height: 1.8 !important;
    }
    
    /* Sidebar styling - Larger fonts */
    [data-testid="stSidebar"] {
        font-size: 1.1rem !important;
    }
    
    [data-testid="stSidebar"] label {
        font-size: 1.1rem !important;
    }
    
    /* Slider styling - Larger */
    .stSlider>div>div>div {
        background: rgba(102, 126, 234, 0.4);
        height: 10px;
    }
    
    .stSlider>div>div>div>div {
        background: linear-gradient(135deg, #667eea, #764ba2);
        height: 10px;
    }
    
    .stSlider label {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }
    
    /* Success/Error/Info/Warning messages - Larger fonts */
    .stSuccess, .stError, .stInfo, .stWarning {
        font-size: 1.15rem !important;
        padding: 1.2rem !important;
        border-radius: 14px !important;
    }
    
    /* Dataframe styling - Larger fonts */
    .dataframe {
        font-size: 1.05rem !important;
    }
    
    .dataframe th {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }
    
    .dataframe td {
        font-size: 1.05rem !important;
        padding: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ======================
# Configuration
# ======================
API_BASE_URL = st.sidebar.text_input(
    "API Base URL",
    value="https://novapay-production-80bc.up.railway.app",
    help="Enter the base URL of your Fraud Detection API"
)

# ======================
# Helper Functions
# ======================
def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        # Surface the actual connection error in the sidebar to help debugging
        try:
            st.sidebar.error(f"API health check failed: {e}")
        except Exception:
            pass
        return False

def predict_fraud(transaction_data):
    """Send transaction data to API and get prediction"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=transaction_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def download_logs():
    """Download model logs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/logs", timeout=10)
        response.raise_for_status()
        
        # Check if response is JSON error
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            error_data = response.json()
            return None, error_data.get('error', 'Unknown error from API')
        
        return response.content, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def get_decision_color(decision):
    """Get color based on decision"""
    if decision == "BLOCK":
        return "#ff4444"
    elif decision == "STEP_UP":
        return "#ffaa00"
    else:
        return "#00cc66"

def get_decision_icon(decision):
    """Get icon based on decision"""
    if decision == "BLOCK":
        return "🚫"
    elif decision == "STEP_UP":
        return "⚠️"
    else:
        return "✅"

# ======================
# Main App
# ======================
# Ultra-Stylish Professional Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ Fraud Detection System</h1>
    <p>Advanced Machine Learning-Powered Transaction Fraud Analysis</p>
    <div style='margin-top: 1.5rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;'>
        <span style='background: rgba(255,255,255,0.2); padding: 0.5rem 1.5rem; border-radius: 20px; font-size: 0.9rem; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3);'>
            ⚡ Real-Time Analysis
        </span>
        <span style='background: rgba(255,255,255,0.2); padding: 0.5rem 1.5rem; border-radius: 20px; font-size: 0.9rem; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3);'>
            ⚖️Scalable
        </span>
        <span style='background: rgba(255,255,255,0.2); padding: 0.5rem 1.5rem; border-radius: 20px; font-size: 0.9rem; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3);'>
            🔒 Secure & Reliable
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Check API health
with st.sidebar:
    st.markdown("### 🔌 API Status")
    if check_api_health():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Not Available")
        st.info("Please ensure the API is running and the URL is correct.")
    
    st.markdown("---")
    
    # Always show download button, check API health when clicked
    if st.button("📥 Download Model Logs", use_container_width=True, help="Download the complete fraud detection API logs"):
        if check_api_health():
            with st.spinner("Downloading logs..."):
                log_content, error = download_logs()
                if error:
                    st.error(f"❌ Error: {error}")
                elif log_content:
                    st.download_button(
                        label="💾 Save Log File",
                        data=log_content,
                        file_name=f"fraud_api_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ No log content received from API")
        else:
            st.error("❌ API is not connected. Please check the API status above.")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 Transaction Details")
    
    with st.form("fraud_prediction_form"):
        # User Information
        st.markdown("#### 👤 User Information")
        user_id = st.text_input("User ID", value="", placeholder="Enter user ID")
        account_age_days = st.number_input("Account Age (days)", min_value=0, value=30, step=1)
        kyc_tier = st.selectbox("KYC Tier", ["LOW", "STANDARD", "ENHANCED", "UNKNOWN"], index=0)
        
        # Transaction Amounts
        st.markdown("#### 💰 Transaction Amounts")
        amount_src = st.number_input("Source Amount", min_value=0.0, value=100.0, step=0.01, format="%.2f")
        amount_usd = st.number_input("Amount (USD)", min_value=0.0, value=100.0, step=0.01, format="%.2f")
        fee = st.number_input("Fee", min_value=0.0, value=2.5, step=0.01, format="%.2f")
        exchange_rate_src_to_dest = st.number_input("Exchange Rate", min_value=0.0, value=1.0, step=0.01, format="%.4f")
        
        # Location & Geography
        st.markdown("#### 🌍 Location & Geography")
        home_country = st.selectbox("Home Country", ["US", "CA", "UK", "UNKNOWN"], index=0)
        ip_country = st.selectbox("IP Country", ["US", "CA", "UK", "UNKNOWN"], index=0)
        source_currency = st.selectbox("Source Currency", ["USD", "CAD", "GBP"], index=0)
        dest_currency = st.selectbox("Destination Currency", ["USD", "CAD", "GBP", "EUR", "NGN", "INR", "MXN", "CNY", "PHP"], index=0)
        channel = st.selectbox("Channel", ["WEB", "MOBILE", "ATM", "UNKNOWN"], index=0)
        
        # Risk Scores
        st.markdown("#### ⚠️ Risk Indicators")
        ip_risk_score = st.slider("IP Risk Score", min_value=0.0, max_value=1.0, value=0.1, step=0.01)
        risk_score_internal = st.slider("Internal Risk Score", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
        corridor_risk = st.slider("Corridor Risk", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
        device_trust_score = st.slider("Device Trust Score", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        
        # Additional Information
        st.markdown("#### 📊 Additional Information")
        chargeback_history_count = st.number_input("Chargeback History Count", min_value=0, value=0, step=1)
        new_device = st.selectbox("New Device", [0, 1], index=0, format_func=lambda x: "No" if x == 0 else "Yes")
        location_mismatch = st.selectbox("Location Mismatch", [0, 1], index=0, format_func=lambda x: "No" if x == 0 else "Yes")
        
        # Time Information
        current_hour = datetime.now().hour
        hour = st.number_input("Transaction Hour (0-23)", min_value=0, max_value=23, value=current_hour, step=1)
        
        # Submit button
        submitted = st.form_submit_button("🔍 Analyze Transaction", use_container_width=True)

with col2:
    st.markdown("### 📊 Prediction Results")
    
    if submitted:
        if not user_id:
            st.error("⚠️ Please enter a User ID")
        else:
            # Prepare transaction data
            transaction_data = {
                "user_id": user_id,
                "amount_src": float(amount_src),
                "amount_usd": float(amount_usd),
                "fee": float(fee),
                "exchange_rate_src_to_dest": float(exchange_rate_src_to_dest),
                "ip_risk_score": float(ip_risk_score),
                "chargeback_history_count": int(chargeback_history_count),
                "risk_score_internal": float(risk_score_internal),
                "account_age_days": int(account_age_days),
                "device_trust_score": float(device_trust_score),
                "corridor_risk": float(corridor_risk),
                "home_country": home_country,
                "source_currency": source_currency,
                "dest_currency": dest_currency,
                "channel": channel,
                "ip_country": ip_country,
                "kyc_tier": kyc_tier,
                "new_device": int(new_device),
                "location_mismatch": int(location_mismatch),
                "hour": int(hour)
            }
            
            # Show loading
            with st.spinner("🔄 Analyzing transaction..."):
                result, error = predict_fraud(transaction_data)
            
            if error:
                st.error(f"❌ Error: {error}")
                st.info("Please check your API connection and try again.")
            else:
                # Display results
                fraud_score = result.get("fraud_score", 0)
                decision = result.get("decision", "ALLOW")
                reason_codes = result.get("reason_codes", [])
                


                # Fraud Score Gauge
                st.markdown("#### Fraud Risk Score")
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = fraud_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Risk Score"},
                    delta = {'reference': 0.5},
                    number = {'valueformat': '.3f'},
                    gauge = {
                        'axis': {'range': [None, 1]},
                        'bar': {'color': get_decision_color(decision)},
                        'steps': [
                            {'range': [0, 0.4], 'color': "lightgray"},
                            {'range': [0.4, 0.6], 'color': "yellow"},
                            {'range': [0.6, 1], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0.6
                        }
                    }
                ))
                fig.update_layout(height=230, margin={'t': 10, 'b': 0, 'l': 0, 'r': 0})
                st.plotly_chart(fig, use_container_width=True)
                
                # Decision Card
                st.markdown("#### Decision")
                decision_icon = get_decision_icon(decision)
                decision_color = get_decision_color(decision)
                
                if decision == "BLOCK":
                    st.markdown(f'<div class="decision-block">{decision_icon} {decision}</div>', unsafe_allow_html=True)
                    st.warning("⚠️ This transaction has been flagged as high risk and should be blocked.")
                elif decision == "STEP_UP":
                    st.markdown(f'<div class="decision-step">{decision_icon} {decision}</div>', unsafe_allow_html=True)
                    st.info("⚠️ Additional verification is recommended for this transaction.")
                else:
                    st.markdown(f'<div class="decision-allow">{decision_icon} {decision}</div>', unsafe_allow_html=True)
                    st.success("✅ This transaction appears to be low risk.")
                
                # Reason Codes - Display prominently right after decision (always 3 reasons)
                if decision in ["BLOCK", "STEP_UP"]:
                    st.markdown("---")
                    st.markdown("#### 🎯 Top 3 Reasons This Transaction Was Flagged")
                    if reason_codes:
                        # Display exactly 3 reasons (API ensures we always get 3)
                        for i, reason in enumerate(reason_codes[:3], 1):
                            st.markdown(f"""
                            <div style='background: rgba(255, 107, 107, 0.15); border-left: 4px solid #ff6b6b; 
                                        padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                                <strong>{i}.</strong> {reason}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Risk factors are being analyzed. Please check back shortly.")
                
                # Transaction Summary
                st.markdown("#### 📋 Transaction Summary")
                summary_data = {
                    "Field": ["User ID", "Amount (USD)", "Source Currency", "Destination Currency", 
                             "Channel", "IP Risk Score", "Device Trust Score", "Fraud Score", "Decision"],
                    "Value": [user_id, f"${amount_usd:,.2f}", source_currency, dest_currency, 
                             channel, f"{ip_risk_score:.2f}", f"{device_trust_score:.2f}", 
                             f"{fraud_score:.3f}", decision]
                }
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # Download results
                st.markdown("---")
                result_json = {
                    "timestamp": datetime.now().isoformat(),
                    "transaction": transaction_data,
                    "prediction": result
                }
                st.download_button(
                    label="📥 Download Results (JSON)",
                    data=json.dumps(result_json, indent=2),
                    file_name=f"fraud_prediction_{user_id}_{int(time.time())}.json",
                    mime="application/json"
                )
    else:
        st.info("👈 Fill out the form on the left and click 'Analyze Transaction' to get started.")
        
        # Show example transaction
        with st.expander("📖 Example Transaction Format"):
            st.json({
                "user_id": "example_user_123",
                "amount_src": 250.0,
                "amount_usd": 270.0,
                "fee": 2.5,
                "exchange_rate_src_to_dest": 1.08,
                "ip_risk_score": 0.12,
                "chargeback_history_count": 1,
                "risk_score_internal": 0.34,
                "account_age_days": 420,
                "device_trust_score": 0.5,
                "corridor_risk": 0.45,
                "home_country": "US",
                "source_currency": "USD",
                "dest_currency": "NGN",
                "channel": "WEB",
                "ip_country": "US",
                "kyc_tier": "standard",
                "new_device": 0,
                "location_mismatch": 0,
                "hour": 14
            })

# Footer
st.markdown("---")
st.markdown(
    "<div class='footer'>"
    "🛡️ Fraud Detection System | Powered by Machine Learning | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>",
    unsafe_allow_html=True
)

