import sys
import os
import logging
from datetime import datetime, timedelta

# Add src to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_manager import fetch_macro_data, fetch_constituent_data
from src.indicators import build_master_dataframe
from src.strategy_backtester import run_alarm_strategy_backtest

# Setup logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_strategy")

def test_strategy():
    logger.info("Starting strategy backtesting test...")
    
    # 2 years of history for testing (enough to calculate 52-week rollings)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")
    
    # Standard testing stocks
    test_tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "BRK-B", "LLY", "AVGO", "JPM", "TSLA", "UNH", "V", "XOM"]
    
    try:
        # Fetching
        macro_df = fetch_macro_data(start_date, end_date)
        constituents_df = fetch_constituent_data(test_tickers, start_date, end_date)
        
        # Build Master
        master_df = build_master_dataframe(macro_df, constituents_df)
        
        # Run Alarm Strategy Backtest
        logger.info("Executing Alarm Strategy backtest simulation...")
        results = run_alarm_strategy_backtest(
            df=master_df,
            hl_threshold=0.025,
            mcclellan_threshold=0.0,
            tnx_sma_factor=1.05,
            lockout_days=20
        )
        
        logger.info("SIMULATION COMPLETE. Printing results:")
        print("="*60)
        print("STRATEGY BACKTEST RESULTS (Benchmark vs Strategy)")
        print("="*60)
        
        bm = results["benchmark_metrics"]
        st = results["strategy_metrics"]
        
        print(f"Initial Capital   : $1.0")
        print(f"Date Range        : {results['wealth_history'][0]['date']} to {results['wealth_history'][-1]['date']}")
        print(f"Total Trading Days: {len(results['wealth_history'])}")
        print(f"Total Trade Events: {len(results['trade_logs'])}")
        print("-"*60)
        print(f"{'Metric':<25} | {'Benchmark (B&H)':<15} | {'Alarm Strategy':<15}")
        print("-"*60)
        print(f"{'Cumulative Return':<25} | {bm['cumulative_return']*100:>13.2f}% | {st['cumulative_return']*100:>13.2f}%")
        print(f"{'Annualized Return':<25} | {bm['annualized_return']*100:>13.2f}% | {st['annualized_return']*100:>13.2f}%")
        print(f"{'Annualized Volatility':<25} | {bm['annualized_volatility']*100:>13.2f}% | {st['annualized_volatility']*100:>13.2f}%")
        print(f"{'Sharpe Ratio':<25} | {bm['sharpe_ratio']:>14.2f} | {st['sharpe_ratio']:>14.2f}")
        print(f"{'Max Drawdown (MDD)':<25} | {bm['max_drawdown']*100:>13.2f}% | {st['max_drawdown']*100:>13.2f}%")
        print("="*60)
        
        # Log recent trades
        if results["trade_logs"]:
            print("Recent Trade Actions:")
            for log in results["trade_logs"][-5:]:
                print(f"  [{log['date']}] {log['action']:<8} @ {log['price']:<8.2f} (Wealth: {log['wealth']:.4f}) - {log['reason']}")
            print("="*60)
            
        logger.info("STRATEGY TEST COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        logger.error(f"Strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_strategy()
