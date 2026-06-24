import os
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tuner  # optimizer helper module

# -----------------------------------------------------------------------------
# 1. 스트림릿 페이지 설정 및 다크 모드 프리미엄 테마 적용
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="나스닥 하락장 위험 경보 & 백테스팅 대시보드",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 프리미엄 다크 스타일 및 가독성 향상을 위한 커스텀 CSS
st.markdown("""
<style>
    /* 전체 앱 배경색 및 폰트 가독성 설정 */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    /* 헤더 스타일링 */
    .main-header {
        font-size: 2.8rem;
        font-weight: 850;
        background: linear-gradient(135deg, #3b82f6 0%, #a855f7 50%, #ff4b4b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: left;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 2.5rem;
        font-weight: 400;
        line-height: 1.6;
    }
    /* 종합 진단 KPI 카드 스타일링 */
    .status-card {
        border-radius: 16px;
        padding: 26px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        margin-bottom: 1.2rem;
        transition: transform 0.2s ease;
    }
    .status-card:hover {
        transform: translateY(-2px);
    }
    .status-safe {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.55) 0%, rgba(2, 44, 34, 0.8) 100%);
        border-color: rgba(16, 185, 129, 0.35);
    }
    .status-warning {
        background: linear-gradient(135deg, rgba(146, 64, 14, 0.55) 0%, rgba(69, 26, 3, 0.8) 100%);
        border-color: rgba(245, 158, 11, 0.35);
    }
    .status-danger {
        background: linear-gradient(135deg, rgba(153, 27, 27, 0.55) 0%, rgba(69, 10, 10, 0.8) 100%);
        border-color: rgba(239, 68, 68, 0.35);
    }
    .card-title {
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #cbd5e1;
        margin-bottom: 10px;
    }
    .card-value {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .card-desc {
        font-size: 0.88rem;
        color: #94a3b8;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 디렉토리 및 캐시 경로 설정 (나스닥용 타겟 캐시)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
CACHE_CONSTITUENTS_PATH = os.path.join(DATA_DIR, "nasdaq100_constituents.parquet")
CACHE_MACRO_PATH = os.path.join(DATA_DIR, "macro_nasdaq_data.parquet")
CACHE_PROCESSED_PATH = os.path.join(DATA_DIR, "master_processed.parquet")

# -----------------------------------------------------------------------------
# 2. 데이터 수집 및 캐싱 파이프라인
# -----------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def scrape_nasdaq100_tickers() -> list:
    """Wikipedia에서 나스닥 100 구성 종목 티커 크롤링."""
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        tickers = []
        for row in table.find_all("tr")[1:]:
            ticker = row.find_all("td")[0].text.strip() # Nasdaq table has symbol in 1st column
            ticker = ticker.replace(".", "-")  # yfinance 호환용 변환
            tickers.append(ticker)
        # Validate that we got tickers
        if not tickers:
            raise ValueError("No tickers found in Wikipedia constituents table.")
        return tickers
    except Exception as e:
        st.warning("Wikipedia 나스닥 100 티커 스크래핑 실패. 주요 30개 종목으로 대체 진행합니다.")
        return [
            "AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "AVGO", "TSLA", "COST",
            "NFLX", "AMD", "ADBE", "PEP", "AZN", "QCOM", "LIN", "TXN", "TMUS", "INTU",
            "AMGN", "ISRG", "AMAT", "CMCSA", "BKNG", "HON", "VRTX", "ADP", "PANW", "MU"
        ]

@st.cache_data(show_spinner=False)
def download_macro_data(start_date: str, end_date: str) -> pd.DataFrame:
    """매크로 지수 데이터 다운로드 (^IXIC: 나스닥종합, HYG: 하이일드채권, ^TNX: 10년물 국채금리)."""
    tickers = ["^IXIC", "HYG", "^TNX"]
    df = yf.download(tickers, start=start_date, end=end_date, group_by="ticker", progress=False)
    if df.empty:
        raise ValueError("yfinance로부터 나스닥 및 매크로 지수를 받지 못했습니다.")
    
    macro_df = pd.DataFrame(index=df.index)
    if "^IXIC" in df.columns.levels[0]:
        nasdaq = df["^IXIC"]
        macro_df["NASDAQ_Open"] = nasdaq["Open"]
        macro_df["NASDAQ_High"] = nasdaq["High"]
        macro_df["NASDAQ_Low"] = nasdaq["Low"]
        macro_df["NASDAQ_Close"] = nasdaq["Close"]
        macro_df["NASDAQ_AdjClose"] = nasdaq["Adj Close"] if "Adj Close" in nasdaq.columns else nasdaq["Close"]
        macro_df["NASDAQ_Volume"] = nasdaq["Volume"]
    if "HYG" in df.columns.levels[0]:
        hyg = df["HYG"]
        macro_df["HYG_Close"] = hyg["Adj Close"] if "Adj Close" in hyg.columns else hyg["Close"]
    if "^TNX" in df.columns.levels[0]:
        tnx = df["^TNX"]
        macro_df["TNX_Close"] = tnx["Adj Close"] if "Adj Close" in tnx.columns else tnx["Close"]
        
    return macro_df.dropna(subset=["NASDAQ_Close"])

@st.cache_data(show_spinner=False)
def download_constituent_data(tickers: list, start_date: str, end_date: str) -> pd.DataFrame:
    """나스닥 100 구성 종목의 주가 데이터를 청크 단위로 병렬 수집."""
    chunk_size = 50
    chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    all_dfs = []
    
    progress_bar = st.progress(0)
    for idx, chunk in enumerate(chunks):
        progress_val = int((idx + 1) / len(chunks) * 100)
        progress_bar.progress(progress_val)
        try:
            chunk_df = yf.download(chunk, start=start_date, end=end_date, group_by="ticker", threads=True, progress=False)
            if not chunk_df.empty:
                all_dfs.append(chunk_df)
        except Exception:
            pass
    progress_bar.empty()
    
    if not all_dfs:
        raise ValueError("나스닥 100 종목 데이터를 다운받지 못했습니다.")
    return pd.concat(all_dfs, axis=1)

def get_complete_data(force_refresh: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """로컬 캐시 확인 혹은 yfinance 다운로드 파이프라인 (나스닥 기준, 증분 동기화 지원)."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    macro_exists = os.path.exists(CACHE_MACRO_PATH)
    constituents_exists = os.path.exists(CACHE_CONSTITUENTS_PATH)
    
    is_incremental = False
    old_macro = None
    old_constituents = None
    
    if macro_exists and constituents_exists:
        try:
            old_macro = pd.read_parquet(CACHE_MACRO_PATH)
            old_constituents = pd.read_parquet(CACHE_CONSTITUENTS_PATH)
            
            if not force_refresh:
                # 강제 갱신이 아니면 이미 로드된 캐시 파일 즉시 반환
                return old_macro, old_constituents
                
            last_date_macro = old_macro.index.max()
            last_date_const = old_constituents.index.max()
            last_date = min(last_date_macro, last_date_const)
            
            start_date = (last_date - timedelta(days=5)).strftime("%Y-%m-%d")
            is_incremental = True
        except Exception:
            pass
            
    if not is_incremental:
        start_date = "1971-01-01"
        
    with st.spinner("Wikipedia에서 나스닥 100 종목 리스트 크롤링 중..."):
        tickers = scrape_nasdaq100_tickers()
        
    with st.spinner(f"매크로 변수 수집 중 ({start_date} ~ {end_date})..."):
        new_macro = download_macro_data(start_date, end_date)
        
    with st.spinner(f"나스닥 100 구성 종목 가격 수집 중 ({start_date} ~ {end_date})..."):
        new_constituents = download_constituent_data(tickers, start_date, end_date)
        
    if is_incremental:
        with st.spinner("증분 데이터와 기존 로컬 캐시 병합 중..."):
            macro_df = pd.concat([old_macro, new_macro])
            macro_df = macro_df[~macro_df.index.duplicated(keep='last')].sort_index()
            
            constituents_df = pd.concat([old_constituents, new_constituents], axis=0)
            constituents_df = constituents_df[~constituents_df.index.duplicated(keep='last')].sort_index()
    else:
        macro_df = new_macro
        constituents_df = new_constituents
        
    # 이동평균 연산 수행
    macro_df["NASDAQ_SMA20"] = macro_df["NASDAQ_Close"].rolling(window=20).mean()
    macro_df["NASDAQ_SMA50"] = macro_df["NASDAQ_Close"].rolling(window=50).mean()
    macro_df["NASDAQ_SMA200"] = macro_df["NASDAQ_Close"].rolling(window=200).mean()
    
    try:
        macro_df.to_parquet(CACHE_MACRO_PATH)
        constituents_df.to_parquet(CACHE_CONSTITUENTS_PATH)
    except Exception:
        pass
        
    return macro_df, constituents_df

# -----------------------------------------------------------------------------
# 3. 복합 금융 전조 지표 연산
# -----------------------------------------------------------------------------

def compute_indicators(macro_df: pd.DataFrame, constituents_df: pd.DataFrame) -> pd.DataFrame:
    """나스닥 100 종목의 시장폭 지표, McClellan, 신용 스프레드 상관관계 등 전조 조건 연산."""
    dates = constituents_df.index
    tickers = constituents_df.columns.levels[0]
    
    breadth_df = pd.DataFrame(index=dates)
    
    # Close, High, Low 임시 로딩 (xs 메서드를 사용하여 고속 및 경고음 없이 컬럼 추출)
    close_prices = constituents_df.xs("Close", axis=1, level=1)
    high_prices = constituents_df.xs("High", axis=1, level=1)
    low_prices = constituents_df.xs("Low", axis=1, level=1)
                
    # 52주(252거래일) 롤링 최고/최저 계산
    rolling_highs = high_prices.rolling(window=252, min_periods=100).max()
    rolling_lows = low_prices.rolling(window=252, min_periods=100).min()
    
    is_new_high = (high_prices >= rolling_highs) & (high_prices.notna())
    is_new_low = (low_prices <= rolling_lows) & (low_prices.notna())
    
    # 전일 대비 상승/하락 여부
    prev_close = close_prices.shift(1)
    is_advancing = (close_prices > prev_close) & (close_prices.notna()) & (prev_close.notna())
    is_declining = (close_prices < prev_close) & (close_prices.notna()) & (prev_close.notna())
    
    is_active = close_prices.notna()
    active_counts = is_active.sum(axis=1)
    active_counts_safe = active_counts.replace(0, np.nan)
    
    # 52주 신/저가 및 매클레런 비율 계산 시 활성 종목이 최소 10개 이상일 때만 유효하게 처리 (가짜 신호 방지)
    valid_breadth = active_counts >= 10
    
    # 조건 A: 시장 폭 분산 비율 계산 (신고가 및 신저가 비율)
    breadth_df["Active_Stocks"] = active_counts
    breadth_df["New_Highs_Pct"] = (is_new_high.sum(axis=1) / active_counts_safe).where(valid_breadth, 0.0)
    breadth_df["New_Lows_Pct"] = (is_new_low.sum(axis=1) / active_counts_safe).where(valid_breadth, 0.0)
    
    # 조건 B: 매클레런 오실레이터 대용 지표
    net_advances_ratio = (((is_advancing.sum(axis=1) - is_declining.sum(axis=1)) / active_counts_safe).fillna(0.0)).where(valid_breadth, 0.0)
    ema19 = net_advances_ratio.ewm(span=19, adjust=False).mean()
    ema39 = net_advances_ratio.ewm(span=39, adjust=False).mean()
    breadth_df["McClellan_Oscillator"] = (ema19 - ema39) * 1000
    
    # 조건 C: 국채 금리 급등 및 스프레드 상관계수 연산
    credit_df = pd.DataFrame(index=macro_df.index)
    if "HYG_Close" in macro_df.columns and "TNX_Close" in macro_df.columns:
        hyg_ret = macro_df["HYG_Close"].pct_change()
        tnx_ret = macro_df["TNX_Close"].pct_change()
        credit_df["HYG_TNX_Corr_20"] = hyg_ret.rolling(window=20).corr(tnx_ret)
        credit_df["Spread_Ratio"] = macro_df["TNX_Close"] / macro_df["HYG_Close"]
        credit_df["Spread_ROC_20"] = credit_df["Spread_Ratio"].pct_change(periods=20)
        credit_df["TNX_Close_SMA20"] = macro_df["TNX_Close"].rolling(window=20).mean()
        
    # 전체 데이터 Join 통합
    master = macro_df.join(breadth_df, how="inner")
    master = master.join(credit_df, how="inner")
    
    # 개장일 기준 필터링: 나스닥 지수가 정상 거래된 날만 사용
    master = master.dropna(subset=["NASDAQ_Close"])
    
    # 남은 NaN 복구
    master = master.ffill().bfill()
    return master

# -----------------------------------------------------------------------------
# 4. 하락장 위험 신호 포트폴리오 백테스팅 시뮬레이터 (조건수 동적 필터 포함)
# -----------------------------------------------------------------------------

def backtest_alarm_strategy(
    df: pd.DataFrame,
    # 매도 (Exit) 조건 파라미터
    hl_threshold_sell: float,
    mcclellan_threshold_sell: float,
    tnx_sma_factor_sell: float,
    min_active_conditions_sell: int,
    # 매수 (Entry) 조건 파라미터
    reentry_strategy: str,
    lockout_days: int,
    hl_threshold_buy: float,
    mcclellan_threshold_buy: float,
    tnx_sma_factor_buy: float,
    sma_pct_buy: float
) -> dict:
    """하락 위험 경보 발동 시 전량 매도(현금화) 및 조건별 매수(재진입) 시뮬레이션."""
    data = df.copy().reset_index()
    n_days = len(data)
    
    # 1. 매도 (Exit) 신호 평가
    cond_a_sell = (data["New_Highs_Pct"] > hl_threshold_sell) & (data["New_Lows_Pct"] > hl_threshold_sell)
    cond_b_sell = data["McClellan_Oscillator"] <= mcclellan_threshold_sell
    cond_c_sell = data["TNX_Close"] > (tnx_sma_factor_sell * data["TNX_Close_SMA20"])
    
    cond_a_sell = cond_a_sell.fillna(False).astype(int)
    cond_b_sell = cond_b_sell.fillna(False).astype(int)
    cond_c_sell = cond_c_sell.fillna(False).astype(int)
    
    # 최근 5일 롤링 결합
    a_rolling_sell = cond_a_sell.rolling(5, min_periods=1).max().astype(int)
    b_rolling_sell = cond_b_sell.rolling(5, min_periods=1).max().astype(int)
    c_rolling_sell = cond_c_sell.rolling(5, min_periods=1).max().astype(int)
    
    active_count_sell = a_rolling_sell + b_rolling_sell + c_rolling_sell
    alarm_sell_signal = active_count_sell >= min_active_conditions_sell
    
    # 2. 매수 (Buy) 복합 시그널 조건 평가 (reentry_strategy == "multi_cond" 시 사용)
    cond_a_buy = data["New_Lows_Pct"] <= hl_threshold_buy
    cond_b_buy = data["McClellan_Oscillator"] > mcclellan_threshold_buy
    cond_c_buy = data["TNX_Close"] <= (tnx_sma_factor_buy * data["TNX_Close_SMA20"])
    
    cond_a_buy = cond_a_buy.fillna(True).astype(int)
    cond_b_buy = cond_b_buy.fillna(False).astype(int)
    cond_c_buy = cond_c_buy.fillna(True).astype(int)
    
    nasdaq_close = data["NASDAQ_Close"].values
    nasdaq_open = data["NASDAQ_Open"].values
    dates = data["Date"].values
    
    benchmark_wealth = nasdaq_close / nasdaq_close[0]
    strategy_wealth = np.ones(n_days)
    
    holding = True
    lockout_counter = 0
    trade_logs = []
    
    for t in range(1, n_days):
        daily_ret = nasdaq_close[t] / nasdaq_close[t-1]
        open_ret = nasdaq_open[t] / nasdaq_close[t-1]
        close_from_open_ret = nasdaq_close[t] / nasdaq_open[t]
        
        # 어제 마감 기준 오늘 아침 시가 거래 판단
        prev_alarm_sell = alarm_sell_signal.iloc[t-1]
        
        if holding:
            if prev_alarm_sell:
                # 경보 발동 -> 오늘 시가에 전량 매도 청산
                holding = False
                lockout_counter = lockout_days
                strategy_wealth[t] = strategy_wealth[t-1] * open_ret
                
                # 로그 기록용 세부 조건 스트링 구성
                reasons = []
                if cond_a_sell.iloc[t-1]: reasons.append("A(시장균열)")
                if cond_b_sell.iloc[t-1]: reasons.append("B(수급악화)")
                if cond_c_sell.iloc[t-1]: reasons.append("C(금리충격)")
                reason_str = f"하락 경보 발동 (충족 조건: {', '.join(reasons)} | 전체 활성: {active_count_sell.iloc[t-1]}개)"
                
                trade_logs.append({
                    "date": dates[t].strftime("%Y-%m-%d") if isinstance(dates[t], datetime) else str(dates[t])[:10],
                    "action": "청산 (현금화)",
                    "price": float(nasdaq_open[t]),
                    "wealth": float(strategy_wealth[t]),
                    "reason": reason_str
                })
            else:
                strategy_wealth[t] = strategy_wealth[t-1] * daily_ret
        else:
            if lockout_counter > 0:
                lockout_counter -= 1
                
            can_reenter = False
            reenter_reason = ""
            
            # 위험 경보가 해제되고 대기기간(lockout)이 끝난 상태에서 재진입 조건 검증
            if not prev_alarm_sell and lockout_counter == 0:
                if reentry_strategy == "lockout":
                    can_reenter = True
                    reenter_reason = "의무 안전 대기기간 종료 및 하락 신호 해제에 따른 재진입"
                elif reentry_strategy == "sma50":
                    nasdaq_c = data["NASDAQ_Close"].iloc[t-1]
                    nasdaq_sma = data["NASDAQ_SMA50"].iloc[t-1]
                    threshold_val = nasdaq_sma * (1 + sma_pct_buy / 100.0)
                    if nasdaq_c > threshold_val:
                        can_reenter = True
                        reenter_reason = f"나스닥 지수({nasdaq_c:.1f})가 50일 이평선 + {sma_pct_buy}%({threshold_val:.1f}) 상회 추세 확인 재진입"
                elif reentry_strategy == "sma20":
                    nasdaq_c = data["NASDAQ_Close"].iloc[t-1]
                    nasdaq_sma = data["NASDAQ_SMA20"].iloc[t-1]
                    threshold_val = nasdaq_sma * (1 + sma_pct_buy / 100.0)
                    if nasdaq_c > threshold_val:
                        can_reenter = True
                        reenter_reason = f"나스닥 지수({nasdaq_c:.1f})가 20일 이평선 + {sma_pct_buy}%({threshold_val:.1f}) 상회 단기 반등 확인 재진입"
                elif reentry_strategy == "mcclellan":
                    mcc = data["McClellan_Oscillator"].iloc[t-1]
                    if mcc > mcclellan_threshold_buy:
                        can_reenter = True
                        reenter_reason = f"매클레런 오실레이터가 매수 기준선({mcclellan_threshold_buy:.1f})을 상회하는 수급 개선({mcc:.2f}) 확인 재진입"
                elif reentry_strategy == "multi_cond":
                    c_a_ok = data["New_Lows_Pct"].iloc[t-1] <= hl_threshold_buy
                    c_b_ok = data["McClellan_Oscillator"].iloc[t-1] > mcclellan_threshold_buy
                    c_c_ok = data["TNX_Close"].iloc[t-1] <= (tnx_sma_factor_buy * data["TNX_Close_SMA20"].iloc[t-1])
                    
                    if c_a_ok and c_b_ok and c_c_ok:
                        can_reenter = True
                        reenter_reason = (f"복합 매수 조건 동시 충족 재진입 (신저가={data['New_Lows_Pct'].iloc[t-1]*100:.2f}% <= {hl_threshold_buy*100:.2f}%, "
                                          f"매클레런={data['McClellan_Oscillator'].iloc[t-1]:.2f} > {mcclellan_threshold_buy:.1f}, 국채금리 안정)")
            
            if can_reenter:
                holding = True
                strategy_wealth[t] = strategy_wealth[t-1] * close_from_open_ret
                trade_logs.append({
                    "date": dates[t].strftime("%Y-%m-%d") if isinstance(dates[t], datetime) else str(dates[t])[:10],
                    "action": "재진입 (매수)",
                    "price": float(nasdaq_open[t]),
                    "wealth": float(strategy_wealth[t]),
                    "reason": reenter_reason
                })
            else:
                strategy_wealth[t] = strategy_wealth[t-1]
                
    def calc_stats(wealth: np.ndarray) -> dict:
        cum_ret = wealth[-1] - 1.0
        daily_rets = pd.Series(wealth).pct_change().dropna()
        n_years = n_days / 252.0
        ann_ret = (wealth[-1]) ** (1.0 / n_years) - 1.0 if wealth[-1] > 0 else -1.0
        ann_vol = daily_rets.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        
        running_max = np.maximum.accumulate(wealth)
        mdd = ((wealth - running_max) / running_max).min()
        
        return {
            "cum_ret": cum_ret,
            "ann_ret": ann_ret,
            "ann_vol": ann_vol,
            "sharpe": sharpe,
            "mdd": mdd
        }
        
    data["CondA_Sell"] = cond_a_sell
    data["CondB_Sell"] = cond_b_sell
    data["CondC_Sell"] = cond_c_sell
    data["Alarm_Signal"] = alarm_sell_signal.astype(int)
    data["Benchmark_Wealth"] = benchmark_wealth
    data["Strategy_Wealth"] = strategy_wealth
    
    return {
        "df": data,
        "bm_stats": calc_stats(benchmark_wealth),
        "st_stats": calc_stats(strategy_wealth),
        "trade_logs": trade_logs
    }

# -----------------------------------------------------------------------------
# 5. 초고속 마스터 가공 완료 캐시 레이어 (슬라이더 조작 지연 제거)
# -----------------------------------------------------------------------------
if "force_refresh" not in st.session_state:
    st.session_state.force_refresh = False

@st.cache_resource
def load_cached_processed_data() -> pd.DataFrame:
    """최종 전조 지표 연산까지 완료된 마스터 데이터프레임 Parquet 캐시 로드."""
    return pd.read_parquet(CACHE_PROCESSED_PATH)

master_dataset = None

# 캐시가 있고 강제 갱신이 아니면 최종 가공 데이터 즉시 로드 (1초 이내)
if not st.session_state.force_refresh and os.path.exists(CACHE_PROCESSED_PATH):
    try:
        master_dataset = load_cached_processed_data()
    except Exception:
        pass

if master_dataset is None:
    # 캐시가 없거나 실시간 갱신을 누른 경우 다운로드 & 지표 연산 진행 후 최종 저장
    try:
        macro_raw, constituents_raw = get_complete_data(st.session_state.force_refresh)
        st.session_state.force_refresh = False
        
        with st.spinner("나스닥 100 복합 전조 지표 연산 중 (처음 한 번만 실행)..."):
            master_dataset = compute_indicators(macro_raw, constituents_raw)
            
        # 최종 마스터 파일 저장 (슬라이더 조작 시 10년치 다운로드 및 연산 루프 전체 생략용)
        master_dataset.to_parquet(CACHE_PROCESSED_PATH)
    except Exception as e:
        st.error(f"데이터 파이프라인 구동 오류: {e}")
        st.stop()

# -----------------------------------------------------------------------------
# 6. 사이드바 제어 패널 (매수/매도 시그널 슬라이더 분리 및 사용자 세팅 JSON 저장)
# -----------------------------------------------------------------------------
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

# 기본 권장 설정값 정의
default_settings = {
    "start_date": "2016-01-01",  # 디폴트는 최근 10년으로 시작하여 로딩 성능 극대화
    "end_date": master_dataset.index.max().strftime("%Y-%m-%d"),
    "hl_threshold_pct_sell": 2.50,
    "mcclellan_threshold_sell": 0.0,
    "tnx_sma_factor_sell": 1.050,
    "min_active_conditions_sell": 2,
    "reentry_strategy": "sma50",
    "lockout_days": 20,
    "sma_pct_buy": 0.0,
    "hl_threshold_pct_buy": 1.50,
    "mcclellan_threshold_buy": 5.0,
    "tnx_sma_factor_buy": 1.020
}

import json

def save_user_settings(settings: dict) -> None:
    st.session_state.user_settings = settings.copy()
    try:
        import tempfile
        temp_dir = os.path.dirname(SETTINGS_PATH)
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, suffix=".tmp", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
            temp_name = f.name
        os.replace(temp_name, SETTINGS_PATH)
    except Exception as e:
        st.warning(f"사용자 설정 저장 실패: {e}")

def get_current_settings() -> dict:
    return {
        "start_date": start_date_val.strftime("%Y-%m-%d"),
        "end_date": end_date_val.strftime("%Y-%m-%d"),
        "hl_threshold_pct_sell": float(hl_threshold_pct_sell),
        "mcclellan_threshold_sell": float(mcclellan_threshold_sell),
        "tnx_sma_factor_sell": float(tnx_sma_factor_sell),
        "min_active_conditions_sell": int(min_active_conditions_sell),
        "reentry_strategy": reentry_strategy,
        "lockout_days": int(lockout_days),
        "sma_pct_buy": float(sma_pct_buy),
        "hl_threshold_pct_buy": float(hl_threshold_pct_buy),
        "mcclellan_threshold_buy": float(mcclellan_threshold_buy),
        "tnx_sma_factor_buy": float(tnx_sma_factor_buy)
    }

# 세션 상태에 저장된 세팅 정보가 없으면 JSON 파일 로드 혹은 기본값 지정
if "user_settings" not in st.session_state:
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                st.session_state.user_settings = json.load(f)
                # 누락된 키가 있으면 기본값 채우기
                for key, val in default_settings.items():
                    if key not in st.session_state.user_settings:
                        st.session_state.user_settings[key] = val
        except Exception:
            st.session_state.user_settings = default_settings.copy()
    else:
        st.session_state.user_settings = default_settings.copy()

st.sidebar.markdown("### 📊 데이터 범위 & 갱신")

min_date = master_dataset.index.min().to_pydatetime()
max_date = master_dataset.index.max().to_pydatetime()

# 날짜 초기값 설정
# Ensure stored start/end dates are valid datetime objects
stored_start = pd.to_datetime(st.session_state.user_settings.get("start_date", "2016-01-01"), errors='coerce')
stored_end = pd.to_datetime(st.session_state.user_settings.get("end_date", max_date.strftime("%Y-%m-%d")), errors='coerce')
# Fallback to defaults if parsing failed
if pd.isna(stored_start):
    stored_start = pd.to_datetime("2016-01-01")
if pd.isna(stored_end):
    stored_end = max_date
# Clamp dates within available data range
stored_start = max(min_date, min(stored_start.to_pydatetime(), max_date))
stored_end = max(min_date, min(stored_end.to_pydatetime(), max_date))

# Date inputs (Streamlit returns datetime.date)
start_date_val = st.sidebar.date_input("분석 시작일", value=stored_start, min_value=min_date, max_value=max_date)
end_date_val = st.sidebar.date_input("분석 종료일", value=stored_end, min_value=min_date, max_value=max_date)

if st.sidebar.button("🔄 야후 파이낸스 실시간 데이터 최신화"):
    st.session_state.force_refresh = True
    st.rerun()

st.sidebar.markdown("---")

# 매도 (Exit) 시그널 설정 섹션
st.sidebar.markdown("### 🚨 매도(청산) 시그널 설정")

hl_threshold_pct_sell = st.sidebar.slider(
    "조건 A(매도): 52주 신/저가 동시 비율 (%)",
    min_value=0.10,
    max_value=10.00,
    value=float(st.session_state.user_settings.get("hl_threshold_pct_sell", 2.50)),
    step=0.01,
    help="나스닥 100 종목 중 52주 신고가 종목 비율과 52주 신저가 종목 비율이 동시에 이 수준을 넘어가면 시장 폭 내부 균열로 판정하여 매도 대기합니다."
)
hl_threshold_sell = hl_threshold_pct_sell / 100.0

mcclellan_threshold_sell = st.sidebar.slider(
    "조건 B(매도): 매클레런 오실레이터 하한선",
    min_value=-50.0,
    max_value=50.0,
    value=float(st.session_state.user_settings.get("mcclellan_threshold_sell", 0.0)),
    step=0.1,
    help="매클레런 오실레이터가 이 값 이하로 내려가면 매도 대기합니다."
)

tnx_sma_factor_sell = st.sidebar.slider(
    "조건 C(매도): 국채 금리 급등율 (SMA20 대비 배수)",
    min_value=1.000,
    max_value=1.200,
    value=float(st.session_state.user_settings.get("tnx_sma_factor_sell", 1.050)),
    step=0.002,
    help="미국 10년물 국채 금리가 최근 20일 이동평균선(SMA20)을 이 배율 이상 초과하면 매도 대기합니다."
)

min_active_conditions_sell = st.sidebar.selectbox(
    "🚨 매도 경보 최소 충족 조건 수",
    options=[1, 2, 3],
    index=[1, 2, 3].index(int(st.session_state.user_settings.get("min_active_conditions_sell", 2))),
    help="설정한 조건 A, B, C 중 최소 몇 개 이상이 만족되어야 대피 신호(경보)를 발동할지 선택합니다."
)

st.sidebar.markdown("---")

# 매수 (Entry/Re-entry) 시그널 설정 섹션
st.sidebar.markdown("### 🟢 매수(재진입) 시그널 설정")
reentry_strategy = st.sidebar.selectbox(
    "🚨 매수 (재진입) 시그널 필터",
    options=["lockout", "sma50", "sma20", "mcclellan", "multi_cond"],
    index=["lockout", "sma50", "sma20", "mcclellan", "multi_cond"].index(st.session_state.user_settings.get("reentry_strategy", "sma50")),
    format_func=lambda x: {
        "lockout": "1. 단순 의무 대기기간",
        "sma50": "2. 50일 이평선 상회 (추천)",
        "sma20": "3. 20일 이평선 상회",
        "mcclellan": "4. 매클레런 지표 반등",
        "multi_cond": "5. 복합 매수 조건 만족"
    }[x],
    help="대피 이후 시장에 재매수 진입할 기준 필터를 선택합니다."
)

lockout_days = st.sidebar.slider(
    "의무 안전 대기기간 (거래일 기준)",
    min_value=0,
    max_value=60,
    value=int(st.session_state.user_settings.get("lockout_days", 20)),
    step=1,
    help="자산을 전량 청산한 후, 재매수 진입이 원천 차단되는 안전 동결 기간을 거래일 기준으로 설정합니다."
)

# 재진입 전략별 상세 파라미터 로출 및 디폴트 설정
sma_pct_buy = float(st.session_state.user_settings.get("sma_pct_buy", 0.0))
hl_threshold_pct_buy = float(st.session_state.user_settings.get("hl_threshold_pct_buy", 1.50))
mcclellan_threshold_buy = float(st.session_state.user_settings.get("mcclellan_threshold_buy", 5.0))
tnx_sma_factor_buy = float(st.session_state.user_settings.get("tnx_sma_factor_buy", 1.020))

if reentry_strategy in ["sma50", "sma20"]:
    sma_pct_buy = st.sidebar.slider(
        "나스닥 돌파 기준 (%)",
        min_value=-2.00,
        max_value=5.00,
        value=sma_pct_buy,
        step=0.05,
        help="지수가 이동평균선 대비 몇 % 이상을 확실히 상회해야 재매수할지 설정합니다. (0%는 골든크로스 즉시 진입)"
    )
elif reentry_strategy == "mcclellan":
    mcclellan_threshold_buy = st.sidebar.slider(
        "매수 매클레런 최소값",
        min_value=-20.0,
        max_value=40.0,
        value=mcclellan_threshold_buy,
        step=0.5,
        help="매클레런 오실레이터가 최소 이 값보다 크게 반등해야 재진입합니다."
    )
elif reentry_strategy == "multi_cond":
    hl_threshold_pct_buy = st.sidebar.slider(
        "조건 A(매수): 52주 신저가 비율 상한 (%)",
        min_value=0.10,
        max_value=10.00,
        value=hl_threshold_pct_buy,
        step=0.01,
        help="신저가 종목 비율이 이 값 이하로 떨어져 투매가 진정되어야 진입합니다."
    )
    mcclellan_threshold_buy = st.sidebar.slider(
        "조건 B(매수): 매클레런 최소값",
        min_value=-20.0,
        max_value=40.0,
        value=mcclellan_threshold_buy,
        step=0.5,
        help="수급 에너지가 이 값보다 높게 반등해야 합니다."
    )
    tnx_sma_factor_buy = st.sidebar.slider(
        "조건 C(매수): 국채 금리 안정 수준 (SMA20 대비 배수)",
        min_value=0.950,
        max_value=1.100,
        value=tnx_sma_factor_buy,
        step=0.002,
        help="미국 10년물 국채 금리가 최근 20일 이동평균선 대비 이 배율 이하로 내려와 진정되어야 진입합니다."
    )

hl_threshold_buy = hl_threshold_pct_buy / 100.0

# 날짜 필터링 및 백테스트 실행 (사전 계산된 마스터 데이터를 사용하므로 0.05초 만에 완료됨)
filtered_df = master_dataset.loc[pd.Timestamp(start_date_val):pd.Timestamp(end_date_val)]

# ── 자동 민감도 튜닝 ────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 자동 민감도 튜닝")
if st.sidebar.button("🚀 매도 시그널 자동 최적화"):
    with st.spinner("매도 파라미터 탐색 중..."):
        sell_grid = {
            "hl_threshold_pct_sell": np.arange(0.5, 5.5, 0.5),
            "mcclellan_threshold_sell": np.arange(-20, 21, 5),
            "tnx_sma_factor_sell": np.arange(1.00, 1.10, 0.01),
            "min_active_conditions_sell": (1, 2, 3),
        }
        buy_grid = {
            "hl_threshold_pct_buy": (hl_threshold_pct_buy,),
            "mcclellan_threshold_buy": (mcclellan_threshold_buy,),
            "tnx_sma_factor_buy": (tnx_sma_factor_buy,),
            "sma_pct_buy": (sma_pct_buy,),
        }
        sell_opt, _ = tuner.grid_search(
            df=filtered_df,
            reentry_strategy=reentry_strategy,
            lockout_days=lockout_days,
            sell_grid=sell_grid,
            buy_grid=buy_grid,
            backtest_func=backtest_alarm_strategy,
        )
        optimized_settings = get_current_settings()
        optimized_settings.update(sell_opt)
        save_user_settings(optimized_settings)
        st.success("매도 파라미터 최적화 완료 🎉")
        st.rerun()

if st.sidebar.button("🚀 매수 시그널 자동 최적화"):
    with st.spinner("매수 파라미터 탐색 중..."):
        sell_grid = {
            "hl_threshold_pct_sell": (hl_threshold_pct_sell,),
            "mcclellan_threshold_sell": (mcclellan_threshold_sell,),
            "tnx_sma_factor_sell": (tnx_sma_factor_sell,),
            "min_active_conditions_sell": (min_active_conditions_sell,),
        }
        buy_grid = {
            "hl_threshold_pct_buy": np.arange(0.5, 3.5, 0.5),
            "mcclellan_threshold_buy": np.arange(-10, 31, 5),
            "tnx_sma_factor_buy": np.arange(0.95, 1.06, 0.01),
            "sma_pct_buy": np.arange(-1.0, 3.1, 0.5),
        }
        _, buy_opt = tuner.grid_search(
            df=filtered_df,
            reentry_strategy=reentry_strategy,
            lockout_days=lockout_days,
            sell_grid=sell_grid,
            buy_grid=buy_grid,
            backtest_func=backtest_alarm_strategy,
        )
        optimized_settings = get_current_settings()
        optimized_settings.update(buy_opt)
        save_user_settings(optimized_settings)
        st.success("매수 파라미터 최적화 완료 🎉")
        st.rerun()

# -----------------------------------------------------------------------------
# 사용자 설정 실시간 파일 저장
# -----------------------------------------------------------------------------
current_settings = get_current_settings()

if current_settings != st.session_state.user_settings:
    save_user_settings(current_settings)
backtest_results = backtest_alarm_strategy(
    df=filtered_df,
    hl_threshold_sell=hl_threshold_sell,
    mcclellan_threshold_sell=mcclellan_threshold_sell,
    tnx_sma_factor_sell=tnx_sma_factor_sell,
    min_active_conditions_sell=min_active_conditions_sell,
    reentry_strategy=reentry_strategy,
    lockout_days=lockout_days,
    hl_threshold_buy=hl_threshold_buy,
    mcclellan_threshold_buy=mcclellan_threshold_buy,
    tnx_sma_factor_buy=tnx_sma_factor_buy,
    sma_pct_buy=sma_pct_buy
)

sim_df = backtest_results["df"]
latest_row = sim_df.iloc[-1]

# -----------------------------------------------------------------------------
# 7. 메인 헤더 레이아웃
# -----------------------------------------------------------------------------
st.markdown("<div class='main-header'>🚨 나스닥 복합 조건 하락장 경보 대시보드</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>나스닥 종합 지수(^IXIC), 나스닥 100 구성 종목 시장폭 내부 분산, 수급 에너지(매클레런), 10년물 국채금리 변동성을 결합한 원클릭 하락 피하기 시뮬레이터</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. 종합 진단 KPI 메트릭 카드 (한글화)
# -----------------------------------------------------------------------------
cond_a_active = latest_row["New_Highs_Pct"] > hl_threshold_sell and latest_row["New_Lows_Pct"] > hl_threshold_sell
cond_b_active = latest_row["McClellan_Oscillator"] <= mcclellan_threshold_sell
cond_c_active = latest_row["TNX_Close"] > (tnx_sma_factor_sell * latest_row["TNX_Close_SMA20"])

active_conditions = int(cond_a_active) + int(cond_b_active) + int(cond_c_active)
status_class = "status-safe"
status_text = "🟢 안전 (SAFE)"
status_desc = "하락 위험 징후가 감지되지 않았습니다. 현재 매수 보유 구간입니다."

# 종합 경보 판단에 min_active_conditions_sell 반영
if active_conditions >= min_active_conditions_sell:
    status_class = "status-danger"
    status_text = "🚨 위험 (DANGER)"
    status_desc = f"다중 조건 위험 신호가 {active_conditions}개 켜졌습니다! 설정된 임계치({min_active_conditions_sell}개)에 도달하여 대피(청산) 권장 구간입니다."
elif active_conditions > 0:
    status_class = "status-warning"
    status_text = "🟡 주의 (CAUTION)"
    status_desc = f"위험 신호가 {active_conditions}개 켜졌습니다. (대피 기준선: {min_active_conditions_sell}개 만족시) 시장 관찰을 요합니다."

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='status-card {status_class}'>
        <div class='card-title'>실시간 시장 종합 진단</div>
        <div class='card-value'>{status_text}</div>
        <div class='card-desc'>{status_desc}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='status-card' style='background-color:#111827;'>
        <div class='card-title'>조건 A: 시장폭 내부 균열</div>
        <div class='card-value' style='color:{"#f87171" if cond_a_active else "#34d399"};'>{"위험" if cond_a_active else "정상"}</div>
        <div class='card-desc'>신고가: {latest_row["New_Highs_Pct"]*100:.2f}% | 신저가: {latest_row["New_Lows_Pct"]*100:.2f}% (기준선: {hl_threshold_pct_sell}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='status-card' style='background-color:#111827;'>
        <div class='card-title'>조건 B: 시장 수급 강도</div>
        <div class='card-value' style='color:{"#f87171" if cond_b_active else "#34d399"};'>{"약세" if cond_b_active else "양호"}</div>
        <div class='card-desc'>매클레런 지표: {latest_row["McClellan_Oscillator"]:.2f} (기준선: {mcclellan_threshold_sell:.1f})</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='status-card' style='background-color:#111827;'>
        <div class='card-title'>조건 C: 금리 변동성 충격</div>
        <div class='card-value' style='color:{"#f87171" if cond_c_active else "#34d399"};'>{"충격" if cond_c_active else "안정"}</div>
        <div class='card-desc'>국채 금리: {latest_row["TNX_Close"]:.2f}% (SMA20 대비: {(latest_row["TNX_Close"]/latest_row["TNX_Close_SMA20"] - 1)*100:+.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. 메인 멀티 플롯 시각화 개선 (휠 줌 scrollZoom 및 렌더링 고속화 다운샘플링 적용)
# -----------------------------------------------------------------------------
st.markdown("### 📈 미국 시장 종합 동향 및 하락 위험 경보 구간 오버레이 (마우스 휠로 줌인/줌아웃 가능)")

# 차트 렌더링용 데이터 다운샘플링 (1,500포인트 내외로 구성하여 렌더링 지연 제거)
chart_step = len(sim_df) // 1500 + 1
chart_df = sim_df.iloc[::chart_step].copy()
dates_idx = chart_df["Date"]
sim_dates = sim_df["Date"]

def build_trade_background_intervals(trade_logs, start_dt, end_dt):
    intervals = []
    current_start = pd.Timestamp(start_dt)
    current_state = "holding"

    for log in trade_logs:
        log_dt = pd.Timestamp(log["date"])
        if log_dt > current_start:
            intervals.append({
                "start": current_start,
                "end": log_dt,
                "state": current_state,
            })

        if log["action"] == "청산 (현금화)":
            current_state = "cash"
        elif log["action"] == "재진입 (매수)":
            current_state = "holding"
        current_start = log_dt

    if pd.Timestamp(end_dt) > current_start:
        intervals.append({
            "start": current_start,
            "end": pd.Timestamp(end_dt),
            "state": current_state,
        })

    return intervals

def add_trade_background(fig_obj, intervals, rows=None):
    colors = {
        "holding": ("#10b981", 0.08),
        "cash": ("#ef4444", 0.14),
    }
    for interval in intervals:
        fillcolor, opacity = colors[interval["state"]]
        if rows:
            for row in rows:
                fig_obj.add_vrect(
                    x0=interval["start"], x1=interval["end"],
                    fillcolor=fillcolor, opacity=opacity,
                    layer="below", line_width=0,
                    row=row, col=1
                )
        else:
            fig_obj.add_vrect(
                x0=interval["start"], x1=interval["end"],
                fillcolor=fillcolor, opacity=opacity,
                layer="below", line_width=0
            )

trade_background_intervals = build_trade_background_intervals(
    backtest_results["trade_logs"],
    sim_dates.iloc[0],
    sim_dates.iloc[-1],
)

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.48, 0.26, 0.26],
    subplot_titles=[
        "<b>[Panel 1] 나스닥 종합 지수 추이 및 전략 보유/현금화 구간 오버레이</b>",
        "<b>[Panel 2] 나스닥 100 내부 구성종목 시장폭 (52주 신고가 vs 신저가 비율)</b>",
        "<b>[Panel 3] 신용 위험 스프레드 대용 지표 (미국 하이일드 채권 및 국채수익률 상관계수)</b>"
    ]
)

# 전략 매매 로그 기준 배경색: 보유 구간은 초록, 현금화 구간은 빨강
add_trade_background(fig, trade_background_intervals, rows=[1, 2, 3])

# Panel 1: NASDAQ Composite Price
fig.add_trace(
    go.Scatter(
        x=dates_idx, 
        y=chart_df["NASDAQ_Close"], 
        name="나스닥 지수 종가", 
        line=dict(color="#3b82f6", width=2.8)
    ),
    row=1, col=1
)

# Panel 2: Market Breadth
fig.add_trace(
    go.Scatter(
        x=dates_idx, 
        y=chart_df["New_Highs_Pct"]*100, 
        name="52주 신고가 종목 비율 (%)", 
        line=dict(color="#10b981", width=2.2)
    ),
    row=2, col=1
)
fig.add_trace(
    go.Scatter(
        x=dates_idx, 
        y=chart_df["New_Lows_Pct"]*100, 
        name="52주 신저가 종목 비율 (%)", 
        line=dict(color="#ef4444", width=2.2)
    ),
    row=2, col=1
)
fig.add_hline(
    y=hl_threshold_pct_sell, line_dash="dash", line_color="#d97706", line_width=1.5,
    annotation_text=f"시장폭 임계치 {hl_threshold_pct_sell}%", annotation_position="top left",
    annotation_font=dict(color="#d97706", size=11),
    row=2, col=1
)

# Panel 3: HYG-TNX Correlation
fig.add_trace(
    go.Scatter(
        x=dates_idx, 
        y=chart_df["HYG_TNX_Corr_20"], 
        name="하이일드(HYG)-국채금리(TNX) 20일 상관계수", 
        line=dict(color="#c084fc", width=2.2)
    ),
    row=3, col=1
)
fig.add_hline(
    y=0.0, line_dash="dot", line_color="#4b5563", line_width=1.5,
    row=3, col=1
)

# 서브플롯 폰트
for annotation in fig['layout']['annotations']:
    annotation['font'] = dict(size=14, color='#f1f5f9', family='Inter, sans-serif')

fig.update_layout(
    height=1050,
    margin=dict(l=60, r=60, t=50, b=50),
    hovermode="x unified",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15, 23, 42, 0.4)",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="right",
        x=1,
        font=dict(size=11, color="#cbd5e1")
    )
)

fig.update_yaxes(title_text="나스닥 지수 종가", gridcolor="rgba(255,255,255,0.08)", row=1, col=1)
fig.update_yaxes(title_text="종목 비율 (%)", gridcolor="rgba(255,255,255,0.08)", row=2, col=1)
fig.update_yaxes(title_text="상관계수 (-1 ~ 1)", gridcolor="rgba(255,255,255,0.08)", row=3, col=1)
fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")

# scrollZoom: True 설정 추가하여 마우스 휠 줌 기능 제공
st.plotly_chart(fig, width="stretch", config={'scrollZoom': True})

# -----------------------------------------------------------------------------
# 10. 백테스트 시뮬레이션 성과 분석
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 🏆 포트폴리오 백테스팅 종합 성과 평가")

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("#### 누적 자산 성장 곡선 (Equity Curve Comparison - 마우스 휠 줌 지원)")
    
    fig_wealth = go.Figure()
    fig_wealth.add_trace(
        go.Scatter(
            x=dates_idx, 
            y=chart_df["Benchmark_Wealth"], 
            name="벤치마크 (Buy & Hold)", 
            line=dict(color="#64748b", width=2.2, dash="dash")
        )
    )
    fig_wealth.add_trace(
        go.Scatter(
            x=dates_idx, 
            y=chart_df["Strategy_Wealth"], 
            name="다중 조건 위험 회피 전략", 
            line=dict(color="#f59e0b", width=3.2)
        )
    )

    # 전략 매매 로그 기준 배경색: 보유 구간은 초록, 현금화 구간은 빨강
    add_trade_background(fig_wealth, trade_background_intervals)
            
    fig_wealth.update_layout(
        height=480,
        margin=dict(l=30, r=30, t=10, b=30),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(size=11, color="#cbd5e1")
        )
    )
    fig_wealth.update_yaxes(title_text="자산 성장 배수 (최초 투자 가치 = 1.0)", gridcolor="rgba(255,255,255,0.08)")
    fig_wealth.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
    
    st.plotly_chart(fig_wealth, width="stretch", config={'scrollZoom': True})

