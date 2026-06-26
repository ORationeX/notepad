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
    Directly run the data pipeline to scrape Wikipedia and download/merge data.
    """
    logger.info("Initializing prefetch mode (Nasdaq-100)...")
    
    import os
    import app
    try:
        # app.py의 get_complete_data 및 compute_indicators 통합 재사용
        macro_raw, constituents_raw = app.get_complete_data(force_refresh=True)
        master_dataset = app.compute_indicators(macro_raw, constituents_raw)
        
        # 캐시 경로가 갱신되도록 app.CACHE_PROCESSED_PATH에 저장
        master_dataset.to_parquet(app.CACHE_PROCESSED_PATH)
        logger.info(f"Prefetch completed successfully. Shape: {master_dataset.shape}")
    except Exception as e:
        logger.error(f"Prefetch data pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

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
