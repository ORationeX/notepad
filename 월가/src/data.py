"""FRED CSV + Yahoo 일간 수집. 캐시는 이 폴더만 사용한다."""

from __future__ import annotations

import io
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

from src.config import (
    CACHE_DIR,
    EVENTS_PATH,
    FRED_CSV,
    FRED_HEADERS,
    FRED_SERIES,
    YAHOO_DAILY,
    YAHOO_INDEX,
)

CACHE_DIR.mkdir(parents=True, exist_ok=True)

FRED_TTL = timedelta(hours=12)
YAHOO_TTL = timedelta(hours=6)


def _fresh(path: Path, ttl: timedelta) -> bool:
    if not path.exists():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return datetime.now(timezone.utc) - mtime < ttl


def fetch_fred_series(sid: str, force: bool = False) -> pd.Series:
    path = CACHE_DIR / f"fred_{sid}.parquet"
    if not force and _fresh(path, FRED_TTL):
        s = pd.read_parquet(path)[sid]
        s.index = pd.to_datetime(s.index)
        return s

    url = FRED_CSV.format(sid=sid)
    resp = requests.get(url, headers=FRED_HEADERS, timeout=30)
    resp.raise_for_status()
    raw = pd.read_csv(io.StringIO(resp.text))
    date_col = raw.columns[0]
    val_col = raw.columns[1]
    frame = raw.rename(columns={date_col: "date", val_col: sid})
    frame["date"] = pd.to_datetime(frame["date"], utc=False)
    frame[sid] = pd.to_numeric(frame[sid], errors="coerce")
    series = frame.set_index("date")[sid].sort_index()
    series.to_frame().to_parquet(path)
    return series


def _yahoo_close(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = raw.columns.get_level_values(0)
        if "Close" in level0:
            close = raw["Close"].copy()
        elif "Adj Close" in level0:
            close = raw["Adj Close"].copy()
        else:
            close = raw.xs(raw.columns.levels[0][-1], axis=1, level=0)
    else:
        col = "Close" if "Close" in raw.columns else raw.columns[0]
        close = raw[[col]].rename(columns={col: tickers[0]})
    close.index = pd.to_datetime(close.index).tz_localize(None)
    close = close.sort_index()
    return close


def fetch_yahoo_daily(force: bool = False) -> pd.DataFrame:
    path = CACHE_DIR / "yahoo_daily.parquet"
    tickers = list(YAHOO_DAILY) + list(YAHOO_INDEX)
    if not force and _fresh(path, YAHOO_TTL):
        cached = pd.read_parquet(path)
        cached.index = pd.to_datetime(cached.index)
        return cached

    raw = yf.download(
        tickers,
        period="10y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="ticker",
    )
    # yfinance 버전에 따라 컬럼 구조가 달라 Close 우선으로 정규화한다.
    if isinstance(raw.columns, pd.MultiIndex):
        names = list(raw.columns.names)
        if names[0] == "Ticker" or "Close" not in raw.columns.get_level_values(0):
            pieces = {}
            for t in tickers:
                try:
                    sub = raw[t]
                except KeyError:
                    continue
                col = "Close" if "Close" in sub.columns else sub.columns[0]
                pieces[t] = sub[col]
            close = pd.DataFrame(pieces)
        else:
            close = _yahoo_close(raw, tickers)
    else:
        close = _yahoo_close(raw, tickers)

    rename = dict(YAHOO_INDEX)
    close = close.rename(columns=rename)
    close.to_parquet(path)
    return close


def load_daily_panel(force: bool = False) -> pd.DataFrame:
    """Yahoo 거래일 인덱스에 FRED를 ffill로 붙인 일간 패널."""
    yahoo = fetch_yahoo_daily(force=force)
    fred_cols = {}
    for sid in FRED_SERIES:
        try:
            fred_cols[sid] = fetch_fred_series(sid, force=force)
            time.sleep(0.15)
        except Exception as exc:  # noqa: BLE001 — 한 시리즈 실패가 전체를 죽이지 않게
            print(f"[data] FRED {sid} 실패: {exc}")
    fred = pd.DataFrame(fred_cols)
    fred.index = pd.to_datetime(fred.index).tz_localize(None)
    panel = yahoo.copy()
    panel.index = pd.to_datetime(panel.index).tz_localize(None)
    aligned = fred.reindex(fred.index.union(panel.index)).sort_index().ffill()
    aligned = aligned.reindex(panel.index)
    out = panel.join(aligned, how="left")
    if "VIX" not in out.columns and "VIXCLS" in out.columns:
        out["VIX"] = out["VIXCLS"]
    elif "VIXCLS" in out.columns and "VIX" in out.columns:
        out["VIX"] = out["VIX"].combine_first(out["VIXCLS"])
    return out


def load_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    payload = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    for row in payload:
        row["date"] = pd.Timestamp(row["date"]).normalize()
    return payload
