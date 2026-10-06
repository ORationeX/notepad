import argparse
import logging
import sys

from src.data_loader import ASSETS, load_market

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nasdaq_rebalance")


def prefetch() -> int:
    failed = False
    for ticker in ASSETS:
        try:
            frame, note = load_market(ticker, refresh=True)
            logger.info("%s 저장 완료: %s행 %s", ticker, len(frame), note)
        except Exception as exc:
            logger.error("%s 시세 갱신 실패: %s", ticker, exc)
            failed = True
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description="나스닥 리밸런싱 공식 탐색")
    parser.add_argument("--fetch-only", action="store_true", help="시세만 받아 캐시에 저장하고 종료합니다.")
    args = parser.parse_args()
    if args.fetch_only:
        sys.exit(prefetch())
    print("대시보드는 run_dashboard.bat 으로 실행합니다.")


if __name__ == "__main__":
    main()
