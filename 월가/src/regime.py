"""지표 vs 테이프 네 레짐. 피처는 이미 인과적이다."""

from __future__ import annotations

import pandas as pd

from src.config import REGIME_SCORE


def classify_regime(row: pd.Series) -> str:
    growth_weak = bool(row.get("growth_weak", False))
    inflation_hot = bool(row.get("inflation_hot", False))
    stocks_up = bool(row.get("stocks_up", False))
    yields_down = bool(row.get("yields_down", False))
    credit_worse = bool(row.get("credit_worse", False))

    if growth_weak and stocks_up and yields_down:
        return "BadNewsIsGoodNews"
    if growth_weak and (not stocks_up) and credit_worse:
        return "GrowthScare"
    if inflation_hot and (not yields_down) and (not stocks_up):
        return "InflationFight"
    if stocks_up and not growth_weak:
        return "SoftLanding"
    if stocks_up:
        return "BadNewsIsGoodNews" if yields_down else "SoftLanding"
    if inflation_hot:
        return "InflationFight"
    return "GrowthScare"


def regime_series(features: pd.DataFrame) -> pd.Series:
    return features.apply(classify_regime, axis=1)


def regime_numeric(regimes: pd.Series) -> pd.Series:
    return regimes.map(REGIME_SCORE).astype(float)
