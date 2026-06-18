import streamlit as st
import yfinance as yf
from fredapi import Fred
from datetime import datetime
import pytz

st.set_page_config(page_title="IJ·HUB", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .stApp { background-color: #0a0d14; }
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    h1, h2, h3 { color: #dce8f8 !important; font-family: monospace; }
    [data-testid="stMetricValue"] { font-family: monospace; font-size: 1.3rem; }
    [data-testid="stMetricLabel"] { font-family: monospace; color: #6a7d98 !important; }
    .judgment-box {
        background: linear-gradient(135deg, #10151f, #141a26);
        border: 1px solid #2a3d5a; border-left: 3px solid #1ecc7a;
        border-radius: 8px; padding: 18px 22px; margin-bottom: 8px;
    }
    .judgment-box.warn { border-left-color: #f0a030; }
    .judgment-box.danger { border-left-color: #e04858; }
    .jb-label { font-family: monospace; font-size: 11px; letter-spacing: 0.1em;
        text-transform: uppercase; color: #6a7d98; }
    .jb-value { font-size: 26px; font-weight: 700; margin: 4px 0; }
    .jb-sub { font-size: 13px; color: #aab8d0; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { font-family: monospace; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def get_yahoo(symbol):
    try:
        data = yf.Ticker(symbol).history(period="2d")
        if len(data) >= 2:
            now = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            return now, (now - prev) / prev * 100
        return None, None
    except Exception:
        return None, None

@st.cache_data(ttl=3600)
def get_fred_latest(series_id):
    try:
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        s = fred.get_series(series_id).dropna()
        return s.iloc[-1], s.iloc[-1] - s.iloc[-2]
    except Exception:
        return None, None

@st.cache_data(ttl=3600)
def get_cpi_yoy():
    try:
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        s = fred.get_series("CPIAUCSL").dropna()
        return (s.iloc[-1] / s.iloc[-13] - 1) * 100
    except Exception:
        return None

kst = datetime.now(pytz.timezone("Asia/Seoul"))
st.markdown("# IJ·HUB")
st.caption("투자 판단 인텔리전스 허브 · {kst.strftime('%Y.%m.%d %H:%M')}
