import argparse
import sys
import uvicorn
import logging

# Set up simple console logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_entrypoint")

def run_server(host: str, port: int, reload: bool):
    """
    Run FastAPI server via Uvicorn.
    """
    logger.info(f"Starting server on {host}:{port} with reload={reload}...")
    uvicorn.run("src.server:app", host=host, port=port, reload=reload)

def prefetch_data():
    """
    Directly run the data pipeline to scrape Wikipedia and download/merge yfinance data for Nasdaq-100.
    Implements incremental updates: downloads only new/today's data if cache is present.
    """
    logger.info("Initializing prefetch mode (Nasdaq-100)...")
    
    import os
    import requests
    import numpy as np
    import pandas as pd
    from bs4 import BeautifulSoup
    import yfinance as yf
    from datetime import datetime, timedelta
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    CACHE_CONSTITUENTS_PATH = os.path.join(DATA_DIR, "nasdaq100_constituents.parquet")
    CACHE_MACRO_PATH = os.path.join(DATA_DIR, "macro_nasdaq_data.parquet")
    CACHE_PROCESSED_PATH = os.path.join(DATA_DIR, "master_processed.parquet")
    
    # Scrape Nasdaq-100 tickers from Wikipedia
    logger.info("Scraping Nasdaq-100 tickers from Wikipedia...")
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        tickers = []
        for row in table.find_all("tr")[1:]:
            ticker = row.find_all("td")[0].text.strip() # Nasdaq table has symbol in 1st column
            ticker = ticker.replace(".", "-")
            tickers.append(ticker)
        if not tickers:
            raise ValueError("No tickers found in Wikipedia constituents table.")
    except Exception as e:
        logger.warning(f"Scraping failed: {e}. Using fallback tickers.")
        tickers = [
            "AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "AVGO", "TSLA", "COST",
            "NFLX", "AMD", "ADBE", "PEP", "AZN", "QCOM", "LIN", "TXN", "TMUS", "INTU",
            "AMGN", "ISRG", "AMAT", "CMCSA", "BKNG", "HON", "VRTX", "ADP", "PANW", "MU"
        ]
        
    macro_exists = os.path.exists(CACHE_MACRO_PATH)
    constituents_exists = os.path.exists(CACHE_CONSTITUENTS_PATH)
    
    is_incremental = False
    old_macro = None
    old_constituents = None
    
    if macro_exists and constituents_exists:
        try:
            logger.info("Reading local caches to check for incremental update...")
            old_macro = pd.read_parquet(CACHE_MACRO_PATH)
            old_constituents = pd.read_parquet(CACHE_CONSTITUENTS_PATH)
            
            last_date_macro = old_macro.index.max()
            last_date_const = old_constituents.index.max()
            last_date = min(last_date_macro, last_date_const)
            
            # Start download from last_date - 5 days to ensure any data adjustments or gaps are handled
            start_date = (last_date - timedelta(days=5)).strftime("%Y-%m-%d")
            is_incremental = True
            logger.info(f"Incremental sync mode active. Last cached date: {last_date.strftime('%Y-%m-%d')}. Fetching from {start_date}...")
        except Exception as e:
            logger.warning(f"Incremental check failed: {e}. Reverting to full fetch.")
            
    if not is_incremental:
        start_date = "1971-01-01"
        logger.info(f"Full fetch mode active. Fetching historical data starting from {start_date}...")
        
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"Downloading macro data (^IXIC, HYG, ^TNX) from {start_date} to {end_date}...")
    macro_tickers = ["^IXIC", "HYG", "^TNX"]
    try:
        macro_df_raw = yf.download(macro_tickers, start=start_date, end=end_date, group_by="ticker")
        if macro_df_raw.empty:
            raise ValueError("yfinance returned empty macro data.")
            
        new_macro_df = pd.DataFrame(index=macro_df_raw.index)
        if "^IXIC" in macro_df_raw.columns.levels[0]:
            nasdaq = macro_df_raw["^IXIC"]
            new_macro_df["NASDAQ_Open"] = nasdaq["Open"]
            new_macro_df["NASDAQ_High"] = nasdaq["High"]
            new_macro_df["NASDAQ_Low"] = nasdaq["Low"]
            new_macro_df["NASDAQ_Close"] = nasdaq["Close"]
            new_macro_df["NASDAQ_AdjClose"] = nasdaq["Adj Close"] if "Adj Close" in nasdaq.columns else nasdaq["Close"]
            new_macro_df["NASDAQ_Volume"] = nasdaq["Volume"]
        if "HYG" in macro_df_raw.columns.levels[0]:
            hyg = macro_df_raw["HYG"]
            new_macro_df["HYG_Close"] = hyg["Adj Close"] if "Adj Close" in hyg.columns else hyg["Close"]
        if "^TNX" in macro_df_raw.columns.levels[0]:
            tnx = macro_df_raw["^TNX"]
            new_macro_df["TNX_Close"] = tnx["Adj Close"] if "Adj Close" in tnx.columns else tnx["Close"]
            
        new_macro_df = new_macro_df.dropna(subset=["NASDAQ_Close"])
    except Exception as e:
        logger.error(f"Error fetching macro data: {e}")
        sys.exit(1)
        
    logger.info(f"Downloading constituent data for {len(tickers)} tickers...")
    chunk_size = 50
    chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    all_dfs = []
    
    for idx, chunk in enumerate(chunks):
        logger.info(f"Downloading chunk {idx+1}/{len(chunks)}...")
        try:
            chunk_df = yf.download(chunk, start=start_date, end=end_date, group_by="ticker", threads=True, progress=False)
            if not chunk_df.empty:
                all_dfs.append(chunk_df)
        except Exception as e:
            logger.warning(f"Error downloading chunk: {e}")
            
    if not all_dfs:
        logger.error("Could not download constituent data.")
        sys.exit(1)
        
    new_constituents_df = pd.concat(all_dfs, axis=1)
    
    # Merge and update caches
    if is_incremental:
        logger.info("Merging incremental data chunks with local caches...")
        macro_df = pd.concat([old_macro, new_macro_df])
        macro_df = macro_df[~macro_df.index.duplicated(keep='last')].sort_index()
        
        constituents_df = pd.concat([old_constituents, new_constituents_df], axis=0)
        constituents_df = constituents_df[~constituents_df.index.duplicated(keep='last')].sort_index()
    else:
        macro_df = new_macro_df
        constituents_df = new_constituents_df
        
    # Calculate moving averages on the sorted, full index series
    macro_df["NASDAQ_SMA20"] = macro_df["NASDAQ_Close"].rolling(window=20).mean()
    macro_df["NASDAQ_SMA50"] = macro_df["NASDAQ_Close"].rolling(window=50).mean()
    macro_df["NASDAQ_SMA200"] = macro_df["NASDAQ_Close"].rolling(window=200).mean()
    
    # Save raw caches
    logger.info("Saving raw cache files...")
    macro_df.to_parquet(CACHE_MACRO_PATH)
    constituents_df.to_parquet(CACHE_CONSTITUENTS_PATH)
    
    # Calculate indicators
    logger.info("Calculating Nasdaq-100 composite indicators...")
    dates = constituents_df.index
    
    breadth_df = pd.DataFrame(index=dates)
    
    close_prices = constituents_df.xs("Close", axis=1, level=1)
    high_prices = constituents_df.xs("High", axis=1, level=1)
    low_prices = constituents_df.xs("Low", axis=1, level=1)
    
    rolling_highs = high_prices.rolling(window=252, min_periods=100).max()
    rolling_lows = low_prices.rolling(window=252, min_periods=100).min()
    
    is_new_high = (high_prices >= rolling_highs) & (high_prices.notna())
    is_new_low = (low_prices <= rolling_lows) & (low_prices.notna())
    
    prev_close = close_prices.shift(1)
    is_advancing = (close_prices > prev_close) & (close_prices.notna()) & (prev_close.notna())
    is_declining = (close_prices < prev_close) & (close_prices.notna()) & (prev_close.notna())
    
    is_active = close_prices.notna()
    active_counts = is_active.sum(axis=1)
    active_counts_safe = active_counts.replace(0, np.nan)
    
    # Guard rails to prevent noise when there are fewer than 10 active stocks
    valid_breadth = active_counts >= 10
    
    breadth_df["Active_Stocks"] = active_counts
    breadth_df["New_Highs_Pct"] = (is_new_high.sum(axis=1) / active_counts_safe).where(valid_breadth, 0.0)
    breadth_df["New_Lows_Pct"] = (is_new_low.sum(axis=1) / active_counts_safe).where(valid_breadth, 0.0)
    
    net_advances_ratio = (((is_advancing.sum(axis=1) - is_declining.sum(axis=1)) / active_counts_safe).fillna(0.0)).where(valid_breadth, 0.0)
    ema19 = net_advances_ratio.ewm(span=19, adjust=False).mean()
    ema39 = net_advances_ratio.ewm(span=39, adjust=False).mean()
    breadth_df["McClellan_Oscillator"] = ema19 - ema39
    
    credit_df = pd.DataFrame(index=macro_df.index)
    if "HYG_Close" in macro_df.columns and "TNX_Close" in macro_df.columns:
        hyg_ret = macro_df["HYG_Close"].pct_change()
        tnx_ret = macro_df["TNX_Close"].pct_change()
        credit_df["HYG_TNX_Corr_20"] = hyg_ret.rolling(window=20).corr(tnx_ret)
        credit_df["Spread_Ratio"] = macro_df["TNX_Close"] / macro_df["HYG_Close"]
        credit_df["Spread_ROC_20"] = credit_df["Spread_Ratio"].pct_change(periods=20)
        credit_df["TNX_Close_SMA20"] = macro_df["TNX_Close"].rolling(window=20).mean()
        
    master = macro_df.join(breadth_df, how="inner")
    master = master.join(credit_df, how="inner")
    master = master.dropna(subset=["NASDAQ_Close"])
    master = master.ffill().bfill()
    
    # Save master processed parquet
    logger.info("Saving master processed data...")
    master.to_parquet(CACHE_PROCESSED_PATH)
    logger.info(f"Prefetch completed successfully. Shape: {master.shape}")

def main():
    parser = argparse.ArgumentParser(
        description="US Market Breadth Dashboard Backend Runner"
    )
    
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Host address to bind the API server to"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to run the API server on"
    )
    
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload on code change (dev mode)"
    )
    
    parser.add_argument(
        "--fetch-only", 
        action="store_true", 
        help="Only download data and build cache, then exit"
    )
    
    args = parser.parse_args()
    
    if args.fetch_only:
        prefetch_data()
    else:
        run_server(args.host, args.port, args.reload)

if __name__ == "__main__":
    main()
