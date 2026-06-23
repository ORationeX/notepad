import os
import logging
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CACHE_CONSTITUENTS_PATH = os.path.join(DATA_DIR, "sp500_constituents.parquet")
CACHE_MACRO_PATH = os.path.join(DATA_DIR, "macro_data.parquet")

def get_sp500_tickers() -> list:
    """
    Scrape the list of S&P 500 tickers from Wikipedia.
    Converts dots to hyphens for yfinance compatibility (e.g. BRK.B -> BRK-B).
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        
        tickers = []
        for row in table.find_all("tr")[1:]:
            ticker = row.find_all("td")[0].text.strip()
            # yfinance uses '-' instead of '.' for classes (e.g. BRK.B -> BRK-B)
            ticker = ticker.replace(".", "-")
            tickers.append(ticker)
            
        logger.info(f"Successfully scraped {len(tickers)} S&P 500 tickers from Wikipedia.")
        return tickers
    except Exception as e:
        logger.error(f"Error scraping S&P 500 tickers: {e}")
        # Return a fallback list of major tickers if scraping fails
        fallback_tickers = [
            "AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "BRK-B", "LLY", "AVGO",
            "JPM", "TSLA", "UNH", "V", "XOM", "MA", "HD", "PG", "COST", "JNJ",
            "MRK", "NFLX", "AMD", "ABBV", "ADBE", "CVX", "CRM", "PEP", "KO", "TMO"
        ]
        logger.warning(f"Using fallback tickers (top {len(fallback_tickers)} S&P 500 stocks).")
        return fallback_tickers

def fetch_macro_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch S&P 500 Index (^GSPC), High Yield ETF (HYG), and 10-Yr Treasury Yield (^TNX)
    """
    tickers = ["^GSPC", "HYG", "^TNX"]
    logger.info(f"Fetching macro data {tickers} from {start_date} to {end_date}...")
    try:
        df = yf.download(tickers, start=start_date, end=end_date, group_by="ticker")
        if df.empty:
            raise ValueError("No macro data returned from yfinance.")
        
        # Structure dataframe nicely: Flatten multi-index columns if needed, but keeping it simple:
        # We only need 'Close' (or Adj Close) for HYG and ^TNX, and OHLC for ^GSPC.
        # Let's extract the clean series we need:
        macro_df = pd.DataFrame(index=df.index)
        
        # Extracted Series
        if "^GSPC" in df.columns.levels[0]:
            gspc_df = df["^GSPC"]
            macro_df["SP500_Open"] = gspc_df["Open"]
            macro_df["SP500_High"] = gspc_df["High"]
            macro_df["SP500_Low"] = gspc_df["Low"]
            macro_df["SP500_Close"] = gspc_df["Close"]
            macro_df["SP500_AdjClose"] = gspc_df["Adj Close"] if "Adj Close" in gspc_df.columns else gspc_df["Close"]
            macro_df["SP500_Volume"] = gspc_df["Volume"]
            
        if "HYG" in df.columns.levels[0]:
            hyg_df = df["HYG"]
            macro_df["HYG_Close"] = hyg_df["Adj Close"] if "Adj Close" in hyg_df.columns else hyg_df["Close"]
            
        if "^TNX" in df.columns.levels[0]:
            tnx_df = df["^TNX"]
            macro_df["TNX_Close"] = tnx_df["Adj Close"] if "Adj Close" in tnx_df.columns else tnx_df["Close"]
            
        # Drop rows where S&P 500 is missing
        macro_df = macro_df.dropna(subset=["SP500_Close"])
        logger.info(f"Successfully fetched macro data: {macro_df.shape[0]} rows.")
        return macro_df
    except Exception as e:
        logger.error(f"Error fetching macro data: {e}")
        raise e

def fetch_constituent_data(tickers: list, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch 10-year OHLCV for all S&P 500 constituents.
    Downloads in chunks to mitigate rate limiting and track failures.
    Returns a multi-indexed columns DataFrame (Ticker, Attribute).
    """
    logger.info(f"Starting constituent data download for {len(tickers)} tickers...")
    chunk_size = 50
    chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    
    all_dfs = []
    
    for idx, chunk in enumerate(chunks):
        logger.info(f"Downloading chunk {idx+1}/{len(chunks)} ({len(chunk)} tickers)...")
        try:
            # We download Close, High, Low, which are needed for McClellan and 52-week High/Low
            chunk_df = yf.download(chunk, start=start_date, end=end_date, group_by="ticker", threads=True)
            if not chunk_df.empty:
                all_dfs.append(chunk_df)
            else:
                logger.warning(f"Empty dataframe returned for chunk {idx+1}")
        except Exception as e:
            logger.error(f"Failed downloading chunk {idx+1}: {e}")
            
    if not all_dfs:
        raise ValueError("Failed to download any constituent stock data.")
        
    logger.info("Merging constituent data...")
    # Concatenate columns
    merged_df = pd.concat(all_dfs, axis=1)
    return merged_df

def get_data_pipeline(force_refresh: bool = False, days_history: int = 365 * 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main pipeline function to get macro and constituent data.
    Uses local cache if available and not forced to refresh.
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_history)).strftime("%Y-%m-%d")
    
    macro_exists = os.path.exists(CACHE_MACRO_PATH)
    constituents_exists = os.path.exists(CACHE_CONSTITUENTS_PATH)
    
    if not force_refresh and macro_exists and constituents_exists:
        logger.info("Loading data from local Parquet cache...")
        try:
            macro_df = pd.read_parquet(CACHE_MACRO_PATH)
            # Constituents multi-index columns parquet loading
            constituents_df = pd.read_parquet(CACHE_CONSTITUENTS_PATH)
            logger.info("Cache successfully loaded.")
            return macro_df, constituents_df
        except Exception as e:
            logger.warning(f"Error loading cache: {e}. Re-fetching from API.")
            
    # Fetch Macro Data
    macro_df = fetch_macro_data(start_date, end_date)
    
    # Fetch Constituent Data
    tickers = get_sp500_tickers()
    constituents_df = fetch_constituent_data(tickers, start_date, end_date)
    
    # Save to Cache
    logger.info("Caching data locally to Parquet files...")
    try:
        # Save macro data
        macro_df.to_parquet(CACHE_MACRO_PATH)
        
        # For constituents_df, PyArrow supports MultiIndex columns.
        # However, to be extra safe, we flatten the column names to strings or save as multi-index directly.
        # Saving multi-index columns is natively supported in Pandas Parquet writing.
        constituents_df.to_parquet(CACHE_CONSTITUENTS_PATH)
        logger.info("Data successfully cached.")
    except Exception as e:
        logger.error(f"Failed to cache data: {e}")
        
    return macro_df, constituents_df

if __name__ == "__main__":
    # Test execution
    macro, constituents = get_data_pipeline(force_refresh=False)
    print("Macro Data Shape:", macro.shape)
    print("Constituents Data Shape:", constituents.shape)
