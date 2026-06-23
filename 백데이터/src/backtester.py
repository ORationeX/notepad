import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def find_trigger_events(
    df: pd.DataFrame,
    hl_threshold: float = 0.028,
    mcclellan_threshold: float = 0.0,
    corr_threshold: float = 0.0,
    use_cond1: bool = True,
    use_cond2: bool = True,
    use_cond3: bool = True
) -> pd.Series:
    """
    Generate boolean mask for dates where specified conditions are met.
    
    Conditions:
    - Cond1 (Breadth): New_Highs_Pct >= hl_threshold AND New_Lows_Pct >= hl_threshold
    - Cond2 (McClellan): McClellan_Oscillator < mcclellan_threshold (low energy/liquidity drain)
    - Cond3 (Credit Spread): HYG_TNX_Corr_20 < corr_threshold (risk-off decoupling)
    """
    mask = pd.Series(True, index=df.index)
    
    if use_cond1:
        cond1 = (df["New_Highs_Pct"] >= hl_threshold) & (df["New_Lows_Pct"] >= hl_threshold)
        mask = mask & cond1
        
    if use_cond2:
        cond2 = df["McClellan_Oscillator"] < mcclellan_threshold
        mask = mask & cond2
        
    if use_cond3:
        cond3 = df["HYG_TNX_Corr_20"] < corr_threshold
        mask = mask & cond3
        
    return mask

def calculate_forward_metrics(
    df: pd.DataFrame, 
    trigger_indices: list, 
    horizons: list[int]
) -> list[dict]:
    """
    For each trigger index, calculate S&P 500 forward returns and maximum drawdown (MDD)
    across defined horizons (in trading days).
    """
    events = []
    close_series = df["SP500_Close"].values
    dates = df["Date"].values
    
    n_rows = len(df)
    
    for idx in trigger_indices:
        trigger_date = dates[idx]
        trigger_price = close_series[idx]
        
        event_entry = {
            "index": int(idx),
            "date": str(trigger_date),
            "sp500_price": float(trigger_price),
            "new_highs_pct": float(df.loc[idx, "New_Highs_Pct"]),
            "new_lows_pct": float(df.loc[idx, "New_Lows_Pct"]),
            "mcclellan": float(df.loc[idx, "McClellan_Oscillator"]),
            "hyg_tnx_corr": float(df.loc[idx, "HYG_TNX_Corr_20"]),
            "returns": {},
            "mdds": {}
        }
        
        for h in horizons:
            end_idx = min(idx + h, n_rows - 1)
            actual_horizon = end_idx - idx
            
            if actual_horizon <= 0:
                event_entry["returns"][f"{h}d"] = None
                event_entry["mdds"][f"{h}d"] = None
                continue
                
            horizon_prices = close_series[idx + 1 : end_idx + 1]
            end_price = close_series[end_idx]
            
            # Forward Return
            fwd_return = (end_price - trigger_price) / trigger_price
            event_entry["returns"][f"{h}d"] = float(fwd_return)
            
            # Max Drawdown (MDD) during the horizon
            # MDD = (Price - Running Max) / Running Max
            running_max = np.maximum.accumulate(horizon_prices)
            drawdowns = (horizon_prices - running_max) / running_max
            # Also need to check drawdown relative to trigger price
            drawdown_from_trigger = (horizon_prices - trigger_price) / trigger_price
            
            # We take the worst drop from any peak in the horizon
            mdd = float(drawdowns.min()) if len(drawdowns) > 0 else 0.0
            event_entry["mdds"][f"{h}d"] = mdd
            
        events.append(event_entry)
        
    return events

def run_backtest(
    df: pd.DataFrame,
    hl_threshold: float = 0.028,
    mcclellan_threshold: float = 0.0,
    corr_threshold: float = 0.0,
    use_cond1: bool = True,
    use_cond2: bool = True,
    use_cond3: bool = True,
    horizons: list[int] = [5, 10, 20, 60, 120, 252]
) -> dict:
    """
    Run backtesting on the master dataset using configured multi-conditions.
    Returns aggregated statistics and individual trigger event records.
    """
    logger.info("Running event-study backtest...")
    
    # Clean dataframe index
    df_clean = df.reset_index(drop=True)
    
    # 1. Find trigger dates
    mask = find_trigger_events(
        df_clean, hl_threshold, mcclellan_threshold, corr_threshold,
        use_cond1, use_cond2, use_cond3
    )
    
    trigger_indices = df_clean.index[mask].tolist()
    total_triggers = len(trigger_indices)
    
    if total_triggers == 0:
        return {
            "total_events": 0,
            "summary_stats": {},
            "events": []
        }
        
    # Filter consecutive trigger dates (e.g. if conditions trigger 3 days in a row, 
    # we might only want the first event (cluster head) to avoid double counting).
    # We will provide both: raw triggers and "clustered" (independent) triggers (e.g. gap of 10 days).
    independent_indices = []
    last_idx = -9999
    min_gap = 10 # 10 trading days gap to treat as separate signal
    
    for idx in trigger_indices:
        if idx - last_idx >= min_gap:
            independent_indices.append(idx)
            last_idx = idx
            
    # Calculate metrics for both
    all_events = calculate_forward_metrics(df_clean, trigger_indices, horizons)
    independent_events = calculate_forward_metrics(df_clean, independent_indices, horizons)
    
    # Compile Summary Statistics for Independent Events
    summary = {}
    for h in horizons:
        h_key = f"{h}d"
        h_returns = [e["returns"][h_key] for e in independent_events if e["returns"][h_key] is not None]
        h_mdds = [e["mdds"][h_key] for e in independent_events if e["mdds"][h_key] is not None]
        
        if h_returns:
            win_rate = sum(1 for r in h_returns if r > 0) / len(h_returns)
            summary[h_key] = {
                "count": len(h_returns),
                "avg_return": float(np.mean(h_returns)),
                "median_return": float(np.median(h_returns)),
                "win_rate": float(win_rate),
                "min_return": float(np.min(h_returns)),
                "max_return": float(np.max(h_returns)),
                "avg_mdd": float(np.mean(h_mdds)),
                "max_mdd": float(np.min(h_mdds)) # min of negative MDDs is the absolute worst drop
            }
        else:
            summary[h_key] = None
            
    # Calculate Average Trajectory around independent events
    # We trace SP500 price index normalized to 100 at trigger date, from T-20 to T+120
    trajectory_window = (-20, 120)
    trajectories = []
    
    for idx in independent_indices:
        start_t = idx + trajectory_window[0]
        end_t = idx + trajectory_window[1]
        
        # Ensure we stay within bounds
        if start_t >= 0 and end_t < len(df_clean):
            prices = df_clean.loc[start_t:end_t, "SP500_Close"].values
            trigger_p = df_clean.loc[idx, "SP500_Close"]
            normalized_prices = (prices / trigger_p) * 100
            trajectories.append(normalized_prices)
            
    avg_trajectory = []
    if trajectories:
        # Average across columns (time steps)
        avg_trajectory = np.mean(np.array(trajectories), axis=0).tolist()
        
    return {
        "total_events": total_triggers,
        "independent_events_count": len(independent_indices),
        "summary_stats": summary,
        "events": independent_events, # Send independent events for detail table
        "all_raw_events": all_events,   # Raw event list if needed
        "trajectory": {
            "x": list(range(trajectory_window[0], trajectory_window[1] + 1)),
            "y": avg_trajectory
        }
    }
