from __future__ import annotations

import numpy as np
import pandas as pd


def make_panel(scenario: str, n: int = 400) -> pd.DataFrame:
    idx = pd.bdate_range("2024-01-02", periods=n)
    rng = np.random.default_rng(7)
    spy = 400 + np.cumsum(rng.normal(0.05, 0.6, n))
    panel = pd.DataFrame(index=idx)
    panel["SPY"] = spy
    panel["QQQ"] = spy * 1.02 + np.cumsum(rng.normal(0, 0.2, n))
    panel["IWM"] = spy * 0.9 + np.cumsum(rng.normal(0, 0.3, n))
    panel["RSP"] = spy * 0.98
    panel["TLT"] = 90 + np.cumsum(rng.normal(0, 0.15, n))
    panel["IEF"] = 95 + np.cumsum(rng.normal(0, 0.08, n))
    panel["HYG"] = 75 + np.cumsum(rng.normal(0.01, 0.12, n))
    panel["LQD"] = 100 + np.cumsum(rng.normal(0, 0.06, n))
    panel["GLD"] = 180 + np.cumsum(rng.normal(0, 0.2, n))
    panel["UUP"] = 28 + np.cumsum(rng.normal(0, 0.03, n))
    panel["BIL"] = 90 + np.linspace(0, 4, n)
    panel["SHY"] = 80 + np.linspace(0, 2, n)
    panel["XLK"] = panel["QQQ"] * 0.5
    panel["XLU"] = 70 + np.cumsum(rng.normal(0, 0.1, n))
    panel["XLP"] = 75 + np.cumsum(rng.normal(0, 0.08, n))
    panel["XLF"] = 40 + np.cumsum(rng.normal(0, 0.12, n))
    panel["VIX"] = 16 + rng.normal(0, 1.0, n)
    panel["DGS2"] = 4.2 + np.cumsum(rng.normal(0, 0.01, n))
    panel["DGS10"] = 4.0 + np.cumsum(rng.normal(0, 0.01, n))
    panel["T10Y2Y"] = panel["DGS10"] - panel["DGS2"]
    panel["DFII10"] = 1.8 + np.cumsum(rng.normal(0, 0.01, n))
    panel["BAMLH0A0HYM2"] = 3.5 + np.cumsum(rng.normal(0, 0.02, n))
    panel["DTWEXBGS"] = 120 + np.cumsum(rng.normal(0, 0.05, n))
    panel["ICSA"] = 220_000 + rng.normal(0, 2000, n)
    # 월별 계단형 CPI — 일간 YoY가 12일로 붕괴하지 않게
    months = idx.to_period("M")
    cpi_level = 300.0 + (months.astype(int) - months.astype(int)[0]) * 0.3
    panel["CPIAUCSL"] = cpi_level.to_numpy()
    panel["T10YIE"] = 2.2 + np.cumsum(rng.normal(0, 0.005, n))

    last = slice(-60, None)
    base_spy = float(panel["SPY"].iloc[-61])
    if scenario == "bnign":
        panel.loc[panel.index[last], "ICSA"] = np.linspace(220_000, 280_000, 60)
        panel.loc[panel.index[last], "SPY"] = np.linspace(base_spy, base_spy * 1.08, 60)
        panel.loc[panel.index[last], "QQQ"] = panel.loc[panel.index[last], "SPY"] * 1.04
        panel.loc[panel.index[last], "DGS2"] = np.linspace(float(panel["DGS2"].iloc[-61]), float(panel["DGS2"].iloc[-61]) - 0.6, 60)
        panel.loc[panel.index[last], "DFII10"] = np.linspace(float(panel["DFII10"].iloc[-61]), float(panel["DFII10"].iloc[-61]) - 0.4, 60)
        panel.loc[panel.index[last], "BAMLH0A0HYM2"] = np.linspace(3.8, 3.1, 60)
        panel.loc[panel.index[last], "TLT"] = np.linspace(float(panel["TLT"].iloc[-61]), float(panel["TLT"].iloc[-61]) * 1.06, 60)
    elif scenario == "scare":
        panel.loc[panel.index[last], "ICSA"] = np.linspace(220_000, 300_000, 60)
        panel.loc[panel.index[last], "SPY"] = np.linspace(base_spy, base_spy * 0.90, 60)
        panel.loc[panel.index[last], "QQQ"] = panel.loc[panel.index[last], "SPY"] * 0.98
        panel.loc[panel.index[last], "IWM"] = panel.loc[panel.index[last], "SPY"] * 0.85
        panel.loc[panel.index[last], "DGS2"] = np.linspace(float(panel["DGS2"].iloc[-61]), float(panel["DGS2"].iloc[-61]) - 0.2, 60)
        panel.loc[panel.index[last], "BAMLH0A0HYM2"] = np.linspace(3.4, 5.2, 60)
        panel.loc[panel.index[last], "HYG"] = np.linspace(float(panel["HYG"].iloc[-61]), float(panel["HYG"].iloc[-61]) * 0.92, 60)
        panel.loc[panel.index[last], "VIX"] = np.linspace(16, 28, 60)
    elif scenario == "landing":
        panel.loc[panel.index[last], "ICSA"] = np.linspace(240_000, 200_000, 60)
        panel.loc[panel.index[last], "SPY"] = np.linspace(base_spy, base_spy * 1.07, 60)
        panel.loc[panel.index[last], "IWM"] = panel.loc[panel.index[last], "SPY"] * 0.95
        panel.loc[panel.index[last], "XLF"] = np.linspace(float(panel["XLF"].iloc[-61]), float(panel["XLF"].iloc[-61]) * 1.08, 60)
        panel.loc[panel.index[last], "DGS2"] = np.linspace(float(panel["DGS2"].iloc[-61]), float(panel["DGS2"].iloc[-61]) + 0.15, 60)
        panel.loc[panel.index[last], "BAMLH0A0HYM2"] = np.linspace(3.6, 3.2, 60)
    elif scenario == "inflation":
        panel.loc[panel.index[last], "ICSA"] = np.linspace(220_000, 210_000, 60)
        cpi0 = float(panel["CPIAUCSL"].iloc[-61])
        panel.loc[panel.index[last], "CPIAUCSL"] = np.linspace(cpi0, cpi0 * 1.05, 60)
        panel.loc[panel.index[last], "T10YIE"] = np.linspace(2.2, 2.8, 60)
        panel.loc[panel.index[last], "DGS2"] = np.linspace(float(panel["DGS2"].iloc[-61]), float(panel["DGS2"].iloc[-61]) + 0.8, 60)
        panel.loc[panel.index[last], "DTWEXBGS"] = np.linspace(float(panel["DTWEXBGS"].iloc[-61]), float(panel["DTWEXBGS"].iloc[-61]) * 1.04, 60)
        panel.loc[panel.index[last], "UUP"] = np.linspace(float(panel["UUP"].iloc[-61]), float(panel["UUP"].iloc[-61]) * 1.04, 60)
        panel.loc[panel.index[last], "SPY"] = np.linspace(base_spy, base_spy * 0.93, 60)
        panel.loc[panel.index[last], "TLT"] = np.linspace(float(panel["TLT"].iloc[-61]), float(panel["TLT"].iloc[-61]) * 0.90, 60)
        panel.loc[panel.index[last], "GLD"] = np.linspace(float(panel["GLD"].iloc[-61]), float(panel["GLD"].iloc[-61]) * 0.96, 60)
    return panel
