"""합성 패널로 네 레짐이 갈리는지 확인한다."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.regime import classify_regime
from src.signals import build_feature_frame
from tests.panels import make_panel


def _last_regime(scenario: str) -> str:
    feat = build_feature_frame(make_panel(scenario))
    row = feat.dropna(how="all").iloc[-1]
    return classify_regime(row)


def test_bnign_regime():
    assert _last_regime("bnign") == "BadNewsIsGoodNews"


def test_scare_regime():
    assert _last_regime("scare") == "GrowthScare"


def test_landing_regime():
    assert _last_regime("landing") == "SoftLanding"


def test_inflation_regime():
    assert _last_regime("inflation") == "InflationFight"


def test_features_are_causal_on_shift():
    panel = make_panel("bnign")
    full = build_feature_frame(panel)
    truncated = build_feature_frame(panel.iloc[:-1])
    col = "money"
    left = truncated[col].dropna().iloc[-1]
    right = full[col].iloc[-2]
    assert abs(left - right) < 1e-9
