"""나스닥이 상승기인지 하락기인지 보여주는 화면."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data import load_prices
from src.features import SAMPLE_START, build_features, window_positions
from src.regime import (
    SEARCH_AXES,
    choose,
    classify_baseline,
    evaluate,
    search_count,
    state_for,
    window_stats,
    worker_count,
)

MARKS = (
    ("2000-03-10", "닷컴 고점"),
    ("2002-10-09", "닷컴 저점"),
    ("2009-03-09", "금융위기 저점"),
    ("2020-03-23", "코로나 저점"),
    ("2021-11-19", "2021년 고점"),
    ("2022-12-28", "2022년 저점"),
)


def percent_points(value: float) -> str:
    if not np.isfinite(value):
        return "—"
    return f"{value * 100:.1f}%"


def cached_features(nonce: int) -> pd.DataFrame:
    return build_features(load_prices(refresh=nonce > 0))


def cached_search(nonce: int, train_end: str):
    return evaluate(
        cached_features(nonce),
        pd.Timestamp(train_end),
        axes=SEARCH_AXES,
        parallel=True,
    )


def _bump_nonce() -> None:
    st.session_state.data_nonce = int(st.session_state.get("data_nonce", 0)) + 1


def regime_frame(features: pd.DataFrame, state: np.ndarray) -> pd.DataFrame:
    view = features.loc[features.index >= SAMPLE_START].copy()
    labels = pd.Series(state, index=features.index).loc[view.index]
    view["label"] = labels.map({1: "상승", -1: "하락", 0: "판정 전"})
    return view


def band_frame(view: pd.DataFrame) -> pd.DataFrame:
    labels = view["label"].to_numpy()
    dates = view.index
    rows = []
    begin = 0
    last = len(labels) - 1
    for i in range(1, len(labels) + 1):
        if i == len(labels) or labels[i] != labels[begin]:
            end = dates[i] if i <= last else dates[last] + pd.Timedelta(days=1)
            rows.append({"start": dates[begin], "end": end, "label": labels[begin]})
            begin = i
    return pd.DataFrame(rows)


def switch_frame(index: pd.DatetimeIndex, state: np.ndarray) -> pd.DataFrame:
    dates = []
    for i in range(1, len(state)):
        if int(state[i]) != 0 and int(state[i]) != int(state[i - 1]) and index[i] >= SAMPLE_START:
            dates.append(index[i])
    return pd.DataFrame({"date": dates})


def price_chart(
    view: pd.DataFrame,
    baseline_switches: pd.DataFrame,
    show_marks: bool,
    split: pd.Timestamp,
):
    import altair as alt

    low = float(view["ixic"].min()) * 0.92
    high = float(view["ixic"].max()) * 1.08
    y_scale = alt.Scale(type="log", domain=[low, high], clamp=True)
    x_lo = pd.Timestamp(view.index.min())
    x_hi = pd.Timestamp(view.index.max())
    x_scale = alt.Scale(domain=[x_lo, x_hi])
    split = pd.Timestamp(split)
    zones = pd.DataFrame(
        [
            {"start": x_lo, "end": split, "y0": 0, "y1": 1, "zone": "설정", "label": "설정"},
            {
                "start": split,
                "end": x_hi + pd.Timedelta(days=1),
                "y0": 0,
                "y1": 1,
                "zone": "예측",
                "label": "예측",
            },
        ]
    )
    zones["mid"] = zones["start"] + (zones["end"] - zones["start"]) / 2
    zone_color = alt.Scale(domain=["설정", "예측"], range=["#0969da", "#8250df"])
    strip = (
        alt.Chart(zones)
        .mark_rect()
        .encode(
            x=alt.X("start:T", title=None, axis=None, scale=x_scale),
            x2="end:T",
            y=alt.Y("y0:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            y2="y1:Q",
            color=alt.Color("zone:N", scale=zone_color, legend=None),
        )
    )
    strip_text = (
        alt.Chart(zones)
        .mark_text(color="white", fontSize=14, fontWeight="bold", clip=True)
        .encode(
            x=alt.X("mid:T", title=None, axis=None, scale=x_scale),
            y=alt.value(18),
            text="label:N",
        )
    )
    cut = pd.DataFrame({"date": [split], "y0": [0], "y1": [1], "low": [low], "high": [high]})
    header_rule = (
        alt.Chart(cut)
        .mark_rule(color="#24292f", strokeWidth=4)
        .encode(
            x=alt.X("date:T", title=None, axis=None, scale=x_scale),
            y=alt.Y("y0:Q", axis=None, scale=alt.Scale(domain=[0, 1])),
            y2="y1:Q",
        )
    )
    header = alt.layer(strip, header_rule, strip_text).properties(height=36)

    bands = band_frame(view)
    bands["low"] = low
    bands["high"] = high
    color = alt.Scale(
        domain=["상승", "하락", "판정 전"],
        range=["#dafbe1", "#ffebe9", "#eef1f4"],
    )
    backdrop = (
        alt.Chart(bands)
        .mark_rect(opacity=0.9)
        .encode(
            x=alt.X("start:T", title=None, scale=x_scale),
            x2="end:T",
            y=alt.Y("low:Q", title="나스닥", scale=y_scale),
            y2="high:Q",
            color=alt.Color("label:N", scale=color, title="국면"),
        )
    )
    prices = view.reset_index()
    line = (
        alt.Chart(prices)
        .mark_line(color="#0969da")
        .encode(
            x=alt.X("date:T", title=None, scale=x_scale),
            y=alt.Y("ixic:Q", title="나스닥", scale=y_scale),
        )
    )
    price_rule = (
        alt.Chart(cut)
        .mark_rule(color="#24292f", strokeWidth=4)
        .encode(
            x=alt.X("date:T", title=None, scale=x_scale),
            y=alt.Y("low:Q", scale=y_scale),
            y2="high:Q",
        )
    )
    layers = [backdrop, line, price_rule]
    if not baseline_switches.empty:
        rules = baseline_switches.copy()
        rules["low"] = low
        rules["high"] = high
        layers.append(
            alt.Chart(rules)
            .mark_rule(strokeDash=[4, 4], color="#57606a", opacity=0.55)
            .encode(
                x=alt.X("date:T", title=None, scale=x_scale),
                y=alt.Y("low:Q", scale=y_scale),
                y2="high:Q",
            )
        )
    if show_marks:
        marks = pd.DataFrame(
            {
                "date": [pd.Timestamp(day) for day, _ in MARKS],
                "name": [name for _, name in MARKS],
                "low": low,
                "high": high,
            }
        )
        layers.append(
            alt.Chart(marks)
            .mark_rule(color="#bf8700", strokeDash=[2, 2])
            .encode(
                x=alt.X("date:T", title=None, scale=x_scale),
                y=alt.Y("low:Q", scale=y_scale),
                y2="high:Q",
            )
        )
    body = alt.layer(*layers).resolve_scale(y="shared").properties(height=420)
    return alt.vconcat(header, body).resolve_scale(x="shared", color="independent")


def span_stats(features: pd.DataFrame, state: np.ndarray, train_end: pd.Timestamp) -> dict[str, dict]:
    index = pd.DatetimeIndex(features.index)
    ret = features["ret"].to_numpy(dtype=np.float64)
    rf = features["rf"].to_numpy(dtype=np.float64)
    end = pd.Timestamp(train_end).normalize()
    spans = {
        "full": window_positions(index, SAMPLE_START, None),
        "train": window_positions(index, SAMPLE_START, end),
        "test": window_positions(index, end + pd.Timedelta(days=1), None),
    }
    return {name: window_stats(state, ret, rf, *bounds) for name, bounds in spans.items()}


def wealth_gap(rule: dict, held: dict) -> float:
    if held["terminal"] <= 0:
        return float("nan")
    return float(rule["terminal"] / held["terminal"] - 1.0)


def multiple(stats: dict) -> str:
    return f"{stats['terminal']:.2f}배"


def choice_text(choice: dict) -> str:
    if choice.get("up_roc") is None:
        return f"200일선, 확인 {int(choice['confirm'])}일"
    return (
        f"상승 {choice['up_roc'] * 100:.0f}%, 하락 {choice['down_roc'] * 100:.0f}%, "
        f"낙폭 {choice['decline_dd'] * 100:.0f}%, 주도 {choice['rs_min'] * 100:.0f}%, "
        f"확인 {int(choice['confirm'])}일"
    )


def metric_row(title: str, selected: dict, baseline: dict, held: dict) -> None:
    st.subheader(title)
    columns = st.columns(3, border=True)
    blocks = (("이 설정", selected), ("200일선", baseline), ("매수 보유", held))
    for column, (name, stats) in zip(columns, blocks):
        with column:
            st.markdown(f"**{name}**")
            st.metric("칼마", f"{stats['calmar']:.3f}")
            st.metric("연수익률", percent_points(stats["cagr"]))
            st.metric("최대낙폭", percent_points(stats["mdd"]))


def ranking_table(grid: pd.DataFrame, baselines: dict, choice: dict) -> pd.DataFrame:
    show = grid.copy()
    base = show["confirm"].map(lambda days: baselines[int(days)]["train"]["calmar"])
    show["기준선보다 높음"] = show["train_calmar"] > base
    if choice.get("up_roc") is None:
        show["채택"] = False
    else:
        show["채택"] = (
            np.isclose(show["up_roc"], choice["up_roc"])
            & np.isclose(show["down_roc"], choice["down_roc"])
            & np.isclose(show["decline_dd"], choice["decline_dd"])
            & np.isclose(show["rs_min"], choice["rs_min"])
            & (show["confirm"] == choice["confirm"])
        )
    show = show.rename(
        columns={
            "up_roc": "상승 수익률",
            "down_roc": "하락 수익률",
            "decline_dd": "하락 낙폭",
            "rs_min": "주도 최소",
            "confirm": "확인 일수",
            "train_calmar": "앞 칼마",
            "train_mdd": "앞 낙폭",
            "train_switches": "앞 전환",
            "train_up": "상승 비중",
            "test_calmar": "뒤 칼마",
            "test_mdd": "뒤 낙폭",
            "stable": "안정",
        }
    )
    keep = [
        "채택",
        "상승 수익률",
        "하락 수익률",
        "하락 낙폭",
        "주도 최소",
        "확인 일수",
        "앞 칼마",
        "앞 낙폭",
        "앞 전환",
        "상승 비중",
        "뒤 칼마",
        "뒤 낙폭",
        "안정",
        "기준선보다 높음",
    ]
    return show[keep].sort_values(["채택", "앞 칼마"], ascending=[False, False], kind="mergesort")


def wealth_block(title: str, rule_stats: dict, hold_stats: dict) -> None:
    gap = wealth_gap(rule_stats, hold_stats)
    st.markdown(f"**{title}**")
    columns = st.columns(3, border=True)
    blocks = (
        ("이 설정", multiple(rule_stats), percent_points(rule_stats["cagr"])),
        ("보유만", multiple(hold_stats), percent_points(hold_stats["cagr"])),
        ("수익 개선", f"{gap * 100:+.1f}%", percent_points(rule_stats["cagr"] - hold_stats["cagr"])),
    )
    for column, (name, primary, secondary) in zip(columns, blocks):
        with column:
            st.metric(name, primary, delta=f"연 {secondary}", delta_color="off")


if __name__ != "__mp_main__":
    import streamlit as st

    cached_features = st.cache_data(ttl="12h", show_spinner=False)(cached_features)
    cached_search = st.cache_data(ttl="12h", show_spinner=False)(cached_search)

    st.set_page_config(page_title="나스닥 상승·하락", page_icon=":material/query_stats:", layout="wide")
    st.title("나스닥 상승·하락")
    jobs = search_count()
    st.caption(
        "1년 수익률, 200일선, 고점 대비 낙폭, 나스닥이 S&P보다 강한지로 상승과 하락을 가릅니다. "
        "깊은 낙폭은 기술 트렌드가 끝나지 않았어도 하락으로 나옵니다. 2008년과 2020년 3월이 그렇습니다. "
        f"기준 시점까지가 설정 구간이고, 다음 날부터 최신까지가 예측 구간입니다. "
        f"설정은 {worker_count(jobs)}개 프로세스로 {jobs:,}개를 전수조사해 고릅니다."
    )

    if "data_nonce" not in st.session_state:
        st.session_state.data_nonce = 0

    try:
        with st.spinner("시세를 읽는 중"):
            features = cached_features(int(st.session_state.data_nonce))
    except Exception as exc:
        st.error(f"시세를 읽지 못했습니다. {exc}")
        st.stop()

    min_split = pd.Timestamp("1998-01-01").date()
    max_split = pd.Timestamp(features.index[-2]).date()
    default_split = pd.Timestamp("2012-12-31").date()
    if "split_date" not in st.session_state:
        st.session_state.split_date = default_split if default_split <= max_split else max_split
    elif not min_split <= st.session_state.split_date <= max_split:
        st.session_state.split_date = min(max(st.session_state.split_date, min_split), max_split)

    with st.sidebar:
        st.header("기준 시점")
        st.caption("이 날까지로 설정을 고릅니다. 그래프에서 이 날 왼쪽이 설정, 오른쪽이 예측입니다.")
        st.date_input(
            "날짜",
            min_value=min_split,
            max_value=max_split,
            format="YYYY-MM-DD",
            key="split_date",
        )

    split = pd.Timestamp(st.session_state.split_date).normalize()
    try:
        with st.spinner(f"{jobs:,}개 설정을 {worker_count(jobs)}개 프로세스로 전수조사하는 중"):
            grid, baselines, _buyhold = cached_search(int(st.session_state.data_nonce), split.strftime("%Y-%m-%d"))
    except Exception as exc:
        st.error(f"이 시점으로는 설정을 고르지 못했습니다. {exc}")
        st.stop()

    winner = choose(grid, baselines)
    preview = features.loc[features.index >= SAMPLE_START].iloc[-1]
    as_of = pd.Timestamp(features.index[-1]).strftime("%Y-%m-%d")
    latest_roc = float(preview["roc"])
    latest_dd = float(preview["dd"])
    latest_rs = float(preview["rs"])
    latest_stretch = float(preview["stretch"])

    with st.sidebar:
        st.caption(f"전수조사로 고른 값 · {choice_text(winner)}")
        if winner.get("source") == "기준선":
            st.caption("이 구간에서는 200일선보다 나은 설정이 없어, 확인 일수는 그 기준을 따릅니다.")
        show_marks = st.checkbox(
            "참고 구간",
            value=False,
            help="닷컴, 금융위기, 코로나, 2022년 고점과 저점입니다. 점수를 매기는 데는 쓰지 않습니다.",
        )
        st.button(
            "최근 3영업일 종가 갱신",
            help="저장된 종가는 그대로 두고, 각 시계열의 최근 3영업일과 그 이후만 다시 받아 붙입니다.",
            on_click=_bump_nonce,
        )

    confirm = int(winner["confirm"])
    state = state_for(features, winner)
    held = np.ones(len(features), dtype=np.int8)
    baseline_state = classify_baseline(features["stretch"].to_numpy(dtype=np.float64), confirm)
    rule_stats = span_stats(features, state, split)
    hold_stats = span_stats(features, held, split)
    line_stats = span_stats(features, baseline_state, split)
    view = regime_frame(features, state)
    baseline_switches = switch_frame(pd.DatetimeIndex(features.index), baseline_state)
    latest = view.iloc[-1]
    state_name = str(latest["label"])
    stance = {
        "상승": ("보유", "green", ":material/trending_up:", "지금은 보유가 적절합니다."),
        "하락": ("판매", "red", ":material/trending_down:", "지금은 판매가 적절합니다."),
        "판정 전": ("판단 전", "gray", ":material/hourglass_empty:", "지표가 모이기 전에는 보유와 판매를 나누지 않습니다."),
    }[state_name]
    price = float(latest["ixic"])
    train_label = f"1995-01-01–{split:%Y-%m-%d}"
    test_label = f"{(split + pd.Timedelta(days=1)):%Y-%m-%d}–최신"
    full_label = "1995-01-01–최신"

    st.badge(stance[0], color=stance[1], icon=stance[2])
    st.markdown(f"**{as_of} 종가 기준 {stance[3]}**")

    with st.container(horizontal=True):
        st.metric(f"나스닥 지수 · {as_of}", f"{price:,.2f}", border=True)
        st.metric("200일선 이격", percent_points(latest_stretch), border=True)
        st.metric("1년 수익률", percent_points(latest_roc), border=True)
        st.metric("고점 낙폭", percent_points(latest_dd), border=True)
        st.metric("나스닥 − S&P", percent_points(latest_rs), border=True)

    st.subheader("보유만 했을 때와 비교")
    st.caption(
        f"같은 시작 금액을 1로 두고, 끝나는 금액이 몇 배인지입니다. "
        f"전수조사로 고른 값은 {choice_text(winner)}입니다."
    )
    wealth_block(f"예측 · {test_label}", rule_stats["test"], hold_stats["test"])
    wealth_block(f"설정 · {train_label}", rule_stats["train"], hold_stats["train"])
    wealth_block(f"전체 · {full_label}", rule_stats["full"], hold_stats["full"])

    st.markdown(f":blue[**설정** {train_label}]  ·  :violet[**예측** {test_label}]")
    st.altair_chart(
        price_chart(view, baseline_switches, show_marks, split),
        width="stretch",
    )
    st.caption(
        "위 칸의 파랑이 설정을 고른 구간이고, 보라는 그 설정을 적용하는 예측 구간입니다. "
        "검은 세로선이 둘의 경계입니다. 회색 점선은 같은 확인 일수의 200일선이 바뀐 날입니다."
    )
    if show_marks:
        st.caption("주황 점선: " + ", ".join(f"{name} {day}" for day, name in MARKS) + ".")

    with st.expander("기간별 칼마와 낙폭"):
        metric_row(train_label, rule_stats["train"], line_stats["train"], hold_stats["train"])
        metric_row(test_label, rule_stats["test"], line_stats["test"], hold_stats["test"])

    with st.expander(f"{split:%Y-%m-%d}까지 전수조사한 {len(grid):,}개 설정"):
        st.caption(
            "채택은 이 날까지의 칼마가 같은 확인 일수의 200일선보다 높고, 이웃 설정의 금액도 비슷한 설정입니다. "
            "예측 구간의 숫자는 설정을 고를 때 쓰지 않습니다."
        )
        table = ranking_table(grid, baselines, winner)
        st.dataframe(
            table,
            hide_index=True,
            width="stretch",
            column_config={
                "상승 수익률": st.column_config.NumberColumn(format="percent"),
                "하락 수익률": st.column_config.NumberColumn(format="percent"),
                "하락 낙폭": st.column_config.NumberColumn(format="percent"),
                "주도 최소": st.column_config.NumberColumn(format="percent"),
                "앞 칼마": st.column_config.NumberColumn(format="%.2f"),
                "앞 낙폭": st.column_config.NumberColumn(format="percent"),
                "상승 비중": st.column_config.NumberColumn(format="percent"),
                "뒤 칼마": st.column_config.NumberColumn(format="%.2f"),
                "뒤 낙폭": st.column_config.NumberColumn(format="percent"),
            },
        )