with col_right:
    st.markdown("#### 성과 비교 지표 요약")
    
    bm_stats = backtest_results["bm_stats"]
    st_stats = backtest_results["st_stats"]
    
    stats_data = {
        "평가 지표": [
            "누적 수익률 (Cumulative Return)",
            "연율화 수익률 (Annualized Return)",
            "연율화 변동성 (Annualized Volatility)",
            "샤프 지수 (Sharpe Ratio)",
            "최대 낙폭 (Maximum Drawdown, MDD)"
        ],
        "벤치마크 (Buy & Hold)": [
            f"{bm_stats['cum_ret']*100:.2f}%",
            f"{bm_stats['ann_ret']*100:.2f}%",
            f"{bm_stats['ann_vol']*100:.2f}%",
            f"{bm_stats['sharpe']:.2f}",
            f"{bm_stats['mdd']*100:.2f}%"
        ],
        "다중 조건 대피 전략": [
            f"{st_stats['cum_ret']*100:.2f}%",
            f"{st_stats['ann_ret']*100:.2f}%",
            f"{st_stats['ann_vol']*100:.2f}%",
            f"{st_stats['sharpe']:.2f}",
            f"{st_stats['mdd']*100:.2f}%"
        ]
    }
    
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, hide_index=True, width="stretch")
    
    outperformance = st_stats["cum_ret"] - bm_stats["cum_ret"]
    mdd_improvement = st_stats["mdd"] - bm_stats["mdd"]
    
    if outperformance > 0:
        st.success(f"📈 대피 전략이 나스닥 벤치마크 대비 **{outperformance*100:.2f}%p 초과 수익**을 달성했습니다.")
    else:
        st.warning(f"📉 대피 전략 수익률이 나스닥 벤치마크 대비 **{abs(outperformance)*100:.2f}%p 하회**했습니다.")
        
    if mdd_improvement > 0:
        st.success(f"🛡️ 최대 낙폭(MDD)을 **{mdd_improvement*100:.2f}%p 만큼 개선하여 나스닥 폭락을 헤지**했습니다.")

# -----------------------------------------------------------------------------
# 11. 전략 매매 로그 한글 매핑
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 📋 전략 매매 신호 기록 로그 (청산 및 재매수 내역)")

logs = backtest_results["trade_logs"]
if logs:
    logs_df = pd.DataFrame(logs)
    logs_df.columns = ["날짜", "포지션 조치", "체결 가격 (NASDAQ)", "누적 자산 가치", "사유"]
    logs_df = logs_df[["날짜", "포지션 조치", "체결 가격 (NASDAQ)", "누적 자산 가치", "사유"]]
    
    def highlight_actions(val):
        if val == '청산 (현금화)':
            color = '#7f1d1d'
        else:
            color = '#064e3b'
        return f'background-color: {color}; color: #f8fafc; font-weight: bold; text-align: center; border-radius: 4px;'

    st.dataframe(
        logs_df.style.map(highlight_actions, subset=["포지션 조치"]),
        width="stretch",
        hide_index=True
    )
else:
    st.info("해당 분석 기간 내에는 다중 조건 충족 신호가 발생하지 않아 매매 로그 내역이 비어 있습니다.")
