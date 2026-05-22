import os
import json
from datetime import datetime
import urllib.request
import re
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup

# 1. Fallback Ticker list & Company Names mapping (used if Wikipedia scraping fails or as a base reference)
FALLBACK_COMPANIES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "AMZN": "Amazon.com Inc.",
    "GOOGL": "Alphabet Inc. (Class A)",
    "GOOG": "Alphabet Inc. (Class C)",
    "META": "Meta Platforms Inc.",
    "BRK-B": "Berkshire Hathaway Inc. (Class B)",
    "LLY": "Eli Lilly and Company",
    "AVGO": "Broadcom Inc.",
    "TSLA": "Tesla Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "UNH": "UnitedHealth Group Inc.",
    "V": "Visa Inc.",
    "XOM": "Exxon Mobil Corporation",
    "MA": "Mastercard Incorporated",
    "PG": "Procter & Gamble Company",
    "HD": "Home Depot Inc.",
    "JNJ": "Johnson & Johnson",
    "ASML": "ASML Holding N.V.",
    "COST": "Costco Wholesale Corporation",
    "MRK": "Merck & Co. Inc.",
    "ORCL": "Oracle Corporation",
    "ABBV": "AbbVie Inc.",
    "CVX": "Chevron Corporation",
    "AMD": "Advanced Micro Devices Inc.",
    "NFLX": "Netflix Inc.",
    "KO": "Coca-Cola Company",
    "PEP": "PepsiCo Inc.",
    "ADBE": "Adobe Inc.",
    "TMO": "Thermo Fisher Scientific Inc.",
    "BAC": "Bank of America Corporation",
    "WMT": "Walmart Inc.",
    "CRM": "Salesforce Inc.",
    "ACN": "Accenture plc",
    "QCOM": "Qualcomm Incorporated",
    "MCD": "McDonald's Corporation",
    "CSCO": "Cisco Systems Inc.",
    "INTU": "Intuit Inc.",
    "GE": "General Electric Company",
    "AMGN": "Amgen Inc.",
    "TXN": "Texas Instruments Incorporated",
    "PM": "Philip Morris International Inc.",
    "AMAT": "Applied Materials Inc.",
    "CAT": "Caterpillar Inc.",
    "NOW": "ServiceNow Inc.",
    "IBM": "International Business Machines Corporation",
    "ISRG": "Intuitive Surgical Inc.",
    "UNP": "Union Pacific Corporation",
    "PFE": "Pfizer Inc.",
    "HON": "Honeywell International Inc.",
    "SYK": "Stryker Corporation",
    "SPGI": "S&P Global Inc.",
    "AXP": "American Express Company",
    "INTC": "Intel Corporation",
    "GS": "Goldman Sachs Group Inc.",
    "DIS": "Walt Disney Company",
    "COP": "ConocoPhillips",
    "LMT": "Lockhead Martin Corporation",
    "LRCX": "Lam Research Corporation",
    "TJX": "TJX Companies Inc.",
    "BLK": "BlackRock Inc.",
    "MDLZ": "Mondelez International Inc.",
    "ADI": "Analog Devices Inc.",
    "SCHW": "Charles Schwab Corporation",
    "VRTX": "Vertex Pharmaceuticals Incorporated",
    "GEHC": "GE HealthCare Technologies Inc.",
    "PLD": "Prologis Inc.",
    "AMX": "América Móvil S.A.B. de C.V.",
    "BA": "Boeing Company",
    "REGN": "Regeneron Pharmaceuticals Inc.",
    "ZTS": "Zoetis Inc.",
    "PANW": "Palo Alto Networks Inc.",
    "SNPS": "Synopsys Inc.",
    "UBER": "Uber Technologies Inc.",
    "MU": "Micron Technology Inc.",
    "CDNS": "Cadence Design Systems Inc.",
    "CI": "Cigna Group",
    "C": "Citigroup Inc.",
    "BMY": "Bristol-Myers Squibb Company",
    "CL": "Colgate-Palmolive Company",
    "DE": "Deere & Company",
    "EL": "Estée Lauder Companies Inc.",
    "EQIX": "Equinix Inc.",
    "FI": "Fiserv Inc.",
    "GD": "General Dynamics Corporation",
    "HCA": "HCA Healthcare Inc.",
    "ITW": "Illinois Tool Works Inc.",
    "KLAC": "KLA Corporation",
    "MCK": "McKesson Corporation",
    "MDT": "Medtronic plc",
    "MMC": "Marsh & McLennan Companies Inc.",
    "MS": "Morgan Stanley",
    "ORLY": "O'Reilly Automotive Inc.",
    "PGR": "Progressive Corporation",
    "SHW": "Sherwin-Williams Company",
    "SYY": "Sysco Corporation",
    "T": "AT&T Inc.",
    "WM": "Waste Management Inc.",
    "BSX": "Boston Scientific Corporation"
}

