import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import ASSETS, load_market, month_span, slice_dates
from src.engine import kelly_fraction, run_constant_mix, run_formula
from src.search import (
    GRID_VERSION,
    OBJECTIVES,
    describe,
    eligible_rows,
    grid_count,
    grid_summary,
    holdout_split,
    initials_for,
    load_table,
    pct_text,
    pick,
    save_table,
    search_table,
    short_name,
)

st.set_page_config(
    page_title="나스닥 리밸런싱 공식",
    page_icon=":material/query_stats:",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SEARCH_PATH = os.path.join(DATA_DIR, "search_table.parquet")


@st.cache_data(show_spinner=False, ttl="6h")
def cached_market(ticker: str) -> tuple[pd.DataFrame, str]:
    return load_market(ticker, refresh=False)


def theme_colors() -> dict:
    base = "dark"
    try:
        base = st.context.theme.base or "dark"
    except Exception:
        base = "dark"
    if base == "dark":
        return {
            "template": "plotly_dark",
            "grid": "rgba(255,255,255,0.08)",
            "font": "#e2e8f0",
        }
    return {
        "template": "plotly_white",
        "grid": "rgba(15,23,42,0.08)",
        "font": "#1f2937",
    }


def search_key(ticker: str, frame: pd.DataFrame, cost_bps: float, max_weight: float) -> str:
    start = pd.Timestamp(frame["date"].iloc[0]).strftime("%Y-%m-%d")
    end = pd.Timestamp(frame["date"].iloc[-1]).strftime("%Y-%m-%d")
    return (
        f"{ticker}|{start}|{end}|{len(frame)}|"
        f"{frame['close'].iloc[0]:.6f}|{frame['close'].iloc[-1]:.6f}|"
        f"{cost_bps:.4f}|w{max_weight:.2f}|g{GRID_VERSION}"
    )


def remember_table(key: str) -> pd.DataFrame | None:
    if st.session_state.get("search_key") == key:
        return st.session_state.get("search_table")
    loaded = load_table(os.path.join(DATA_DIR, "search_table.parquet"), key)
    if loaded is None:
        return None
    st.session_state["search_key"] = key
    st.session_state["search_table"] = loaded
    return loaded


def formula_of(row) -> tuple[float, float, float, float, float]:
    return (float(row["initial"]), float(row["up"]), float(row["down"]), float(row["sell"]), float(row["buy"]))


def same_formula(left, right) -> bool:
    return np.allclose(formula_of(left), formula_of(right), atol=1e-6)


def _neighbor_note(opens, closes, rfs, cost, row, max_weight: float) -> str:
    """오름·내림 폭을 1%p만 바꿨을 때 최종 배수가 무너지면 그 사실을 적는다."""
    params = list(formula_of(row))
    bits = []
    for label, index in (("오름 폭", 1), ("내림 폭", 2)):
        worst = None
        for delta in (-0.01, 0.01):
            trial = params.copy()
            trial[index] = round(params[index] + delta, 2)
            if trial[index] < 0.02 - 1e-9 or trial[index] > 2.0 + 1e-9:
                continue
            result = run_formula(opens, closes, rfs, *trial, cost=cost, max_weight=max_weight)
            if worst is None or result.terminal < worst[0]:
                worst = (result.terminal, trial[index], label)
        if worst is not None and float(row["terminal"]) > 0 and worst[0] < float(row["terminal"]) * 0.85:
            bits.append(f"{worst[2]}만 {pct_text(worst[1])}로 바꾸면 {worst[0]:.2f}배가 됩니다.")
    if not bits:
        return ""
    return "바로 옆 숫자에서는 성적이 크게 달라집니다. " + " ".join(bits)


def apply_layout(fig: go.Figure, title: str, y_title: str, log_y: bool = False) -> go.Figure:
    colors = theme_colors()
    fig.update_layout(
        template=colors["template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Malgun Gothic, sans-serif", color=colors["font"]),
        title=dict(text=title, x=0),
        margin=dict(l=8, r=8, t=48, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
        height=460,
        yaxis_title=y_title,
    )
    fig.update_xaxes(gridcolor=colors["grid"])
    fig.update_yaxes(gridcolor=colors["grid"], type="log" if log_y else "linear")
    return fig


def wealth_figure(dates, series: list[tuple[str, np.ndarray, str]], log_y: bool) -> go.Figure:
    fig = go.Figure()
    for name, values, color in series:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                name=name,
                mode="lines",
                line=dict(color=color, width=2),
            )
        )
    return apply_layout(fig, "시작 자본을 1로 둔 자산", "자산", log_y)


