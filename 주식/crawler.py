import requests
from bs4 import BeautifulSoup
import re
import time

def crawl_etf_constituents(idx, date_str):
    """
    TimeETF 웹페이지에서 특정 ETF(idx)의 특정 일자(date_str: YYYY-MM-DD) 구성종목 데이터를 크롤링합니다.
    """
    url = f"https://timeetf.co.kr/m11_view.php?idx={idx}&pdfDate={date_str}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[CRAWL] status code {response.status_code} for idx={idx}, date={date_str}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 구성종목 테이블 찾기 (class가 table3 moreList1 인 테이블 또는 '종목코드' 헤더가 있는 테이블)
        table = None
        for t in soup.find_all('table'):
            thead = t.find('thead')
            if thead and '종목코드' in thead.text:
                table = t
                break
                
        if not table:
            print(f"[CRAWL] Table not found for idx={idx}, date={date_str}")
            return None
            
        tbody = table.find('tbody')
        if not tbody:
            return []
            
        rows = tbody.find_all('tr')
        if not rows:
            return []
            
        constituents = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
                
            code = cols[0].text.strip()
            name = cols[1].text.strip()
            quantity_str = cols[2].text.strip().replace(',', '')
            amount_str = cols[3].text.strip().replace(',', '')
            weight_str = cols[4].text.strip().replace(',', '')
            
            # 현금 자산 처리 또는 종목코드 유효성 처리
            if name == "현금" or not code:
                code = "CASH"
                name = "현금"
            
            # 숫자 파싱
            try:
                quantity = int(quantity_str) if quantity_str else 0
            except ValueError:
                try:
                    quantity = float(quantity_str) if quantity_str else 0.0
                except ValueError:
                    quantity = 0
                    
            try:
                amount = int(amount_str) if amount_str else 0
            except ValueError:
                try:
                    amount = float(amount_str) if amount_str else 0.0
                except ValueError:
                    amount = 0
                    
            try:
                weight = float(weight_str) if weight_str else 0.0
            except ValueError:
                weight = 0.0
                
            constituents.append({
                "code": code,
                "name": name,
                "quantity": quantity,
                "amount": amount,
                "weight": weight
            })
            
        return constituents
        
    except Exception as e:
        print(f"[CRAWL] Exception occurred: {e}")
        return None

if __name__ == "__main__":
    # 단독 테스트 코드
    print("Testing crawler for idx=6, date=2026-06-19...")
    data = crawl_etf_constituents(6, "2026-06-19")
    if data:
        print(f"Successfully crawled {len(data)} constituents.")
        for item in data[:5]:
            print(item)
    else:
        print("Failed to crawl or empty.")
