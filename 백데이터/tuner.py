import numpy as np
import pandas as pd
from itertools import product
from typing import Callable, Dict, Tuple

def _evaluate_sell(params: Tuple[float, float, float, int],
                   df: pd.DataFrame,
                   reentry_strategy: str,
                   lockout_days: int,
                   buy_params: Tuple[float, float, float, float],
                   backtest_func: Callable) -> float:
    hl_thr, mcc_thr, tnx_mul, min_cond = params
    hl_thr_sell = hl_thr / 100.0
    result = backtest_func(
        df,
        hl_threshold_sell=hl_thr_sell,
        mcclellan_threshold_sell=mcc_thr,
        tnx_sma_factor_sell=tnx_mul,
        min_active_conditions_sell=min_cond,
        reentry_strategy=reentry_strategy,
        lockout_days=lockout_days,
        hl_threshold_buy=buy_params[0] / 100.0,
        mcclellan_threshold_buy=buy_params[1],
        tnx_sma_factor_buy=buy_params[2],
        sma_pct_buy=buy_params[3],
    )
    st_wealth = result["st_stats"]["cum_ret"]
    mdd = result["st_stats"]["mdd"]
    penalty = 0 if mdd > -0.20 else -abs(mdd)
    return st_wealth + penalty

def _evaluate_buy(params: Tuple[float, float, float, float],
                  df: pd.DataFrame,
                  sell_params: Tuple[float, float, float, int],
                  reentry_strategy: str,
                  lockout_days: int,
                  backtest_func: Callable) -> float:
    hl_thr, mcc_thr, tnx_mul, sma_pct = params
    result = backtest_func(
        df,
        hl_threshold_sell=sell_params[0] / 100.0,
        mcclellan_threshold_sell=sell_params[1],
        tnx_sma_factor_sell=sell_params[2],
        min_active_conditions_sell=sell_params[3],
        reentry_strategy=reentry_strategy,
        lockout_days=lockout_days,
        hl_threshold_buy=hl_thr / 100.0,
        mcclellan_threshold_buy=mcc_thr,
        tnx_sma_factor_buy=tnx_mul,
        sma_pct_buy=sma_pct,
    )
    return result["st_stats"]["cum_ret"]

def grid_search(
    df: pd.DataFrame,
    reentry_strategy: str,
    lockout_days: int,
    sell_grid: Dict[str, Tuple],
    buy_grid: Dict[str, Tuple],
    backtest_func: Callable,
) -> Tuple[Dict, Dict]:
    """Return best sell‑params and best buy‑params dicts.

    The search is a simple exhaustive grid over the provided ranges.
    """
    sell_candidates = list(product(
        sell_grid["hl_threshold_pct_sell"],
        sell_grid["mcclellan_threshold_sell"],
        sell_grid["tnx_sma_factor_sell"],
        sell_grid["min_active_conditions_sell"],
    ))
    best_sell_score = -np.inf
    best_sell = None
    # temporary buy defaults for sell evaluation
    buy_default = (
        1.5,   # hl_threshold_pct_buy (%): default
        5.0,   # mcclellan_threshold_buy
        1.02,  # tnx_sma_factor_buy
        0.0,   # sma_pct_buy
    )
    for cand in sell_candidates:
        score = _evaluate_sell(cand, df, reentry_strategy, lockout_days, buy_default, backtest_func)
        if score > best_sell_score:
            best_sell_score = score
            best_sell = cand

    # BUY SEARCH using best sell params
    buy_candidates = list(product(
        buy_grid["hl_threshold_pct_buy"],
        buy_grid["mcclellan_threshold_buy"],
        buy_grid["tnx_sma_factor_buy"],
        buy_grid["sma_pct_buy"],
    ))
    best_buy_score = -np.inf
    best_buy = None
    for cand in buy_candidates:
        score = _evaluate_buy(cand, df, best_sell, reentry_strategy, lockout_days, backtest_func)
        if score > best_buy_score:
            best_buy_score = score
            best_buy = cand

    sell_dict = {
        "hl_threshold_pct_sell": best_sell[0],
        "mcclellan_threshold_sell": best_sell[1],
        "tnx_sma_factor_sell": best_sell[2],
        "min_active_conditions_sell": best_sell[3],
    }
    buy_dict = {
        "hl_threshold_pct_buy": best_buy[0],
        "mcclellan_threshold_buy": best_buy[1],
        "tnx_sma_factor_buy": best_buy[2],
        "sma_pct_buy": best_buy[3],
    }
    return sell_dict, buy_dict
