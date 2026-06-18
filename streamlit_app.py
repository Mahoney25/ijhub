import streamlit as st
import yfinance as yf
from fredapi import Fred

st.set_page_config(page_title="IJ·HUB", layout="wide")

st.title("IJ·HUB — 시장 + 매크로 통합")
st.caption("Yahoo Finance + FRED 실시간 연동")

# ─── 비밀 금고에서 FRED 키 꺼내기 ───
fred = Fred(api_key=st.secrets["FRED_API_KEY"])

# ═══ 1. 시장 데이터 (Yahoo) ═══
st.header("📈 시장 지표")

tickers = {
    "S&P 500": "^GSPC",
    "나스닥": "^IXIC",
    "KOSPI": "^KS11",
    "USD/KRW": "KRW=X",
    "S&P 선물": "ES=F",
    "VIX": "^VIX",
    "WTI 원유": "CL=F",
    "금": "GC=F",
    "USD/JPY": "JPY=X",
}

cols = st.columns(3)
for i, (name, symbol) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(symbol).history(period="2d")
        if len(data) >= 2:
            now = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            change = (now - prev) / prev * 100
            cols[i % 3].metric(name, f"{now:,.2f}", f"{change:+.2f}%")
        else:
            cols[i % 3].metric(name, "데이터 없음")
    except Exception:
        cols[i % 3].metric(name, "실패")

st.divider()

# ═══ 2. 매크로 데이터 (FRED) ═══
st.header("🌍 매크로 지표")

# FRED 시리즈 ID 정의
fred_series = {
    "CPI (전년비)": "CPIAUCSL",
    "10년물 금리": "DGS10",
    "2년물 금리": "DGS2",
    "실업률": "UNRATE",
    "HY 신용스프레드": "BAMLH0A0HYM2",
    "연준 기준금리": "DFEDTARU",
}

mcols = st.columns(3)
for i, (name, series_id) in enumerate(fred_series.items()):
    try:
        s = fred.get_series(series_id).dropna()
        latest = s.iloc[-1]
        prev = s.iloc[-2]
        change = latest - prev

        # CPI는 전년비로 변환
        if series_id == "CPIAUCSL":
            yoy = (s.iloc[-1] / s.iloc[-13] - 1) * 100
            mcols[i % 3].metric(name, f"{yoy:.2f}%")
        else:
            mcols[i % 3].metric(name, f"{latest:.2f}", f"{change:+.2f}")
    except Exception:
        mcols[i % 3].metric(name, "실패")

st.divider()
st.caption("데이터: Yahoo Finance + FRED(미연준) · 새로고침 시 갱신")
