import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

def calculate_market_breadth(constituents_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Condition 1 (Market Breadth Divergence):
    S&P 500 stocks making new 52-week highs AND 52-week lows simultaneously exceeding 2.8%.
    
    Also calculates daily active stock counts, advancing/declining counts, 
    and Condition 2 (McClellan Oscillator Proxy).
    """
    logger.info("Calculating market breadth indicators...")
    
    # Extract Close, High, Low from the multi-index DataFrame
    # Columns of constituents_df are (Ticker, Attribute)
    tickers = constituents_df.columns.levels[0]
    
    # We want to align indices
    dates = constituents_df.index
    breadth_df = pd.DataFrame(index=dates)
    
    # Initialize series
    high_ratios = []
    low_ratios = []
    adv_dec_ratios = [] # (Advancing - Declining) / Active
    
    # For speed, we can compute rolling high/low for each ticker beforehand
    # components of rolling calculation:
    logger.info("Computing rolling 52-week highs and lows for all constituent stocks...")
    
    # Create temporary DataFrames for Close, High, Low, and Prev Close
    close_prices = pd.DataFrame(index=dates)
    high_prices = pd.DataFrame(index=dates)
    low_prices = pd.DataFrame(index=dates)
    
    for ticker in tickers:
        if ticker in constituents_df.columns.levels[0]:
            ticker_data = constituents_df[ticker]
            if "Close" in ticker_data.columns:
                close_prices[ticker] = ticker_data["Close"]
            if "High" in ticker_data.columns:
                high_prices[ticker] = ticker_data["High"]
            if "Low" in ticker_data.columns:
                low_prices[ticker] = ticker_data["Low"]

    # 52-week (252 trading days) rolling max of High and min of Low
    # To determine if today is a 52-week high, we check if today's High is >= the rolling max of the past 252 days.
    # Note: rolling(252) includes today. If today's High is the highest of the last 252 days, High == rolling_max.
    rolling_highs = high_prices.rolling(window=252, min_periods=100).max()
    rolling_lows = low_prices.rolling(window=252, min_periods=100).min()
    
    # Check if High/Low hits the 52-week High/Low
    is_new_high = (high_prices >= rolling_highs) & (high_prices.notna())
    is_new_low = (low_prices <= rolling_lows) & (low_prices.notna())
    
    # Advancing and Declining stocks
    # Current Close vs Previous Close
    prev_close = close_prices.shift(1)
    is_advancing = (close_prices > prev_close) & (close_prices.notna()) & (prev_close.notna())
    is_declining = (close_prices < prev_close) & (close_prices.notna()) & (prev_close.notna())
    
    # Active tickers per day (tickers with non-null close prices)
    is_active = close_prices.notna()
    active_counts = is_active.sum(axis=1)
    
    # Calculate ratios per day
    high_counts = is_new_high.sum(axis=1)
    low_counts = is_new_low.sum(axis=1)
    
    adv_counts = is_advancing.sum(axis=1)
    dec_counts = is_declining.sum(axis=1)
    
    # Avoid division by zero
    active_counts_safe = active_counts.replace(0, np.nan)
    
    breadth_df["Active_Stocks"] = active_counts
    breadth_df["New_Highs_Pct"] = high_counts / active_counts_safe
    breadth_df["New_Lows_Pct"] = low_counts / active_counts_safe
    
    # Condition 1: Both New Highs Pct and New Lows Pct > 2.8% (0.028)
    breadth_df["Cond1_Breadth_Divergence"] = (
        (breadth_df["New_Highs_Pct"] >= 0.028) & 
        (breadth_df["New_Lows_Pct"] >= 0.028)
    ).astype(int)
    
    # Condition 2: McClellan Oscillator Proxy
    # NetRatio = (Advances - Declines) / Active
    net_ratio = (adv_counts - dec_counts) / active_counts_safe
    breadth_df["Net_Advances_Ratio"] = net_ratio.fillna(0.0)
    
    # McClellan Oscillator 대용 = EMA19(NetRatio) - EMA39(NetRatio)
    # Using standard exponential moving average (EMA)
    ema19 = breadth_df["Net_Advances_Ratio"].ewm(span=19, adjust=False).mean()
    ema39 = breadth_df["Net_Advances_Ratio"].ewm(span=39, adjust=False).mean()
    
    breadth_df["McClellan_Oscillator"] = ema19 - ema39
    
    logger.info("Successfully calculated market breadth & McClellan Oscillator.")
    return breadth_df

def calculate_credit_spread_indicators(macro_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Condition 3 (Credit Spread proxy indicators):
    - 20-day rolling correlation of daily returns between HYG and ^TNX.
    - Spread proxy (TNX_Close / HYG_Close) and its 20-day Rate of Change (ROC).
    """
    logger.info("Calculating credit spread indicators...")
    df = pd.DataFrame(index=macro_df.index)
    
    if "HYG_Close" not in macro_df.columns or "TNX_Close" not in macro_df.columns:
        logger.warning("HYG_Close or TNX_Close missing from macro data. Skipping Credit Spread indicators.")
        df["HYG_TNX_Corr_20"] = np.nan
        df["Spread_Ratio"] = np.nan
        df["Spread_ROC_20"] = np.nan
        return df
        
    hyg_ret = macro_df["HYG_Close"].pct_change()
    tnx_ret = macro_df["TNX_Close"].pct_change()
    
    # 20-day Rolling Correlation between daily returns
    df["HYG_TNX_Corr_20"] = hyg_ret.rolling(window=20).corr(tnx_ret)
    
    # Spread Proxy (Ratio of yields to prices)
    df["Spread_Ratio"] = macro_df["TNX_Close"] / macro_df["HYG_Close"]
    
    # Rate of Change of Spread over 20 days
    df["Spread_ROC_20"] = df["Spread_Ratio"].pct_change(periods=20)
    
    # 20-day SMA of TNX Close (Treasury Yield)
    df["TNX_Close_SMA20"] = macro_df["TNX_Close"].rolling(window=20).mean()
    
    logger.info("Successfully calculated credit spread indicators.")
    return df

def build_master_dataframe(macro_df: pd.DataFrame, constituents_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine S&P 500 macro data with calculated breadth, liquidity, and credit spread indicators.
    """
    logger.info("Building Master DataFrame...")
    
    # Calculate components
    breadth_df = calculate_market_breadth(constituents_df)
    credit_df = calculate_credit_spread_indicators(macro_df)
    
    # Combine everything using 'Date' index
    master_df = macro_df.join(breadth_df, how="inner")
    master_df = master_df.join(credit_df, how="inner")
    
    # Handle NaNs: forward fill then backward fill for minor gaps
    # But for rolling indicators, some leading NaNs are expected and should stay NaN or be filled carefully
    master_df = master_df.ffill().bfill()
    
    # We will reset index to make 'Date' a column (JSON serialization ready)
    master_df = master_df.reset_index()
    
    # Ensure Date is formatted nicely
    if "Date" in master_df.columns:
        master_df["Date"] = master_df["Date"].dt.strftime("%Y-%m-%d")
        
    logger.info(f"Master DataFrame build complete. Shape: {master_df.shape}")
    return master_df

if __name__ == "__main__":
    from data_manager import get_data_pipeline
    macro, constituents = get_data_pipeline()
    master = build_master_dataframe(macro, constituents)
    print(master.head())
