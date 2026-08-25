import os
import numpy as np
import pandas as pd
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Dict, Tuple, Any, List

def prepare_fast_data(df: pd.DataFrame, selected_asset: str = "QQQ") -> Dict[str, np.ndarray]:
    """DataFrame에서 백테스트에 필요한 컬럼들을 순수 1차원 NumPy 배열로 추출하여 캐싱."""
    data = df.reset_index()
    n_days = len(data)
    
    close_col = f"{selected_asset}_Close"
    open_col = f"{selected_asset}_Open"
    sma50_col = f"{selected_asset}_SMA50"
    sma20_col = f"{selected_asset}_SMA20"
    
    def _to_arr(col: str, fill_val: float = 0.0) -> np.ndarray:
        if col in data.columns:
            return data[col].fillna(fill_val).to_numpy(dtype=np.float64)
        return np.zeros(n_days, dtype=np.float64)

    return {
        "n_days": n_days,
        "new_highs_pct": _to_arr("New_Highs_Pct"),
        "new_lows_pct": _to_arr("New_Lows_Pct"),
        "mcclellan": _to_arr("McClellan_Oscillator"),
        "tnx_close": _to_arr("TNX_Close"),
        "tnx_sma20": _to_arr("TNX_Close_SMA20", 1.0),
        "vix_spread_ratio": _to_arr("VIX_Spread_Ratio", 1.0),
        "oas_close": _to_arr("OAS_Close", 0.0),
        "asset_close": _to_arr(close_col, 1.0),
        "asset_open": _to_arr(open_col, 1.0),
        "asset_sma50": _to_arr(sma50_col, 1.0),
        "asset_sma20": _to_arr(sma20_col, 1.0),
    }

def _rolling_5_max_uint8(arr_bool: np.ndarray, n: int) -> np.ndarray:
    """최근 5일 롤링 max를 넘파이 비트연산으로 초고속(O(1) 수준) 계산."""
    r = arr_bool.astype(np.uint8)
    roll = r.copy()
    if n > 1:
        roll[1:] |= r[:-1]
    if n > 2:
        roll[2:] |= r[:-2]
    if n > 3:
        roll[3:] |= r[:-3]
    if n > 4:
        roll[4:] |= r[:-4]
    return roll

