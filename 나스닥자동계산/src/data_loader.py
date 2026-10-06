"""야후 파이낸스 시세를 받아 로컬 Parquet에 둔다."""

from __future__ import annotations

import logging
import os

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

ASSETS = {
    "QQQ": "QQQ (나스닥100 ETF)",
    "^NDX": "나스닥100 지수",
    "TQQQ": "TQQQ (3배 ETF)",
}

FIELD_NAMES = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}


def cache_path(ticker: str) -> str:
    safe = ticker.replace("^", "").replace("/", "_")
    return os.path.join(DATA_DIR, f"{safe.lower()}.parquet")


def is_fresh(last_date, today=None, max_age_days: int = 5) -> bool:
    today_ts = pd.Timestamp.today().normalize() if today is None else pd.Timestamp(today).normalize()
    last = pd.Timestamp(last_date).normalize()
    return (today_ts - last).days <= max_age_days


def flatten_download(frame: pd.DataFrame) -> pd.DataFrame:
    """야후가 단일 종목에도 다중 열을 주는 경우를 한 층으로 만든다."""
    out = frame
    if isinstance(out.columns, pd.MultiIndex):
        chosen = None
        for level in range(out.columns.nlevels):
            values = {str(v) for v in out.columns.get_level_values(level)}
            if FIELD_NAMES & values:
                chosen = level
                break
        if chosen is None:
            out = out.copy()
            out.columns = [" ".join(str(part) for part in col if str(part) != "").strip() for col in out.columns]
        else:
            out = out.droplevel([i for i in range(out.columns.nlevels) if i != chosen], axis=1)
            out.columns = [str(col) for col in out.columns]
    if out.columns.duplicated().any():
        out = out.loc[:, ~out.columns.duplicated()]
    return out


def slice_dates(frame: pd.DataFrame, start, end) -> pd.DataFrame:
    ordered = frame.sort_values("date")
    days = pd.to_datetime(ordered["date"]).dt.normalize()
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    if start_ts > end_ts:
        start_ts, end_ts = end_ts, start_ts
    chosen = ordered.loc[(days >= start_ts) & (days <= end_ts)]
    return chosen.reset_index(drop=True)


def month_span(dates) -> int:
    periods = pd.to_datetime(pd.Series(dates)).dt.to_period("M")
    return int(periods.nunique())


def slice_years(frame: pd.DataFrame, years: int | None) -> pd.DataFrame:
    ordered = frame.sort_values("date")
    if years is None or ordered.empty:
        return ordered.reset_index(drop=True)
    end = pd.Timestamp(ordered["date"].iloc[-1])
    start = end - pd.DateOffset(years=int(years))
    return ordered.loc[ordered["date"] >= start].reset_index(drop=True)


def _session_index(frame: pd.DataFrame) -> pd.DatetimeIndex:
    idx = pd.to_datetime(frame.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    return pd.DatetimeIndex(idx).normalize()


def build_market(price: pd.DataFrame, irx: pd.DataFrame | None) -> pd.DataFrame:
    flat = flatten_download(price)
    if "Close" not in flat.columns and "Adj Close" not in flat.columns:
        raise ValueError("종가 열을 찾지 못했습니다.")
    raw_close = pd.to_numeric(flat["Close"] if "Close" in flat.columns else flat["Adj Close"], errors="coerce")
    adj = pd.to_numeric(flat["Adj Close"], errors="coerce") if "Adj Close" in flat.columns else raw_close
    raw_open = pd.to_numeric(flat["Open"] if "Open" in flat.columns else raw_close, errors="coerce")
    factor = adj / raw_close.replace(0, np.nan)
    market = pd.DataFrame(
        {
            "date": _session_index(flat),
            "open": (raw_open * factor).to_numpy(dtype=np.float64),
            "close": adj.to_numpy(dtype=np.float64),
        }
    )
    market = market.replace([np.inf, -np.inf], np.nan).dropna()
    market = market[(market["open"] > 0) & (market["close"] > 0)]
    market = market.drop_duplicates(subset=["date"], keep="last").sort_values("date")
    market["rf"] = _daily_cash_yield(market["date"], irx)
    return market.reset_index(drop=True)


def _daily_cash_yield(dates: pd.Series, irx: pd.DataFrame | None) -> np.ndarray:
    if irx is None or irx.empty:
        return np.zeros(len(dates), dtype=np.float64)
    flat = flatten_download(irx)
    col = "Close" if "Close" in flat.columns else flat.columns[0]
    yield_pct = pd.Series(pd.to_numeric(flat[col], errors="coerce").to_numpy(), index=_session_index(flat))
    yield_pct = yield_pct[~yield_pct.index.duplicated(keep="last")].sort_index()
    aligned = yield_pct.reindex(pd.DatetimeIndex(pd.to_datetime(dates))).ffill().fillna(0.0)
    daily = (1.0 + aligned.to_numpy(dtype=np.float64) / 100.0) ** (1.0 / 252.0) - 1.0
    shifted = np.zeros_like(daily)
    if len(daily) > 1:
        shifted[1:] = daily[:-1]
    return shifted


def _download(ticker: str) -> pd.DataFrame:
    frame = yf.download(ticker, period="max", auto_adjust=False, progress=False, threads=False)
    if frame is None or frame.empty:
        raise ValueError(f"{ticker} 시세를 받지 못했습니다.")
    return frame


def load_market(ticker: str, refresh: bool = False) -> tuple[pd.DataFrame, str]:
    """(시세, 안내 문구). 받기에 실패하면 기존 캐시를 쓴다."""
    path = cache_path(ticker)
    cached = _read_cache(path)
    if cached is not None and not refresh and is_fresh(cached["date"].iloc[-1]):
        return cached, ""
    try:
        price = _download(ticker)
        try:
            irx = _download("^IRX")
        except Exception as exc:
            logger.warning("13주 국채 수익률을 받지 못했습니다: %s", exc)
            irx = None
        market = build_market(price, irx)
        if market.empty:
            raise ValueError("정리한 시세가 비어 있습니다.")
        market.to_parquet(path, index=False)
        note = "" if irx is not None else "현금 수익률을 받지 못해 이 구간 현금은 0%로 두었습니다."
        return market, note
    except Exception as exc:
        if cached is not None:
            logger.warning("시세 갱신 실패, 캐시를 사용합니다: %s", exc)
            return cached, f"최신 시세를 받지 못해 저장된 데이터로 계산합니다. ({exc})"
        raise


def _read_cache(path: str) -> pd.DataFrame | None:
    if not os.path.exists(path):
        return None
    frame = pd.read_parquet(path)
    frame["date"] = pd.to_datetime(frame["date"])
    return frame.sort_values("date").reset_index(drop=True)