def price_figure(dates, close, trades: list[dict]) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=close, name="수정종가", mode="lines", line=dict(color="#94a3b8", width=1.6)))
    buys = [row for row in trades if row["side"] == "매수"]
    sells = [row for row in trades if row["side"] == "매도"]
    if buys:
        fig.add_trace(
            go.Scatter(
                x=[row["date"] for row in buys],
                y=[row["price"] for row in buys],
                name="매수",
                mode="markers",
                marker=dict(symbol="triangle-up", size=9, color="#34d399"),
            )
        )
    if sells:
        fig.add_trace(
            go.Scatter(
                x=[row["date"] for row in sells],
                y=[row["price"] for row in sells],
                name="매도",
                mode="markers",
                marker=dict(symbol="triangle-down", size=9, color="#f87171"),
            )
        )
    fig = apply_layout(fig, "체결 위치", "수정가격")
    fig.update_layout(height=340)
    return fig


def weight_figure(dates, weights) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=weights * 100,
            name="투자 비중",
            mode="lines",
            line=dict(color="#60a5fa", width=1.5),
            fill="tozeroy",
        )
    )
    fig = apply_layout(fig, "종가 기준 투자 비중", "%")
    fig.update_layout(height=340, showlegend=False)
    fig.update_yaxes(range=[0, 100])
    return fig


def ranking_frame(table: pd.DataFrame, score_col: str, active_only: bool, min_trades: int = 0) -> pd.DataFrame:
    sub = eligible_rows(table, score_col, min_trades=min_trades, active_only=active_only)
    ranked = sub.sort_values(
        [score_col, "terminal", "trades", "up", "down"],
        ascending=[False, False, True, False, False],
        kind="mergesort",
    ).head(20)
    view = pd.DataFrame(
        {
            "순위": np.arange(1, len(ranked) + 1),
            "공식": [short_name(row) for _, row in ranked.iterrows()],
            "최종 배수": ranked["terminal"].to_numpy(),
            "누적 수익(%)": (ranked["terminal"].to_numpy() - 1.0) * 100,
            "연수익(%)": ranked["cagr"].to_numpy() * 100,
            "최대 낙폭(%)": ranked["mdd"].to_numpy() * 100,
            "샤프": ranked["sharpe"].to_numpy(),
            "수익÷낙폭": ranked["calmar"].to_numpy(),
            "매수": ranked["buys"].to_numpy(),
            "매도": ranked["sells"].to_numpy(),
            "평균 비중(%)": ranked["avg_weight"].to_numpy() * 100,
        }
    )
    return view


def arrays_of(frame: pd.DataFrame):
    return (
        frame["open"].to_numpy(np.float64),
        frame["close"].to_numpy(np.float64),
        frame["rf"].to_numpy(np.float64),
        frame["date"].to_numpy(),
    )


st.title("나스닥 리밸런싱 공식")
st.caption(
    "금리나 지표는 보지 않습니다. 기준가에서 정해 둔 만큼 오르면 보유 수량의 일부를 팔고, "
    "정해 둔 만큼 내리면 남은 현금의 일부를 삽니다. "
    "투자 비중은 100%까지 올리지 않고, 고른 달력 기간에는 한 달에 한 번 이상 거래한 공식만 비교합니다."
)

with st.sidebar:
    st.header("데이터")
    ticker = st.selectbox(
        "종목",
        list(ASSETS),
        format_func=lambda item: ASSETS[item],
        key="asset",
    )
    objective_label = st.selectbox(
        "무엇을 최대로 볼까",
        list(OBJECTIVES),
        key="objective",
        help="최종 수익은 끝나는 날의 금액입니다. 수익÷낙폭은 연수익을 최대낙폭으로 나눈 값입니다. 샤프는 현금 수익률을 뺀 수익을 흔들림으로 나눈 값입니다.",
    )
    with st.expander("거래 비용"):
        cost_bps = st.number_input(
            "편도 비용 (bp)",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=1.0,
            key="cost_bps",
            help="1bp는 0.01%입니다. 매수와 매도 각각 이 비율만큼 체결이 불리해집니다.",
        )
    if st.button("시세 새로고침", width="stretch", icon=":material/refresh:"):
        with st.spinner("야후 파이낸스에서 시세를 받는 중"):
            load_market(ticker, refresh=True)
        cached_market.clear()
        st.rerun()
    st.caption("시세는 Yahoo Finance 수정주가, 현금은 미국 13주 국채(^IRX)입니다.")

