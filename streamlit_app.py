import streamlit as st
import yfinance as yf
from fredapi import Fred
from datetime import datetime, timedelta
import pandas as pd
import pytz
import plotly.graph_objects as go

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
.div-card {
    background: #10151f; border: 1px solid #2a3d5a;
    border-radius: 7px; padding: 12px 15px; margin-bottom: 8px;
}
.div-card.high { border-left: 3px solid #e04858; }
.div-card.mid { border-left: 3px solid #f0a030; }
.div-pair { font-family: monospace; font-size: 12px; font-weight: 700; color: #dce8f8; }
.div-desc { font-size: 12px; color: #aab8d0; margin-top: 4px; }
.div-imp { font-size: 11px; color: #f0a030; margin-top: 5px; }
.scen-box {
    background: #10151f; border: 1px solid #2a3d5a;
    border-radius: 8px; padding: 16px 18px; height: 100%;
}
.scen-box.bear { border-top: 2px solid #e04858; }
.scen-box.base { border-top: 2px solid #4a8ef0; }
.scen-box.bull { border-top: 2px solid #1ecc7a; }
.scen-label { font-family: monospace; font-size: 12px; font-weight: 700;
    letter-spacing: 0.08em; margin-bottom: 8px; }
.scen-text { font-size: 12px; color: #aab8d0; line-height: 1.7; }
.sec-row {
    display: flex; align-items: center; gap: 10px;
    padding: 6px 0; border-bottom: 1px solid #1a2236;
}
.sec-rank { font-family: monospace; font-size: 11px; color: #6a7d98; width: 22px; }
.sec-name { font-size: 12px; color: #dce8f8; flex: 1; }
.sec-pct { font-family: monospace; font-size: 12px; font-weight: 600; width: 64px; text-align: right; }
.trend-box {
    background: #10151f; border: 1px solid #2a3d5a; border-radius: 8px;
    padding: 14px 16px; margin-top: 8px;
}
.earn-row {
    display: flex; align-items: center; gap: 12px;
    padding: 9px 12px; border-bottom: 1px solid #1a2236;
}
.earn-dday { font-family: monospace; font-size: 11px; font-weight: 700;
    min-width: 52px; padding: 3px 8px; border-radius: 4px; text-align: center; }
.earn-name { font-size: 13px; color: #dce8f8; flex: 1; font-weight: 600; }
.earn-date { font-family: monospace; font-size: 11px; color: #6a7d98; }
.kr-card {
    background: #10151f; border: 1px solid #2a3d5a;
    border-radius: 8px; padding: 14px 16px;
}
.kr-flow-label { font-family: monospace; font-size: 10px; color: #6a7d98; }
.kr-flow-val { font-size: 22px; font-weight: 700; }
.stTabs [data-baseweb="tab"] { font-family: monospace; font-size: 12px; }

/* Phase 0: 카드형 버튼을 judgment-box와 동일한 치수/타이포로 맞춤 */
div[data-testid="stPopover"] > div > button {
    background: linear-gradient(135deg, #10151f, #141a26) !important;
    border: 1px solid #2a3d5a !important;
    border-left: 3px solid #6a7d98 !important;
    border-radius: 8px !important;
    padding: 18px 22px !important;
    width: 100% !important;
    text-align: left !important;
    height: auto !important;
    min-height: 0 !important;
    display: block !important;
    line-height: 1.3 !important;
}
div[data-testid="stPopover"] > div > button:hover {
    border-color: #4a8ef0 !important;
}
div[data-testid="stPopover"] > div > button:focus,
div[data-testid="stPopover"] > div > button:active {
    background: linear-gradient(135deg, #10151f, #141a26) !important;
    border-left: 3px solid #4a8ef0 !important;
}
div[data-testid="stPopover"] > div > button div[data-testid="stMarkdownContainer"] p {
    font-family: monospace !important;
    text-align: left !important;
    color: #dce8f8 !important;
    margin: 0 !important;
    white-space: normal !important;
}
/* 1줄: jb-label과 동일 (11px, 회색, uppercase 트래킹) */
div[data-testid="stPopover"] > div > button div[data-testid="stMarkdownContainer"] p:nth-of-type(1) {
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    color: #6a7d98 !important;
    text-transform: uppercase !important;
    margin-bottom: 4px !important;
}
/* 2줄: jb-value와 동일 (26px, bold) */
div[data-testid="stPopover"] > div > button div[data-testid="stMarkdownContainer"] p:nth-of-type(2) {
    font-size: 26px !important;
    font-weight: 700 !important;
    margin: 4px 0 !important;
    color: #dce8f8 !important;
}
/* 3줄: jb-sub와 동일 (13px, 옅은 회색) */
div[data-testid="stPopover"] > div > button div[data-testid="stMarkdownContainer"] p:nth-of-type(3) {
    font-size: 13px !important;
    color: #aab8d0 !important;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def get_yahoo(symbol):
    try:
        data = yf.Ticker(symbol).history(period="5d")
        if len(data) >= 2:
            now = data["Close"].iloc[-1]
            prev = data["Close"].iloc[-2]
            return now, (now - prev) / prev * 100
        return None, None
    except Exception:
        return None, None


@st.cache_data(ttl=600)
def get_yahoo_52w(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1y")
        if len(data) >= 20:
            now = data["Close"].iloc[-1]
            hi = data["Close"].max()
            lo = data["Close"].min()
            pct = (now - lo) / (hi - lo) * 100 if hi > lo else 50
            return now, pct
        return None, None
    except Exception:
        return None, None


@st.cache_data(ttl=1800)
def get_weekly_return(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1mo")
        if len(data) >= 6:
            now = data["Close"].iloc[-1]
            week_ago = data["Close"].iloc[-6]
            return (now - week_ago) / week_ago * 100
        return None
    except Exception:
        return None


@st.cache_data(ttl=300)
def get_overnight():
    futures = {
        "S&P": "ES=F", "나스닥": "NQ=F", "다우": "YM=F",
        "VIX": "^VIX", "WTI": "CL=F", "금": "GC=F", "USD/KRW": "KRW=X",
    }
    out = []
    for name, sym in futures.items():
        val, chg = get_yahoo(sym)
        if val is not None:
            out.append((name, val, chg))
    return out


@st.cache_data(ttl=1800)
def get_ohlc(symbol, interval):
    try:
        period = "2y" if interval == "1wk" else "5y"
        data = yf.Ticker(symbol).history(period=period, interval=interval)
        if len(data) >= 10:
            return data
        return None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def get_earnings_date(symbol):
    try:
        t = yf.Ticker(symbol)
        try:
            cal = t.calendar
            if isinstance(cal, dict) and cal.get("Earnings Date"):
                ed = cal["Earnings Date"]
                if isinstance(ed, list) and len(ed) > 0:
                    return ed[0]
                return ed
        except Exception:
            pass
        try:
            df = t.get_earnings_dates(limit=8)
            if df is not None and len(df) > 0:
                now = pd.Timestamp.now(tz=df.index.tz)
                future = df[df.index >= now]
                if len(future) > 0:
                    return future.index.min().date()
        except Exception:
            pass
        return None
    except Exception:
        return None


@st.cache_data(ttl=1800)
def get_korea_flow():
    result = {"mode": None}
    try:
        from pykrx import stock
        today = datetime.now()
        for back in range(0, 6):
            d = (today - timedelta(days=back)).strftime("%Y%m%d")
            try:
                df = stock.get_market_trading_value_by_investor(d, d, "KOSPI")
                if df is not None and len(df) > 0 and "외국인" in df.index and "순매수" in df.columns:
                    result["mode"] = "direct"
                    result["date"] = d
                    result["foreign"] = float(df.loc["외국인", "순매수"])
                    if "기관합계" in df.index:
                        result["inst"] = float(df.loc["기관합계", "순매수"])
                    else:
                        result["inst"] = None
                    return result
            except Exception:
                continue
    except Exception:
        pass

    result["mode"] = "indirect"
    ewy, ewy_chg = get_yahoo("EWY")
    krw, krw_chg = get_yahoo("KRW=X")
    samsung, samsung_chg = get_yahoo("005930.KS")
    result["ewy"] = (ewy, ewy_chg)
    result["krw"] = (krw, krw_chg)
    result["samsung"] = (samsung, samsung_chg)
    score = 0
    if ewy_chg is not None and ewy_chg > 0: score += 1
    if krw_chg is not None and krw_chg < 0: score += 1
    if samsung_chg is not None and samsung_chg > 0: score += 1
    result["score"] = score
    return result


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


@st.cache_data(ttl=1800)
def compute_sector_rs():
    sectors = {
        "반도체·IT": "XLK", "방산·항공": "ITA", "금융": "XLF",
        "헬스케어": "XLV", "에너지": "XLE", "필수소비": "XLP",
        "임의소비": "XLY", "산업재": "XLI", "소재": "XLB",
        "유틸리티": "XLU", "부동산": "XLRE", "커뮤니케이션": "XLC",
    }
    results = []
    for name, ticker in sectors.items():
        ret = get_weekly_return(ticker)
        if ret is not None:
            results.append((name, ticker, ret))
    results.sort(key=lambda x: x[2], reverse=True)
    return results


# === Phase 0 신규: VIX 1년 히스토리 + percentile 계산 ===
@st.cache_data(ttl=1800)
def get_vix_history_1y():
    try:
        data = yf.Ticker("^VIX").history(period="1y")
        if len(data) >= 30:
            return data["Close"]
        return None
    except Exception:
        return None


def percentile_1y(series, current):
    if series is None or current is None or len(series) == 0:
        return None
    below = (series < current).sum()
    return below / len(series) * 100


# 하위호환 별칭
def vix_percentile_1y(vix_series, current):
    return percentile_1y(vix_series, current)


def analyze_trend(data):
    close = data["Close"]
    ma_short = close.rolling(10).mean().iloc[-1]
    ma_long = close.rolling(30).mean().iloc[-1] if len(close) >= 30 else close.rolling(len(close)).mean().iloc[-1]
    now = close.iloc[-1]
    msgs = []
    if now > ma_short > ma_long:
        msgs.append(("정배열", "#1ecc7a", "현재가 > 단기MA > 장기MA — 상승 추세 견고"))
    elif now < ma_short < ma_long:
        msgs.append(("역배열", "#e04858", "현재가 < 단기MA < 장기MA — 하락 추세"))
    else:
        msgs.append(("혼조", "#f0a030", "이동평균 배열 혼재 — 방향성 불분명, 관망"))

    recent = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100 if len(close) >= 5 else 0
    if recent > 3:
        msgs.append(("모멘텀", "#1ecc7a", "최근 5봉 +" + format(recent, ".1f") + "% — 강한 상승 탄력"))
    elif recent < -3:
        msgs.append(("모멘텀", "#e04858", "최근 5봉 " + format(recent, ".1f") + "% — 하락 가속"))
    else:
        msgs.append(("모멘텀", "#6a7d98", "최근 5봉 " + format(recent, "+.1f") + "% — 횡보권"))
    return msgs


def make_chart(data, title):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data["Open"], high=data["High"],
        low=data["Low"], close=data["Close"],
        increasing_line_color="#1ecc7a", decreasing_line_color="#e04858",
        name="가격",
    )])
    close = data["Close"]
    fig.add_trace(go.Scatter(x=data.index, y=close.rolling(10).mean(),
                              line=dict(color="#4a8ef0", width=1), name="MA10"))
    fig.add_trace(go.Scatter(x=data.index, y=close.rolling(30).mean(),
                              line=dict(color="#f0a030", width=1), name="MA30"))
    fig.update_layout(
        title=title, template="plotly_dark",
        paper_bgcolor="#0a0d14", plot_bgcolor="#0a0d14",
        height=380, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_rangeslider_visible=False,
        font=dict(family="monospace", size=11, color="#aab8d0"),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    return fig


# === Phase 0/1: 범용 1년 추이 미니차트 (popover 내부용) ===
def make_mini_chart(series, current, line_color="#4a8ef0",
                     band_low=None, band_high=None, invert_bands=False):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values,
        line=dict(color=line_color, width=1.5), name="값",
        fill="tozeroy", fillcolor="rgba(74,142,240,0.08)",
    ))
    if current is not None:
        fig.add_hline(y=current, line_dash="dot", line_color="#f0a030",
                       annotation_text="현재", annotation_font_color="#f0a030")
    # band_low = 안정 기준선(보통 녹색), band_high = 경계 기준선(보통 적색)
    # invert_bands=True면 낮을수록 위험(예: 신용스프레드는 반대로 높을수록 위험이라 기본 False)
    low_color = "#e04858" if invert_bands else "#1ecc7a"
    high_color = "#1ecc7a" if invert_bands else "#e04858"
    if band_low is not None:
        fig.add_hline(y=band_low, line_dash="dash", line_color=low_color, opacity=0.4)
    if band_high is not None:
        fig.add_hline(y=band_high, line_dash="dash", line_color=high_color, opacity=0.4)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0d14", plot_bgcolor="#0a0d14",
        height=220, margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="monospace", size=10, color="#aab8d0"),
        showlegend=False,
    )
    return fig


# 하위호환 별칭
def make_vix_mini_chart(vix_series, current):
    return make_mini_chart(vix_series, current, band_low=18, band_high=25)


@st.cache_data(ttl=3600)
def get_fred_history_1y(series_id):
    try:
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        s = fred.get_series(series_id).dropna()
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=400)
        return s[s.index >= cutoff]
    except Exception:
        return None


@st.cache_data(ttl=1800)
def get_yahoo_history_1y(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1y")
        if len(data) >= 30:
            return data["Close"]
        return None
    except Exception:
        return None


@st.cache_data(ttl=1800)
def get_korea_foreign_flow_series(days=20):
    """최근 N영업일 KOSPI 외국인 순매수 추이 (pykrx 직접 데이터만 해당)"""
    try:
        from pykrx import stock
        today = datetime.now()
        start = (today - timedelta(days=days + 15)).strftime("%Y%m%d")
        end = today.strftime("%Y%m%d")
        df = stock.get_market_trading_value_by_date(start, end, "KOSPI", on="순매수")
        if df is not None and len(df) > 0 and "외국인합계" in df.columns:
            s = df["외국인합계"].tail(days)
            return s
        return None
    except Exception:
        return None


def _normalize_index(series):
    """tz-aware/naive 혼용 문제를 막기 위해 날짜만 남기고 인덱스 정규화"""
    s = series.copy()
    try:
        if s.index.tz is not None:
            s.index = s.index.tz_localize(None)
    except (AttributeError, TypeError):
        pass
    s.index = pd.to_datetime(s.index).normalize()
    return s


def compute_correlation(series_a, series_b, window=None):
    """두 시리즈를 날짜 기준 정렬 후 상관계수 계산. window 지정 시 최근 window일만 사용."""
    if series_a is None or series_b is None:
        return None
    try:
        a = _normalize_index(series_a)
        b = _normalize_index(series_b)
        df = pd.DataFrame({"a": a, "b": b}).dropna()
        if window is not None:
            df = df.tail(window)
        if len(df) < 5:
            return None
        return df["a"].corr(df["b"])
    except Exception:
        return None


# === Phase 2: Rolling Correlation 엔진 ===

def compute_rolling_correlation_series(series_a, series_b, window=60):
    """두 시리즈의 rolling correlation 시계열 자체를 반환 (상관계수가 시간에 따라 어떻게 변했는지)"""
    if series_a is None or series_b is None:
        return None
    try:
        a = _normalize_index(series_a)
        b = _normalize_index(series_b)
        df = pd.DataFrame({"a": a, "b": b}).dropna()
        if len(df) < window + 5:
            return None
        roll = df["a"].rolling(window).corr(df["b"]).dropna()
        return roll
    except Exception:
        return None


@st.cache_data(ttl=3600)
def get_fred_history_long(series_id, days=500):
    """2s10s 등 장기 window(120일) 계산에 충분한 길이의 FRED 히스토리"""
    try:
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        s = fred.get_series(series_id).dropna()
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        return s[s.index >= cutoff]
    except Exception:
        return None


@st.cache_data(ttl=1800)
def get_yahoo_history_long(symbol, days=500):
    try:
        data = yf.Ticker(symbol).history(period="2y")
        if len(data) >= 30:
            s = data["Close"]
            cutoff = pd.Timestamp.now(tz=s.index.tz) - pd.Timedelta(days=days)
            return s[s.index >= cutoff]
        return None
    except Exception:
        return None


# 5개 핵심 페어 정의: (표시명, A시리즈 로더, B시리즈 로더, 메커니즘 가설, 시황신호 해석)
def _strong_sector_etf_history():
    """현재 섹터RS 1위 ETF의 가격 히스토리 (compute_sector_rs 결과 재사용)"""
    rs = compute_sector_rs()
    if not rs:
        return None
    top_ticker = rs[0][1]
    return get_yahoo_history_long(top_ticker)


def _strong_sector_label():
    rs = compute_sector_rs()
    if not rs:
        return "강세섹터"
    return rs[0][0] + "(" + rs[0][1] + ")"


CORRELATION_PAIRS = {
    "VIX ↔ S&P500": {
        "loader_a": lambda: get_yahoo_history_long("^VIX"),
        "loader_b": lambda: get_yahoo_history_long("^GSPC"),
        "label_a": "VIX", "label_b": "S&P500",
        "expected_sign": "음(-) — 항상 반대로 움직이는 게 정상",
        "why_watch": "주가가 오를 때 공포지수가 내려가는 건 당연합니다. 이 관계가 '깨질 때'가 진짜 신호입니다.",
        "mechanism": "주가가 떨어지면 투자자들이 보험(풋옵션)을 사기 시작합니다. 그 수요가 VIX를 밀어 올립니다. 주가 하락 = VIX 상승, 이 연결고리는 시장이 존재하는 한 구조적으로 유지됩니다.",
        "signal_meaning": "📌 이렇게 읽으세요\n\n"
                           "상관이 -0.7 이상(강하게 반대): 정상 — 지금은 그냥 시장이 제대로 작동하는 겁니다.\n\n"
                           "상관이 -0.3 이하로 약해짐: 주의 — 주가가 내려가는데 VIX가 별로 안 오른다면 아직 진짜 공포가 시작 안 됐다는 뜻. 하락이 더 올 수 있습니다.\n\n"
                           "상관이 -0.9 이상으로 너무 강함: 옵션·헤지 수요가 시장을 흔드는 변동성 장세. 방향성보다 변동성 자체가 거래되고 있는 상태입니다.",
    },
    "HY스프레드 ↔ S&P500": {
        "loader_a": lambda: get_fred_history_long("BAMLH0A0HYM2"),
        "loader_b": lambda: get_yahoo_history_long("^GSPC"),
        "label_a": "HY스프레드", "label_b": "S&P500",
        "expected_sign": "음(-) — 스프레드 좁을 때 주가 높은 게 정상",
        "why_watch": "채권시장과 주식시장이 같은 방향을 보고 있는지 확인합니다. 두 시장이 서로 다른 신호를 보낼 때, 채권이 보통 먼저 맞습니다.",
        "mechanism": "HY스프레드는 '위험한 회사 채권'과 '안전한 국채' 사이의 금리 차이입니다. 스프레드가 벌어지면 투자자들이 기업 부도를 걱정한다는 뜻 → 주가도 같이 내려가는 게 정상입니다.",
        "signal_meaning": "📌 이렇게 읽으세요\n\n"
                           "상관이 정상(-0.5 이하): 주식과 채권이 같은 판단을 하고 있는 상태. 큰 이상 없음.\n\n"
                           "⚠️ 상관이 약해짐(주가는 오르는데 스프레드도 벌어짐): 가장 위험한 신호입니다. 채권시장은 '이상하다'고 경고하는데 주식시장만 올라가고 있는 상황. 역사적으로 채권이 먼저 맞는 경우가 많았습니다. 주식 비중 점검을 시작할 신호입니다.",
    },
    "섹터RS 1위 ↔ KOSPI": {
        "loader_a": _strong_sector_etf_history,
        "loader_b": lambda: get_yahoo_history_long("^KS11"),
        "label_a": "강세섹터", "label_b": "KOSPI",
        "expected_sign": "양(+) — 강세섹터가 시장 전체를 끌고 가면 정상",
        "why_watch": "지금 가장 강한 섹터 혼자만 오르는지, 아니면 시장 전체가 따라오는지를 봅니다. 혼자만 오르면 그 랠리가 오래 못 갑니다.",
        "mechanism": "강세섹터 ETF와 KOSPI가 같이 오르면 '시장 전체가 건강하게 상승'하는 것입니다. 강세섹터만 오르고 KOSPI가 제자리면 '일부 종목만 끌어올리는 좁은 장세'입니다.",
        "signal_meaning": "📌 이렇게 읽으세요\n\n"
                           "상관이 강함(+0.7 이상): 현재 강세섹터가 시장 전체를 끌고 있는 상태. 그 섹터에 올라타고 있다면 시장과 함께 가는 겁니다.\n\n"
                           "⚠️ 상관이 약해짐: 강세섹터만 혼자 오르고 시장은 안 따라오는 상태. 소수 종목 주도의 '좁은 장세'일 가능성. 그 섹터가 꺾이면 충격이 집중됩니다. 포지션 집중도를 점검하세요.",
    },
    "USD/KRW ↔ 삼성전자": {
        "loader_a": lambda: get_yahoo_history_long("KRW=X"),
        "loader_b": lambda: get_yahoo_history_long("005930.KS"),
        "label_a": "USD/KRW", "label_b": "삼성전자",
        "expected_sign": "음(-) — 원화 약세면 삼성전자 약세가 정상",
        "why_watch": "환율이 삼성전자를 어떤 방향으로 더 크게 움직이는지 파악합니다. 수급 압력이 강한지, 수출 기대가 강한지에 따라 방향이 바뀝니다.",
        "mechanism": "원화가 약해지면(달러 환율 상승) 외국인 투자자 입장에서는 한국 주식의 달러 환산 가치가 낮아집니다 → 외국인이 매도 → 삼성전자 하락. 이게 평소의 패턴입니다.",
        "signal_meaning": "📌 이렇게 읽으세요\n\n"
                           "상관이 음수로 유지(-0.4 이하): 정상 패턴. 환율이 삼성전자 주가에 영향을 주고 있는 상태.\n\n"
                           "⚠️ 상관이 깨짐(환율 오르는데 삼성전자도 오름): 외국인 수급보다 '원화 약세 = 반도체 수출 가격 경쟁력 강화' 기대가 더 크게 작동하는 상태. 삼성전자를 보는 시장의 시각이 '수급'에서 '실적 기대'로 전환되는 신호입니다.",
    },
    "VIX ↔ HY스프레드": {
        "loader_a": lambda: get_yahoo_history_long("^VIX"),
        "loader_b": lambda: get_fred_history_long("BAMLH0A0HYM2"),
        "label_a": "VIX", "label_b": "HY스프레드",
        "expected_sign": "양(+) — 둘 다 같이 오르거나 같이 내리는 게 정상",
        "why_watch": "VIX(주식시장 공포)와 HY스프레드(채권시장 공포)가 같은 방향을 가리키는지 확인합니다. 서로 엇갈릴 때 어디서 진짜 문제가 생기고 있는지 파악할 수 있습니다.",
        "mechanism": "시장에 충격이 오면 주식시장(VIX)과 채권시장(HY스프레드) 모두 동시에 반응하는 게 정상입니다. 한쪽만 반응하면 그 충격이 특정 시장에 국한된 이벤트일 가능성이 높습니다.",
        "signal_meaning": "📌 이렇게 읽으세요\n\n"
                           "둘 다 같이 움직임(상관 +0.5 이상): 거시적 리스크오프가 진행 중. 방어 포지션을 점검할 시점입니다.\n\n"
                           "VIX만 급등, HY는 잠잠: 주식시장에서만 생긴 단기 이벤트(옵션 만기, 뉴스 충격 등). 채권이 동조하지 않으면 구조적 위기일 가능성은 낮습니다. 과잉반응 확인 후 매수 검토 가능.\n\n"
                           "HY만 확대, VIX는 낮음: 특정 기업·섹터의 신용 문제. 주식시장보다 채권시장이 먼저 경고를 보내는 패턴 — 시차를 두고 주식에 영향 올 수 있습니다.",
    },
}


def correlation_strength_label(corr):
    if corr is None:
        return "데이터 부족", "#6a7d98"
    abs_c = abs(corr)
    if abs_c >= 0.7:
        return "강한 상관", "#1ecc7a" if corr > 0 else "#e04858"
    elif abs_c >= 0.4:
        return "중간 상관", "#f0a030"
    else:
        return "약한/없음", "#6a7d98"


def make_rolling_corr_chart(roll_series, window):
    fig = go.Figure()
    colors = ["#1ecc7a" if v >= 0 else "#e04858" for v in roll_series.values]
    fig.add_trace(go.Bar(x=roll_series.index, y=roll_series.values, marker_color=colors, name="상관계수"))
    fig.add_hline(y=0, line_color="#3d5070", opacity=0.6)
    fig.add_hline(y=0.7, line_dash="dash", line_color="#1ecc7a", opacity=0.3)
    fig.add_hline(y=-0.7, line_dash="dash", line_color="#e04858", opacity=0.3)
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0a0d14", plot_bgcolor="#0a0d14",
        height=200, margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="monospace", size=10, color="#aab8d0"), showlegend=False,
        yaxis=dict(range=[-1, 1]),
    )
    return fig


kst = datetime.now(pytz.timezone("Asia/Seoul"))
now_str = kst.strftime("%Y.%m.%d %H:%M")

st.markdown("# IJ-HUB")
st.caption("투자 판단 인텔리전스 허브 | " + now_str + " KST | 오늘의 결론 + 근거자료 탭 구조")

vix, vix_chg = get_yahoo("^VIX")
spx, spx_chg = get_yahoo("^GSPC")
spx_price, spx_52w = get_yahoo_52w("^GSPC")
hy, hy_chg = get_fred_latest("BAMLH0A0HYM2")
y10, _ = get_fred_latest("DGS10")
y2, _ = get_fred_latest("DGS2")
cpi = get_cpi_yoy()
sector_rs = compute_sector_rs()

if sector_rs:
    top_sectors = " · ".join([s[0] for s in sector_rs[:3]])
    strong_sector = sector_rs[0][0]
else:
    top_sectors = "데이터 수집 실패"
    strong_sector = "주요 섹터"


def judge_regime(vix, hy):
    score = 0
    reasons = []
    if vix is not None:
        if vix < 18:
            score += 1; reasons.append("VIX " + format(vix, ".1f") + " 안정")
        elif vix > 25:
            score -= 1; reasons.append("VIX " + format(vix, ".1f") + " 경계")
        else:
            reasons.append("VIX " + format(vix, ".1f") + " 중립")
    if hy is not None:
        if hy < 3.5:
            score += 1; reasons.append("신용 " + format(hy, ".2f") + "% 타이트")
        elif hy > 5.0:
            score -= 1; reasons.append("신용 " + format(hy, ".2f") + "% 확대")
        else:
            reasons.append("신용 " + format(hy, ".2f") + "% 보통")
    if score >= 2:
        return "Risk-On", "ok", " / ".join(reasons), score
    elif score <= -1:
        return "Risk-Off", "danger", " / ".join(reasons), score
    else:
        return "중립", "warn", " / ".join(reasons), score


regime, level, reason, regime_score = judge_regime(vix, hy)
if level == "ok":
    box_class, regime_color = "judgment-box", "#1ecc7a"
elif level == "warn":
    box_class, regime_color = "judgment-box warn", "#f0a030"
else:
    box_class, regime_color = "judgment-box danger", "#e04858"

spx_str = format(spx, ",.0f") if spx is not None else "-"
spx_sub = format(spx_chg, "+.2f") + "%" if spx_chg is not None else "-"
spx_col = "#1ecc7a" if (spx_chg or 0) >= 0 else "#e04858"

vix_str = format(vix, ".1f") if vix is not None else "-"
vix_sub = format(vix_chg, "+.2f") + "%" if vix_chg is not None else "-"
vix_col = "#1ecc7a" if (vix is not None and vix < 18) else "#f0a030"

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    # ============================================================
    # Phase 1: 시장국면판단 카드를 popover로 교체
    # HY스프레드 상세는 여기 안에서만 노출 (별도 메인 카드 없음)
    # ============================================================
    regime_btn_label = "시장 국면 판단\n\n" + regime + "\n\n" + reason
    with st.popover(regime_btn_label, use_container_width=True):
        st.markdown("**시장 국면 판단 — 지금 시장이 탐욕 상태인가요, 공포 상태인가요?**")
        st.caption("VIX(주식시장 공포 온도)와 HY스프레드(채권시장 기업 부도 우려)를 합산해서 판단합니다. 둘 다 낮으면 Risk-On(탐욕), 둘 다 높으면 Risk-Off(공포)입니다.")

        st.markdown("---")
        st.markdown("**① VIX 기여**")
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            st.metric("현재", vix_str, vix_sub)
        with vcol2:
            vix_score_txt = "+1 (안정)" if (vix is not None and vix < 18) else (
                "-1 (경계)" if (vix is not None and vix > 25) else "0 (중립)")
            st.metric("점수 기여", vix_score_txt)

        st.markdown("**② HY 신용스프레드 기여**")
        hy_hist = get_fred_history_1y("BAMLH0A0HYM2")
        hy_pct = percentile_1y(hy_hist, hy) if hy_hist is not None else None
        hcol1, hcol2 = st.columns(2)
        with hcol1:
            st.metric("현재", format(hy, ".2f") + "%" if hy is not None else "-",
                       format(hy_chg, "+.2f") if hy_chg is not None else None)
        with hcol2:
            hy_score_txt = "+1 (타이트)" if (hy is not None and hy < 3.5) else (
                "-1 (확대)" if (hy is not None and hy > 5.0) else "0 (보통)")
            st.metric("점수 기여", hy_score_txt)

        if hy_hist is not None:
            st.plotly_chart(
                make_mini_chart(hy_hist, hy, band_low=3.5, band_high=5.0, invert_bands=True),
                use_container_width=True
            )
            if hy_pct is not None:
                pct_msg = "낮음(기업 우려 적음)" if hy_pct < 30 else ("높음(기업 우려 큼)" if hy_pct > 70 else "중간")
                st.caption(
                    "1년 중 " + format(hy_pct, ".0f") + "%의 날보다 현재 스프레드가 넓습니다 → " + pct_msg +
                    " / 녹색선 3.5%=안심 기준 / 빨간선 5.0%=위험 기준"
                )
        else:
            st.warning("HY스프레드 데이터 로드 실패 (FRED API)")

        st.markdown("---")
        st.markdown("**종합 점수: " + str(regime_score) + "점** (-2~+2 범위, +2에 가까울수록 안전한 시장)")
        st.caption("⚠️ 한계: 이 판단은 2개 지표만 봅니다. 실제 시장은 유동성·기업 밸류에이션·정치 리스크 등 더 많은 요소로 움직입니다. 방향성 참고용으로 쓰고, 단독으로 매매 판단에 사용하지 마세요.")

with c2:
    # ============================================================
    # Phase 1: S&P500 카드를 popover로 교체
    # ============================================================
    spx_btn_label = "S&P 500\n\n" + spx_str + "\n\n" + spx_sub
    with st.popover(spx_btn_label, use_container_width=True):
        st.markdown("**S&P500 — 지금 미국 주식이 1년 중 어느 위치에 있나요?**")
        spx_hist = get_yahoo_history_1y("^GSPC")

        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.metric("현재가", spx_str, spx_sub)
        with mcol2:
            if spx_52w is not None:
                pos_msg = "고점 근처" if spx_52w > 80 else ("저점 근처" if spx_52w < 20 else "중간")
                st.metric("1년 위치", format(spx_52w, ".0f") + "% (" + pos_msg + ")")
            else:
                st.metric("1년 위치", "-")

        if spx_hist is not None:
            st.plotly_chart(make_mini_chart(spx_hist, spx), use_container_width=True)
            st.caption("1년 가격 추이 — 점선이 현재가 위치입니다")
        else:
            st.warning("1년 히스토리 로드 실패")

        st.markdown("---")
        st.caption("1년 위치(%)는 지난 1년 중 지금이 어느 높이에 있는지를 보여줍니다. 80% 이상이면 고점 근처, 20% 이하면 저점 근처입니다. 단, 고점이라도 더 오를 수 있고 저점이라도 더 내릴 수 있어 단독 판단 기준으로 쓰지 마세요.")

with c3:
    # ============================================================
    # Phase 0 핵심 변경 구간: VIX 카드를 HTML div → popover로 교체
    # ============================================================
    vix_btn_label = "VIX 변동성\n\n" + vix_str + "\n\n" + vix_sub
    with st.popover(vix_btn_label, use_container_width=True):
        st.markdown("**VIX 공포지수 — 지금 시장이 얼마나 불안해하고 있나요?**")
        st.caption("VIX는 '투자자들이 앞으로 주가가 얼마나 크게 흔들릴 것 같다고 생각하는가'를 숫자로 보여줍니다. 18 아래 → 시장이 편안한 상태 / 25 이상 → 불안과 공포 구간.")

        vix_hist = get_vix_history_1y()
        pct_1y = vix_percentile_1y(vix_hist, vix) if vix_hist is not None else None

        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.metric("현재가", vix_str, vix_sub)
        with mcol2:
            if pct_1y is not None:
                pos_msg = "매우 낮음(편안)" if pct_1y < 20 else ("매우 높음(공포)" if pct_1y > 80 else "중간")
                st.metric("1년 중 위치", format(pct_1y, ".0f") + "% (" + pos_msg + ")")
            else:
                st.metric("1년 중 위치", "-")

        if vix_hist is not None:
            st.plotly_chart(make_vix_mini_chart(vix_hist, vix), use_container_width=True)
            st.caption("녹색선 18 아래 = 편안한 구간 / 빨간선 25 위 = 공포 구간 / 점선 = 현재값")
        else:
            st.warning("1년 히스토리 로드 실패")

        st.markdown("---")
        st.caption("⚠️ 역설: VIX가 너무 낮을 때(시장이 너무 편안할 때)가 오히려 위험할 수 있습니다. 모두가 방심한 상태에서 예상치 못한 충격이 오면 반응이 더 급격합니다. 지금 낮다면 안심이 아니라 '조용한 시장이 언제까지 유지될까'를 생각해볼 시점입니다.")

st.divider()

st.subheader("🔀 발산 감지 — 지표 간 모순 자동 탐지")
divergences = []
if vix is not None and spx_52w is not None:
    if vix < 16 and spx_52w > 85:
        divergences.append(("high", "VIX 저점 ↔ 주가 고점권",
                             "VIX " + format(vix, ".1f") + " (매우 낮음) + S&P 52주 " + format(spx_52w, ".0f") + "%ile (고점 부근)",
                             "과도한 안도감 신호. 작은 악재에도 변동성 급등 가능."))
if y10 is not None and y2 is not None and spx_52w is not None:
    spread = (y10 - y2) * 100
    if spread < 0 and spx_52w > 75:
        divergences.append(("mid", "금리 역전 ↔ 주가 강세",
                             "2s10s " + format(spread, ".0f") + "bp 역전 (침체 선행) + S&P 52주 " + format(spx_52w, ".0f") + "%ile",
                             "채권시장은 침체 경고, 주식시장은 낙관. 역사적으로 채권이 먼저 맞은 경우 많음."))
if cpi is not None and hy is not None:
    if cpi > 3.0 and hy < 3.5:
        divergences.append(("mid", "인플레 잔존 ↔ 신용 안일",
                             "CPI " + format(cpi, ".1f") + "% (목표 상회) + HY스프레드 " + format(hy, ".2f") + "% (매우 타이트)",
                             "물가 부담 남았는데 신용시장은 무위험 인식. 재반등 시 스프레드 급확대 위험."))
if vix is not None and hy is not None:
    if vix < 18 and hy > 4.5:
        divergences.append(("high", "주식 평온 ↔ 신용 경고",
                             "VIX " + format(vix, ".1f") + " (낮음) + HY스프레드 " + format(hy, ".2f") + "% (확대 중)",
                             "주식은 평온한데 신용시장에 스트레스. 신용이 보통 선행 — 주의."))

if divergences:
    for sev, pair, desc, imp in divergences:
        h = ('<div class="div-card ' + sev + '">'
             '<div class="div-pair">⚠ ' + pair + '</div>'
             '<div class="div-desc">' + desc + '</div>'
             '<div class="div-imp">→ ' + imp + '</div></div>')
        st.markdown(h, unsafe_allow_html=True)
else:
    st.success("✓ 현재 주요 지표 간 모순 신호 없음 — 정렬 상태")

st.divider()

st.subheader("📋 시나리오 — Bear / Base / Bull")
div_count = len(divergences)
spread_txt = format((y10 - y2) * 100, ".0f") + "bp" if (y10 and y2) else "-"
cpi_txt = format(cpi, ".1f") + "%" if cpi else "-"
hy_txt = format(hy, ".2f") + "%" if hy else "-"

bear_text = ("현 국면 [" + regime + "]에도 발산 " + str(div_count) + "건 감지. "
             "신용스프레드(" + hy_txt + ") 확대 전환 또는 CPI(" + cpi_txt + ") 재반등 시 "
             "위험자산 동시 조정 가능. 2s10s(" + spread_txt + ") 추가 역전은 침체 우려 자극. "
             "현 강세 섹터(" + strong_sector + ")도 변동성 국면 전환 시 차익실현 압력.")
base_text = ("국면 점수 " + str(regime_score) + " 기준 현 추세 유지가 기본선. "
             "신용 건전(" + hy_txt + ") + VIX 안정 시 " + strong_sector + " 주도 지속. "
             "발산 신호는 잠재 리스크로 두되, 트리거 부재 시 급변 가능성 낮음. "
             "이벤트(CPI·FOMC) 전후 관망 권장.")
bull_text = ("신용 추가 타이트 + VIX 추가 하락 시 위험선호 강화. "
             "CPI(" + cpi_txt + ") 둔화 지속 + 금리 하락 전환 시 성장주 밸류 재평가. "
             + strong_sector + " 모멘텀 가속이 추가 상승 견인 가능. "
             "단, 현 발산 신호가 상단 제한 가능 — 과열 경계.")

sc1, sc2, sc3 = st.columns(3)
with sc1:
    h = ('<div class="scen-box bear"><div class="scen-label" style="color:#e04858">▼ BEAR</div>'
         '<div class="scen-text">' + bear_text + '</div></div>')
    st.markdown(h, unsafe_allow_html=True)
with sc2:
    h = ('<div class="scen-box base"><div class="scen-label" style="color:#4a8ef0">— BASE</div>'
         '<div class="scen-text">' + base_text + '</div></div>')
    st.markdown(h, unsafe_allow_html=True)
with sc3:
    h = ('<div class="scen-box bull"><div class="scen-label" style="color:#1ecc7a">▲ BULL</div>'
         '<div class="scen-text">' + bull_text + '</div></div>')
    st.markdown(h, unsafe_allow_html=True)
st.caption("규칙 기반 자동 생성 · 강세 섹터 실시간 반영 · Bear 우선")

st.divider()

# ============================================================
# 오늘의 리포트 — 데이터를 Claude 프롬프트로 변환 (API 비용 없음)
# ============================================================
spread_val = format((y10 - y2) * 100, ".0f") + "bp" if (y10 and y2) else "-"
cpi_val = format(cpi, ".1f") + "%" if cpi else "-"
hy_val = format(hy, ".2f") + "%" if hy else "-"
spx_val = format(spx, ",.0f") if spx else "-"
vix_val = format(vix, ".1f") if vix else "-"
top3 = " / ".join([s[0] for s in sector_rs[:3]]) if sector_rs else "-"

div_lines = "\n".join(["- ⚠️ " + p + ": " + d for _, p, d, _ in divergences]) if divergences else "- 없음 (모든 지표 정렬 상태)"

report_prompt = (
    "아래는 오늘 IJ-HUB 대시보드가 수집한 실시간 시장 데이터입니다.\n"
    "이 데이터를 바탕으로 오늘의 시황 분석 리포트를 작성해주세요.\n\n"
    "## 오늘의 핵심 지표\n"
    "- 시장 국면: " + regime + " (점수 " + str(regime_score) + "/2)\n"
    "- S&P500: " + spx_val + " (" + (format(spx_chg, "+.2f") + "%" if spx_chg else "-") + ")\n"
    "- VIX 공포지수: " + vix_val + "\n"
    "- HY 신용스프레드: " + hy_val + "\n"
    "- 2s10s 금리차: " + spread_val + "\n"
    "- CPI (전년비): " + cpi_val + "\n"
    "- 강세 섹터 Top3: " + top3 + "\n\n"
    "## 발산 감지 (경고 신호)\n"
    + div_lines + "\n\n"
    "## 분석 요청\n"
    "1. 위 데이터를 바탕으로 오늘 시장의 핵심 메시지를 1~2문장으로 요약해주세요.\n"
    "2. Bear / Base / Bull 시나리오별로 향후 1~4주 전망을 써주세요.\n"
    "3. 한국 주식 투자자 입장에서 지금 가장 주의해야 할 리스크 1가지를 콕 짚어주세요.\n"
    "4. 모든 서술은 쉬운 말로, '지금 좋아 나빠 → 왜'의 순서로 써주세요.\n\n"
    "운영지침: Bear 시나리오 먼저 / Fact·해석·의견 레이어 구분 / 면책 문구 최소화"
)

with st.expander("📝 오늘의 리포트 — claude.ai에 붙여넣기", expanded=False):
    st.caption("버튼 하나로 복사 → claude.ai 새 대화창에 붙여넣기 → 전송. 추가 비용 없음.")

    # 프롬프트를 JS에서 안전하게 쓰기 위해 이스케이프 처리
    prompt_escaped = (report_prompt
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    import streamlit.components.v1 as components
    components.html(
        """
        <div style="text-align:center; padding: 8px 0;">
          <button id="copyBtn" onclick="copyPrompt()" style="
            background: #1ecc7a;
            color: #0a0d14;
            border: none;
            border-radius: 8px;
            padding: 14px 32px;
            font-size: 15px;
            font-weight: 700;
            font-family: monospace;
            cursor: pointer;
            width: 100%;
            letter-spacing: 0.05em;
          ">📋 프롬프트 복사하기</button>
          <div id="msg" style="
            margin-top: 10px;
            font-family: monospace;
            font-size: 12px;
            color: #1ecc7a;
            display: none;
          ">✅ 복사됐습니다! claude.ai에 붙여넣으세요.</div>
        </div>
        <script>
        function copyPrompt() {
          var text = `""" + prompt_escaped + """`;
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function() {
              document.getElementById('msg').style.display = 'block';
              document.getElementById('copyBtn').textContent = '✅ 복사 완료!';
              document.getElementById('copyBtn').style.background = '#4a8ef0';
            });
          } else {
            var ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            document.getElementById('msg').style.display = 'block';
            document.getElementById('copyBtn').textContent = '✅ 복사 완료!';
            document.getElementById('copyBtn').style.background = '#4a8ef0';
          }
        }
        </script>
        """,
        height=100,
    )

st.divider()
st.caption("⬆ 오늘의 결론 (고정 영역) · 아래는 근거자료 탭")
st.divider()

maintabs = st.tabs(["🏆 섹터·수급", "📊 상관관계", "📅 실적·차트", "🌍 매크로 원자료"])

with maintabs[0]:
    st.subheader("🏆 섹터 상대강도 — 자동 계산 (주간 수익률 기준)")
    if sector_rs:
        rcol1, rcol2 = st.columns(2)
        half = (len(sector_rs) + 1) // 2
        for ci, group in enumerate([sector_rs[:half], sector_rs[half:]]):
            target = rcol1 if ci == 0 else rcol2
            with target:
                for rank, (name, ticker, ret) in enumerate(group, start=(1 if ci == 0 else half + 1)):
                    color = "#1ecc7a" if ret > 0 else "#e04858"
                    h = ('<div class="sec-row">'
                         '<span class="sec-rank">' + format(rank, "02d") + '</span>'
                         '<span class="sec-name">' + name + ' (' + ticker + ')</span>'
                         '<span class="sec-pct" style="color:' + color + '">' + format(ret, "+.2f") + '%</span>'
                         '</div>')
                    st.markdown(h, unsafe_allow_html=True)
        st.caption("강세 Top3: " + top_sectors + " | 11개 섹터 ETF 주간 비교")
    else:
        st.warning("섹터 데이터 수집 실패 — 잠시 후 새로고침")
    
    st.divider()

    st.subheader("🇰🇷 한국 수급 — 외국인 동향")
    kr = get_korea_flow()
    
    # 삼성전자 1년 가격 시리즈 (상관관계 계산용, 두 모드 공통 사용)
    samsung_hist = get_yahoo_history_1y("005930.KS")
    
    if kr["mode"] == "direct":
        f = kr["foreign"]
        f_eok = f / 1e8
        fcol = "#1ecc7a" if f >= 0 else "#e04858"
        kc1, kc2 = st.columns(2)
        with kc1:
            # ============================================================
            # Phase 1: 외국인 순매수 카드를 popover로 교체
            # ============================================================
            flow_btn_label = "외국인 순매수 (KOSPI, " + kr["date"] + ")\n\n" + format(f_eok, "+,.0f") + " 억원"
            with st.popover(flow_btn_label, use_container_width=True):
                st.markdown("**외국인이 오늘 한국 주식을 사고 있나요, 팔고 있나요?**")
                st.caption("외국인은 KOSPI 시가총액의 약 30%를 보유하고 있어, 외국인이 사면 주가가 오르고 팔면 내리는 경향이 강합니다. 특히 삼성전자 비중이 크기 때문에 외국인 매수·매도는 삼성전자 주가와 밀접하게 움직입니다.")

                flow_series = get_korea_foreign_flow_series(20)
                if flow_series is not None and samsung_hist is not None:
                    corr = compute_correlation(flow_series, samsung_hist, window=20)
                else:
                    corr = None

                if corr is not None:
                    corr_msg = "외국인 수급과 삼성전자가 강하게 연동" if abs(corr) > 0.5 else "수급 외 다른 요인이 삼성전자에 영향 중"
                    st.metric("수급↔삼성전자 연동도 (20일)", format(corr, "+.2f") + " (" + corr_msg + ")")
                else:
                    st.metric("수급↔삼성전자 연동도", "-")
                    st.caption("데이터 부족")

                if flow_series is not None:
                    fig = go.Figure()
                    colors = ["#1ecc7a" if v >= 0 else "#e04858" for v in flow_series.values]
                    fig.add_trace(go.Bar(x=flow_series.index, y=flow_series.values / 1e8,
                                          marker_color=colors, name="외국인 순매수(억원)"))
                    fig.update_layout(
                        template="plotly_dark", paper_bgcolor="#0a0d14", plot_bgcolor="#0a0d14",
                        height=200, margin=dict(l=10, r=10, t=10, b=10),
                        font=dict(family="monospace", size=10, color="#aab8d0"), showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("초록 막대 = 외국인 순매수(사는 날) / 빨간 막대 = 외국인 순매도(파는 날) · 최근 20영업일")
                else:
                    st.warning("외국인 순매수 추이 로드 실패")

                st.markdown("---")
                st.caption("⚠️ 주의: 하루 이틀의 외국인 매도만으로 추세를 판단하지 마세요. 누적 방향(10~20일 합산)이 중요합니다. 연동도 수치가 낮아질 때는 외국인 수급보다 다른 요인(실적 기대, 테마)이 삼성전자를 움직이고 있다는 신호입니다.")
            st.caption("KRX 직접 데이터 (pykrx) · 최근 영업일 기준")
        with kc2:
            if kr.get("inst") is not None:
                i_eok = kr["inst"] / 1e8
                icol = "#1ecc7a" if kr["inst"] >= 0 else "#e04858"
                h = ('<div class="kr-card"><div class="kr-flow-label">기관 순매수 (KOSPI)</div>'
                     '<div class="kr-flow-val" style="color:' + icol + '">' + format(i_eok, "+,.0f") + ' 억원</div></div>')
                st.markdown(h, unsafe_allow_html=True)
    else:
        score = kr.get("score", 0)
        if score >= 2:
            verdict, vcol = "외국인 유입 우호", "#1ecc7a"
        elif score == 1:
            verdict, vcol = "중립", "#f0a030"
        else:
            verdict, vcol = "외국인 이탈 압력", "#e04858"

        flow_btn_label = "외국인 수급 환경 (간접 추정)\n\n" + verdict
        with st.popover(flow_btn_label, use_container_width=True):
            st.markdown("**KRX 직접 데이터가 안 잡힐 때 — 3가지 신호로 간접 추정합니다**")
            st.caption("EWY(해외에서 한국 주식 담는 ETF), USD/KRW 환율, 삼성전자 주가 방향을 합산해서 '외국인이 사고 있는지 팔고 있는지'를 추정합니다. 정확도는 KRX 직접 데이터보다 낮습니다.")

            ewy_hist = get_yahoo_history_1y("EWY")
            if ewy_hist is not None and samsung_hist is not None:
                corr_ewy_sam = compute_correlation(ewy_hist, samsung_hist, window=60)
            else:
                corr_ewy_sam = None

            if corr_ewy_sam is not None:
                st.metric("EWY ↔ 삼성전자 60일 연동도", format(corr_ewy_sam, "+.2f"))
            else:
                st.metric("EWY ↔ 삼성전자 60일 연동도", "-")

            st.markdown("---")
            st.caption("EWY 안에 삼성전자 비중이 제일 크기 때문에 둘은 거의 항상 같이 움직입니다. 이 수치가 갑자기 낮아지면 삼성전자에 개별적인 이슈가 생긴 것으로 봐도 됩니다.")
        kc1, kc2, kc3 = st.columns(3)
        ewy, ewy_chg = kr["ewy"]
        krw, krw_chg = kr["krw"]
        sam, sam_chg = kr["samsung"]
        kc1.metric("EWY (한국ETF)", format(ewy, ".2f") if ewy else "-", format(ewy_chg, "+.2f") + "%" if ewy_chg is not None else "-")
        kc2.metric("USD/KRW", format(krw, ",.0f") if krw else "-", format(krw_chg, "+.2f") + "%" if krw_chg is not None else "-")
        kc3.metric("삼성전자", format(sam, ",.0f") if sam else "-", format(sam_chg, "+.2f") + "%" if sam_chg is not None else "-")
        st.caption("KRX 직접 연결 실패 → 간접 추정 (EWY+환율+삼성전자) · 원화강세=외국인 유입 우호")

with maintabs[1]:
    st.subheader("📊 상관관계 모니터 — 두 지표가 평소처럼 움직이고 있나요?")
    st.caption("평소에 같이 움직이던 두 지표가 갑자기 반대로 움직이기 시작하면 — 그게 경고 신호입니다. 이 섹션은 그 '패턴이 깨지는 순간'을 포착하기 위해 존재합니다.")
    window_choice = st.radio("분석 기간", ["60일", "90일", "120일"], index=1, horizontal=True, key="corr_window")
    corr_window = {"60일": 60, "90일": 90, "120일": 120}[window_choice]
    
    ccol1, ccol2 = st.columns(2)
    pair_items = list(CORRELATION_PAIRS.items())
    half = (len(pair_items) + 1) // 2
    
    for ci, group in enumerate([pair_items[:half], pair_items[half:]]):
        target = ccol1 if ci == 0 else ccol2
        with target:
            for pair_name, meta in group:
                series_a = meta["loader_a"]()
                series_b = meta["loader_b"]()
                corr = compute_correlation(series_a, series_b, window=corr_window)
                label, color = correlation_strength_label(corr)
                corr_str = format(corr, "+.2f") if corr is not None else "-"
    
                btn_label = pair_name + "\n\n" + corr_str + "\n\n" + label
                with st.popover(btn_label, use_container_width=True):
                    title_extra = ""
                    if pair_name == "섹터RS 1위 ↔ KOSPI":
                        title_extra = " (현재 1위: " + _strong_sector_label() + ")"
                    st.markdown("**" + pair_name + title_extra + " — " + window_choice + " 상관관계 상세**")
    
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric(window_choice + " 상관계수", corr_str)
                    with mcol2:
                        st.metric("기대 방향성", meta["expected_sign"])
    
                    roll = compute_rolling_correlation_series(series_a, series_b, window=corr_window)
                    if roll is not None and len(roll) > 0:
                        st.plotly_chart(make_rolling_corr_chart(roll, corr_window), use_container_width=True)
                        roll_now = roll.iloc[-1]
                        roll_avg = roll.mean()
                        deviation = roll_now - roll_avg
                        if abs(deviation) >= 0.2:
                            dev_msg = "⚠️ 평균 대비 " + format(deviation, "+.2f") + " — 평소와 다른 패턴입니다"
                        else:
                            dev_msg = "평균 대비 " + format(deviation, "+.2f") + " — 정상 범위"
                        st.caption("현재값 " + format(roll_now, "+.2f") + " / 기간 평균 " + format(roll_avg, "+.2f") + " / " + dev_msg)
                    else:
                        st.warning("데이터가 충분하지 않아 추이 차트를 그릴 수 없습니다.")

                    st.markdown("---")
                    st.markdown("**🔍 왜 이 두 지표를 같이 보나요?**")
                    st.caption(meta["why_watch"])
                    st.markdown("**⚙️ 작동 원리**")
                    st.caption(meta["mechanism"])
                    st.markdown("**" + meta["signal_meaning"].split("\n")[0] + "**")
                    st.caption("\n".join(meta["signal_meaning"].split("\n")[1:]).strip())
    
    st.caption("5개 핵심 페어 · window 변경 시 전체 재계산 · 상관계수는 인과관계를 증명하지 않음")

with maintabs[2]:
    st.subheader("📅 실적 캘린더 — 주요 종목 다음 발표일")
    earnings_targets = {
        "NVIDIA": "NVDA", "Microsoft": "MSFT", "Apple": "AAPL",
        "Alphabet": "GOOGL", "Amazon": "AMZN", "Meta": "META",
        "AMD": "AMD", "Broadcom": "AVGO", "TSMC": "TSM",
        "삼성전자": "005930.KS", "SK하이닉스": "000660.KS",
    }
    earn_list = []
    today = datetime.now().date()
    for name, sym in earnings_targets.items():
        ed = get_earnings_date(sym)
        if ed is not None:
            try:
                if hasattr(ed, "date"):
                    ed = ed.date()
                dday = (ed - today).days
                if dday >= 0:
                    earn_list.append((name, sym, ed, dday))
            except Exception:
                pass
    
    if earn_list:
        earn_list.sort(key=lambda x: x[3])
        ecol1, ecol2 = st.columns(2)
        half = (len(earn_list) + 1) // 2
        for ci, group in enumerate([earn_list[:half], earn_list[half:]]):
            target = ecol1 if ci == 0 else ecol2
            with target:
                for name, sym, ed, dday in group:
                    if dday <= 3:
                        dcolor = "#e04858"; dbg = "rgba(224,72,88,0.12)"
                    elif dday <= 10:
                        dcolor = "#f0a030"; dbg = "rgba(240,160,48,0.12)"
                    else:
                        dcolor = "#4a8ef0"; dbg = "rgba(74,142,240,0.10)"
                    h = ('<div class="earn-row">'
                         '<span class="earn-dday" style="color:' + dcolor + ';background:' + dbg + ';">D-' + str(dday) + '</span>'
                         '<span class="earn-name">' + name + ' (' + sym + ')</span>'
                         '<span class="earn-date">' + str(ed) + '</span>'
                         '</div>')
                    st.markdown(h, unsafe_allow_html=True)
        st.caption("Yahoo Finance 추정 발표일 · 변경될 수 있음 · D-3 이내 빨강 강조")
    else:
        st.warning("실적 발표일 수집 실패 — 잠시 후 새로고침")
    
    st.divider()

    st.subheader("📈 차트 — 주봉 / 월봉 + 추세 해석")
    chart_targets = {
        "S&P 500": "^GSPC", "나스닥": "^IXIC", "KOSPI": "^KS11",
        "반도체 ETF (SOXX)": "SOXX", "NVIDIA": "NVDA", "삼성전자": "005930.KS",
    }
    ccol1, ccol2 = st.columns([1, 1])
    with ccol1:
        sel_name = st.selectbox("종목 선택", list(chart_targets.keys()))
    with ccol2:
        tf = st.radio("기간", ["주봉", "월봉"], horizontal=True)
    
    interval = "1wk" if tf == "주봉" else "1mo"
    ohlc = get_ohlc(chart_targets[sel_name], interval)
    if ohlc is not None:
        st.plotly_chart(make_chart(ohlc, sel_name + " (" + tf + ")"), use_container_width=True)
        trend_msgs = analyze_trend(ohlc)
        th = '<div class="trend-box"><div style="font-family:monospace;font-size:11px;color:#6a7d98;margin-bottom:8px;">🔍 추세 해석 (' + tf + ' 기준)</div>'
        for label, color, desc in trend_msgs:
            th += ('<div style="margin-bottom:6px;">'
                   '<span style="font-family:monospace;font-size:11px;font-weight:600;color:' + color + ';">[' + label + ']</span> '
                   '<span style="font-size:12px;color:#aab8d0;">' + desc + '</span></div>')
        th += '</div>'
        st.markdown(th, unsafe_allow_html=True)
    else:
        st.warning("차트 데이터 수집 실패 — 다른 종목 선택 또는 잠시 후 재시도")

with maintabs[3]:
    overnight = get_overnight()
    if overnight:
        strip = '<div style="background:#090c13;border:1px solid #1a2236;border-radius:6px;padding:8px 12px;margin-bottom:12px;display:flex;flex-wrap:wrap;gap:14px;align-items:center;">'
        strip += '<span style="font-family:monospace;font-size:10px;color:#3d5070;font-weight:600;">🌙 야간선물</span>'
        for name, val, chg in overnight:
            col = "#1ecc7a" if (chg or 0) >= 0 else "#e04858"
            arrow = "▲" if (chg or 0) >= 0 else "▼"
            strip += ('<span style="font-family:monospace;font-size:11px;">'
                      '<span style="color:#6a7d98;">' + name + '</span> '
                      '<span style="color:#dce8f8;font-weight:600;">' + format(val, ",.1f") + '</span> '
                      '<span style="color:' + col + ';">' + arrow + format(abs(chg), ".2f") + '%</span>'
                      '</span>')
        strip += '</div>'
        st.markdown(strip, unsafe_allow_html=True)
    else:
        st.caption("야간선물 데이터 수집 실패")

    subtab1, subtab2, subtab3 = st.tabs(["📈 시장", "🌍 매크로", "💱 환율-원자재"])

    with subtab1:
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
    with subtab2:
        st.subheader("매크로 / 금리 / 신용")
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
    
        if y10 is not None and y2 is not None:
            spread = (y10 - y2) * 100
            st.divider()
            if spread < 0:
                st.warning("2s10s 금리차 " + format(spread, ".0f") + "bp - 역전 (침체 선행 신호)")
            else:
                st.info("2s10s 금리차 " + format(spread, ".0f") + "bp - 정상")
    with subtab3:
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
st.caption("데이터: Yahoo + FRED + KRX(pykrx) | 한국수급 직접/간접 자동전환")
