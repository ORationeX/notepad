"""닫힌 바구니에 확대/유지/축소/회피. 개별 주식은 고르지 않는다."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.glossary import REGIME_KO, STANCE_KO
from src.config import (
    BASKET_BY_TICKER,
    BASKETS,
    CUT_MAX,
    ENLARGE_MAX,
    UUP_ENLARGE_MIN,
)
from src.score import Snapshot


@dataclass
class BasketAction:
    ticker: str
    group: str
    slot: str
    name: str
    action: str
    score: float
    reason: str
    ret_21: float | None = None


@dataclass
class Book:
    enlarge: list[BasketAction] = field(default_factory=list)
    reduce: list[BasketAction] = field(default_factory=list)
    avoid: list[BasketAction] = field(default_factory=list)
    hold: list[BasketAction] = field(default_factory=list)
    all_rows: list[BasketAction] = field(default_factory=list)
    sentence: str = ""


def _ret(features: pd.Series, key: str) -> float:
    val = features.get(key, 0.0)
    try:
        return float(val) if pd.notna(val) else 0.0
    except (TypeError, ValueError):
        return 0.0


def score_baskets(regime: str, stance: str, features: pd.Series) -> dict[str, float]:
    scores = {b["ticker"]: 0.0 for b in BASKETS}

    if stance == "RISK_ON":
        for t in ("SPY", "QQQ", "XLK", "HYG"):
            scores[t] += 1.00
        scores["BIL"] -= 1.20
        scores["XLU"] -= 0.50
        scores["XLP"] -= 0.35
    elif stance == "RISK_OFF":
        scores["BIL"] += 1.50
        scores["TLT"] += 0.60
        scores["XLU"] += 0.40
        scores["QQQ"] -= 1.20
        scores["IWM"] -= 1.20
        scores["HYG"] -= 1.00
        scores["XLK"] -= 0.90
    else:
        scores["IEF"] += 0.35
        scores["SPY"] += 0.10
        scores["BIL"] += 0.15

    if regime == "BadNewsIsGoodNews":
        scores["QQQ"] += 0.80
        scores["XLK"] += 0.55
        scores["TLT"] += 0.80
        scores["GLD"] += 0.50
        scores["BIL"] -= 0.80
        scores["XLU"] -= 0.40
    elif regime == "GrowthScare":
        scores["BIL"] += 1.00
        scores["TLT"] += 0.80
        scores["XLU"] += 0.60
        scores["XLP"] += 0.50
        scores["QQQ"] -= 1.00
        scores["IWM"] -= 1.00
        scores["HYG"] -= 0.80
        scores["XLK"] -= 0.70
    elif regime == "SoftLanding":
        scores["SPY"] += 0.60
        scores["XLF"] += 0.70
        scores["IWM"] += 0.40
        scores["QQQ"] += 0.50
        scores["RSP"] += 0.35
        scores["TLT"] -= 0.30
        scores["BIL"] -= 0.40
    elif regime == "InflationFight":
        scores["BIL"] += 0.80
        scores["UUP"] += 0.70
        scores["XLF"] += 0.20
        scores["TLT"] -= 1.00
        scores["GLD"] -= 0.40
        scores["IWM"] -= 0.80
        scores["HYG"] -= 0.60

    qqq_21 = _ret(features, "qqq_21")
    xlu_21 = _ret(features, "xlu_21")
    iwm_21 = _ret(features, "iwm_21")
    spy_21 = _ret(features, "spy_21")
    rsp_21 = _ret(features, "rsp_21")
    tlt_21 = _ret(features, "tlt_21")
    hyg_21 = _ret(features, "hyg_21")
    lqd_21 = _ret(features, "lqd_21")
    gld_21 = _ret(features, "gld_21")
    uup_21 = _ret(features, "uup_21")

    if qqq_21 > xlu_21:
        scores["QQQ"] += 0.30
        scores["XLU"] -= 0.20
    else:
        scores["XLU"] += 0.30
        scores["QQQ"] -= 0.20

    if iwm_21 > 0 and stance == "RISK_ON":
        scores["IWM"] += 0.40
    else:
        scores["IWM"] -= 0.15

    if rsp_21 > spy_21:
        scores["RSP"] += 0.30
    if tlt_21 > 0 and _ret(features, "dgs2_chg") < 0:
        scores["TLT"] += 0.30
        scores["IEF"] += 0.15
    if hyg_21 > lqd_21:
        scores["HYG"] += 0.30
        scores["LQD"] -= 0.10
    else:
        scores["LQD"] += 0.20
        scores["HYG"] -= 0.20
    if gld_21 > 0 and _ret(features, "dollar_chg") < 0:
        scores["GLD"] += 0.40
    if uup_21 > 0.01:
        scores["UUP"] += 0.25
    return scores


def _reason(ticker: str, action: str, regime: str, stance: str) -> str:
    regime_ko = REGIME_KO.get(regime, regime)
    stance_ko = STANCE_KO.get(stance, stance)
    meta = BASKET_BY_TICKER[ticker]
    label = meta["name"]
    if action == "확대":
        return f"{regime_ko} 국면 → {label} 매수"
    if action == "회피":
        return f"{regime_ko} 국면 → {label} 매도 (신규 매수 금지)"
    if action == "축소":
        return f"{stance_ko} → {label} 일부 매도"
    return f"{label} 보유 유지"


def decide_book(snap: Snapshot) -> Book:
    features = snap.features
    scores = score_baskets(snap.regime, snap.stance, features)
    ret_map = {
        "SPY": "spy_21",
        "QQQ": "qqq_21",
        "IWM": "iwm_21",
        "RSP": "rsp_21",
        "TLT": "tlt_21",
        "HYG": "hyg_21",
        "LQD": "lqd_21",
        "GLD": "gld_21",
        "UUP": "uup_21",
        "XLU": "xlu_21",
        "XLF": "xlf_21",
    }

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    enlarge_tickers: list[str] = []
    for ticker, sc in ranked:
        if ticker == "UUP" and sc < UUP_ENLARGE_MIN:
            continue
        if sc >= 0.70 and len(enlarge_tickers) < ENLARGE_MAX:
            enlarge_tickers.append(ticker)

    avoid_tickers: list[str] = []
    reduce_tickers: list[str] = []
    for ticker, sc in sorted(scores.items(), key=lambda kv: kv[1]):
        if ticker in enlarge_tickers:
            continue
        if sc <= -0.80 and len(avoid_tickers) < 2:
            avoid_tickers.append(ticker)
        elif sc <= -0.30 and len(avoid_tickers) + len(reduce_tickers) < CUT_MAX:
            reduce_tickers.append(ticker)

    book = Book()
    for spec in BASKETS:
        ticker = spec["ticker"]
        sc = scores[ticker]
        if ticker in enlarge_tickers:
            action = "확대"
        elif ticker in avoid_tickers:
            action = "회피"
        elif ticker in reduce_tickers:
            action = "축소"
        else:
            action = "유지"
        ret_key = ret_map.get(ticker)
        row = BasketAction(
            ticker=ticker,
            group=spec["group"],
            slot=spec["slot"],
            name=spec["name"],
            action=action,
            score=sc,
            reason=_reason(ticker, action, snap.regime, snap.stance),
            ret_21=_ret(features, ret_key) if ret_key else None,
        )
        book.all_rows.append(row)
        if action == "확대":
            book.enlarge.append(row)
        elif action == "회피":
            book.avoid.append(row)
        elif action == "축소":
            book.reduce.append(row)
        else:
            book.hold.append(row)

    book.enlarge.sort(key=lambda r: r.score, reverse=True)
    book.avoid.sort(key=lambda r: r.score)
    book.reduce.sort(key=lambda r: r.score)

    buys = "·".join(r.name for r in book.enlarge) or "없음"
    sells = "·".join(r.name for r in (book.avoid + book.reduce)[:3]) or "없음"
    extra = f" {snap.overlay_note}." if snap.overlay_note else ""
    book.sentence = (
        f"지금 국면은 {REGIME_KO.get(snap.regime, snap.regime)}입니다. "
        f"살 것: {buys}. 팔 것: {sells}.{extra}"
    )
    return book


def enlarge_tickers(book: Book) -> list[str]:
    names = [r.ticker for r in book.enlarge]
    return names or ["BIL"]


def avoid_tickers(book: Book) -> list[str]:
    return [r.ticker for r in book.avoid]
