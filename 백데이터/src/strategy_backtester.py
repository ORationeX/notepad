import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def run_alarm_strategy_backtest(
    df: pd.DataFrame,
    hl_threshold: float = 0.025,
    mcclellan_threshold: float = 0.0,
    tnx_sma_factor: float = 1.05,
    lockout_days: int = 20
) -> dict:
    """
    Run backtest for the 'Multi-Condition Downmarket Alarm' strategy.
    
    Conditions:
    - Condition A (Internal Crack): Both New Highs & New Lows Pct > hl_threshold
    - Condition B (Breadth/Liquidity): McClellan Oscillator <= mcclellan_threshold
    - Condition C (Macro/Rates): TNX Close > tnx_sma_factor * TNX 20-day SMA
    
    Signal:
    - Trigger alarm if >= 2 of these conditions are met within a rolling 5-day window.
    
    Simulation:
    - Exit S&P 500 to cash on the next day's Open when alarm triggers.
    - Stay in cash for at least `lockout_days` (default 20).
    - After lockout, re-enter S&P 500 on the next day's Open once the alarm is cleared.
    """
    logger.info("Initializing Strategy Backtester...")
    
    # 1. Prepare clean data copy
    # Make sure we sort by Date and reset index
    data = df.sort_values("Date").reset_index(drop=True)
    n_days = len(data)
    
    if n_days < 40:
        raise ValueError("Insufficient data rows to run strategy backtest (need at least 40 rows).")
        
    # Calculate Binary Conditions
    cond_a = (data["New_Highs_Pct"] > hl_threshold) & (data["New_Lows_Pct"] > hl_threshold)
    cond_b = data["McClellan_Oscillator"] <= mcclellan_threshold
    
    if "TNX_Close_SMA20" not in data.columns:
        # Fallback if SMA20 is somehow missing
        data["TNX_Close_SMA20"] = data["TNX_Close"].rolling(window=20).mean().ffill().bfill()
        
    cond_c = data["TNX_Close"] > (tnx_sma_factor * data["TNX_Close_SMA20"])
    
    # Fill any NaNs in conditions with False
    cond_a = cond_a.fillna(False).astype(int)
    cond_b = cond_b.fillna(False).astype(int)
    cond_c = cond_c.fillna(False).astype(int)
    
    # Apply 5-day rolling window (any occurrence in the last 5 days)
    # rolling(5) with min_periods=1
    a_rolling = cond_a.rolling(window=5, min_periods=1).max().fillna(0).astype(int)
    b_rolling = cond_b.rolling(window=5, min_periods=1).max().fillna(0).astype(int)
    c_rolling = cond_c.rolling(window=5, min_periods=1).max().fillna(0).astype(int)
    
    # Sum of active conditions in the 5-day window
    active_conditions_count = a_rolling + b_rolling + c_rolling
    
    # Alarm is triggered if count >= 2
    alarm_signal = active_conditions_count >= 2
    
    # Store intermediate signals back to dataframe for logs
    data["Signal_Cond_A"] = cond_a
    data["Signal_Cond_B"] = cond_b
    data["Signal_Cond_C"] = cond_c
    data["Alarm_Signal"] = alarm_signal.astype(int)
    
    # 2. Portfolio Simulation
    benchmark_wealth = np.ones(n_days)
    strategy_wealth = np.ones(n_days)
    
    # Setup initial benchmark wealth tracking
    sp500_close = data["SP500_Close"].values
    sp500_open = data["SP500_Open"].values
    dates = data["Date"].values
    
    initial_price = sp500_close[0]
    for i in range(n_days):
        benchmark_wealth[i] = sp500_close[i] / initial_price
        
    # Strategy State Tracking
    holding = True
    lockout_counter = 0
    trade_logs = []
    
    # We start fully invested on day 0
    strategy_wealth[0] = 1.0
    
    for t in range(1, n_days):
        daily_ret = sp500_close[t] / sp500_close[t-1]
        open_ret = sp500_open[t] / sp500_close[t-1]
        close_from_open_ret = sp500_close[t] / sp500_open[t]
        
        # Check yesterdays alarm signal to act on todays Open
        prev_alarm = alarm_signal.iloc[t-1]
        
        if holding:
            if prev_alarm:
                # Trigger exit at Open today
                holding = False
                lockout_counter = lockout_days
                strategy_wealth[t] = strategy_wealth[t-1] * open_ret
                trade_logs.append({
                    "date": str(dates[t]),
                    "action": "EXIT",
                    "price": float(sp500_open[t]),
                    "wealth": float(strategy_wealth[t]),
                    "reason": f"Alarm triggered. Conds: A={int(cond_a.iloc[t-1])}, B={int(cond_b.iloc[t-1])}, C={int(cond_c.iloc[t-1])}"
                })
            else:
                # Continue holding
                strategy_wealth[t] = strategy_wealth[t-1] * daily_ret
        else:
            # We are currently in cash
            # Decrement lockout timer
            if lockout_counter > 0:
                lockout_counter -= 1
                
            # Can we re-enter today?
            # Re-enter if lockout finished AND yesterdays alarm is cleared
            if lockout_counter == 0 and not prev_alarm:
                holding = True
                strategy_wealth[t] = strategy_wealth[t-1] * close_from_open_ret
                trade_logs.append({
                    "date": str(dates[t]),
                    "action": "RE_ENTRY",
                    "price": float(sp500_open[t]),
                    "wealth": float(strategy_wealth[t]),
                    "reason": "Lockout ended and alarm cleared."
                })
            else:
                # Stay in cash
                strategy_wealth[t] = strategy_wealth[t-1]
                
    # 3. Calculate Performance Metrics
    def compute_metrics(wealth_series: np.ndarray) -> dict:
        # Returns
        cum_return = wealth_series[-1] - 1.0
        
        # Daily Returns for volatility and Sharpe
        daily_returns = pd.Series(wealth_series).pct_change().dropna()
        
        # Annualized Return (compounded)
        n_years = n_days / 252.0
        ann_return = (wealth_series[-1]) ** (1.0 / n_years) - 1.0 if wealth_series[-1] > 0 else -1.0
        
        # Annualized Volatility
        ann_vol = daily_returns.std() * np.sqrt(252)
        
        # Sharpe Ratio (Assuming 0% risk free rate)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
        
        # Maximum Drawdown (MDD)
        running_max = np.maximum.accumulate(wealth_series)
        drawdowns = (wealth_series - running_max) / running_max
        mdd = drawdowns.min()
        
        return {
            "cumulative_return": float(cum_return),
            "annualized_return": float(ann_return),
            "annualized_volatility": float(ann_vol),
            "sharpe_ratio": float(sharpe),
            "max_drawdown": float(mdd)
        }
        
    benchmark_metrics = compute_metrics(benchmark_wealth)
    strategy_metrics = compute_metrics(strategy_wealth)
    
    # 4. Generate Timeseries data for chart comparison
    wealth_history = []
    for i in range(n_days):
        wealth_history.append({
            "date": str(dates[i]),
            "benchmark": float(benchmark_wealth[i]),
            "strategy": float(strategy_wealth[i]),
            "alarm_active": int(alarm_signal.iloc[i])
        })
        
    return {
        "benchmark_metrics": benchmark_metrics,
        "strategy_metrics": strategy_metrics,
        "wealth_history": wealth_history,
        "trade_logs": trade_logs,
        "parameters": {
            "hl_threshold": hl_threshold,
            "mcclellan_threshold": mcclellan_threshold,
            "tnx_sma_factor": tnx_sma_factor,
            "lockout_days": lockout_days
        }
    }