def fast_eval_sell(
    sell_params: Tuple[float, float, float, float, float, int],
    fast_data: Dict[str, np.ndarray],
    reentry_strategy: str,
    lockout_days: int,
    buy_params: Tuple[float, float, float, float, float, float]
) -> float:
    """매도 파라미터 탐색용 초고속 백테스트 평가."""
    hl_sell_pct, mcc_sell, tnx_f_sell, vix_sell, oas_sell, min_active_sell = sell_params
    hl_sell = hl_sell_pct / 100.0
    
    hl_buy_pct, mcc_buy, tnx_f_buy, vix_buy, oas_buy, sma_pct_buy = buy_params
    hl_buy = hl_buy_pct / 100.0
    
    n_days = fast_data["n_days"]
    
    # 매도 조건 평가
    c_a = (fast_data["new_highs_pct"] > hl_sell) & (fast_data["new_lows_pct"] > hl_sell)
    c_b = fast_data["mcclellan"] <= mcc_sell
    c_c = fast_data["tnx_close"] > (tnx_f_sell * fast_data["tnx_sma20"])
    c_d = fast_data["vix_spread_ratio"] > vix_sell
    c_e = fast_data["oas_close"] > oas_sell
    
    roll_a = _rolling_5_max_uint8(c_a, n_days)
    roll_b = _rolling_5_max_uint8(c_b, n_days)
    roll_c = _rolling_5_max_uint8(c_c, n_days)
    roll_d = _rolling_5_max_uint8(c_d, n_days)
    roll_e = _rolling_5_max_uint8(c_e, n_days)
    
    active_count = roll_a + roll_b + roll_c + roll_d + roll_e
    alarm_sell = active_count >= min_active_sell
    
    # 매수 조건 사전 계산 (multi_cond 용)
    if reentry_strategy == "multi_cond":
        buy_ok = (
            (fast_data["new_lows_pct"] <= hl_buy) &
            (fast_data["mcclellan"] > mcc_buy) &
            (fast_data["tnx_close"] <= (tnx_f_buy * fast_data["tnx_sma20"])) &
            (fast_data["vix_spread_ratio"] <= vix_buy) &
            (fast_data["oas_close"] <= oas_buy)
        )
    else:
        buy_ok = None
        
    close_arr = fast_data["asset_close"]
    open_arr = fast_data["asset_open"]
    sma50_arr = fast_data["asset_sma50"]
    sma20_arr = fast_data["asset_sma20"]
    mcc_arr = fast_data["mcclellan"]
    
    wealth = 1.0
    max_wealth = 1.0
    min_dd = 0.0
    
    holding = True
    lockout_cnt = 0
    
    for t in range(1, n_days):
        prev_alarm = alarm_sell[t-1]
        
        if holding:
            if prev_alarm:
                holding = False
                lockout_cnt = lockout_days
                wealth *= (open_arr[t] / close_arr[t-1])
            else:
                wealth *= (close_arr[t] / close_arr[t-1])
        else:
            if lockout_cnt > 0:
                lockout_cnt -= 1
            can_reenter = False
            if not prev_alarm and lockout_cnt == 0:
                if reentry_strategy == "lockout":
                    can_reenter = True
                elif reentry_strategy == "sma50":
                    threshold = sma50_arr[t-1] * (1.0 + sma_pct_buy / 100.0)
                    if close_arr[t-1] > threshold:
                        can_reenter = True
                elif reentry_strategy == "sma20":
                    threshold = sma20_arr[t-1] * (1.0 + sma_pct_buy / 100.0)
                    if close_arr[t-1] > threshold:
                        can_reenter = True
                elif reentry_strategy == "mcclellan":
                    if mcc_arr[t-1] > mcc_buy:
                        can_reenter = True
                elif reentry_strategy == "multi_cond":
                    if buy_ok[t-1]:
                        can_reenter = True
                        
            if can_reenter:
                holding = True
                wealth *= (close_arr[t] / open_arr[t])
                
        if wealth > max_wealth:
            max_wealth = wealth
        else:
            dd = (wealth - max_wealth) / max_wealth
            if dd < min_dd:
                min_dd = dd
                
    cum_ret = wealth - 1.0
    penalty = 0.0 if min_dd > -0.20 else -abs(min_dd)
    return cum_ret + penalty

def fast_eval_buy(
    buy_params: Tuple[float, float, float, float, float, float],
    fast_data: Dict[str, np.ndarray],
    alarm_sell: np.ndarray,
    reentry_strategy: str,
    lockout_days: int
) -> float:
    """매수 파라미터 탐색용 초고속 백테스트 평가 (매도 알람 마스크는 사전 계산되어 재활용)."""
    hl_buy_pct, mcc_buy, tnx_f_buy, vix_buy, oas_buy, sma_pct_buy = buy_params
    hl_buy = hl_buy_pct / 100.0
    
    n_days = fast_data["n_days"]
    
    if reentry_strategy == "multi_cond":
        buy_ok = (
            (fast_data["new_lows_pct"] <= hl_buy) &
            (fast_data["mcclellan"] > mcc_buy) &
            (fast_data["tnx_close"] <= (tnx_f_buy * fast_data["tnx_sma20"])) &
            (fast_data["vix_spread_ratio"] <= vix_buy) &
            (fast_data["oas_close"] <= oas_buy)
        )
    else:
        buy_ok = None
        
    close_arr = fast_data["asset_close"]
    open_arr = fast_data["asset_open"]
    sma50_arr = fast_data["asset_sma50"]
    sma20_arr = fast_data["asset_sma20"]
    mcc_arr = fast_data["mcclellan"]
    
    wealth = 1.0
    holding = True
    lockout_cnt = 0
    
    for t in range(1, n_days):
        prev_alarm = alarm_sell[t-1]
        
        if holding:
            if prev_alarm:
                holding = False
                lockout_cnt = lockout_days
                wealth *= (open_arr[t] / close_arr[t-1])
            else:
                wealth *= (close_arr[t] / close_arr[t-1])
        else:
            if lockout_cnt > 0:
                lockout_cnt -= 1
            can_reenter = False
            if not prev_alarm and lockout_cnt == 0:
                if reentry_strategy == "lockout":
                    can_reenter = True
                elif reentry_strategy == "sma50":
                    threshold = sma50_arr[t-1] * (1.0 + sma_pct_buy / 100.0)
                    if close_arr[t-1] > threshold:
                        can_reenter = True
                elif reentry_strategy == "sma20":
                    threshold = sma20_arr[t-1] * (1.0 + sma_pct_buy / 100.0)
                    if close_arr[t-1] > threshold:
                        can_reenter = True
                elif reentry_strategy == "mcclellan":
                    if mcc_arr[t-1] > mcc_buy:
                        can_reenter = True
                elif reentry_strategy == "multi_cond":
                    if buy_ok[t-1]:
                        can_reenter = True
                        
            if can_reenter:
                holding = True
                wealth *= (close_arr[t] / open_arr[t])
                
    return wealth - 1.0

