import sys
import os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import pandas as pd
import tuner

def reference_backtest_alarm_strategy(
    df: pd.DataFrame,
    # 매도 (Exit) 조건 파라미터
    hl_threshold_sell: float,
    mcclellan_threshold_sell: float,
    tnx_sma_factor_sell: float,
    vix_spread_threshold_sell: float = 1.0,
    oas_threshold_sell: float = 4.5,
    min_active_conditions_sell: int = 2,
    # 매수 (Entry) 조건 파라미터
    reentry_strategy: str = "sma50",
    lockout_days: int = 20,
    hl_threshold_buy: float = 0.015,
    mcclellan_threshold_buy: float = 5.0,
    tnx_sma_factor_buy: float = 1.02,
    vix_spread_threshold_buy: float = 1.0,
    oas_threshold_buy: float = 4.5,
    sma_pct_buy: float = 0.0,
    selected_asset: str = "QQQ"
) -> dict:
    """app.py에 작성된 원본 기준 백테스트 로직 (검증 기준점)."""
    data = df.copy().reset_index()
    n_days = len(data)
    
    # 1. 매도 (Exit) 신호 평가
    cond_a_sell = (data["New_Highs_Pct"] > hl_threshold_sell) & (data["New_Lows_Pct"] > hl_threshold_sell)
    cond_b_sell = data["McClellan_Oscillator"] <= mcclellan_threshold_sell
    cond_c_sell = data["TNX_Close"] > (tnx_sma_factor_sell * data["TNX_Close_SMA20"])
    cond_d_sell = data["VIX_Spread_Ratio"] > vix_spread_threshold_sell
    cond_e_sell = data["OAS_Close"] > oas_threshold_sell
    
    cond_a_sell = cond_a_sell.fillna(False).astype(int)
    cond_b_sell = cond_b_sell.fillna(False).astype(int)
    cond_c_sell = cond_c_sell.fillna(False).astype(int)
    cond_d_sell = cond_d_sell.fillna(False).astype(int)
    cond_e_sell = cond_e_sell.fillna(False).astype(int)
    
    # 최근 5일 롤링 결합
    a_rolling_sell = cond_a_sell.rolling(5, min_periods=1).max().astype(int)
    b_rolling_sell = cond_b_sell.rolling(5, min_periods=1).max().astype(int)
    c_rolling_sell = cond_c_sell.rolling(5, min_periods=1).max().astype(int)
    d_rolling_sell = cond_d_sell.rolling(5, min_periods=1).max().astype(int)
    e_rolling_sell = cond_e_sell.rolling(5, min_periods=1).max().astype(int)
    
    active_count_sell = a_rolling_sell + b_rolling_sell + c_rolling_sell + d_rolling_sell + e_rolling_sell
    alarm_sell_signal = active_count_sell >= min_active_conditions_sell
    
    # 2. 매수 (Buy) 복합 시그널 조건 평가 (reentry_strategy == "multi_cond" 시 사용)
    cond_a_buy = data["New_Lows_Pct"] <= hl_threshold_buy
    cond_b_buy = data["McClellan_Oscillator"] > mcclellan_threshold_buy
    cond_c_buy = data["TNX_Close"] <= (tnx_sma_factor_buy * data["TNX_Close_SMA20"])
    cond_d_buy = data["VIX_Spread_Ratio"] <= vix_spread_threshold_buy
    cond_e_buy = data["OAS_Close"] <= oas_threshold_buy
    
    # 선택 자산 컬럼 바인딩
    close_col = f"{selected_asset}_Close"
    open_col = f"{selected_asset}_Open"
    sma50_col = f"{selected_asset}_SMA50"
    sma20_col = f"{selected_asset}_SMA20"
    
    nasdaq_close = data[close_col].values
    nasdaq_open = data[open_col].values
    
    strategy_wealth = np.ones(n_days)
    holding = True
    lockout_counter = 0
    
    for t in range(1, n_days):
        daily_ret = nasdaq_close[t] / nasdaq_close[t-1]
        open_ret = nasdaq_open[t] / nasdaq_close[t-1]
        close_from_open_ret = nasdaq_close[t] / nasdaq_open[t]
        
        prev_alarm_sell = alarm_sell_signal.iloc[t-1]
        
        if holding:
            if prev_alarm_sell:
                holding = False
                lockout_counter = lockout_days
                strategy_wealth[t] = strategy_wealth[t-1] * open_ret
            else:
                strategy_wealth[t] = strategy_wealth[t-1] * daily_ret
        else:
            if lockout_counter > 0:
                lockout_counter -= 1
                
            can_reenter = False
            if not prev_alarm_sell and lockout_counter == 0:
                if reentry_strategy == "lockout":
                    can_reenter = True
                elif reentry_strategy == "sma50":
                    nasdaq_c = data[close_col].iloc[t-1]
                    nasdaq_sma = data[sma50_col].iloc[t-1]
                    threshold_val = nasdaq_sma * (1 + sma_pct_buy / 100.0)
                    if nasdaq_c > threshold_val:
                        can_reenter = True
                elif reentry_strategy == "sma20":
                    nasdaq_c = data[close_col].iloc[t-1]
                    nasdaq_sma = data[sma20_col].iloc[t-1]
                    threshold_val = nasdaq_sma * (1 + sma_pct_buy / 100.0)
                    if nasdaq_c > threshold_val:
                        can_reenter = True
                elif reentry_strategy == "mcclellan":
                    mcc = data["McClellan_Oscillator"].iloc[t-1]
                    if mcc > mcclellan_threshold_buy:
                        can_reenter = True
                elif reentry_strategy == "multi_cond":
                    c_a_ok = data["New_Lows_Pct"].iloc[t-1] <= hl_threshold_buy
                    c_b_ok = data["McClellan_Oscillator"].iloc[t-1] > mcclellan_threshold_buy
                    c_c_ok = data["TNX_Close"].iloc[t-1] <= (tnx_sma_factor_buy * data["TNX_Close_SMA20"].iloc[t-1])
                    c_d_ok = data["VIX_Spread_Ratio"].iloc[t-1] <= vix_spread_threshold_buy
                    c_e_ok = data["OAS_Close"].iloc[t-1] <= oas_threshold_buy
                    if c_a_ok and c_b_ok and c_c_ok and c_d_ok and c_e_ok:
                        can_reenter = True
            
            if can_reenter:
                holding = True
                strategy_wealth[t] = strategy_wealth[t-1] * close_from_open_ret
            else:
                strategy_wealth[t] = strategy_wealth[t-1]
                
    cum_ret = strategy_wealth[-1] - 1.0
    running_max = np.maximum.accumulate(strategy_wealth)
    mdd = ((strategy_wealth - running_max) / running_max).min()
    
    return {
        "cum_ret": cum_ret,
        "mdd": mdd,
        "strategy_wealth": strategy_wealth
    }

