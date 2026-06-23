import sys
import os
import logging
from datetime import datetime, timedelta

# Add src to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_manager import fetch_macro_data, fetch_constituent_data
from src.indicators import build_master_dataframe
from src.backtester import run_backtest

# Setup logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_pipeline")

def test_pipeline():
    logger.info("Starting quick test of the pipeline...")
    
    # 2 years of history is enough to test 52-week indicators (252 trading days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")
    
    # Use top 15 tickers as constituents to speed up testing
    test_tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "BRK-B", "LLY", "AVGO", "JPM", "TSLA", "UNH", "V", "XOM"]
    
    try:
        # 1. Fetch macro data
        macro_df = fetch_macro_data(start_date, end_date)
        logger.info(f"Macro data fetched successfully. Shape: {macro_df.shape}")
        
        # 2. Fetch constituent data
        constituents_df = fetch_constituent_data(test_tickers, start_date, end_date)
        logger.info(f"Constituents data fetched successfully. Shape: {constituents_df.shape}")
        
        # 3. Build master DataFrame
        master_df = build_master_dataframe(macro_df, constituents_df)
        logger.info(f"Master DataFrame built successfully. Shape: {master_df.shape}")
        
        # 4. Check critical indicators are not null
        critical_cols = [
            "SP500_Close", "New_Highs_Pct", "New_Lows_Pct", 
            "Cond1_Breadth_Divergence", "McClellan_Oscillator", 
            "HYG_TNX_Corr_20", "Spread_Ratio", "Spread_ROC_20"
        ]
        
        # S&P 500 data will be verified
        for col in critical_cols:
            if col not in master_df.columns:
                raise AssertionError(f"Column '{col}' is missing from the master dataframe!")
            
            # Print the number of valid rows for each column
            non_null_count = master_df[col].notnull().sum()
            logger.info(f"Column '{col}' has {non_null_count} / {len(master_df)} valid values.")
            
        # 5. Run backtest with very relaxed thresholds to ensure we capture some events
        logger.info("Testing backtesting engine...")
        results = run_backtest(
            df=master_df,
            hl_threshold=0.0,            # 0% high/low (always triggers)
            mcclellan_threshold=100.0,    # very high (always triggers)
            corr_threshold=1.0,           # correlation < 1.0 (nearly always triggers)
            use_cond1=True,
            use_cond2=True,
            use_cond3=True,
            horizons=[5, 10, 20]
        )
        
        logger.info(f"Backtest run succeeded. Total events captured: {results['total_events']}")
        logger.info(f"Independent events count: {results['independent_events_count']}")
        
        if results['independent_events_count'] > 0:
            logger.info(f"Example Event Date: {results['events'][0]['date']}")
            logger.info(f"Example Forward Returns: {results['events'][0]['returns']}")
            
        logger.info("PIPELINE TEST PASSED SUCCESSFULLY!")
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_pipeline()
