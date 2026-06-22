import os
import json
import shutil
from datetime import datetime

DATA_DIR = "data"
BACKUP_DIR = "backups"
DB_FILE = os.path.join(DATA_DIR, "etf_data.json")
PENDING_FILE = os.path.join(DATA_DIR, "pending_update.json")

def initialize_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

def get_default_structure():
    return {
        "etfs": {
            "2": {
                "name": "TIME 미국나스닥100액티브",
                "code": "426030",
                "history": {}
            },
            "6": {
                "name": "TIME 글로벌AI인공지능액티브",
                "code": "456600",
                "history": {}
            }
        }
    }

def load_data():
    initialize_directories()
    if not os.path.exists(DB_FILE):
        default_data = get_default_structure()
        save_data(default_data)
        return default_data
        
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[DATA] Error loading {DB_FILE}: {e}")
        # 파일이 비었거나 깨졌을 경우 백업 복구 또는 기본구조 반환
        return get_default_structure()

def save_data(data):
    initialize_directories()
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[DATA] Error saving {DB_FILE}: {e}")
        return False

def create_backup():
    initialize_directories()
    if not os.path.exists(DB_FILE):
        return None
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"etf_data_backup_{timestamp}.json")
    try:
        shutil.copy2(DB_FILE, backup_file)
        print(f"[DATA] Backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"[DATA] Failed to create backup: {e}")
        return None

def validate_data(data):
    """
    저장할 JSON 데이터의 정합성을 검증합니다.
    """
    if not isinstance(data, dict) or "etfs" not in data:
        return False, "루트 오브젝트에 'etfs' 키가 없습니다."
        
    for idx in ["2", "6"]:
        if idx not in data["etfs"]:
            return False, f"etfs 아래에 ETF ID '{idx}'가 없습니다."
        etf = data["etfs"][idx]
        if "history" not in etf:
            return False, f"ETF {idx}에 'history' 키가 없습니다."
        
        # history 내부 데이터 형식 검증
        for date_str, constituents in etf["history"].items():
            if not isinstance(constituents, list):
                return False, f"{date_str}의 데이터가 리스트 형식이 아닙니다."
            for item in constituents:
                required_keys = {"code", "name", "quantity", "amount", "weight"}
                if not required_keys.issubset(item.keys()):
                    return False, f"{date_str}의 종목 정보에 필수 키가 누락되었습니다: {item}"
                    
    return True, "검증 통과"

def load_pending():
    if not os.path.exists(PENDING_FILE):
        return {}
    try:
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[DATA] Error loading pending file: {e}")
        return {}

def save_pending(pending_data):
    initialize_directories()
    try:
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(pending_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[DATA] Error saving pending file: {e}")
        return False

def clear_pending():
    if os.path.exists(PENDING_FILE):
        try:
            os.remove(PENDING_FILE)
            return True
        except Exception as e:
            print(f"[DATA] Error removing pending file: {e}")
    return False

def merge_pending_to_db():
    """
    대기 중인 업데이트(pending_update.json)를 본 DB(etf_data.json)에 안전하게 병합합니다.
    병합 전 반드시 백업을 생성합니다.
    """
    pending = load_pending()
    if not pending:
        return False, "대기 중인 업데이트가 없습니다."
        
    db = load_data()
    
    # 병합용 임시 복사본 작성 후 검증
    import copy
    temp_db = copy.deepcopy(db)
    
    merged_count = 0
    for idx_str, history in pending.items():
        if idx_str not in temp_db["etfs"]:
            continue
        for date_str, constituents in history.items():
            temp_db["etfs"][idx_str]["history"][date_str] = constituents
            merged_count += 1
            
    is_valid, msg = validate_data(temp_db)
    if not is_valid:
        return False, f"병합 데이터 정합성 검증 실패: {msg}"
        
    # 백업 생성
    backup_file = create_backup()
    if not backup_file:
        return False, "데이터 백업을 생성하지 못해 안전을 위해 업데이트를 중단합니다."
        
    # 저장
    if save_data(temp_db):
        clear_pending()
        return True, f"성공적으로 {merged_count}개의 일자 데이터를 업데이트했습니다. 백업본: {os.path.basename(backup_file)}"
    else:
        return False, "메인 데이터베이스 파일 저장에 실패했습니다."

def calculate_events(prev_list, curr_list):
    """
    이전 일자 리스트와 현재 일자 리스트를 비교하여
    신규, 삭제, 수량 증가, 수량 감소 이벤트를 계산합니다.
    """
    prev_map = {item["code"]: item for item in prev_list}
    curr_map = {item["code"]: item for item in curr_list}
    
    events = {
        "new": [],
        "deleted": [],
        "increased": [],
        "decreased": []
    }
    
    # 1. 신규 종목 & 증가/감소 감지
    for code, curr_item in curr_map.items():
        if code not in prev_map:
            events["new"].append({
                "code": code,
                "name": curr_item["name"],
                "quantity": curr_item["quantity"],
                "weight": curr_item["weight"]
            })
        else:
            prev_item = prev_map[code]
            curr_qty = curr_item["quantity"]
            prev_qty = prev_item["quantity"]
            
            qty_diff = curr_qty - prev_qty
            qty_rate = (qty_diff / prev_qty * 100) if prev_qty > 0 else 0.0
            
            weight_diff = curr_item["weight"] - prev_item["weight"]
            
            detail = {
                "code": code,
                "name": curr_item["name"],
                "prev_quantity": prev_qty,
                "quantity": curr_qty,
                "change_qty": qty_diff,
                "change_rate": round(qty_rate, 2),
                "prev_weight": prev_item["weight"],
                "weight": curr_item["weight"],
                "change_weight": round(weight_diff, 2)
            }
            
            if qty_diff > 0:
                events["increased"].append(detail)
            elif qty_diff < 0:
                events["decreased"].append(detail)
                
    # 2. 삭제 종목 감지
    for code, prev_item in prev_map.items():
        if code not in curr_map:
            events["deleted"].append({
                "code": code,
                "name": prev_item["name"],
                "quantity": prev_item["quantity"],
                "weight": prev_item["weight"]
            })
            
    return events