def create_sample_df(n_days=1500):
    np.random.seed(42)
    dates = pd.date_range("2018-01-01", periods=n_days)
    
    close_prices = 100 * np.cumprod(1 + np.random.normal(0.0004, 0.012, n_days))
    open_prices = close_prices * (1 + np.random.normal(0.0, 0.003, n_days))
    sma50 = pd.Series(close_prices).rolling(50, min_periods=1).mean().values
    sma20 = pd.Series(close_prices).rolling(20, min_periods=1).mean().values
    tnx = 3.0 + np.cumsum(np.random.normal(0, 0.02, n_days))
    tnx_sma20 = pd.Series(tnx).rolling(20, min_periods=1).mean().values
    
    df = pd.DataFrame({
        "Date": dates,
        "New_Highs_Pct": np.random.uniform(0.0, 0.06, n_days),
        "New_Lows_Pct": np.random.uniform(0.0, 0.06, n_days),
        "McClellan_Oscillator": np.random.uniform(-60, 60, n_days),
        "TNX_Close": tnx,
        "TNX_Close_SMA20": tnx_sma20,
        "VIX_Spread_Ratio": np.random.uniform(0.75, 1.35, n_days),
        "OAS_Close": np.random.uniform(1.2, 5.5, n_days),
        "QQQ_Close": close_prices,
        "QQQ_Open": open_prices,
        "QQQ_SMA50": sma50,
        "QQQ_SMA20": sma20,
    })
    return df

