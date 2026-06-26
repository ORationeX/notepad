import numpy as np
import pandas as pd
from itertools import product
from typing import Callable, Dict, Tuple, Any

def _evaluate_sell_generic(
    sell_kwargs: Dict[str, Any],
    df: pd.DataFrame,
    reentry_strategy: str,
    lockout_days: int,
    buy_defaults: Dict[str, Any],
    backtest_func: Callable
) -> float:
    kwargs = {}
    
    # 매도 파라미터 바인딩
    for k, v in sell_kwargs.items():
        if k == "hl_threshold_pct_sell":
            kwargs["hl_threshold_sell"] = float(v) / 100.0
        else:
            kwargs[k] = v
            
    # 매수 디폴트 파라미터 바인딩
    for k, v in buy_defaults.items():
        if k == "hl_threshold_pct_buy":
            kwargs["hl_threshold_buy"] = float(v) / 100.0
        else:
            kwargs[k] = v
            
    result = backtest_func(
        df,
        reentry_strategy=reentry_strategy,
        lockout_days=lockout_days,
        **kwargs
    )
    st_wealth = result["st_stats"]["cum_ret"]
    mdd = result["st_stats"]["mdd"]
    penalty = 0 if mdd > -0.20 else -abs(mdd)
    return st_wealth + penalty

def _evaluate_buy_generic(
    buy_kwargs: Dict[str, Any],
    df: pd.DataFrame,
    sell_best: Dict[str, Any],
    reentry_strategy: str,
    lockout_days: int,
    backtest_func: Callable
) -> float:
    kwargs = {}
    
    # 최적의 매도 파라미터 바인딩
    for k, v in sell_best.items():
        if k == "hl_threshold_pct_sell":
            kwargs["hl_threshold_sell"] = float(v) / 100.0
        else:
            kwargs[k] = v
            
    # 매수 파라미터 바인딩
    for k, v in buy_kwargs.items():
        if k == "hl_threshold_pct_buy":
            kwargs["hl_threshold_buy"] = float(v) / 100.0
        else:
            kwargs[k] = v
            
    result = backtest_func(
        df,
        reentry_strategy=reentry_strategy,
        lockout_days=lockout_days,
        **kwargs
    )
    return result["st_stats"]["cum_ret"]

def grid_search(
    df: pd.DataFrame,
    reentry_strategy: str,
    lockout_days: int,
    sell_grid: Dict[str, Tuple],
    buy_grid: Dict[str, Tuple],
    backtest_func: Callable,
    progress_callback: Callable[[float], None] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """유동적인 키를 기반으로 그리드 서치를 수행하고 진행 상황 콜백을 지원함."""
    sell_keys = list(sell_grid.keys())
    sell_candidates = list(product(*[sell_grid[k] for k in sell_keys]))
    
    buy_keys = list(buy_grid.keys())
    buy_candidates = list(product(*[buy_grid[k] for k in buy_keys]))
    
    total_steps = len(sell_candidates) + len(buy_candidates)
    current_step = 0
    
    # 매수 디폴트 설정
    buy_default = {}
    for k in buy_keys:
        buy_default[k] = buy_grid[k][0]
        
    best_sell_score = -np.inf
    best_sell_vals = None
    
    # 1. 매도 파라미터 탐색
    for cand in sell_candidates:
        sell_kwargs = dict(zip(sell_keys, cand))
        score = _evaluate_sell_generic(sell_kwargs, df, reentry_strategy, lockout_days, buy_default, backtest_func)
        if score > best_sell_score:
            best_sell_score = score
            best_sell_vals = cand
            
        current_step += 1
        if progress_callback:
            progress_callback(current_step / total_steps)
            
    best_sell_dict = dict(zip(sell_keys, best_sell_vals))
    
    # 2. 매수 파라미터 탐색
    best_buy_score = -np.inf
    best_buy_vals = None
    
    for cand in buy_candidates:
        buy_kwargs = dict(zip(buy_keys, cand))
        score = _evaluate_buy_generic(buy_kwargs, df, best_sell_dict, reentry_strategy, lockout_days, backtest_func)
        if score > best_buy_score:
            best_buy_score = score
            best_buy_vals = cand
            
        current_step += 1
        if progress_callback:
            progress_callback(current_step / total_steps)
            
    best_buy_dict = dict(zip(buy_keys, best_buy_vals))
    
    return best_sell_dict, best_buy_dict
