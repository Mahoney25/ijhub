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

kst = datetime.now(pytz.timezone("Asia/Seoul"))
now_str = kst.strftime("%Y.%m.%d %H:%M")

st.markdown("# IJ-HUB")
st.caption("투자 판단 인텔리전스 허브 | " + now_str + " KST | 한국수급+실적+차트")

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
    h = ('<div class="' + box_class + '"><div class="jb-label">시장 국면 판단</div>'
         '<div class="jb-value" style="color:' + regime_color + '">' + regime + '</div>'
         '<div class="jb-sub">' + reason + '</div></div>')
    st.markdown(h, unsafe_allow_html=True)
with c2:
    h = ('<div class="judgment-box"><div class="jb-label">S&P 500</div>'
         '<div class="jb-value" style="color:' + spx_col + '">' + spx_str + '</div>'
         '<div class="jb-sub">' + spx_sub + '</div></div>')
    st.markdown(h, unsafe_allow_html=True)
with c3:
    h = ('<div class="judgment-box"><div class="jb-label">VIX 변동성</div>'
         '<div class="jb-value" style="color:' + vix_col + '">' + vix_str + '</div>'
         '<div class="jb-sub">' + vix_sub + '</div></div>')
    st.markdown(h, unsafe_allow_html=True)

st.divider()

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
if kr["mode"] == "direct":
    f = kr["foreign"]
    f_eok = f / 1e8
    fcol = "#1ecc7a" if f >= 0 else "#e04858"
    kc1, kc2 = st.columns(2)
    with kc1:
        h = ('<div class="kr-card"><div class="kr-flow-label">외국인 순매수 (KOSPI, ' + kr["date"] + ')</div>'
             '<div class="kr-flow-val" style="color:' + fcol + '">' + format(f_eok, "+,.0f") + ' 억원</div></div>')
        st.markdown(h, unsafe_allow_html=True)
    with kc2:
        if kr.get("inst") is not None:
            i_eok = kr["inst"] / 1e8
            icol = "#1ecc7a" if kr["inst"] >= 0 else "#e04858"
            h = ('<div class="kr-card"><div class="kr-flow-label">기관 순매수 (KOSPI)</div>'
                 '<div class="kr-flow-val" style="color:' + icol + '">' + format(i_eok, "+,.0f") + ' 억원</div></div>')
            st.markdown(h, unsafe_allow_html=True)
    st.caption("KRX 직접 데이터 (pykrx) · 최근 영업일 기준")
else:
    score = kr.get("score", 0)
    if score >= 2:
        verdict, vcol = "외국인 유입 우호", "#1ecc7a"
    elif score == 1:
        verdict, vcol = "중립", "#f0a030"
    else:
        verdict, vcol = "외국인 이탈 압력", "#e04858"
    h = ('<div class="kr-card"><div class="kr-flow-label">외국인 수급 환경 (간접 추정)</div>'
         '<div class="kr-flow-val" style="color:' + vcol + '">' + verdict + '</div></div>')
    st.markdown(h, unsafe_allow_html=True)
    kc1, kc2, kc3 = st.columns(3)
    ewy, ewy_chg = kr["ewy"]
    krw, krw_chg = kr["krw"]
    sam, sam_chg = kr["samsung"]
    kc1.metric("EWY (한국ETF)", format(ewy, ".2f") if ewy else "-", format(ewy_chg, "+.2f") + "%" if ewy_chg is not None else "-")
    kc2.metric("USD/KRW", format(krw, ",.0f") if krw else "-", format(krw_chg, "+.2f") + "%" if krw_chg is not None else "-")
    kc3.metric("삼성전자", format(sam, ",.0f") if sam else "-", format(sam_chg, "+.2f") + "%" if sam_chg is not None else "-")
    st.caption("KRX 직접 연결 실패 → 간접 추정 (EWY+환율+삼성전자) · 원화강세=유입 우호")

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
st.caption("데이터: Yahoo + FRED + KRX(pykrx) | 한국수급 직접/간접 자동전환")
