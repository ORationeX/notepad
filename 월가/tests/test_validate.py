from __future__ import annotations

import numpy as np

from src.score import compute_signal_frame
from src.validate import validate
from tests.panels import make_panel


def test_score_has_no_lookahead():
    panel = make_panel("bnign")
    full = compute_signal_frame(panel)
    cut = compute_signal_frame(panel.iloc[:-5])
    overlap = cut.dropna(subset=["score"]).index.intersection(full.dropna(subset=["score"]).index)
    assert len(overlap) > 50
    a = full.loc[overlap, "score"]
    b = cut.loc[overlap, "score"]
    assert np.nanmax(np.abs(a - b)) < 1e-9


def test_mutating_last_row_does_not_change_history():
    panel = make_panel("landing")
    base = compute_signal_frame(panel)
    mutated = panel.copy()
    mutated.iloc[-1, mutated.columns.get_loc("SPY")] *= 1.2
    other = compute_signal_frame(mutated)
    hist = base.index[:-1]
    assert np.nanmax(np.abs(base.loc[hist, "score"] - other.loc[hist, "score"])) < 1e-9


def test_validate_returns_kpis_and_aligned_series():
    panel = make_panel("bnign")
    result = validate(panel, years=1)
    assert len(result.book_equity) == len(result.prices)
    assert "book_vs_spy" in result.kpis
    assert result.book_equity.iloc[0] == 100.0
    assert result.last_stance in {"RISK_ON", "MIXED", "RISK_OFF"}