# ── 병렬 워커 함수 (Top-level for multiprocessing pickle support) ─────────────

def _worker_sell_chunk(chunk: List[Tuple], fast_data: Dict[str, np.ndarray], reentry_strategy: str, lockout_days: int, buy_params: Tuple) -> Tuple[float, Tuple]:
    best_score = -np.inf
    best_cand = None
    for cand in chunk:
        score = fast_eval_sell(cand, fast_data, reentry_strategy, lockout_days, buy_params)
        if score > best_score:
            best_score = score
            best_cand = cand
    return best_score, best_cand, len(chunk)

def _worker_buy_chunk(chunk: List[Tuple], fast_data: Dict[str, np.ndarray], alarm_sell: np.ndarray, reentry_strategy: str, lockout_days: int) -> Tuple[float, Tuple]:
    best_score = -np.inf
    best_cand = None
    for cand in chunk:
        score = fast_eval_buy(cand, fast_data, alarm_sell, reentry_strategy, lockout_days)
        if score > best_score:
            best_score = score
            best_cand = cand
    return best_score, best_cand, len(chunk)

def _compute_alarm_sell_mask(sell_params: Tuple, fast_data: Dict[str, np.ndarray]) -> np.ndarray:
    """최적화된 매도 파라미터로 알람 불리언 마스크 계산."""
    hl_sell_pct, mcc_sell, tnx_f_sell, vix_sell, oas_sell, min_active_sell = sell_params
    hl_sell = hl_sell_pct / 100.0
    n_days = fast_data["n_days"]
    
    c_a = (fast_data["new_highs_pct"] > hl_sell) & (fast_data["new_lows_pct"] > hl_sell)
    c_b = fast_data["mcclellan"] <= mcc_sell
    c_c = fast_data["tnx_close"] > (tnx_f_sell * fast_data["tnx_sma20"])
    c_d = fast_data["vix_spread_ratio"] > vix_sell
    c_e = fast_data["oas_close"] > oas_sell
    
    roll_a = _rolling_5_max_uint8(c_a, n_days)
    roll_b = _rolling_5_max_uint8(c_b, n_days)
    roll_c = _rolling_5_max_uint8(c_c, n_days)
    roll_d = _rolling_5_max_uint8(c_d, n_days)
    roll_e = _rolling_5_max_uint8(c_e, n_days)
    
    active_count = roll_a + roll_b + roll_c + roll_d + roll_e
    return active_count >= min_active_sell

# ── 공개 최적화 API ──────────────────────────────────────────────────────────