WIKI_SP100_URL = "https://en.wikipedia.org/wiki/S%26P_100"
WIKI_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
WIKI_NASDAQ100_URL = "https://en.wikipedia.org/wiki/Nasdaq-100"

FALLBACK_NASDAQ = {
    "MSFT": "Microsoft Corp.",
    "AAPL": "Apple Inc.",
    "NVDA": "NVIDIA Corp.",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms Inc.",
    "AVGO": "Broadcom Inc.",
    "TSLA": "Tesla Inc.",
    "COST": "Costco Wholesale Corp.",
    "GOOGL": "Alphabet Inc. (Class A)",
    "GOOG": "Alphabet Inc. (Class C)",
    "NFLX": "Netflix Inc.",
    "AMD": "Advanced Micro Devices Inc.",
    "PEP": "PepsiCo Inc.",
    "ADBE": "Adobe Inc.",
    "CSCO": "Cisco Systems Inc.",
    "QCOM": "Qualcomm Inc.",
    "TMUS": "T-Mobile US Inc.",
    "TXN": "Texas Instruments Inc.",
    "INTU": "Intuit Inc.",
    "AMGN": "Amgen Inc."
}

FALLBACK_KOREA = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "373220.KS": "LG에너지솔루션",
    "207940.KS": "삼성바이오로직스",
    "005380.KS": "현대차",
    "005490.KS": "POSCO홀딩스",
    "051910.KS": "LG화학",
    "035420.KS": "NAVER",
    "000270.KS": "기아",
    "006400.KS": "삼성SDI",
    "068270.KS": "셀트리온",
    "003550.KS": "LG",
    "035720.KS": "카카오",
    "012330.KS": "현대모비스",
    "105560.KS": "KB금융",
    "055550.KS": "신한지주",
    "066570.KS": "LG전자",
    "096770.KS": "SK이노베이션",
    "003670.KS": "포스코퓨처엠",
    "032830.KS": "삼성생명"
}

