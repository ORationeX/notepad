"""미국 장중 Yahoo 테이프. 일간 골격과 별도로 짧게만 산다."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

from src.config import LIVE_RENAME, LIVE_TICKERS

NY = ZoneInfo("America/New_York")
SEOUL = ZoneInfo("Asia/Seoul")


@dataclass
class LiveTape:
    asof_ny: datetime
    asof_kst: datetime
    session: str
    session_ko: str
    returns: dict[str, float] = field(default_factory=dict)
    last_price: dict[str, float] = field(default_factory=dict)
    source: str = "yahoo-5m"


def session_now(now: datetime | None = None) -> tuple[str, datetime]:
    current = now.astimezone(NY) if now else datetime.now(NY)
    if current.weekday() >= 5:
        return "weekend", current
    clock = current.time()
    if time(9, 30) <= clock <= time(16, 0):
        return "open", current
    if clock < time(9, 30):
        return "pre", current
    return "closed", current


def session_label(session: str) -> str:
    return {
        "open": "미국 정규장",
        "pre": "장 시작 전",
        "closed": "장 마감",
        "weekend": "주말",
    }.get(session, session)


def _close_frame(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        names = list(raw.columns.names)
        if names and names[0] == "Ticker":
            pieces = {}
            for t in tickers:
                if t not in raw.columns.get_level_values(0):
                    continue
                sub = raw[t]
                col = "Close" if "Close" in getattr(sub, "columns", []) else None
                if col is None and hasattr(sub, "columns"):
                    col = sub.columns[0]
                pieces[t] = sub[col] if col else sub
            return pd.DataFrame(pieces)
        if "Close" in raw.columns.get_level_values(0):
            return raw["Close"].copy()
    if "Close" in raw.columns:
        return raw[["Close"]].rename(columns={"Close": tickers[0]})
    return raw.copy()


def fetch_live_tape(now: datetime | None = None) -> LiveTape:
    session, ny = session_now(now)
    tape = LiveTape(
        asof_ny=ny,
        asof_kst=ny.astimezone(SEOUL),
        session=session,
        session_ko=session_label(session),
    )
    tickers = list(LIVE_TICKERS)
    try:
        raw = yf.download(
            tickers,
            period="2d",
            interval="5m" if session == "open" else "1d",
            auto_adjust=True,
            progress=False,
            threads=True,
            group_by="ticker",
        )
        close = _close_frame(raw, tickers)
        close = close.rename(columns=LIVE_RENAME)
        close = close.dropna(how="all")
        if close.empty:
            return tape
        last = close.iloc[-1]
        if len(close) >= 2:
            # 5분봉이면 전일 종가 근사: 날짜가 바뀌는 마지막 봉
            idx = pd.to_datetime(close.index)
            if getattr(idx, "tz", None) is not None:
                days = idx.tz_convert(NY).date
            else:
                days = pd.DatetimeIndex(idx).date
            unique_days = list(dict.fromkeys(days))
            if len(unique_days) >= 2:
                prev_day = unique_days[-2]
                prev = close.loc[[d == prev_day for d in days]].iloc[-1]
            else:
                prev = close.iloc[0]
        else:
            prev = last
        for col in last.index:
            px = last[col]
            base = prev[col] if col in prev.index else pd.NA
            if pd.isna(px):
                continue
            tape.last_price[str(col)] = float(px)
            if pd.notna(base) and float(base) != 0:
                tape.returns[str(col)] = float(px) / float(base) - 1.0
        tape.source = "yahoo-5m" if session == "open" else "yahoo-daily"
    except Exception as exc:  # noqa: BLE001
        tape.source = f"error:{exc}"
    return tape