try:
    if not os.path.exists(os.path.join(DATA_DIR, f"{ticker.replace('^', '').lower()}.parquet")):
        with st.spinner("나스닥 시세를 불러오는 중"):
            market, note = cached_market(ticker)
    else:
        market, note = cached_market(ticker)
except Exception as exc:
    st.error("시세를 준비하지 못했습니다. 인터넷 연결을 확인한 뒤 사이드바에서 시세를 다시 받아 주세요.")
    st.exception(exc)
    st.stop()

data_min = pd.Timestamp(market["date"].min()).date()
data_max = pd.Timestamp(market["date"].max()).date()
default_start = (pd.Timestamp(data_max) - pd.DateOffset(years=3)).date()
if default_start < data_min:
    default_start = data_min

with st.sidebar:
    start_date = st.date_input("시작일", value=default_start, min_value=data_min, max_value=data_max, key="start_date")
    end_date = st.date_input("종료일", value=data_max, min_value=data_min, max_value=data_max, key="end_date")
    max_pct = st.slider(
        "최대 투자 비중",
        20,
        90,
        70,
        5,
        format="%d%%",
        key="max_weight_pct",
        help="이 비율을 넘겨서 사지 않습니다. 100%는 두지 않습니다.",
    )

view = slice_dates(market, start_date, end_date)
if len(view) < 60:
    st.error("이 기간의 거래일이 너무 적습니다. 달력에서 기간을 더 길게 잡아 주세요.")
    st.stop()

opens, closes, rfs, dates = arrays_of(view)
cost = float(cost_bps) / 10000.0
max_weight = max_pct / 100.0
key = search_key(ticker, view, float(cost_bps), max_weight)
score_col = OBJECTIVES[objective_label]
start_label = pd.Timestamp(dates[0]).strftime("%Y-%m-%d")
end_label = pd.Timestamp(dates[-1]).strftime("%Y-%m-%d")
cash_annual = float(np.mean(rfs) * 252)
months = month_span(dates)
formula_total = grid_count(initials=initials_for(max_weight))

if note:
    st.warning(note)
st.caption(
    f"{ASSETS[ticker]} · {start_label} ~ {end_label} · {len(view):,}거래일 · {months}개월 · "
    f"현금 수익률 연평균 {cash_annual:.2%}"
)
st.caption(f"이 기간의 후보는 매매가 {months}번 이상인 공식입니다. 투자 비중은 {max_pct}%에서 멈춥니다.")

with st.expander("예시 숫자 바꾸기"):
    c1, c2, c3 = st.columns(3)
    with c1:
        initial_pct = st.slider("처음 사는 비중", 5, 90, 30, 5, format="%d%%", key="ex_initial")
    with c2:
        up_pct = st.slider("오르면 파는 기준", 2, 100, 5, 1, format="%d%%", key="ex_up")
    with c3:
        down_pct = st.slider("내리면 사는 기준", 2, 100, 5, 1, format="%d%%", key="ex_down")
    c4, c5 = st.columns(2)
    with c4:
        sell_pct = st.slider("그때 파는 수량", 5, 100, 25, 5, format="%d%%", key="ex_sell")
    with c5:
        buy_pct = st.slider("그때 사는 현금", 5, 100, 25, 5, format="%d%%", key="ex_buy")

example_initial = min(initial_pct, max_pct) / 100.0
example = (example_initial, up_pct / 100, down_pct / 100, sell_pct / 100, buy_pct / 100)
st.caption(grid_summary(max_weight))
find_clicked = st.button(
    "수익이 가장 큰 공식 찾기",
    type="primary",
    icon=":material/calculate:",
    width="content",
)