def get_tickers_from_wikipedia(url):
    """Scrapes Wikipedia's constituents table. Returns dict of {ticker: company_name}."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        print(f"Fetching companies from Wikipedia ({url})...")
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': 'constituents'})
            
            companies = {}
            if table:
                rows = table.find_all('tr')[1:] # skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ticker = cols[0].text.strip()
                        # yfinance prefers '-' over '.' for classes (e.g. BRK-B)
                        ticker = ticker.replace('.', '-')
                        name = cols[1].text.strip()
                        companies[ticker] = name
                print(f"Successfully scraped {len(companies)} tickers.")
                return companies
    except Exception as e:
        print(f"Failed to scrape from Wikipedia ({url}): {e}")
    
    return {}

def get_korea_top100():
    """Scrapes Naver Finance's KOSPI market capitalization ranking page 1 and 2 to get top 100 Korean stocks.
    Returns dict of {ticker: company_name} where ticker ends with .KS.
    """
    companies = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for page in [1, 2]:
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?&page={page}"
        req = urllib.request.Request(url, headers=headers)
        try:
            print(f"Fetching Korean companies from Naver Finance (Page {page})...")
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', {'class': 'type_2'})
                if table:
                    for tr in table.find_all('tr'):
                        a = tr.find('a', href=True)
                        if a and 'code=' in a['href']:
                            code = a['href'].split('code=')[1].strip()
                            ticker = f"{code}.KS"
                            name = a.text.strip()
                            companies[ticker] = name
        except Exception as e:
            print(f"Failed to scrape Korean companies from page {page}: {e}")
            
    print(f"Successfully scraped {len(companies)} Korean tickers.")
    return companies

def analyze_stocks(tickers, companies_map, raw_data):
    """Analyzes moving averages and breakout conditions for given tickers. Returns (recommended, filtered, failed)."""
    recommended = []
    filtered = []
    failed = []

    for ticker in tickers:
        name = companies_map.get(ticker, ticker)
        
        try:
            # Extract ticker-specific columns
            if ticker not in raw_data.columns.levels[0]:
                failed.append({
                    "ticker": ticker,
                    "name": name,
                    "reason": "데이터 수집 실패 (티커 정보 없음)"
                })
                continue
            
            # Clean data (drop rows where everything is NaN)
            df = raw_data[ticker].dropna(how='all')
            
            if df.empty or 'Close' not in df.columns or len(df) < 200:
                failed.append({
                    "ticker": ticker,
                    "name": name,
                    "reason": f"데이터 부족 (조회된 거래일수: {len(df)}일, 최소 200일 필요)"
                })
                continue

            # Calculate Moving Averages (SMA)
            df['SMA7'] = df['Close'].rolling(window=7).mean()
            df['SMA30'] = df['Close'].rolling(window=30).mean()
            df['SMA200'] = df['Close'].rolling(window=200).mean()

            # Check if SMA200 is available for the latest row
            if pd.isna(df['SMA200'].iloc[-1]):
                failed.append({
                    "ticker": ticker,
                    "name": name,
                    "reason": "이동평균선 계산 실패 (200일선 데이터 누락)"
                })
                continue

            # Latest values
            close_today = float(df['Close'].iloc[-1])
            sma7_today = float(df['SMA7'].iloc[-1])
            sma30_today = float(df['SMA30'].iloc[-1])
            sma200_today = float(df['SMA200'].iloc[-1])

            # Filtering conditions:
            # 1. 7일선 > 200일선
            cond1 = sma7_today > sma200_today
            # 2. 현재가 > 200일선
            cond2 = close_today > sma200_today
            # 3. 현재가 > 7일선 이면서, 3거래일 이내에 상향 돌파가 일어났을 것
            close_series = df['Close']
            sma7_series = df['SMA7']
            
            cond3 = False
            breakout_days_ago = -1
            
            if close_series.iloc[-1] > sma7_series.iloc[-1]:
                if close_series.iloc[-2] <= sma7_series.iloc[-2]:
                    cond3 = True
                    breakout_days_ago = 0
                elif close_series.iloc[-2] > sma7_series.iloc[-2] and close_series.iloc[-3] <= sma7_series.iloc[-3]:
                    cond3 = True
                    breakout_days_ago = 1
                elif (close_series.iloc[-2] > sma7_series.iloc[-2] and 
                      close_series.iloc[-3] > sma7_series.iloc[-3] and 
                      close_series.iloc[-4] <= sma7_series.iloc[-4]):
                    cond3 = True
                    breakout_days_ago = 2
                elif (close_series.iloc[-2] > sma7_series.iloc[-2] and 
                      close_series.iloc[-3] > sma7_series.iloc[-3] and 
                      close_series.iloc[-4] > sma7_series.iloc[-4] and 
                      close_series.iloc[-5] <= sma7_series.iloc[-5]):
                    cond3 = True
                    breakout_days_ago = 3

            # 4. 현재가가 200일선을 돌파한 지 3거래일 이내일 것
            cond4 = False
            breakout_200_days_ago = -1
            sma200_series = df['SMA200']
            
            if close_series.iloc[-1] > sma200_series.iloc[-1]:
                if close_series.iloc[-2] <= sma200_series.iloc[-2]:
                    cond4 = True
                    breakout_200_days_ago = 0
                elif close_series.iloc[-2] > sma200_series.iloc[-2] and close_series.iloc[-3] <= sma200_series.iloc[-3]:
                    cond4 = True
                    breakout_200_days_ago = 1
                elif (close_series.iloc[-2] > sma200_series.iloc[-2] and 
                      close_series.iloc[-3] > sma200_series.iloc[-3] and 
                      close_series.iloc[-4] <= sma200_series.iloc[-4]):
                    cond4 = True
                    breakout_200_days_ago = 2
                elif (close_series.iloc[-2] > sma200_series.iloc[-2] and 
                      close_series.iloc[-3] > sma200_series.iloc[-3] and 
                      close_series.iloc[-4] > sma200_series.iloc[-4] and 
                      close_series.iloc[-5] <= sma200_series.iloc[-5]):
                    cond4 = True
                    breakout_200_days_ago = 3

            # Prepare historical data for charting (last 120 trading days)
            chart_df = df.iloc[-120:]
            dates = [d.strftime('%Y-%m-%d') for d in chart_df.index]
            prices = [round(float(v), 2) for v in chart_df['Close']]
            sma7_hist = [round(float(v), 2) if not pd.isna(v) else None for v in chart_df['SMA7']]
            sma30_hist = [round(float(v), 2) if not pd.isna(v) else None for v in chart_df['SMA30']]
            sma200_hist = [round(float(v), 2) if not pd.isna(v) else None for v in chart_df['SMA200']]

            stock_info = {
                "ticker": ticker,
                "name": name,
                "current_price": round(close_today, 2),
                "sma7": round(sma7_today, 2),
                "sma30": round(sma30_today, 2),
                "sma200": round(sma200_today, 2),
                "breakout_days_ago": breakout_days_ago,
                "breakout_200_days_ago": breakout_200_days_ago,
                "history": {
                    "dates": dates,
                    "prices": prices,
                    "sma7": sma7_hist,
                    "sma30": sma30_hist,
                    "sma200": sma200_hist
                }
            }

            if cond1 and cond2 and cond3 and cond4:
                recommended.append(stock_info)
            else:
                filtered_stock = stock_info.copy()
                filtered_stock.pop("history")
                filtered.append(filtered_stock)

        except Exception as e:
            failed.append({
                "ticker": ticker,
                "name": name,
                "reason": f"오류 발생 ({str(e)})"
            })
            
    return recommended, filtered, failed

def main():
    # 2. Get tickers and names
    sp100_companies = get_tickers_from_wikipedia(WIKI_SP100_URL)
    sp500_companies = get_tickers_from_wikipedia(WIKI_SP500_URL)
    nasdaq100_companies = get_tickers_from_wikipedia(WIKI_NASDAQ100_URL)
    korea100_companies = get_korea_top100()
    
    # Fallback checks
    if len(sp100_companies) < 20:
        print("S&P 100 fetch failed or returned too few tickers. Using fallback subset...")
        sp100_companies = {k: FALLBACK_COMPANIES[k] for k in list(FALLBACK_COMPANIES.keys())[:100] if k in FALLBACK_COMPANIES}
        
    if len(sp500_companies) < 50:
        print("S&P 500 fetch failed or returned too few tickers. Using fallback...")
        sp500_companies = FALLBACK_COMPANIES

    if len(nasdaq100_companies) < 20:
        print("Nasdaq 100 fetch failed or returned too few tickers. Using fallback...")
        nasdaq100_companies = FALLBACK_NASDAQ

    if len(korea100_companies) < 10:
        print("Korean Top 100 fetch failed or returned too few tickers. Using fallback...")
        korea100_companies = FALLBACK_KOREA

    # Combine all unique tickers for bulk download
    all_tickers = sorted(list(set(
        list(sp100_companies.keys()) + 
        list(sp500_companies.keys()) + 
        list(nasdaq100_companies.keys()) + 
        list(korea100_companies.keys())
    )))
    print(f"Total unique tickers to analyze: {len(all_tickers)}")

    # 3. Bulk download historical daily data for the past 2 years (approx 500 trading days)
    print("Downloading historical data using yfinance...")
    try:
        raw_data = yf.download(all_tickers, period="2y", group_by="ticker", auto_adjust=True, threads=True)
    except Exception as e:
        print(f"Fatal error during download: {e}")
        raw_data = pd.DataFrame()

    # 4. Process each group separately
    print("Analyzing S&P 100 stocks...")
    top100_recommended, top100_filtered, top100_failed = analyze_stocks(
        list(sp100_companies.keys()), sp100_companies, raw_data
    )

    print("Analyzing S&P 500 stocks...")
    top500_recommended, top500_filtered, top500_failed = analyze_stocks(
        list(sp500_companies.keys()), sp500_companies, raw_data
    )

    print("Analyzing Nasdaq 100 stocks...")
    nasdaq100_recommended, nasdaq100_filtered, nasdaq100_failed = analyze_stocks(
        list(nasdaq100_companies.keys()), nasdaq100_companies, raw_data
    )

    print("Analyzing Korean Top 100 stocks...")
    korea100_recommended, korea100_filtered, korea100_failed = analyze_stocks(
        list(korea100_companies.keys()), korea100_companies, raw_data
    )

    # 5. Build output data JSON
    result_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "top100": {
            "stats": {
                "total": len(sp100_companies),
                "recommended": len(top100_recommended),
                "filtered": len(top100_filtered),
                "failed": len(top100_failed)
            },
            "recommended": top100_recommended,
            "filtered": top100_filtered,
            "failed": top100_failed
        },
        "top500": {
            "stats": {
                "total": len(sp500_companies),
                "recommended": len(top500_recommended),
                "filtered": len(top500_filtered),
                "failed": len(top500_failed)
            },
            "recommended": top500_recommended,
            "filtered": top500_filtered,
            "failed": top500_failed
        },
        "nasdaq100": {
            "stats": {
                "total": len(nasdaq100_companies),
                "recommended": len(nasdaq100_recommended),
                "filtered": len(nasdaq100_filtered),
                "failed": len(nasdaq100_failed)
            },
            "recommended": nasdaq100_recommended,
            "filtered": nasdaq100_filtered,
            "failed": nasdaq100_failed
        },
        "korea100": {
            "stats": {
                "total": len(korea100_companies),
                "recommended": len(korea100_recommended),
                "filtered": len(korea100_filtered),
                "failed": len(korea100_failed)
            },
            "recommended": korea100_recommended,
            "filtered": korea100_filtered,
            "failed": korea100_failed
        }
    }

    # 6. Read template.html and write index.html
    template_path = "template.html"
    output_path = "index.html"
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found.")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Replace the placeholder with actual data JSON
    json_str = json.dumps(result_data, ensure_ascii=False, indent=2)
    html_content = html_content.replace("/*INSERT_STOCK_DATA_HERE*/", json_str)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nAnalysis complete!")
    print(f"Top 100 Stats - Total: {result_data['top100']['stats']['total']}, Recommended: {len(top100_recommended)}")
    print(f"Top 500 Stats - Total: {result_data['top500']['stats']['total']}, Recommended: {len(top500_recommended)}")
    print(f"Nasdaq 100 Stats - Total: {result_data['nasdaq100']['stats']['total']}, Recommended: {len(nasdaq100_recommended)}")
    print(f"Korea 100 Stats - Total: {result_data['korea100']['stats']['total']}, Recommended: {len(korea100_recommended)}")
    print(f"Results written to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
