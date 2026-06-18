import streamlit as st
import yfinance as yf
from fredapi import Fred
from datetime import datetime
import pytz

st.set_page_config(page_title="IJ-HUB", layout="wide", page_icon="📊")

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
now_str = kst.strftime("%Y.%m.%d %H:%M")

st.markdown("# IJ-HUB")
st.caption("투자 판단 인텔리전스 허브 | " + now_str + " KST | Yahoo + FRED")

vix, vix_chg = get_yahoo("^VIX")
spx, spx_chg = get_yahoo("^GSPC")
hy, hy_chg = get_fred_latest("BAMLH0A0HYM2")

def judge_regime(vix, hy):
    score = 0
    reasons = []
    if vix is not None:
        if vix < 18:
            score += 1
            reasons.append("VIX " + format(vix, ".1f") + " 안정")
        elif vix > 25:
            score -= 1
            reasons.append("VIX " + format(vix, ".1f") + " 경계")
        else:
            reasons.append("VIX " + format(vix, ".1f") + " 중립")
    if hy is not None:
        if hy < 3.5:
            score += 1
            reasons.append("신용스프레드 " + format(hy, ".2f") + "% 타이트")
        elif hy > 5.0:
            score -= 1
            reasons.append("신용스프레드 " + format(hy, ".2f") + "% 확대")
        else:
            reasons.append("신용스프레드 " + format(hy, ".2f") + "% 보통")
    if score >= 2:
        return "Risk-On", "ok", " / ".join(reasons)
    elif score <= -1:
        return "Risk-Off", "danger", " / ".join(reasons)
    else:
        return "중립", "warn", " / ".join(reasons)

regime, level, reason = judge_regime(vix, hy)

if level == "ok":
    box_class = "judgment-box"
    regime_color = "#1ecc7a"
elif level == "warn":
    box_class = "judgment-box warn"
    regime_color = "#f0a030"
else:
    box_class = "judgment-box danger"
    regime_color = "#e04858"

spx_str = format(spx, ",.0f") if spx is not None else "-"
spx_sub = format(spx_chg, "+.2f") + "%" if spx_chg is not None else "-"
spx_col = "#1ecc7a" if (spx_chg or 0) >= 0 else "#e04858"
vix_str = format(vix, ".1f") if vix is not None else "-"
vix_sub = format(vix_chg, "+.2f") + "%" if vix_chg is not None else "-"
vix_col = "#1ecc7a" if (vix is not None and vix < 18) else "#f0a030"

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    html1 = (
        '<div class="' + box_class + '">'
        '<div class="jb-label">시장 국면 판단</div>'
        '<div class="jb-value" style="color:' + regime_color + '">' + regime + '</div>'
        '<div class="jb-sub">' + reason + '</div>'
        '</div>'
    )
    st.markdown(html1, unsafe_allow_html=True)
with c2:
    html2 = (
        '<div class="judgment-box">'
        '<div class="jb-label">S&P 500</div>'
        '<div class="jb-value" style="color:' + spx_col + '">' + spx_str + '</div>'
        '<div class="jb-sub">' + spx_sub + '</div>'
        '</div>'
    )
    st.markdown(html2, unsafe_allow_html=True)
with c3:
    html3 = (
        '<div class="judgment-box">'
        '<div class="jb-label">VIX 변동성</div>'
        '<div class="jb-value" style="color:' + vix_col + '">' + vix_str + '</div>'
        '<div class="jb-sub">' + vix_sub + '</div>'
        '</div>'
    )
    st.markdown(html3, unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["📈 시장", "🌍 매크로", "💱 환율-원자재"])

with tab1:
    st.subheader("주요 지수 / 선물")
    market = {
        "S&P 500": "^GSPC", "나스닥": "^IXIC", "다우": "^DJI",
        "KOSPI": "^KS11", "니케이": "^N225", "S&P 선물": "ES=F",
        "나스닥 선물": "NQ=F", "VIX": "^VIX", "러셀2000": "^RUT",
    }
    cols = st.columns(3)
    for i, (name, sym) in enumerate(market.items()):
        val, chg = get_yahoo(sym)
        if val is not None:
            cols[i % 3].metric(name, format(val, ",.2f"), format(chg, "+.2f") + "%")
        else:
            cols[i % 3].metric(name, "-")

with tab2:
    st.subheader("매크로 / 금리 / 신용")
    cpi = get_cpi_yoy()
    macro = {
        "10년물 금리": "DGS10", "2년물 금리": "DGS2",
        "실업률": "UNRATE", "HY 신용스프레드": "BAMLH0A0HYM2",
        "IG 신용스프레드": "BAMLC0A0CM", "기준금리": "DFEDTARU",
    }
    cols = st.columns(3)
    cols[0].metric("CPI 전년비", format(cpi, ".2f") + "%" if cpi is not None else "-")
    idx = 1
    for name, sid in macro.items():
        val, chg = get_fred_latest(sid)
        if val is not None:
            cols[idx % 3].metric(name, format(val, ".2f"), format(chg, "+.2f"))
        else:
            cols[idx % 3].metric(name, "-")
        idx += 1
    y10, _ = get_fred_latest("DGS10")
    y2, _ = get_fred_latest("DGS2")
    if y10 is not None and y2 is not None:
        spread = (y10 - y2) * 100
        st.divider()
        if spread < 0:
            st.warning("2s10s 금리차 " + format(spread, ".0f") + "bp - 역전 (침체 선행 신호)")
        else:
            st.info("2s10s 금리차 " + format(spread, ".0f") + "bp - 정상")

with tab3:
    st.subheader("환율 / 원자재")
    fx = {
        "USD/KRW": "KRW=X", "USD/JPY": "JPY=X", "USD/CNY": "CNY=X",
        "EUR/USD": "EURUSD=X", "달러인덱스": "DX-Y.NYB", "WTI 원유": "CL=F",
        "브렌트유": "BZ=F", "금": "GC=F", "은": "SI=F",
    }
    cols = st.columns(3)
    for i, (name, sym) in enumerate(fx.items()):
        val, chg = get_yahoo(sym)
        if val is not None:
            cols[i % 3].metric(name, format(val, ",.2f"), format(chg, "+.2f") + "%")
        else:
            cols[i % 3].metric(name, "-")

st.divider()
st.caption("데이터: Yahoo Finance(15분 지연) + FRED(미연준) | 캐시 10분~1시간")
