import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.engine import eval_params, run_formula


def _flat(n, price=100.0, rf=0.0):
    closes = np.full(n, price, dtype=np.float64)
    opens = closes.copy()
    rfs = np.zeros(n, dtype=np.float64)
    rfs[1:] = rf
    return opens, closes, rfs


class EngineTests(unittest.TestCase):
    def test_sell_then_buy_matches_hand_calculation(self):
        prices = np.array([100, 100, 106, 106, 100, 100], dtype=np.float64)
        rfs = np.zeros(len(prices))
        result = run_formula(prices, prices, rfs, 0.5, 0.05, 0.05, 0.5, 0.5)
        shares = 0.5 / 100.0
        qty = shares * 0.5
        cash = 0.5 + qty * 106.0
        wealth = (shares - qty) * 100.0 + cash
        self.assertEqual(result.sells, 1)
        self.assertEqual(result.buys, 1)
        self.assertAlmostEqual(result.terminal, wealth, places=10)
        self.assertAlmostEqual(result.mdd, wealth / 1.03 - 1.0, places=10)
        self.assertEqual([row["side"] for row in result.trades], ["시작", "매도", "매수"])

    def test_cost_lowers_the_same_path(self):
        prices = np.array([100, 100, 106, 106, 100, 100], dtype=np.float64)
        rfs = np.zeros(len(prices))
        plain = run_formula(prices, prices, rfs, 0.5, 0.05, 0.05, 0.5, 0.5, cost=0.0)
        costly = run_formula(prices, prices, rfs, 0.5, 0.05, 0.05, 0.5, 0.5, cost=0.01)
        self.assertLess(costly.terminal, plain.terminal)

    def test_idle_cash_compounds(self):
        opens, closes, rfs = _flat(5, rf=0.01)
        result = run_formula(opens, closes, rfs, 0.5, 0.5, 0.5, 0.0, 0.0)
        cash = 0.5 * (1.01 ** 4)
        self.assertAlmostEqual(result.terminal, cash + 0.5, places=10)
        self.assertEqual(result.buys, 0)
        self.assertEqual(result.sells, 0)

    def test_buy_hold_is_close_to_close(self):
        rng = np.random.default_rng(7)
        closes = 100 * np.cumprod(1 + rng.normal(0.0005, 0.01, 80))
        opens = closes * (1 + rng.normal(0, 0.002, 80))
        opens = np.maximum(opens, 1.0)
        rfs = np.full(80, 0.0001)
        result = run_formula(opens, closes, rfs, 1.0, 10.0, 10.0, 0.0, 0.0)
        self.assertAlmostEqual(result.terminal, closes[-1] / closes[0], places=10)
        self.assertAlmostEqual(result.mdd, _drawdown(closes / closes[0]), places=10)

    def test_grid_matches_path_and_train_prefix(self):
        rng = np.random.default_rng(3)
        closes = 100 * np.cumprod(1 + rng.normal(0.0003, 0.012, 90))
        opens = np.maximum(closes * (1 + rng.normal(0, 0.001, 90)), 1.0)
        rfs = np.full(90, 0.00005)
        params = np.array(
            [
                [0.3, 0.05, 0.05, 0.25, 0.25],
                [1.0, 0.1, 0.1, 0.5, 0.5],
                [0.5, 0.03, 0.2, 1.0, 0.1],
            ],
            dtype=np.float64,
        )
        split = 50
        raw = eval_params(opens, closes, rfs, params, cost=0.001, split=split)
        for i, row in enumerate(params):
            full = run_formula(opens, closes, rfs, *row, cost=0.001)
            train = run_formula(opens[:split], closes[:split], rfs[:split], *row, cost=0.001)
            self.assertAlmostEqual(raw[i, 0], full.terminal, places=8)
            self.assertAlmostEqual(raw[i, 1], full.mdd, places=8)
            self.assertEqual(int(raw[i, 4]), full.buys)
            self.assertEqual(int(raw[i, 5]), full.sells)
            self.assertAlmostEqual(raw[i, 6], full.avg_weight, places=8)
            self.assertAlmostEqual(raw[i, 7], train.terminal, places=8)
            self.assertEqual(int(raw[i, 11]), train.buys)
            self.assertEqual(int(raw[i, 12]), train.sells)

    def test_buy_stops_at_the_weight_cap(self):
        prices = np.array([100, 90, 90], dtype=np.float64)
        rfs = np.zeros(len(prices))
        plain = run_formula(prices, prices, rfs, 0.3, 0.5, 0.05, 0.0, 1.0, max_weight=1.0)
        capped = run_formula(prices, prices, rfs, 0.3, 0.5, 0.05, 0.0, 1.0, max_weight=0.5)
        self.assertGreater(plain.weights[-1], 0.9)
        self.assertLessEqual(capped.weights[-1], 0.5 + 1e-8)
        self.assertEqual(capped.buys, 1)
        self.assertAlmostEqual(capped.weights[-1], 0.5, places=6)

    def test_thresholds_block_small_moves(self):
        prices = np.array([100, 103, 103, 97, 97], dtype=np.float64)
        result = run_formula(prices, prices, np.zeros(5), 0.4, 0.05, 0.05, 1.0, 1.0)
        self.assertEqual(result.buys, 0)
        self.assertEqual(result.sells, 0)


def _drawdown(wealth):
    peak = np.maximum.accumulate(wealth)
    return float(np.min(wealth / peak - 1.0))


if __name__ == "__main__":
    unittest.main()