if find_clicked:
    total = formula_total
    bar = st.progress(0, text=f"0 / {total:,}개 공식")

    def _on_progress(fraction, text):
        bar.progress(min(float(fraction), 1.0), text=text)

    try:
        split_now = holdout_split(len(opens))
        table = search_table(
            opens,
            closes,
            rfs,
            cost=cost,
            split=split_now,
            on_progress=_on_progress,
            max_weight=max_weight,
            min_trades=months,
            train_min_trades=month_span(dates[:split_now]) if split_now else 0,
        )
    except Exception as exc:
        st.exception(exc)
        st.stop()
    bar.empty()
    save_table(SEARCH_PATH, key, table)
    st.session_state["search_key"] = key
    st.session_state["search_table"] = table

table = remember_table(key)
if st.session_state.get("search_key") not in (None, key) and table is None:
    st.caption("종목, 기간, 비용, 최대 비중이 바뀌었습니다. 이 조건으로 다시 계산하면 1위가 바뀝니다.")

split = holdout_split(len(opens))
winner = pick(table, score_col, min_trades=months) if table is not None else None
winner_30 = (
    pick(table, score_col, initial=0.30, min_trades=months)
    if table is not None and max_weight + 1e-9 >= 0.30
    else None
)

focus = winner if winner is not None else {
    "initial": example[0],
    "up": example[1],
    "down": example[2],
    "sell": example[3],
    "buy": example[4],
}
focus_run = run_formula(opens, closes, rfs, *formula_of(focus), cost=cost, dates=dates, max_weight=max_weight)
held = run_formula(opens, closes, rfs, 1.0, 10.0, 10.0, 0.0, 0.0, cost=cost, dates=dates)
capped_hold = run_formula(
    opens, closes, rfs, max_weight, 10.0, 10.0, 0.0, 0.0, cost=cost, dates=dates, max_weight=max_weight
)
example_run = focus_run if winner is None and formula_of(focus) == example else run_formula(
    opens, closes, rfs, *example, cost=cost, dates=dates, max_weight=max_weight
)
static_run = run_formula(
    opens, closes, rfs, example[0], 10.0, 10.0, 0.0, 0.0, cost=cost, dates=dates, max_weight=max_weight
)

if winner is None:
    st.subheader("예시 공식")
    st.write(describe(focus))
    st.caption("이 숫자는 출발점입니다. 위 버튼이 같은 규칙에서 최종 금액이 더 큰 조합을 찾습니다.")
else:
    lead = {
        "terminal": "최종 금액이 가장 큰 공식",
        "calmar": "연수익을 최대낙폭으로 나눈 값이 가장 큰 공식",
        "sharpe": "샤프가 가장 큰 공식",
    }[score_col]
    with st.container(border=True):
        st.subheader(lead)
        st.write(describe(winner))
        raw_best = table.sort_values(
            ["terminal", "trades", "up", "down"],
            ascending=[False, True, False, False],
            kind="mergesort",
        ).iloc[0]
        same_peak = same_formula(raw_best, winner)
        trade_count = int(winner["buys"]) + int(winner["sells"])
        pace = trade_count / months if months else 0.0
        limit_text = (
            f"{formula_total:,}개 가운데, 비중 {max_pct}% 이하이고 "
            f"{months}개월 동안 매매가 {months}번 이상인 공식 중 1위입니다. "
            f"시작 자본은 {winner['terminal']:.2f}배가 됩니다. "
            f"비중 {max_pct}%만 들고 있으면 {capped_hold.terminal:.2f}배, "
            f"100% 보유는 {held.terminal:.2f}배입니다. "
            f"매매는 {trade_count}번이라 한 달에 {pace:.1f}번입니다."
        )
        if score_col == "terminal" and same_peak:
            st.write(limit_text)
        elif score_col == "terminal":
            st.write(limit_text)
            st.caption(
                f"눈금 한 칸을 따지지 않은 최고 성적은 {short_name(raw_best)} 로 {raw_best['terminal']:.2f}배입니다. "
                f"그 옆 눈금은 {raw_best['floor']:.2f}배까지 내려갑니다."
            )
        else:
            st.write(limit_text)
        if trade_count < months:
            st.caption(
                f"한 달에 한 번을 채운 공식이 없습니다. 매매가 {trade_count}번으로 가장 잦은 공식을 보여 줍니다."
            )
        peak = table.sort_values(["terminal", "trades"], ascending=[False, True], kind="mergesort").iloc[0]
        if int(peak["trades"]) < months and not same_formula(peak, winner):
            st.caption(
                f"매매 횟수를 따지지 않으면 {short_name(peak)} 이 {peak['terminal']:.2f}배이지만, "
                f"매매는 {int(peak['trades'])}번입니다."
            )
        fragile = _neighbor_note(opens, closes, rfs, cost, winner, max_weight)
        if fragile:
            st.caption(fragile)
        if int(winner["buys"]) < 1 or int(winner["sells"]) < 1:
            st.caption("이 기간에는 매수와 매도가 모두 일어난 조합이 없어, 금액이 가장 큰 조합을 보여 줍니다.")

