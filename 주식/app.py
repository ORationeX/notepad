import os
from flask import Flask, jsonify, request, send_from_directory
import threading
import time
from datetime import datetime, timedelta

import crawler
import data_manager

app = Flask(__name__, static_folder='static', static_url_path='')

# 백그라운드 크롤링 상태 관리
crawl_status = {
    "status": "idle",       # idle, running, completed, error
    "total_days": 0,
    "current_day": 0,
    "current_date": "",
    "errors": [],
    "last_run": None
}

def get_weekdays_range(start_date, end_date):
    """시작일부터 종료일까지의 주중(월~금) 날짜 리스트를 반환합니다."""
    dates = []
    curr = start_date
    while curr <= end_date:
        if curr.weekday() < 5:  # 월~금요일만 포함 (0~4)
            dates.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)
    return dates

def background_crawl_task(idx, start_date_str, end_date_str):
    global crawl_status
    crawl_status["status"] = "running"
    crawl_status["errors"] = []
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError as e:
        crawl_status["status"] = "error"
        crawl_status["errors"].append(f"날짜 형식이 올바르지 않습니다: {e}")
        return

    # 주중 날짜 생성
    all_dates = get_weekdays_range(start_date, end_date)
    
    # 이미 로컬 DB에 저장된 날짜는 제외
    db_data = data_manager.load_data()
    existing_dates = set()
    if str(idx) in db_data["etfs"]:
        existing_dates = set(db_data["etfs"][str(idx)]["history"].keys())
        
    dates_to_crawl = [d for d in all_dates if d not in existing_dates]
    
    crawl_status["total_days"] = len(dates_to_crawl)
    crawl_status["current_day"] = 0
    
    if not dates_to_crawl:
        crawl_status["status"] = "completed"
        crawl_status["current_date"] = "새로 크롤링할 날짜가 없습니다."
        return

    pending_data = data_manager.load_pending()
    if str(idx) not in pending_data:
        pending_data[str(idx)] = {}
        
    for date_str in dates_to_crawl:
        crawl_status["current_date"] = date_str
        print(f"[CRAWL TASK] Crawling ETF {idx} for {date_str}...")
        
        # 크롤링 수행
        constituents = crawler.crawl_etf_constituents(idx, date_str)
        
        if constituents is not None:
            # 빈 리스트(휴장일)도 저장하여 다음번에 다시 크롤링하지 않도록 함
            pending_data[str(idx)][date_str] = constituents
            # 메모리 절약을 위해 정기적으로 pending 파일에 세이브
            data_manager.save_pending(pending_data)
        else:
            msg = f"{date_str} 크롤링 실패 (웹페이지 응답 에러)"
            print(f"[CRAWL TASK] {msg}")
            crawl_status["errors"].append(msg)
            
        crawl_status["current_day"] += 1
        # 서버 차단 및 과부하 방지를 위한 딜레이 (0.5초)
        time.sleep(0.5)
        
    crawl_status["status"] = "completed"
    crawl_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- API 엔드포인트 ---

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/etf/list')
def get_etf_list():
    db = data_manager.load_data()
    etfs = []
    for idx, info in db["etfs"].items():
        etfs.append({
            "idx": idx,
            "name": info["name"],
            "code": info["code"],
            "data_count": len(info["history"])
        })
    return jsonify(etfs)

@app.route('/api/etf/<idx>/history')
def get_etf_history(idx):
    """
    달력 렌더링에 필요한 날짜별 이벤트 요약 데이터를 가져옵니다.
    """
    db = data_manager.load_data()
    if idx not in db["etfs"]:
        return jsonify({"error": "존재하지 않는 ETF 인덱스입니다."}), 404
        
    history = db["etfs"][idx]["history"]
    sorted_dates = sorted(history.keys())
    
    threshold = request.args.get("threshold", default=0.5, type=float)
    
    events_summary = {}
    for i, date_str in enumerate(sorted_dates):
        curr_list = history[date_str]
        # 데이터가 없는 날(휴장일 등)은 요약 제외
        if not curr_list:
            continue
            
        # 이전 영업일 데이터 찾기
        prev_list = []
        for j in range(i - 1, -1, -1):
            if history[sorted_dates[j]]:
                prev_list = history[sorted_dates[j]]
                break
                
        if prev_list:
            evs = data_manager.calculate_events(prev_list, curr_list, threshold)
            events_summary[date_str] = {
                "new": len(evs["new"]),
                "deleted": len(evs["deleted"]),
                "increased": len(evs["increased"]),
                "decreased": len(evs["decreased"])
            }
        else:
            # 첫 데이터는 비교 대상이 없으므로 모두 '신규'로 처리
            events_summary[date_str] = {
                "new": len(curr_list),
                "deleted": 0,
                "increased": 0,
                "decreased": 0
            }
            
    return jsonify({
        "name": db["etfs"][idx]["name"],
        "code": db["etfs"][idx]["code"],
        "events": events_summary
    })


