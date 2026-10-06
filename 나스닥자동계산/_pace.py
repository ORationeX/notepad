import numpy as np
import pandas as pd

from src.data_loader import slice_years
from src.engine import run_formula
from src.search import describe, holdout_split, monthly_min, pick, search_table

frame = slice_years(pd.read_parquet("data/qqq.parquet"), 10)
opens = frame["open"].to_numpy(np.float64)
closes = frame["close"].to_numpy(np.float64)
rfs = frame["rf"].to_numpy(np.float64)
dates = pd.to_datetime(frame["date"])
split = holdout_split(len(frame))
need = monthly_min(len(frame))
print("days", len(frame), "min_trades", need, flush=True)
table = search_table(opens, closes, rfs, split=split)
raw = table.sort_values("terminal", ascending=False).iloc[0]
best = pick(table, "terminal", min_trades=need)
best30 = pick(table, "terminal", initial=0.30, min_trades=need)
print("raw", int(raw["trades"]), round(float(raw["terminal"]), 3), describe(raw), flush=True)
print("best", int(best["trades"]), round(float(best["terminal"]), 3), "floor", round(float(best["floor"]), 3), flush=True)
print(describe(best), flush=True)
print("i30", int(best30["trades"]), round(float(best30["terminal"]), 3), describe(best30), flush=True)
detail = run_formula(opens, closes, rfs, best["initial"], best["up"], best["down"], best["sell"], best["buy"], dates=dates)
points = [dates.iloc[0]]
for row in detail.trades:
    if row["side"] != "시작":
        points.append(pd.Timestamp(row["date"]))
points.append(dates.iloc[-1])
gaps = [(points[i + 1] - points[i]).days for i in range(len(points) - 1)]
print("idle_max", max(gaps), "idle_median", int(np.median(gaps)), "trades", len(detail.trades) - 1, flush=True)
held = run_formula(opens, closes, rfs, 1, 10, 10, 0, 0)
print("hold", round(held.terminal, 3), flush=True)