def parallel_grid_search_sell(
    fast_data: Dict[str, np.ndarray],
    reentry_strategy: str,
    lockout_days: int,
    sell_grid: Dict[str, Any],
    buy_defaults: Tuple[float, float, float, float, float, float],
    progress_callback: Callable[[float], None] = None,
    n_workers: int = None
) -> Dict[str, Any]:
    sell_keys = ["hl_threshold_pct_sell", "mcclellan_threshold_sell", "tnx_sma_factor_sell", "vix_spread_threshold_sell", "oas_threshold_sell", "min_active_conditions_sell"]
    sell_candidates = list(product(*[sell_grid[k] for k in sell_keys]))
    total = len(sell_candidates)
    
    if total == 0:
        return {}
        
    cpu_cores = os.cpu_count() or 4
    if n_workers is None:
        n_workers = min(cpu_cores, 16)
        
    chunk_size = max(1, total // (n_workers * 16))
    chunks = [sell_candidates[i:i + chunk_size] for i in range(0, total, chunk_size)]
    
    best_score = -np.inf
    best_vals = None
    processed = 0
    
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [
            executor.submit(_worker_sell_chunk, chunk, fast_data, reentry_strategy, lockout_days, buy_defaults)
            for chunk in chunks
        ]
        for f in as_completed(futures):
            score, cand, count = f.result()
            if score > best_score:
                best_score = score
                best_vals = cand
            processed += count
            if progress_callback:
                progress_callback(processed / total)
                
    return dict(zip(sell_keys, best_vals))

def parallel_grid_search_buy(
    fast_data: Dict[str, np.ndarray],
    reentry_strategy: str,
    lockout_days: int,
    buy_grid: Dict[str, Any],
    sell_best_tuple: Tuple[float, float, float, float, float, int],
    progress_callback: Callable[[float], None] = None,
    n_workers: int = None
) -> Dict[str, Any]:
    buy_keys = ["hl_threshold_pct_buy", "mcclellan_threshold_buy", "tnx_sma_factor_buy", "vix_spread_threshold_buy", "oas_threshold_buy", "sma_pct_buy"]
    buy_candidates = list(product(*[buy_grid[k] for k in buy_keys]))
    total = len(buy_candidates)
    
    if total == 0:
        return {}
        
    alarm_sell = _compute_alarm_sell_mask(sell_best_tuple, fast_data)
    
    cpu_cores = os.cpu_count() or 4
    if n_workers is None:
        n_workers = min(cpu_cores, 16)
        
    chunk_size = max(1, total // (n_workers * 16))
    chunks = [buy_candidates[i:i + chunk_size] for i in range(0, total, chunk_size)]
    
    best_score = -np.inf
    best_vals = None
    processed = 0
    
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [
            executor.submit(_worker_buy_chunk, chunk, fast_data, alarm_sell, reentry_strategy, lockout_days)
            for chunk in chunks
        ]
        for f in as_completed(futures):
            score, cand, count = f.result()
            if score > best_score:
                best_score = score
                best_vals = cand
            processed += count
            if progress_callback:
                progress_callback(processed / total)
                
    return dict(zip(buy_keys, best_vals))

def optimize_all_signals(
    df: pd.DataFrame,
    selected_asset: str,
    reentry_strategy: str,
    lockout_days: int,
    sell_grid: Dict[str, Any],
    buy_grid: Dict[str, Any],
    buy_defaults_tuple: Tuple[float, float, float, float, float, float],
    progress_callback: Callable[[float, str], None] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """매도와 매수를 초고속 2단계 파이프라인으로 일괄 전수조사 최적화."""
    fast_data = prepare_fast_data(df, selected_asset)
    
    # 1단계: 매도 파라미터 탐색 (0% ~ 50%)
    def sell_progress(pct: float):
        if progress_callback:
            progress_callback(pct * 0.5, f"1단계/2단계: 매도 시그널 전수조사 중 ({pct * 100:.1f}%)")
            
    best_sell = parallel_grid_search_sell(
        fast_data=fast_data,
        reentry_strategy=reentry_strategy,
        lockout_days=lockout_days,
        sell_grid=sell_grid,
        buy_defaults=buy_defaults_tuple,
        progress_callback=sell_progress
    )
    
    sell_best_tuple = (
        best_sell["hl_threshold_pct_sell"],
        best_sell["mcclellan_threshold_sell"],
        best_sell["tnx_sma_factor_sell"],
        best_sell["vix_spread_threshold_sell"],
        best_sell["oas_threshold_sell"],
        best_sell["min_active_conditions_sell"]
    )
    
    # 2단계: 매수 파라미터 탐색 (50% ~ 100%)
    def buy_progress(pct: float):
        if progress_callback:
            progress_callback(0.5 + pct * 0.5, f"2단계/2단계: 매수 시그널 전수조사 중 ({pct * 100:.1f}%)")
            
    best_buy = parallel_grid_search_buy(
        fast_data=fast_data,
        reentry_strategy=reentry_strategy,
        lockout_days=lockout_days,
        buy_grid=buy_grid,
        sell_best_tuple=sell_best_tuple,
        progress_callback=buy_progress
    )
    
    return best_sell, best_buy
