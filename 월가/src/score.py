"""종합 스탠스와 장중 오버라이드."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.config import STANCE_OFF, STANCE_ON, WEIGHTS
from src.live import LiveTape
from src.regime import classify_regime, regime_series
from src.signals import build_feature_frame, clip_score


def stance_from_score(score: float) -> str:
    if score >= STANCE_ON:
        return "RISK_ON"
    if score <= STANCE_OFF:
        return "RISK_OFF"
    return "MIXED"


def compute_signal_frame(panel: pd.DataFrame) -> pd.DataFrame:
    feat = build_feature_frame(panel)
    feat["regime"] = regime_series(feat)
    feat["regime_score"] = feat["regime"].map(
        {
            "BadNewsIsGoodNews": 1.20,
            "SoftLanding": 1.00,
            "InflationFight": -1.00,
            "GrowthScare": -1.20,
        }
    )
    raw = (
        WEIGHTS["regime"] * feat["regime_score"].fillna(0)
        + WEIGHTS["money"] * feat["money"].fillna(0)
        + WEIGHTS["risk"] * feat["risk"].fillna(0)
        + WEIGHTS["relative"] * feat["relative"].fillna(0)
    )
    feat["score"] = clip_score(raw)
    feat["stance"] = feat["score"].map(stance_from_score)
    return feat


def latest_row(frame: pd.DataFrame) -> pd.Series:
    return frame.dropna(subset=["score"]).iloc[-1]


def apply_live_overlay(score: float, stance: str, tape: LiveTape | None) -> tuple[float, str, str | None]:
    if tape is None or tape.session != "open" or not tape.returns:
        return score, stance, None
    spy = tape.returns.get("SPY", 0.0) * 100
    qqq = tape.returns.get("QQQ", 0.0) * 100
    tlt = tape.returns.get("TLT", 0.0) * 100
    hyg = tape.returns.get("HYG", 0.0) * 100
    note = None
    adjusted = score
    if spy < -0.4 and qqq < -0.4 and tlt > 0.1 and hyg < -0.2:
        adjusted -= 0.80
        note = "장중 주식·신용이 같이 빠지고 국채가 오른다"
    elif spy > 0.4 and qqq > 0.4 and hyg > 0.15:
        adjusted += 0.50
        note = "장중 위험자산과 신용을 같이 산다"
    adjusted = float(max(-2.0, min(2.0, adjusted)))
    return adjusted, stance_from_score(adjusted), note


@dataclass
class Snapshot:
    asof: pd.Timestamp
    regime: str
    stance: str
    score: float
    daily_score: float
    daily_stance: str
    overlay_note: str | None
    features: pd.Series


def snapshot_from(panel: pd.DataFrame, tape: LiveTape | None = None) -> Snapshot:
    frame = compute_signal_frame(panel)
    row = latest_row(frame)
    daily_score = float(row["score"])
    daily_stance = str(row["stance"])
    score, stance, note = apply_live_overlay(daily_score, daily_stance, tape)
    return Snapshot(
        asof=row.name,
        regime=str(row["regime"]),
        stance=stance,
        score=score,
        daily_score=daily_score,
        daily_stance=daily_stance,
        overlay_note=note,
        features=row,
    )


def classify_one(features_row: pd.Series) -> str:
    return classify_regime(features_row)