with st.container(horizontal=True):
    step = max(1, len(focus_run.wealth) // 80)
    st.metric(
        "누적 수익",
        f"{(focus_run.terminal - 1) * 100:.1f}%",
        delta=f"{(focus_run.terminal - held.terminal) * 100:+.1f}%p",
        help="같은 기간 100% 보유와의 누적 수익 차이입니다.",
        border=True,
        chart_data=focus_run.wealth[::step].tolist(),
        chart_type="line",
    )
    st.metric("연환산", f"{focus_run.cagr * 100:.1f}%", border=True)
    st.metric("최대 낙폭", f"{focus_run.mdd * 100:.1f}%", border=True, help="고점 대비 가장 많이 줄었던 비율입니다.")
    st.metric("평균 투자 비중", f"{focus_run.avg_weight * 100:.0f}%", border=True)
    st.metric("매수 / 매도", f"{focus_run.buys} / {focus_run.sells}", border=True, help="시작 매수는 횟수에서 빼 두었습니다.")

log_y = st.toggle("자산 곡선을 로그 눈금으로", value=False)
series = [
    ("100% 보유", held.wealth, "#94a3b8"),
    ("예시 비중만 보유", static_run.wealth, "#64748b"),
    ("예시 공식", example_run.wealth, "#fbbf24"),
]
if winner is not None:
    series.append(("수익 1위", focus_run.wealth, "#60a5fa"))
    if winner_30 is not None and not same_formula(winner_30, winner):
        run_30 = run_formula(opens, closes, rfs, *formula_of(winner_30), cost=cost, dates=dates, max_weight=max_weight)
        series.insert(-1, ("초기 30% 최적", run_30.wealth, "#c084fc"))
    else:
        run_30 = focus_run
else:
    run_30 = None

raw_kelly = kelly_fraction(closes, rfs)
capped_kelly = float(np.clip(raw_kelly, 0.0, 1.0))
if capped_kelly < 0.98:
    mix = run_constant_mix(opens, closes, rfs, capped_kelly, dates, cost=cost)
    series.insert(1, (f"켈리 고정 {capped_kelly:.0%}", mix.wealth, "#34d399"))
else:
    mix = None

st.plotly_chart(wealth_figure(dates, series, log_y), width="stretch")
if raw_kelly > 1.01:
    st.caption(
        f"이 구간 수익률과 변동성으로 계산한 켈리 비중은 {raw_kelly:.0%}입니다. "
        "빌려서 사지 않으면 상한은 100%라서, 고정 비중만 고르면 전량 보유와 같습니다."
    )
elif mix is not None:
    st.caption(
        f"매달 비중을 {capped_kelly:.0%}로 되돌리면 최종 {mix.terminal:.2f}배입니다. "
        "비교용이며, 위의 오르면 팔고 내리면 사는 공식과는 규칙이 다릅니다."
    )

left, right = st.columns(2)
with left:
    st.plotly_chart(price_figure(dates, closes, focus_run.trades), width="stretch")
with right:
    st.plotly_chart(weight_figure(dates, focus_run.weights), width="stretch")

if winner is not None and winner_30 is not None:
    if run_30 is None:
        run_30 = run_formula(opens, closes, rfs, *formula_of(winner_30), cost=cost, dates=dates, max_weight=max_weight)
    static_30 = run_formula(
        opens, closes, rfs, 0.30, 10.0, 10.0, 0.0, 0.0, cost=cost, dates=dates, max_weight=max_weight
    )
    hold_col, check_col = st.columns(2)
    with hold_col:
        with st.container(border=True):
            st.markdown("**처음 30%에서 가장 나은 공식**")
            if same_formula(winner_30, winner):
                st.write("전체 1위가 이미 처음 30%를 사는 공식입니다.")
            st.write(describe(winner_30))
            st.write(
                f"이 공식은 {winner_30['terminal']:.2f}배입니다. "
                f"30%를 사고 그대로 두면 {static_30.terminal:.2f}배, "
                f"100% 보유는 {held.terminal:.2f}배입니다."
            )
    with check_col:
        with st.container(border=True):
            st.markdown("**뒤 구간에 다시 적용**")
            if split is None:
                st.write("거래일이 2년보다 적어서 앞 구간과 뒤 구간을 나누지 않았습니다.")
            else:
                train_months = month_span(dates[:split])
                train_row = pick(
                    table,
                    f"train_{score_col}",
                    buys_col="train_buys",
                    sells_col="train_sells",
                    min_trades=train_months,
                )
                test = run_formula(
                    opens[split:],
                    closes[split:],
                    rfs[split:],
                    *formula_of(train_row),
                    cost=cost,
                    dates=dates[split:],
                    max_weight=max_weight,
                )
                test_hold = run_formula(
                    opens[split:], closes[split:], rfs[split:], 1.0, 10.0, 10.0, 0.0, 0.0, cost=cost, dates=dates[split:]
                )
                train_end = pd.Timestamp(dates[split - 1]).strftime("%Y-%m-%d")
                test_start = pd.Timestamp(dates[split]).strftime("%Y-%m-%d")
                st.write(
                    f"{start_label}–{train_end}에서 고른 공식을 {test_start}–{end_label}에 자본을 다시 넣고 적용했습니다. "
                    f"검증 구간에서 이 공식은 {test.terminal:.2f}배, 100% 보유는 {test_hold.terminal:.2f}배입니다. "
                    f"학습 구간에서는 {train_row['train_terminal']:.2f}배였습니다."
                )
                if same_formula(train_row, winner):
                    st.caption("검증에 쓴 공식은 전체 기간 1위와 같습니다.")
                else:
                    st.caption("검증에 쓴 공식은 전체 기간 1위와 다릅니다. " + describe(train_row))

if table is not None:
    st.subheader("계산한 공식 상위 20개")
    active_only = st.toggle("매수와 매도가 모두 있던 공식만", value=True)
    ranked = ranking_frame(table, score_col, active_only, min_trades=months)
    st.dataframe(
        ranked,
        width="stretch",
        hide_index=True,
        height=420,
        column_config={
            "최종 배수": st.column_config.NumberColumn(format="%.2f"),
            "누적 수익(%)": st.column_config.NumberColumn(format="%.1f"),
            "연수익(%)": st.column_config.NumberColumn(format="%.1f"),
            "최대 낙폭(%)": st.column_config.NumberColumn(format="%.1f"),
            "샤프": st.column_config.NumberColumn(format="%.2f"),
            "수익÷낙폭": st.column_config.NumberColumn(format="%.2f"),
            "평균 비중(%)": st.column_config.NumberColumn(format="%.0f"),
        },
    )
    st.caption(
        grid_summary(max_weight)
        + " 순위표에는 앞선 공식만 남깁니다. 매수·매도 횟수에는 첫날 매수가 빠집니다."
    )

trade_view = pd.DataFrame(focus_run.trades)
if not trade_view.empty:
    trade_view = trade_view.rename(
        columns={"date": "날짜", "side": "구분", "price": "체결가", "notional": "규모(시작=1)", "weight": "체결 직후 비중(%)"}
    )
    trade_view["체결가"] = trade_view["체결가"].round(2)
    trade_view["규모(시작=1)"] = trade_view["규모(시작=1)"].round(2)
    trade_view["체결 직후 비중(%)"] = (trade_view["체결 직후 비중(%)"] * 100).round(0)
    trade_view = trade_view.iloc[::-1]
    st.subheader("매매 기록")
    st.dataframe(
        trade_view,
        width="stretch",
        hide_index=True,
        height=360,
        column_config={
            "체결가": st.column_config.NumberColumn(format="%.2f"),
            "규모(시작=1)": st.column_config.NumberColumn(format="%.2f", help="시작 자본을 1로 둔 체결 금액입니다."),
            "체결 직후 비중(%)": st.column_config.NumberColumn(format="%.0f"),
        },
    )

st.caption("선택한 기간 전체에서 금액이 가장 컸던 공식입니다. 다음 구간에도 같다는 뜻은 아니며, 뒤 구간 결과가 그 차이를 보여 줍니다.")
