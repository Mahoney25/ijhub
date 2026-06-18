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

kst = datetime.now(pytz.timezone("Asia/Seoul"))
now_str = kst.strftime("%Y.%m.%d %H:%M")

st.markdown("# IJ-HUB")
st.caption("투자 판단 인텔리전스 허브 | " + now_str + " KST | 섹터 RS 자동 계산")

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
st.caption("데이터: Yahoo Finance(15분 지연) + FRED(미연준) | 섹터 RS 자동 계산 무료")