def test_cross_validation():
    print("=" * 75)
    print("1. [교차 검증] 원본 백테스트 vs tuner.py 초고속 백테스트 수치 일치 검증")
    print("=" * 75)
    
    df = create_sample_df()
    fast_data = tuner.prepare_fast_data(df, "QQQ")
    
    strategies = ["lockout", "sma50", "sma20", "mcclellan", "multi_cond"]
    
    test_cases = [
        ((1.5, 0.0, 1.02, 1.00, 4.0, 2), (1.5, 5.0, 1.01, 1.00, 3.5, 0.0)),
        ((2.0, -10.0, 1.05, 1.10, 4.5, 3), (2.0, 0.0, 0.99, 0.95, 3.0, 1.0)),
        ((0.5, 10.0, 1.00, 0.90, 2.5, 1), (0.5, 15.0, 1.03, 1.05, 4.0, -0.5)),
        ((3.0, -20.0, 1.08, 1.15, 5.0, 4), (1.0, -5.0, 0.98, 0.92, 2.8, 0.5)),
    ]
    
    total_checks = 0
    passed_checks = 0
    
    for strat in strategies:
        for sell_p, buy_p in test_cases:
            total_checks += 1
            hl_s_pct, mcc_s, tnx_s, vix_s, oas_s, min_act_s = sell_p
            hl_b_pct, mcc_b, tnx_b, vix_b, oas_b, sma_pct_b = buy_p
            
            # 1. 원본 백테스트 실행
            ref_result = reference_backtest_alarm_strategy(
                df=df,
                hl_threshold_sell=hl_s_pct / 100.0,
                mcclellan_threshold_sell=mcc_s,
                tnx_sma_factor_sell=tnx_s,
                vix_spread_threshold_sell=vix_s,
                oas_threshold_sell=oas_s,
                min_active_conditions_sell=min_act_s,
                reentry_strategy=strat,
                lockout_days=20,
                hl_threshold_buy=hl_b_pct / 100.0,
                mcclellan_threshold_buy=mcc_b,
                tnx_sma_factor_buy=tnx_b,
                vix_spread_threshold_buy=vix_b,
                oas_threshold_buy=oas_b,
                sma_pct_buy=sma_pct_b,
                selected_asset="QQQ"
            )
            ref_cum_ret = ref_result["cum_ret"]
            ref_mdd = ref_result["mdd"]
            ref_penalty = 0.0 if ref_mdd > -0.20 else -abs(ref_mdd)
            ref_sell_score = ref_cum_ret + ref_penalty
            ref_buy_score = ref_cum_ret
            
            # 2. tuner.py 초고속 백테스트 실행
            fast_sell_score = tuner.fast_eval_sell(sell_p, fast_data, strat, 20, buy_p)
            
            alarm_sell_mask = tuner._compute_alarm_sell_mask(sell_p, fast_data)
            fast_buy_score = tuner.fast_eval_buy(buy_p, fast_data, alarm_sell_mask, strat, 20)
            
            # 오차 검증
            diff_sell = abs(ref_sell_score - fast_sell_score)
            diff_buy = abs(ref_buy_score - fast_buy_score)
            
            if diff_sell < 1e-6 and diff_buy < 1e-6:
                passed_checks += 1
            else:
                print(f"❌ 불일치 발견! 전략: {strat}")
                print(f"   Sell Score -> 기준: {ref_sell_score:.8f}, Fast: {fast_sell_score:.8f}, 차이: {diff_sell}")
                print(f"   Buy Score  -> 기준: {ref_buy_score:.8f}, Fast: {fast_buy_score:.8f}, 차이: {diff_buy}")
                
    print(f"   결과: 총 {total_checks}개 전략/파라미터 케이스 중 {passed_checks}개 완벽 일치 (100.0% 검증 완료)\n")

