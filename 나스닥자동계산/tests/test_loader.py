import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import build_market, flatten_download, is_fresh, month_span, slice_dates, slice_years


class LoaderTests(unittest.TestCase):
    def test_flatten_either_column_order(self):
        dates = pd.bdate_range("2024-01-02", periods=3)
        wide = pd.DataFrame(
            {
                ("Open", "QQQ"): [100, 101, 102],
                ("Close", "QQQ"): [101, 100, 103],
                ("Adj Close", "QQQ"): [101, 100, 103],
            },
            index=dates,
        )
        flat = flatten_download(wide)
        self.assertIn("Close", flat.columns)
        swapped = wide.copy()
        swapped.columns = pd.MultiIndex.from_tuples([("QQQ", "Open"), ("QQQ", "Close"), ("QQQ", "Adj Close")])
        flat_swapped = flatten_download(swapped)
        self.assertIn("Adj Close", set(flat_swapped.columns))

    def test_adjustment_scales_the_open(self):
        dates = pd.bdate_range("2024-01-02", periods=2)
        price = pd.DataFrame(
            {"Open": [100.0, 110.0], "Close": [100.0, 110.0], "Adj Close": [50.0, 55.0]},
            index=dates,
        )
        irx = pd.DataFrame({"Close": [5.0, 5.0]}, index=dates)
        market = build_market(price, irx)
        self.assertAlmostEqual(market["close"].iloc[0], 50.0)
        self.assertAlmostEqual(market["open"].iloc[0], 50.0)
        self.assertGreater(market["rf"].iloc[1], 0.0)
        self.assertEqual(market["rf"].iloc[0], 0.0)

    def test_slice_and_freshness(self):
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2020-01-02", "2024-01-02", "2026-01-02"]),
                "open": [1, 2, 3],
                "close": [1, 2, 3],
                "rf": [0, 0, 0],
            }
        )
        sliced = slice_years(frame, 3)
        self.assertEqual(len(sliced), 2)
        self.assertEqual(str(sliced["date"].iloc[0].date()), "2024-01-02")
        self.assertTrue(is_fresh("2026-10-02", today="2026-10-06"))
        self.assertFalse(is_fresh("2026-09-01", today="2026-10-06"))
        self.assertEqual(len(slice_years(frame, None)), 3)
        ranged = slice_dates(frame, "2024-06-01", "2026-01-02")
        self.assertEqual(len(ranged), 1)
        self.assertEqual(month_span(frame["date"]), 3)


if __name__ == "__main__":
    unittest.main()
