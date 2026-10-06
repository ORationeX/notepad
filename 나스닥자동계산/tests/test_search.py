import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.engine import eval_params, run_formula
from src.search import (
    BUYS,
    DOWNS,
    INITIALS,
    SELLS,
    UPS,
    build_params,
    grid_count,
    initials_for,
    holdout_split,
    load_table,
    neighborhood,
    neighbor_floor,
    pick,
    save_table,
    search_table,
    select_leaders,
)


class SearchTests(unittest.TestCase):
    def test_default_grid_size(self):
        self.assertEqual(len(INITIALS), 20)
        self.assertEqual(len(UPS), 38)
        self.assertEqual(len(DOWNS), 38)
        self.assertEqual(len(SELLS), 20)
        self.assertEqual(len(BUYS), 20)
        self.assertEqual(grid_count(), 20 * 38 * 38 * 20 * 20)
        self.assertAlmostEqual(float(UPS[0]), 0.02)
        self.assertAlmostEqual(float(UPS[28]), 0.30)
        self.assertAlmostEqual(float(UPS[-1]), 2.00)
        self.assertEqual(len(np.unique(np.round(UPS, 2))), 38)
        self.assertAlmostEqual(float(np.max(np.abs(np.diff(UPS[:29]) - 0.01))), 0.0, places=6)
        small = build_params(
            initials=np.array([0.3, 1.0]),
            ups=np.array([0.05]),
            downs=np.array([0.05, 0.10]),
            sells=np.array([0.25]),
            buys=np.array([0.25, 1.0]),
        )
        self.assertEqual(len(small), 8)
        self.assertTrue(np.allclose(small[0], [0.3, 0.05, 0.05, 0.25, 0.25]))
        self.assertTrue(np.allclose(small[-1], [1.0, 0.05, 0.10, 0.25, 1.0]))

    def test_holdout_split_needs_two_years(self):
        self.assertIsNone(holdout_split(400))
        self.assertIsNotNone(holdout_split(752))
        split = holdout_split(1000)
        self.assertIsNotNone(split)
        self.assertGreaterEqual(split, 252)
        self.assertGreaterEqual(1000 - split, 126)

    def test_neighborhood_stays_inside_bounds_and_can_lock_initial(self):
        near = neighborhood(np.array([1.0, 0.03, 0.30, 0.10, 1.0]))
        self.assertTrue(((near[:, 0] >= 0.05) & (near[:, 0] <= 1.0)).all())
        self.assertTrue(((near[:, 1] >= 0.02) & (near[:, 1] <= 0.40)).all())
        locked = neighborhood(np.array([0.30, 0.05, 0.05, 0.25, 0.25]), lock_initial=True)
        self.assertTrue(np.allclose(locked[:, 0], 0.30))

    def test_smooth_uptrend_prefers_staying_invested(self):
        prices = 100 * np.cumprod(np.r_[1.0, np.full(250, 1.002)])
        rfs = np.zeros(len(prices))
        grid = build_params(
            initials=np.array([0.3, 1.0]),
            ups=np.array([0.05, 0.30]),
            downs=np.array([0.05]),
            sells=np.array([0.10, 1.0]),
            buys=np.array([0.25]),
        )
        table = search_table(prices, prices, rfs, params=grid)
        chosen = pick(table, "terminal")
        held = run_formula(prices, prices, rfs, 1.0, 10.0, 10.0, 0.0, 0.0)
        self.assertEqual(chosen["initial"], 1.0)
        self.assertEqual(chosen["up"], 0.30)
        self.assertEqual(chosen["sell"], 0.10)
        self.assertGreaterEqual(chosen["sells"], 1)
        self.assertLess(chosen["terminal"], held.terminal)

    def test_smooth_decline_avoids_full_investment(self):
        prices = 100 * np.cumprod(np.r_[1.0, np.full(200, 0.998)])
        rfs = np.zeros(len(prices))
        grid = build_params(
            initials=np.array([0.1, 0.5, 1.0]),
            ups=np.array([0.05]),
            downs=np.array([0.05, 0.30]),
            sells=np.array([0.5]),
            buys=np.array([0.10, 1.0]),
        )
        table = search_table(prices, prices, rfs, params=grid)
        chosen = pick(table, "terminal")
        held = run_formula(prices, prices, rfs, 1.0, 10.0, 10.0, 0.0, 0.0)
        self.assertGreater(chosen["terminal"], held.terminal)
        self.assertEqual(chosen["initial"], 0.1)

    def test_round_trip_at_the_extremes_beats_holding(self):
        prices = np.array(
            [100, 110, 110, 100, 90, 90, 100, 110, 110, 100, 90, 90, 100],
            dtype=np.float64,
        )
        rfs = np.zeros(len(prices))
        good = (0.5, 0.05, 0.05, 0.5, 0.5)
        traded = run_formula(prices, prices, rfs, *good)
        held = run_formula(prices, prices, rfs, 1.0, 10.0, 10.0, 0.0, 0.0)
        self.assertGreater(traded.terminal, held.terminal + 0.01)
        grid = build_params(
            initials=np.array([0.5, 1.0]),
            ups=np.array([0.05, 0.20]),
            downs=np.array([0.05, 0.20]),
            sells=np.array([0.5, 1.0]),
            buys=np.array([0.5, 1.0]),
        )
        table = search_table(prices, prices, rfs, params=grid)
        chosen = pick(table, "terminal")
        self.assertGreaterEqual(chosen["terminal"] + 1e-9, traded.terminal)

    def test_neighbor_floor_uses_one_step_on_every_axis(self):
        values = np.ones(16, dtype=np.float64)
        values[0] = 10.0
        floor = neighbor_floor(values, (2, 2, 2, 2))
        self.assertAlmostEqual(float(floor[0]), 1.0)
        self.assertGreater(float(floor[-1]), 0.99)

    def test_pick_skips_a_threshold_spike(self):
        table = pd.DataFrame(
            [
                {
                    "initial": 0.05, "up": 0.21, "down": 0.02, "sell": 1.0, "buy": 1.0,
                    "terminal": 10.0, "trades": 4, "buys": 2, "sells": 2, "floor": 1.5,
                },
                {
                    "initial": 1.0, "up": 0.20, "down": 0.03, "sell": 0.75, "buy": 1.0,
                    "terminal": 8.0, "trades": 6, "buys": 3, "sells": 3, "floor": 7.0,
                },
            ]
        )
        chosen = pick(table, "terminal")
        self.assertAlmostEqual(float(chosen["terminal"]), 8.0)
        self.assertAlmostEqual(float(chosen["up"]), 0.20)

    def test_initials_stop_at_the_weight_cap(self):
        capped = initials_for(0.70)
        self.assertAlmostEqual(float(capped.max()), 0.70)
        self.assertTrue(np.any(np.isclose(capped, 0.30)))
        self.assertFalse(np.any(np.isclose(capped, 1.0)))

    def test_pick_keeps_a_formula_that_trades_every_month(self):
        table = pd.DataFrame(
            [
                {
                    "initial": 1.0, "up": 0.20, "down": 0.05, "sell": 1.0, "buy": 1.0,
                    "terminal": 10.0, "trades": 3, "buys": 1, "sells": 2,
                },
                {
                    "initial": 0.30, "up": 0.05, "down": 0.05, "sell": 0.25, "buy": 0.25,
                    "terminal": 4.0, "trades": 40, "buys": 20, "sells": 20,
                },
            ]
        )
        chosen = pick(table, "terminal", min_trades=12)
        self.assertEqual(int(chosen["trades"]), 40)
        self.assertAlmostEqual(float(chosen["initial"]), 0.30)

    def test_pick_prefers_fewer_trades_on_a_tie(self):
        table = pd.DataFrame(
            [
                {"initial": 0.3, "up": 0.05, "down": 0.05, "sell": 0.5, "buy": 0.5,
                 "terminal": 1.2, "trades": 30, "buys": 15, "sells": 15},
                {"initial": 0.3, "up": 0.10, "down": 0.05, "sell": 0.5, "buy": 0.5,
                 "terminal": 1.2, "trades": 4, "buys": 2, "sells": 2},
            ]
        )
        chosen = pick(table, "terminal")
        self.assertEqual(chosen["trades"], 4)
        self.assertEqual(chosen["up"], 0.10)

    def test_table_cache_round_trip(self):
        table = pd.DataFrame({"initial": [0.3], "terminal": [1.5]})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search_table.parquet"
            save_table(path, "abc", table)
            self.assertIsNone(load_table(path, "다른키"))
            loaded = load_table(path, "abc")
            self.assertAlmostEqual(float(loaded["terminal"].iloc[0]), 1.5)

    def test_objective_names_exist_on_the_default_columns(self):
        self.assertTrue(np.any(np.isclose(INITIALS, 0.30)))
        self.assertTrue(np.any(np.isclose(UPS, 0.05)))
        self.assertTrue(np.any(np.isclose(SELLS, 0.25)))
        self.assertTrue(np.any(np.isclose(BUYS, 0.25)))

    def test_leaders_keep_the_same_winner_as_the_full_table(self):
        prices = 100 * np.cumprod(np.r_[1.0, np.full(80, 1.001)])
        prices = np.where(np.arange(len(prices)) % 17 == 0, prices * 0.9, prices)
        rfs = np.zeros(len(prices))
        params = build_params(
            initials=np.array([0.3, 1.0]),
            ups=np.array([0.05, 0.10, 0.20]),
            downs=np.array([0.05, 0.10]),
            sells=np.array([0.25, 0.5, 1.0]),
            buys=np.array([0.25, 1.0]),
        )
        split = 50
        raw = eval_params(prices, prices, rfs, params, split=split)
        full = search_table(prices, prices, rfs, split=split, params=params)
        leaders = select_leaders(params, raw, len(prices), split, keep=5)
        self.assertLess(len(leaders), len(full))
        full_best = pick(full, "terminal")
        lead_best = pick(leaders, "terminal")
        self.assertTrue(np.allclose(
            [full_best[name] for name in ("initial", "up", "down", "sell", "buy")],
            [lead_best[name] for name in ("initial", "up", "down", "sell", "buy")],
        ))
        train_full = pick(full, "train_terminal", buys_col="train_buys", sells_col="train_sells")
        train_lead = pick(leaders, "train_terminal", buys_col="train_buys", sells_col="train_sells")
        self.assertAlmostEqual(float(train_full["train_terminal"]), float(train_lead["train_terminal"]))
        held = run_formula(prices, prices, rfs, *full_best[["initial", "up", "down", "sell", "buy"]], cost=0.0)
        self.assertAlmostEqual(float(full_best["cagr"]), held.cagr, places=6)
        self.assertAlmostEqual(float(full_best["sharpe"]), held.sharpe, places=6)
        self.assertAlmostEqual(float(full_best["calmar"]), held.calmar, places=6)


if __name__ == "__main__":
    unittest.main()
