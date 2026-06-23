import os
import threading
import logging
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd

from src.data_manager import get_data_pipeline, CACHE_CONSTITUENTS_PATH, CACHE_MACRO_PATH
from src.indicators import build_master_dataframe
from src.backtester import run_backtest
from src.strategy_backtester import run_alarm_strategy_backtest

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="US Market Crisis Breadth Dashboard API",
    description="Backend API for S&P 500 Market Breadth, McClellan Oscillator, and Credit Spread multi-condition analysis.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production security if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory data store
DATA_STORE = {
    "master_df": None,
    "is_updating": False,
    "last_updated": None,
    "error_message": None
}

class BacktestRequest(BaseModel):
    hl_threshold: float = Field(default=0.028, description="Threshold for 52-week High/Low stock ratio (Condition 1)")
    mcclellan_threshold: float = Field(default=0.0, description="Threshold for McClellan Oscillator proxy (Condition 2)")
    corr_threshold: float = Field(default=0.0, description="Threshold for HYG and ^TNX correlation (Condition 3)")
    use_cond1: bool = Field(default=True, description="Enable Condition 1 (Market Breadth Divergence)")
    use_cond2: bool = Field(default=True, description="Enable Condition 2 (Liquidity Energy)")
    use_cond3: bool = Field(default=True, description="Enable Condition 3 (Credit Spread Proxy)")
    horizons: list[int] = Field(default=[5, 10, 20, 60, 120, 252], description="Forward horizons in trading days")

class StrategyBacktestRequest(BaseModel):
    hl_threshold: float = Field(default=0.025, description="Condition A: 52-week High/Low ratio threshold")
    mcclellan_threshold: float = Field(default=0.0, description="Condition B: McClellan Oscillator threshold")
    tnx_sma_factor: float = Field(default=1.05, description="Condition C: TNX SMA multiplier factor")
    lockout_days: int = Field(default=20, description="Minimum days to stay in cash after exit")

def load_data_into_memory(force_refresh: bool = False):
    """
    Helper function to trigger the data pipeline and load the master dataframe into memory.
    """
    DATA_STORE["is_updating"] = True
    DATA_STORE["error_message"] = None
    try:
        logger.info(f"Loading data pipeline (force_refresh={force_refresh})...")
        macro_df, constituents_df = get_data_pipeline(force_refresh=force_refresh)
        
        # Build Master DataFrame
        master = build_master_dataframe(macro_df, constituents_df)
        
        # Update memory store
        DATA_STORE["master_df"] = master
        DATA_STORE["last_updated"] = datetime.now().isoformat()
        logger.info("Data pipeline load completed successfully.")
    except Exception as e:
        logger.error(f"Error during data pipeline execution: {e}")
        DATA_STORE["error_message"] = str(e)
    finally:
        DATA_STORE["is_updating"] = False

# Startup event to load cached data
@app.on_event("startup")
def startup_event():
    # Run in a background thread to prevent blocking fast startup
    thread = threading.Thread(target=load_data_into_memory, args=(False,))
    thread.start()

@app.get("/api/status")
def get_status():
    """
    Check current database status and last update time.
    """
    cache_exists = os.path.exists(CACHE_MACRO_PATH) and os.path.exists(CACHE_CONSTITUENTS_PATH)
    
    # Calculate row count and date range if loaded
    details = {}
    if DATA_STORE["master_df"] is not None:
        df = DATA_STORE["master_df"]
        details = {
            "row_count": len(df),
            "start_date": str(df["Date"].min()),
            "end_date": str(df["Date"].max())
        }
        
    return {
        "status": "ready" if DATA_STORE["master_df"] is not None else "initializing",
        "cache_exists": cache_exists,
        "is_updating": DATA_STORE["is_updating"],
        "last_updated": DATA_STORE["last_updated"],
        "error": DATA_STORE["error_message"],
        "details": details
    }

@app.post("/api/fetch")
def fetch_data(background_tasks: BackgroundTasks):
    """
    Trigger manual data update from yfinance API in the background.
    """
    if DATA_STORE["is_updating"]:
        raise HTTPException(status_code=400, detail="Data update is already in progress.")
        
    logger.info("Manual data fetch requested.")
    background_tasks.add_task(load_data_into_memory, True)
    return {"message": "Data fetch started in the background."}

@app.get("/api/indicators")
def get_indicators(years: float = 10.0):
    """
    Get full timeseries data of indices and calculated indicators.
    'years' parameter filters historical window size (default 10 years).
    """
    if DATA_STORE["master_df"] is None:
        raise HTTPException(status_code=503, detail="Server is still loading data. Please try again shortly.")
        
    df = DATA_STORE["master_df"]
    
    # Filter by years
    if years > 0:
        cutoff_date = (datetime.now() - pd.Timedelta(days=years * 365.25)).strftime("%Y-%m-%d")
        df_filtered = df[df["Date"] >= cutoff_date]
    else:
        df_filtered = df

    # Replace inf and nan values with None for clean JSON serialization
    df_clean = df_filtered.replace([np.inf, -np.inf], None).where(pd.notnull(df_filtered), None)
    
    # Convert dataframe to list of dicts (JSON)
    records = df_clean.to_dict(orient="records")
    return {
        "count": len(records),
        "data": records
    }

@app.post("/api/backtest")
def execute_backtest(req: BacktestRequest):
    """
    Perform on-the-fly backtest using customizable multi-condition parameters.
    """
    if DATA_STORE["master_df"] is None:
        raise HTTPException(status_code=503, detail="Server is still loading data. Please try again shortly.")
        
    df = DATA_STORE["master_df"]
    
    try:
        results = run_backtest(
            df=df,
            hl_threshold=req.hl_threshold,
            mcclellan_threshold=req.mcclellan_threshold,
            corr_threshold=req.corr_threshold,
            use_cond1=req.use_cond1,
            use_cond2=req.use_cond2,
            use_cond3=req.use_cond3,
            horizons=req.horizons
        )
        return results
    except Exception as e:
        logger.error(f"Backtesting error: {e}")
        raise HTTPException(status_code=500, detail=f"Backtest execution failed: {str(e)}")

@app.post("/api/strategy-backtest")
def execute_strategy_backtest(req: StrategyBacktestRequest):
    """
    Perform S&P 500 Buy & Hold vs Multi-Condition Alarm Strategy Backtest.
    """
    if DATA_STORE["master_df"] is None:
        raise HTTPException(status_code=503, detail="Server is still loading data. Please try again shortly.")
        
    df = DATA_STORE["master_df"]
    
    try:
        results = run_alarm_strategy_backtest(
            df=df,
            hl_threshold=req.hl_threshold,
            mcclellan_threshold=req.mcclellan_threshold,
            tnx_sma_factor=req.tnx_sma_factor,
            lockout_days=req.lockout_days
        )
        return results
    except Exception as e:
        logger.error(f"Strategy Backtesting error: {e}")
        raise HTTPException(status_code=500, detail=f"Strategy backtest execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=True)
