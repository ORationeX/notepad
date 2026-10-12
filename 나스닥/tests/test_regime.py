"""판정은 과거만 보고, 2013년 이후는 고르는 데 쓰지 않는다."""

import numpy as np
import pandas as pd

from src.features import build_features
from src.regime import SEARCH_AXES, choose, classify, evaluate, search_count, window_stats


def _prices(n=400, end_scale=1.0):
    index = pd.bdate_range("2000-01-03", periods=n)
    ixic = pd.Series(np.linspace(100.0, 180.0, n), index=index)
    ixic.iloc[-1] = ixic.iloc[-1] * end_scale
    frame = pd.DataFrame(
        {
            "ixic": ixic,
            "gspc": ixic * 0.8,
            "rf": 0.0,
            "sox": ixic * 1.05,
            "vix": 18.0,
        },
        index=index,
    )
    return frame


def test_features_ignore_future_close():
    base = build_features(_prices())
    changed = build_features(_prices(end_scale=3.0))
    for column in ("stretch", "roc", "dd", "rs", "accel", "semi"):
        pd.testing.assert_series_equal(base[column].iloc[:-1], changed[column].iloc[:-1])
    roc = base["roc"]
    known = base.index[300]
    close = _prices()["ixic"]
    expected = close.loc[known] / close.shift(252).loc[known] - 1.0
    assert roc.loc[known] == expected
    assert pd.isna(base["roc"].iloc[251])
    assert pd.notna(base["roc"].iloc[252])


def test_position_starts_the_next_day():
    state = np.array([0, 0, 1, 1, 1], dtype=np.int8)
    ret = np.array([0.0, 0.10, 0.10, -0.50, 0.0])
    rf = np.zeros(5)
    stats = window_stats(state, ret, rf, 1, 4)
    assert stats["terminal"] == 0.5
    assert stats["switches"] == 1
    assert stats["up_share"] == 1.0
    assert stats["mdd"] == -0.5


def test_confirm_days_keep_the_previous_state():
    n = 40
    roc = np.full(n, 0.0)
    stretch = np.zeros(n)
    dd = np.full(n, -0.01)
    rs = np.zeros(n)
    roc[:9] = 0.20
    state = classify(roc, stretch, dd, rs, 0.08, -0.05, -0.12, 0.0, 10)
    assert set(state.tolist()) == {0}

    roc[:] = 0.20
    state = classify(roc, stretch, dd, rs, 0.08, -0.05, -0.12, 0.0, 10)
    assert state[8] == 0
    assert state[9] == 1
    assert state[-1] == 1

    roc[:] = 0.20
    dd[-9:] = -0.20
    state = classify(roc, stretch, dd, rs, 0.08, -0.05, -0.12, 0.0, 10)
    assert state[-10] == 1
    assert state[-1] == 1


def _market(after=1.0):
    index = pd.bdate_range("1993-01-04", "2016-12-30")
    rng = np.random.default_rng(7)
    moves = rng.normal(0.0004, 0.012, len(index))
    moves = np.clip(moves, -0.08, 0.08)
    moves[index >= "2013-01-01"] *= after
    ixic = 100.0 * np.cumprod(1.0 + moves)
    gspc = 100.0 * np.cumprod(1.0 + moves * 0.7)
    return pd.DataFrame(
        {"ixic": ixic, "gspc": gspc, "rf": 0.01 / 252.0, "sox": ixic, "vix": 20.0},
        index=index,
    )


def test_holdout_returns_do_not_change_the_train_pick():
    first, _, _ = evaluate(build_features(_market(1.0)))
    second, _, _ = evaluate(build_features(_market(4.0)))
    train_cols = [column for column in first.columns if column.startswith("train") or column == "stable"]
    pd.testing.assert_frame_equal(first[train_cols], second[train_cols])


def test_search_lattice_steps_are_five_points():
    up, down, drawdown, relative, confirms = SEARCH_AXES
    assert up[0] == 0.0 and up[-1] == 0.40 and len(up) == 9
    assert down[0] == -0.40 and down[-1] == 0.0 and len(down) == 9
    assert drawdown[0] == -0.50 and drawdown[-1] == -0.10 and len(drawdown) == 9
    assert relative[0] == -0.10 and relative[-1] == 0.20 and len(relative) == 7
    assert confirms == (10, 21)
    assert search_count() == 9 * 9 * 9 * 7 * 2


def test_parallel_search_matches_serial():
    features = build_features(_market(1.0))
    serial, _, _ = evaluate(features, parallel=False)
    parallel, _, _ = evaluate(features, parallel=True)
    pd.testing.assert_frame_equal(serial, parallel)


def test_requested_cutoff_changes_which_days_are_scored():
    features = build_features(_market(4.0))
    early, _, _ = evaluate(features, train_end=pd.Timestamp("2008-12-31"))
    late, _, _ = evaluate(features, train_end=pd.Timestamp("2015-12-31"))
    assert not np.allclose(early["train_calmar"], late["train_calmar"])


def _row(**overrides):
    base = {
        "up_roc": 0.15,
        "down_roc": -0.15,
        "decline_dd": -0.18,
        "rs_min": 0.0,
        "confirm": 10,
        "train_calmar": 0.2,
        "train_terminal": 1.5,
        "train_mdd": -0.3,
        "train_cagr": 0.06,
        "train_up": 0.6,
        "train_down": 0.4,
        "train_switches": 6,
        "test_calmar": 3.0,
        "test_terminal": 4.0,
        "test_mdd": -0.2,
        "test_cagr": 0.12,
        "stable": True,
    }
    base.update(overrides)
    return base


def _baselines(calmar_10=0.5, calmar_21=0.4):
    def block(calmar, confirm):
        stats = {"calmar": calmar, "terminal": 1.2, "mdd": -0.4, "cagr": 0.05, "up_share": 0.5, "down_share": 0.5, "switches": 8}
        return {"confirm": confirm, "train": dict(stats), "test": dict(stats)}

    return {10: block(calmar_10, 10), 21: block(calmar_21, 21)}


def test_weaker_than_baseline_is_not_first():
    grid = pd.DataFrame([_row(train_calmar=0.2, test_calmar=9.0), _row(confirm=21, train_calmar=0.1)])
    picked = choose(grid, _baselines())
    assert picked["source"] == "기준선"
    assert picked["confirm"] == 10


def test_stable_rule_beats_a_higher_unstable_score():
    grid = pd.DataFrame(
        [
            _row(up_roc=0.25, train_calmar=2.0, stable=False),
            _row(up_roc=0.08, train_calmar=1.0, stable=True),
        ]
    )
    picked = choose(grid, _baselines(calmar_10=0.3))
    assert picked["source"] == "격자"
    assert picked["up_roc"] == 0.08
    assert picked["stable"] is True
