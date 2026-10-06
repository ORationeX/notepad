"""시리즈, 바구니, 가중치. 외부 프로젝트 경로를 참조하지 않는다."""

from __future__ import annotations

from pathlib import Path

from src.glossary import REGIME_KO, STANCE_KO

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
EVENTS_PATH = DATA_DIR / "events.json"

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
FRED_HEADERS = {"User-Agent": "wall-street-intent/1.0"}

FRED_SERIES = {
    "DGS2": "2년물",
    "DGS10": "10년물",
    "T10Y2Y": "장단기차",
    "DFII10": "10년 실질금리",
    "BAMLH0A0HYM2": "하이일드 OAS",
    "DTWEXBGS": "광의달러",
    "VIXCLS": "VIX",
    "ICSA": "주간실업수당",
    "CPIAUCSL": "CPI",
    "T10YIE": "10년 기대인플레",
}

YAHOO_DAILY = {
    "SPY": "대형주식",
    "QQQ": "나스닥",
    "IWM": "중소형",
    "RSP": "동일가중",
    "TLT": "장기국채",
    "IEF": "중기국채",
    "HYG": "하이일드",
    "LQD": "투자등급",
    "GLD": "금",
    "UUP": "달러",
    "BIL": "초단기",
    "SHY": "단기국채",
    "XLK": "기술",
    "XLU": "유틸리티",
    "XLP": "필수소비",
    "XLF": "금융",
}

YAHOO_INDEX = {
    "^VIX": "VIX",
    "^TNX": "TNX",
    "^FVX": "FVX",
}

LIVE_TICKERS = [
    "SPY",
    "QQQ",
    "IWM",
    "RSP",
    "TLT",
    "IEF",
    "HYG",
    "LQD",
    "GLD",
    "UUP",
    "BIL",
    "XLK",
    "XLU",
    "XLP",
    "XLF",
    "^VIX",
    "^TNX",
]

LIVE_RENAME = {"^VIX": "VIX", "^TNX": "TNX"}

# 레짐 30 / 돈의가격 25 / 리스크예산 25 / 상대강도 20
WEIGHTS = {
    "regime": 0.30,
    "money": 0.25,
    "risk": 0.25,
    "relative": 0.20,
}

STANCE_ON = 0.40
STANCE_OFF = -0.40
Z_WINDOW = 252
Z_MIN = 60
SLOPE_WINDOW = 21
LIVE_REFRESH_SEC = 180

REGIME_SCORE = {
    "BadNewsIsGoodNews": 1.20,
    "SoftLanding": 1.00,
    "InflationFight": -1.00,
    "GrowthScare": -1.20,
}

BASKETS = [
    {"ticker": "BIL", "group": "현금", "slot": "초단기", "name": "초단기 채권"},
    {"ticker": "TLT", "group": "채권", "slot": "장기국채", "name": "장기 국채"},
    {"ticker": "IEF", "group": "채권", "slot": "중기국채", "name": "중기 국채"},
    {"ticker": "LQD", "group": "채권", "slot": "투자등급", "name": "투자등급 회사채"},
    {"ticker": "HYG", "group": "채권", "slot": "하이일드", "name": "하이일드"},
    {"ticker": "SPY", "group": "주식", "slot": "대형", "name": "S&P 500"},
    {"ticker": "QQQ", "group": "주식", "slot": "성장/나스닥", "name": "나스닥 100"},
    {"ticker": "XLK", "group": "주식", "slot": "성장/나스닥", "name": "기술 섹터"},
    {"ticker": "IWM", "group": "주식", "slot": "중소형", "name": "러셀 2000"},
    {"ticker": "RSP", "group": "주식", "slot": "동일가중", "name": "동일가중 S&P"},
    {"ticker": "XLU", "group": "주식", "slot": "방어", "name": "유틸리티"},
    {"ticker": "XLP", "group": "주식", "slot": "방어", "name": "필수소비"},
    {"ticker": "XLF", "group": "주식", "slot": "금융", "name": "금융"},
    {"ticker": "GLD", "group": "금", "slot": "금", "name": "금"},
    {"ticker": "UUP", "group": "달러", "slot": "달러", "name": "달러"},
]

BASKET_BY_TICKER = {b["ticker"]: b for b in BASKETS}
CHART_ASSETS = ["SPY", "TLT", "GLD", "BIL"]

ENLARGE_MAX = 3
CUT_MAX = 3
UUP_ENLARGE_MIN = 1.20