@app.route('/api/etf/<idx>/date/<date_str>')
def get_etf_date_details(idx, date_str):
    """
    특정 날짜의 구성종목 상세 내역 및 이전 영업일 대비 변화 목록을 반환합니다.
    """
    db = data_manager.load_data()
    if idx not in db["etfs"]:
        return jsonify({"error": "존재하지 않는 ETF 인덱스입니다."}), 404
        
    history = db["etfs"][idx]["history"]
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 서버 당일 날짜(오늘) 요청에 대한 실시간 크롤링 예외 처리
    is_live = False
    if date_str == today_str:
        print(f"[API] Live crawling requested for today: {date_str}")
        curr_list = crawler.crawl_etf_constituents(idx, date_str)
        is_live = True
        if curr_list is None:
            # 실시간 크롤링에 실패하면 DB의 가장 최신 데이터로 폴백 시도
            sorted_dates = sorted(history.keys())
            if sorted_dates:
                date_str = sorted_dates[-1]
                curr_list = history[date_str]
                is_live = False
            else:
                return jsonify({"error": "오늘 데이터 크롤링에 실패했으며, 저장된 과거 데이터가 없습니다."}), 500
    else:
        # 과거 데이터는 로컬 DB에서 조회
        if date_str not in history:
            return jsonify({"error": f"{date_str}의 저장된 데이터가 없습니다."}), 404
        curr_list = history[date_str]
        
    # 2. 이전 영업일 데이터 찾기
    sorted_dates = sorted(history.keys())
    prev_list = []
    
    # 조회 대상 날짜가 DB 내에 있는 경우
    if date_str in sorted_dates:
        idx_in_db = sorted_dates.index(date_str)
        for j in range(idx_in_db - 1, -1, -1):
            if history[sorted_dates[j]]:
                prev_list = history[sorted_dates[j]]
                break
    else:
        # 오늘 날짜 실시간 데이터 등으로 DB에 아직 없는 경우 -> DB의 최신 데이터와 비교
        for j in range(len(sorted_dates) - 1, -1, -1):
            if history[sorted_dates[j]]:
                prev_list = history[sorted_dates[j]]
                break
                
    # 3. 이벤트 계산
    threshold = request.args.get("threshold", default=0.5, type=float)
    events = data_manager.calculate_events(prev_list, curr_list, threshold) if prev_list else {
        "new": [{"code": x["code"], "name": x["name"], "quantity": x["quantity"], "weight": x["weight"]} for x in curr_list],
        "deleted": [],
        "increased": [],
        "decreased": []
    }
    
    return jsonify({
        "date": date_str,
        "is_live": is_live,
        "constituents": curr_list,
        "events": events
    })

