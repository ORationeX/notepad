"""당일까지의 종가만 쓰는 지표."""

from __future__ import annotations

import numpy as np
import pandas as pd

MA_DAYS = 200
YEAR_DAYS = 252
RS_DAYS = 126
FAST_DAYS = 63
ACCEL_LAG = 21

SAMPLE_START = pd.Timestamp("1995-01-01")
TRAIN_END = pd.Timestamp("2012-12-31")
HOLDOUT_START = pd.Timestamp("2013-01-01")


def build_features(prices: pd.DataFrame) -> pd.DataFrame:
    ixic = prices["ixic"].astype(float)
    gspc = prices["gspc"].astype(float)
    out = pd.DataFrame(index=prices.index)
    out["ixic"] = ixic
    out["rf"] = prices["rf"].astype(float).fillna(0.0)
    out["ret"] = ixic.pct_change()
    average = ixic.rolling(MA_DAYS, min_periods=MA_DAYS).mean()
    out["stretch"] = ixic / average - 1.0
    out["roc"] = ixic / ixic.shift(YEAR_DAYS) - 1.0
    out["dd"] = ixic / ixic.rolling(YEAR_DAYS, min_periods=YEAR_DAYS).max() - 1.0
    nasdaq_rs = ixic / ixic.shift(RS_DAYS) - 1.0
    sp_rs = gspc / gspc.shift(RS_DAYS) - 1.0
    out["rs"] = nasdaq_rs - sp_rs
    fast = ixic / ixic.shift(FAST_DAYS) - 1.0
    out["accel"] = fast - fast.shift(ACCEL_LAG)
    if "sox" in prices.columns:
        sox = prices["sox"].astype(float)
        sox_rs = sox / sox.shift(RS_DAYS) - 1.0
        out["semi"] = sox_rs - nasdaq_rs
    else:
        out["semi"] = np.nan
    if "vix" in prices.columns:
        out["vix"] = prices["vix"].astype(float)
    else:
        out["vix"] = np.nan
    return out


def window_positions(index: pd.DatetimeIndex, start: pd.Timestamp, end: pd.Timestamp | None) -> tuple[int, int]:
    """포함 구간의 정수 위치. end가 없으면 마지막 날까지."""
    start_i = int(index.searchsorted(pd.Timestamp(start)))
    if end is None:
        end_i = len(index) - 1
    else:
        end_i = int(index.searchsorted(pd.Timestamp(end), side="right")) - 1
    if start_i < 1 or end_i < start_i or end_i >= len(index):
        raise ValueError("성적 구간이 시세 안에 없습니다.")
    return start_i, end_i