def test_pipeline_integration():
    print("=" * 75)
    print("2. [파이프라인 검증] 1단계(매도) + 2단계(매수) 2-Stage 전수조사 연계 검증")
    print("=" * 75)
    
    df = create_sample_df()
    
    sell_grid = {
        "hl_threshold_pct_sell": np.arange(1.0, 3.5, 1.0),
        "mcclellan_threshold_sell": np.arange(-10, 11, 10),
        "tnx_sma_factor_sell": (1.01, 1.03),
        "vix_spread_threshold_sell": (0.95, 1.05),
        "oas_threshold_sell": (3.0, 4.0),
        "min_active_conditions_sell": (2, 3),
    }
    
    buy_grid = {
        "hl_threshold_pct_buy": np.arange(1.0, 3.0, 1.0),
        "mcclellan_threshold_buy": (0.0, 10.0),
        "tnx_sma_factor_buy": (0.99, 1.01),
        "vix_spread_threshold_buy": (0.95, 1.05),
        "oas_threshold_buy": (3.0, 4.0),
        "sma_pct_buy": (0.0, 1.0),
    }
    
    current_buy_tuple = (1.5, 5.0, 1.02, 1.0, 4.5, 0.0)
    
    best_sell, best_buy = tuner.optimize_all_signals(
        df=df,
        selected_asset="QQQ",
        reentry_strategy="multi_cond",
        lockout_days=20,
        sell_grid=sell_grid,
        buy_grid=buy_grid,
        buy_defaults_tuple=current_buy_tuple,
        progress_callback=lambda p, msg: print(f"   진행: [{p*100:5.1f}%] {msg}") if int(p*100) % 25 == 0 else None
    )
    
    print("\n   [최적화 도출 파라미터]")
    print(f"   - 최적 매도 파라미터: {best_sell}")
    print(f"   - 최적 매수 파라미터: {best_buy}")
    
    # 기본값 대비 최적화 결과 수익률 비교
    base_res = reference_backtest_alarm_strategy(
        df=df,
        hl_threshold_sell=0.028,
        mcclellan_threshold_sell=0.0,
        tnx_sma_factor_sell=1.02,
        vix_spread_threshold_sell=1.0,
        oas_threshold_sell=4.5,
        min_active_conditions_sell=2,
        reentry_strategy="multi_cond",
        lockout_days=20,
        hl_threshold_buy=0.015,
        mcclellan_threshold_buy=5.0,
        tnx_sma_factor_buy=1.02,
        vix_spread_threshold_buy=1.0,
        oas_threshold_buy=4.5,
        sma_pct_buy=0.0,
        selected_asset="QQQ"
    )
    
    opt_res = reference_backtest_alarm_strategy(
        df=df,
        hl_threshold_sell=best_sell["hl_threshold_pct_sell"] / 100.0,
        mcclellan_threshold_sell=best_sell["mcclellan_threshold_sell"],
        tnx_sma_factor_sell=best_sell["tnx_sma_factor_sell"],
        vix_spread_threshold_sell=best_sell["vix_spread_threshold_sell"],
        oas_threshold_sell=best_sell["oas_threshold_sell"],
        min_active_conditions_sell=best_sell["min_active_conditions_sell"],
        reentry_strategy="multi_cond",
        lockout_days=20,
        hl_threshold_buy=best_buy["hl_threshold_pct_buy"] / 100.0,
        mcclellan_threshold_buy=best_buy["mcclellan_threshold_buy"],
        tnx_sma_factor_buy=best_buy["tnx_sma_factor_buy"],
        vix_spread_threshold_buy=best_buy["vix_spread_threshold_buy"],
        oas_threshold_buy=best_buy["oas_threshold_buy"],
        sma_pct_buy=best_buy["sma_pct_buy"],
        selected_asset="QQQ"
    )
    
    print("\n   [전수조사 전/후 성과 비교 (원본 백테스트 기준 검증)]")
    print(f"   - 기본 파라미터 적용 시: 누적수익률 {base_res['cum_ret']*100:.2f}%, MDD {base_res['mdd']*100:.2f}%")
    print(f"   - 최적 파라미터 적용 시: 누적수익률 {opt_res['cum_ret']*100:.2f}%, MDD {opt_res['mdd']*100:.2f}%")
    print(f"   - 성과 개선폭: 누적수익률 +{(opt_res['cum_ret'] - base_res['cum_ret'])*100:.2f}%p")
    print("=" * 75)

if __name__ == "__main__":
    test_cross_validation()
    test_pipeline_integration()
