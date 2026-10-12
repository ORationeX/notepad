"""나스닥·S&P·단기금리 시세. 이 폴더 밖 모듈을 쓰지 않는다."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache"
HISTORY_START = "1993-01-01"

SERIES = {
    "ixic": "^IXIC",
    "gspc": "^GSPC",
    "irx": "^IRX",
    "sox": "^SOX",
    "vix": "^VIX",
}
REQUIRED = ("ixic", "gspc", "irx")
TAIL_SESSIONS = 3


def cache_path(name: str) -> Path:
    return CACHE_DIR / f"{name}.parquet"


def _close_series(frame: pd.DataFrame) -> pd.Series:
    columns = frame.columns
    if isinstance(columns, pd.MultiIndex):
        if "Close" in columns.get_level_values(0):
            close = frame.xs("Close", axis=1, level=0)
        elif "Close" in columns.get_level_values(-1):
            close = frame.xs("Close", axis=1, level=-1)
        else:
            raise ValueError("종가 열이 없습니다.")
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
    else:
        if "Close" not in columns:
            raise ValueError("종가 열이 없습니다.")
        close = frame["Close"]
    series = pd.Series(close.to_numpy(dtype=float), index=pd.to_datetime(close.index), name="close")
    if getattr(series.index, "tz", None) is not None:
        series.index = series.index.tz_localize(None)
    series.index = series.index.normalize()
    series = series[~series.index.duplicated(keep="last")].sort_index()
    return series[np.isfinite(series.to_numpy())]


def _download(ticker: str, start: pd.Timestamp | None = None) -> pd.Series:
    frame = yf.download(
        ticker,
        start=HISTORY_START if start is None else pd.Timestamp(start).strftime("%Y-%m-%d"),
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if frame is None or len(frame) == 0:
        raise ValueError(f"{ticker} 시세를 받지 못했습니다.")
    series = _close_series(frame)
    if series.empty:
        raise ValueError(f"{ticker} 종가가 비어 있습니다.")
    return series


def _read_cache(name: str) -> pd.Series | None:
    path = cache_path(name)
    if not path.exists():
        return None
    frame = pd.read_parquet(path)
    series = pd.Series(frame["close"].to_numpy(dtype=float), index=pd.to_datetime(frame["date"]), name="close")
    series.index = series.index.normalize()
    return series.sort_index()


def _write_cache(name: str, series: pd.Series) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame({"date": series.index, "close": series.to_numpy(dtype=float)})
    frame.to_parquet(cache_path(name), index=False)


def _without_recent_sessions(series: pd.Series, sessions: int = TAIL_SESSIONS) -> tuple[pd.Series, pd.Timestamp | None]:
    """마지막 영업일 sessions개를 다시 받을 시작일로 떼어 낸다."""
    if len(series) <= sessions:
        return series.iloc[0:0], None
    start = pd.Timestamp(series.index[-sessions])
    return series.iloc[:-sessions], start


def _merge_tail(kept: pd.Series, fresh: pd.Series) -> pd.Series:
    combined = pd.concat([kept, fresh])
    combined = combined[~combined.index.duplicated(keep="last")].sort_index()
    return combined


def _refresh_tail(cached: pd.Series, ticker: str) -> pd.Series:
    kept, start = _without_recent_sessions(cached)
    if start is None:
        return _download(ticker)
    fresh = _download(ticker, start=start)
    if fresh.empty:
        raise ValueError(f"{ticker} 최근 종가를 받지 못했습니다.")
    return _merge_tail(kept, fresh)


def load_series(name: str, refresh: bool = False) -> pd.Series:
    """캐시가 있으면 그대로 쓴다. refresh일 때만 최근 3영업일을 다시 받아 붙인다."""
    ticker = SERIES[name]
    cached = _read_cache(name)
    if cached is not None and not cached.empty and not refresh:
        return cached
    if cached is None or cached.empty:
        series = _download(ticker)
    else:
        series = _refresh_tail(cached, ticker)
    _write_cache(name, series)
    return series


def load_optional(name: str, refresh: bool = False) -> pd.Series | None:
    try:
        return load_series(name, refresh=refresh)
    except (ValueError, KeyError, OSError):
        if refresh:
            cached = _read_cache(name)
            if cached is not None and not cached.empty:
                return cached
        return None


def load_prices(refresh: bool = False) -> pd.DataFrame:
    """거래일 기준 표. 금리는 연율을 252로 나눈 일별 수익이다."""
    ixic = load_series("ixic", refresh=refresh)
    gspc = load_series("gspc", refresh=refresh)
    irx = load_series("irx", refresh=refresh)
    sox = load_optional("sox", refresh=refresh)
    vix = load_optional("vix", refresh=refresh)

    frame = pd.DataFrame({"ixic": ixic, "gspc": gspc}).dropna()
    frame = frame[frame["ixic"] > 0]
    irx_aligned = irx.reindex(frame.index).ffill()
    frame["rf"] = (irx_aligned.to_numpy(dtype=float) / 100.0) / 252.0
    frame["rf"] = frame["rf"].fillna(0.0)
    if sox is not None:
        frame["sox"] = sox.reindex(frame.index).ffill()
    else:
        frame["sox"] = np.nan
    if vix is not None:
        frame["vix"] = vix.reindex(frame.index).ffill()
    else:
        frame["vix"] = np.nan
    frame.index.name = "date"
    return frame
