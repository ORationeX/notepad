import sys
import os
sys.path.insert(0, os.path.abspath("."))
import time
import numpy as np
import pandas as pd
import tuner

if __name__ == "__main__":
    n_days = 2000
    dates = pd.date_range("2016-01-01", periods=n_days)
    df = pd.DataFrame({
        "Date": dates,
        "New_Highs_Pct": np.random.uniform(0.01, 0.05, n_days),
        "New_Lows_Pct": np.random.uniform(0.01, 0.05, n_days),
        "McClellan_Oscillator": np.random.uniform(-50, 50, n_days),
        "TNX_Close": np.random.uniform(1.5, 4.5, n_days),
        "TNX_Close_SMA20": np.random.uniform(1.5, 4.5, n_days),
        "VIX_Spread_Ratio": np.random.uniform(0.8, 1.3, n_days),
        "OAS_Close": np.random.uniform(2.0, 5.0, n_days),
        "QQQ_Close": np.cumprod(1 + np.random.normal(0.0005, 0.01, n_days)) * 100,
        "QQQ_Open": np.cumprod(1 + np.random.normal(0.0005, 0.01, n_days)) * 100,
        "QQQ_SMA50": np.cumprod(1 + np.random.normal(0.0005, 0.01, n_days)) * 100,
        "QQQ_SMA20": np.cumprod(1 + np.random.normal(0.0005, 0.01, n_days)) * 100,
    })

    sell_grid = {
        "hl_threshold_pct_sell": np.arange(1.0, 4.0, 0.5), # 6
        "mcclellan_threshold_sell": np.arange(-20, 20, 5), # 8
        "tnx_sma_factor_sell": np.arange(1.00, 1.05, 0.01), # 5
        "vix_spread_threshold_sell": np.arange(0.9, 1.1, 0.05), # 4
        "oas_threshold_sell": np.arange(2.0, 4.0, 0.5), # 4
        "min_active_conditions_sell": (2, 3, 4), # 3
    }
    # 6*8*5*4*4*3 = 11,520개 매도 조합

    buy_grid = {
        "hl_threshold_pct_buy": np.arange(1.0, 3.0, 0.5), # 4
        "mcclellan_threshold_buy": np.arange(-10, 20, 5), # 6
        "tnx_sma_factor_buy": np.arange(0.98, 1.04, 0.01), # 6
        "vix_spread_threshold_buy": np.arange(0.9, 1.1, 0.05), # 4
        "oas_threshold_buy": np.arange(2.0, 4.0, 0.5), # 4
        "sma_pct_buy": np.arange(0.0, 2.0, 0.5), # 4
    }
    # 4*6*6*4*4*4 = 9,216개 매수 조합
    # 총 20,736 조합!

    buy_defaults = (1.5, 5.0, 1.02, 1.0, 4.5, 0.0)

    n_sell = np.prod([len(v) for v in sell_grid.values()])
    n_buy = np.prod([len(v) for v in buy_grid.values()])
    print(f"Starting test: {n_sell} sell combinations + {n_buy} buy combinations = {n_sell + n_buy} total combinations...")
    t0 = time.time()

    best_sell, best_buy = tuner.optimize_all_signals(
        df=df,
        selected_asset="QQQ",
        reentry_strategy="multi_cond",
        lockout_days=20,
        sell_grid=sell_grid,
        buy_grid=buy_grid,
        buy_defaults_tuple=buy_defaults,
        progress_callback=lambda pct, msg: print(f"[{pct*100:.1f}%] {msg}") if int(pct*100)%25==0 else None
    )
    elapsed = time.time() - t0
    print(f"Done 20,736 backtests in {elapsed:.2f} seconds! (Speed: {(n_sell+n_buy)/elapsed:.0f} backtests/sec)")
    print("Best sell:", best_sell)
    print("Best buy:", best_buy)
