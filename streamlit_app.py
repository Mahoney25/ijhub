import streamlit as st
import yfinance as yf

st.set_page_config(page_title="IJ·HUB", layout="wide")

st.title("IJ·HUB — 실시간 시장 데이터")
st.caption("Yahoo Finance 실시간 연동 (15분 지연)")

# 가져올 종목 정의
tickers = {
    "S&P 500": "^GSPC",
    "나스닥": "^IXIC",
    "KOSPI": "^KS11",
    "USD/KRW": "KRW=X",
    "S&P 선물 (ES)": "ES=F",
    "나스닥 선물 (NQ)": "NQ=F",
    "VIX": "^VIX",
    "WTI 원유": "CL=F",
    "금": "GC=F",
}

st.subheader("주요 지표")

# 한 줄에 3개씩 표시
cols = st.columns(3)

for i, (name, symbol) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(symbol).history(period="2d")
        if len(data) >= 2:
            now = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            change = (now - prev) / prev * 100
            cols[i % 3].metric(
                label=name,
                value=f"{now:,.2f}",
                delta=f"{change:+.2f}%"
            )
        else:
            cols[i % 3].metric(label=name, value="데이터 없음")
    except Exception as e:
        cols[i % 3].metric(label=name, value="불러오기 실패")

st.divider()
st.caption("데이터 출처: Yahoo Finance · 새로고침하면 최신값으로 갱신됩니다")