@app.route('/api/etf/<idx>/stock/<stock_code>')
def get_stock_history_chart(idx, stock_code):
    """
    특정 단일 종목의 수량 및 비중의 역사적 추이를 반환합니다.
    """
    db = data_manager.load_data()
    if idx not in db["etfs"]:
        return jsonify({"error": "존재하지 않는 ETF 인덱스입니다."}), 404
        
    history = db["etfs"][idx]["history"]
    sorted_dates = sorted(history.keys())
    
    # 1. 먼저 stock_code가 한 번이라도 존재했었는지 확인하고 실제 종목 이름을 구합니다.
    stock_name = None
    found_any = False
    for date_str in sorted_dates:
        constituents = history[date_str]
        for item in constituents:
            # 부분 일치 검색 지원 (예: "NVDA" -> "NVDA US EQUITY", "NVIDIA" -> "NVIDIA Corp")
            if (stock_code.lower() in item["code"].lower()) or (stock_code.lower() in item["name"].lower()):
                stock_name = item["name"]
                # 검색된 실제 매칭 코드로 정정합니다.
                stock_code = item["code"]
                found_any = True
                break
        if found_any:
            break
            
    if not found_any:
        return jsonify({"error": f"종목 코드/명 '{stock_code}'에 대한 내역을 찾을 수 없습니다."}), 404
        
    # --- 야후 파이낸스 API 연동 및 캐싱 적용 ---
    yahoo_ticker = data_manager.bloomberg_to_yahoo_ticker(stock_code)
    yahoo_prices = {}
    currency = "USD"
    if yahoo_ticker and sorted_dates:
        yahoo_prices, currency = data_manager.get_yahoo_cached_prices(
            yahoo_ticker, 
            sorted_dates[0], 
            sorted_dates[-1]
        )
        
    # 2. 전체 날짜에 대해서 데이터를 생성합니다.
    stock_history = []
    for date_str in sorted_dates:
        constituents = history[date_str]
        found = False
        for item in constituents:
            if item["code"].lower() == stock_code.lower():
                eval_price = round(item["amount"] / item["quantity"]) if item["quantity"] > 0 else 0
                real_price = yahoo_prices.get(date_str, 0)
                
                stock_history.append({
                    "date": date_str,
                    "quantity": item["quantity"],
                    "weight": item["weight"],
                    "amount": item["amount"],
                    "eval_price": eval_price,
                    "real_price": real_price,
                    "currency": currency,
                    "name": item["name"],
                    "present": True
                })
                found = True
                break
        if not found:
            stock_history.append({
                "date": date_str,
                "quantity": 0,
                "weight": 0.0,
                "amount": 0,
                "eval_price": 0,
                "real_price": 0,
                "currency": currency,
                "name": stock_name,
                "present": False
            })
            
    # 3. 증감률 및 추가/삭제 플래그 계산
    for i in range(len(stock_history)):
        curr = stock_history[i]
        curr["is_readded"] = False
        curr["is_deleted"] = False
        
        if i == 0:
            curr["change_rate"] = 0.0
            curr["real_price_change_rate"] = 0.0
        else:
            prev = stock_history[i-1]
            if not prev["present"] and curr["present"]:
                # 재추가 / 신규 진입
                curr["is_readded"] = True
                curr["change_rate"] = 999999.0 # Special indicator or handle in JS
                curr["real_price_change_rate"] = 0.0
            elif prev["present"] and not curr["present"]:
                # 삭제됨
                curr["is_deleted"] = True
                curr["change_rate"] = -100.0
                curr["real_price_change_rate"] = -100.0
            elif not prev["present"] and not curr["present"]:
                # 계속 없는 상태
                curr["change_rate"] = 0.0
                curr["real_price_change_rate"] = 0.0
            else:
                # 계속 존재하는 상태
                prev_qty = prev["quantity"]
                curr_qty = curr["quantity"]
                if prev_qty > 0:
                    curr["change_rate"] = round(((curr_qty - prev_qty) / prev_qty) * 100, 2)
                else:
                    curr["change_rate"] = 0.0
                    
                prev_real_price = prev["real_price"]
                curr_real_price = curr["real_price"]
                if prev_real_price > 0:
                    curr["real_price_change_rate"] = round(((curr_real_price - prev_real_price) / prev_real_price) * 100, 2)
                else:
                    curr["real_price_change_rate"] = 0.0
                    
    return jsonify({
        "stock_code": stock_code,
        "stock_name": stock_name,
        "currency": currency,
        "history": stock_history
    })


@app.route('/api/etf/crawl-range', methods=['POST'])
def start_crawl_range():
    """
    특정 날짜 범위의 데이터를 백그라운드 크롤링으로 시작합니다.
    """
    global crawl_status
    if crawl_status["status"] == "running":
        return jsonify({"error": "이미 크롤링 작업이 진행 중입니다."}), 400
        
    req_data = request.json or {}
    idx = req_data.get("idx")
    start_date_str = req_data.get("startDate")
    end_date_str = req_data.get("endDate")
    
    if not idx or not start_date_str or not end_date_str:
        return jsonify({"error": "필수 파라미터(idx, startDate, endDate)가 누락되었습니다."}), 400
        
    # 백그라운드 스레드 가동
    thread = threading.Thread(
        target=background_crawl_task,
        args=(idx, start_date_str, end_date_str)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "크롤링이 백그라운드에서 시작되었습니다.", "status": crawl_status})

@app.route('/api/etf/crawl-progress')
def get_crawl_progress():
    return jsonify(crawl_status)

@app.route('/api/etf/update/pending')
def get_pending_updates():
    """대기 중인 업데이트의 목록(ETF 종류, 포함된 일자 개수 등)을 요약하여 반환합니다."""
    pending = data_manager.load_pending()
    summary = {}
    for idx_str, history in pending.items():
        summary[idx_str] = {
            "dates": sorted(list(history.keys())),
            "count": len(history)
        }
    return jsonify({
        "has_pending": len(pending) > 0,
        "pending": summary
    })

@app.route('/api/etf/update/confirm', methods=['POST'])
def confirm_updates():
    """대기 중인 데이터 업데이트를 승인하고 메인 DB에 병합합니다."""
    success, msg = data_manager.merge_pending_to_db()
    if success:
        return jsonify({"message": msg, "success": True})
    else:
        return jsonify({"error": msg, "success": False}), 500

@app.route('/api/etf/update/cancel', methods=['POST'])
def cancel_updates():
    """대기 중인 업데이트를 취소하고 버퍼를 비웁니다."""
    if data_manager.clear_pending():
        return jsonify({"message": "대기 중인 업데이트가 성공적으로 취소되었습니다.", "success": True})
    else:
        return jsonify({"message": "취소할 대기 중인 업데이트가 없습니다.", "success": True})

if __name__ == '__main__':
    # 디렉토리 초기화
    data_manager.initialize_directories()
    # Flask 앱 구동
    app.run(host='0.0.0.0', port=5000, debug=True)
