"""월가 의도 트래커 — UI만. 로직은 src/."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.book import BasketAction, Book, decide_book
from src.config import FRED_SERIES, LIVE_REFRESH_SEC, YAHOO_DAILY
from src.data import load_daily_panel, load_events
from src.glossary import (
    ACTION_KO,
    FRED_HELP,
    LAYER_HELP,
    METRIC_HELP,
    REGIME_HELP,
    REGIME_KO,
    STANCE_KO,
    TERM_GLOSSARY,
    TICKER_HELP,
)
from src.live import fetch_live_tape
from src.score import snapshot_from
from src.validate import build_figure, validate

st.set_page_config(page_title="월가 의도 트래커", page_icon=":material/account_balance:", layout="wide")


@st.cache_data(ttl="6h", show_spinner="일간 골격(FRED·Yahoo)을 불러오는 중...")
def cached_panel() -> pd.DataFrame:
    return load_daily_panel()


@st.cache_data(ttl="90s")
def cached_tape():
    return fetch_live_tape()


@st.cache_data(ttl="6h")
def cached_validation(panel: pd.DataFrame, years: int):
    return validate(panel, years=years)


def _pct(v: float | None, digits: int = 1) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{v * 100:.{digits}f}%"


def _event_rows(panel: pd.DataFrame, tape_returns: dict[str, float]) -> pd.DataFrame:
    events = load_events()
    if not events:
        return pd.DataFrame()
    today = pd.Timestamp(date.today()).normalize()
    rows = []
    spy = panel["SPY"] if "SPY" in panel.columns else None
    tlt = panel["TLT"] if "TLT" in panel.columns else None
    hyg = panel["HYG"] if "HYG" in panel.columns else None
    for ev in events:
        d = ev["date"]
        if d > today or d < today - pd.Timedelta(days=180):
            continue
        rec = {"날짜": d.strftime("%Y-%m-%d"), "이벤트": ev["name"]}
        if d.normalize() == today and tape_returns:
            rec["SPY"] = _pct(tape_returns.get("SPY"))
            rec["TLT"] = _pct(tape_returns.get("TLT"))
            rec["HYG"] = _pct(tape_returns.get("HYG"))
            rec["읽는 법"] = "당일 장중"
        elif spy is not None and d in spy.index:

            def day_ret(series: pd.Series) -> float | None:
                loc = series.index.get_loc(d)
                if loc == 0:
                    return None
                prev = series.iloc[loc - 1]
                cur = series.iloc[loc]
                if pd.isna(prev) or prev == 0:
                    return None
                return float(cur / prev - 1)

            rec["SPY"] = _pct(day_ret(spy))
            rec["TLT"] = _pct(day_ret(tlt)) if tlt is not None else "—"
            rec["HYG"] = _pct(day_ret(hyg)) if hyg is not None else "—"
            rec["읽는 법"] = "당일 종가"
        else:
            continue
        rows.append(rec)
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows).tail(6)
    return frame.iloc[::-1]


def _action_card(row: BasketAction, tape_returns: dict[str, float], sell_kind: str | None = None) -> None:
    live = tape_returns.get(row.ticker)
    tag = sell_kind or ACTION_KO.get(row.action, row.action)
    with st.container(border=True):
        st.markdown(f"**{row.name}**  `{row.ticker}`")
        st.caption(f"{row.group} · {tag}")
        st.markdown(row.reason)
        bits = [f"21일 {_pct(row.ret_21)}"]
        if live is not None:
            bits.append(f"당일 {_pct(live)}")
        st.caption(" · ".join(bits))
        with st.expander("이 ETF는"):
            st.write(TICKER_HELP.get(row.ticker, row.name))


def render_hero(snap, tape) -> None:
    stance_ko = STANCE_KO.get(snap.stance, snap.stance)
    regime_ko = REGIME_KO.get(snap.regime, snap.regime)
    st.title("월가 의도 트래커")
    st.caption("경제 뉴스가 아니라, 월가가 어느 바구니에 돈을 넣고 빼는지를 봅니다. 개별 주식은 고르지 않습니다.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("지금 방향", stance_ko, help=METRIC_HELP["방향"], border=True)
    c2.metric(
        "지금 국면",
        regime_ko,
        help=METRIC_HELP["국면"] + " " + REGIME_HELP.get(snap.regime, ""),
        border=True,
    )
    score_delta = f"장중 조정 {snap.daily_score:+.2f}→{snap.score:+.2f}" if snap.overlay_note else None
    c3.metric("종합 점수", f"{snap.score:+.2f}", score_delta, help=METRIC_HELP["점수"], border=True)
    c4.metric("미국 장", f"{tape.session_ko} · {tape.asof_kst.strftime('%H:%M')}", border=True)


def render_actions(book: Book, tape_returns: dict[str, float]) -> None:
    st.subheader("오늘 사기 / 팔기")
    st.info(book.sentence)
    buy_col, sell_col = st.columns(2)
    with buy_col:
        st.markdown("### :green[사라]")
        if not book.enlarge:
            st.caption("오늘은 새로 살 바구니가 없습니다.")
        for row in book.enlarge:
            _action_card(row, tape_returns)
    with sell_col:
        st.markdown("### :red[팔아라]")
        sells = [("전량", r) for r in book.avoid] + [("일부", r) for r in book.reduce]
        if not sells:
            st.caption("오늘은 팔 바구니가 없습니다.")
        for kind, row in sells:
            _action_card(row, tape_returns, sell_kind=kind)
    if book.hold:
        with st.expander(f"나머지는 그대로 ({len(book.hold)}개)"):
            names = ", ".join(f"{r.name}(`{r.ticker}`)" for r in book.hold)
            st.write(names)


def render_meaning() -> None:
    st.subheader("이 데이터가 의미하는 것")
    st.markdown(LAYER_HELP)
    with st.expander("경제 용어"):
        for title, body in TERM_GLOSSARY:
            st.markdown(f"**{title}**")
            st.write(body)
    with st.expander("바구니 ETF"):
        for ticker, name in YAHOO_DAILY.items():
            st.markdown(f"**{name} (`{ticker}`)** — {TICKER_HELP.get(ticker, '')}")
    with st.expander("금리·물가·신용 (FRED)"):
        for sid, name in FRED_SERIES.items():
            st.markdown(f"**{name} (`{sid}`)** — {FRED_HELP.get(sid, '')}")


def render_validation(panel: pd.DataFrame) -> None:
    st.subheader("신호가 맞았는가")
    st.caption(
        "배경색은 당시 방향입니다(초록=위험자산 쪽, 빨강=현금·방어 쪽). "
        "굵은 선은 그 규칙을 매주 따랐을 때, 점선은 S&P 500만 들고 갔을 때입니다."
    )
    years = st.segmented_control("기간", options=[1, 3, 5], format_func=lambda y: f"{y}년", default=3, key="val_years")
    if years is None:
        years = 3
    result = cached_validation(panel, int(years))
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("북 vs SPY", _pct(result.kpis["book_vs_spy"]), help=METRIC_HELP["북 vs SPY"], border=True)
    k2.metric(
        "위험자산 쪽 이후 20일",
        _pct(result.kpis["risk_on_fwd20"]),
        help=METRIC_HELP["위험자산 쪽 이후 20일"],
        border=True,
    )
    k3.metric(
        "현금·방어 쪽 이후 20일",
        _pct(result.kpis["risk_off_fwd20"]),
        help=METRIC_HELP["현금·방어 쪽 이후 20일"],
        border=True,
    )
    k4.metric(
        "사라 > 팔아라 주 비율",
        _pct(result.kpis["enlarge_beats_avoid"], 0),
        help=METRIC_HELP["사라 > 팔아라 주 비율"],
        border=True,
    )
    st.plotly_chart(build_figure(result), width="stretch")


@st.fragment(run_every=f"{LIVE_REFRESH_SEC}s")
def live_tape_panel(panel: pd.DataFrame) -> dict[str, float]:
    tape = fetch_live_tape()
    st.subheader("지금 가격 (장중 테이프)")
    st.caption(
        "테이프는 거래소에 찍히는 가격 흐름입니다. "
        "지표 발표가 나쁜데도 이 숫자가 오르면, 월가가 지표를 무시하고 있다는 뜻입니다."
    )
    if tape.session != "open":
        st.caption(f"{tape.session_ko} — 장중 자동갱신은 쉽니다. 마지막 {tape.asof_kst.strftime('%H:%M KST')}")
    else:
        st.caption(f"{tape.session_ko} · {LIVE_REFRESH_SEC}초마다 갱신 · {tape.asof_kst.strftime('%H:%M KST')}")

    keys = ["SPY", "QQQ", "IWM", "TLT", "HYG", "GLD", "VIX"]
    cols = st.columns(len(keys))
    for col, key in zip(cols, keys):
        ret = tape.returns.get(key)
        px = tape.last_price.get(key)
        label = {"SPY": "대형주", "QQQ": "나스닥", "IWM": "중소형", "TLT": "장기국채", "HYG": "하이일드", "GLD": "금", "VIX": "변동성"}.get(key, key)
        col.metric(
            f"{label}",
            f"{px:.2f}" if px is not None else "—",
            _pct(ret) if ret is not None else None,
            help=f"{key}. " + TICKER_HELP.get(key, ""),
            border=True,
        )

    events = _event_rows(panel, tape.returns)
    if not events.empty:
        st.markdown("**최근 지표 발표 날, 월가가 어떻게 반응했는가**")
        st.caption("같은 날 주식(SPY)·국채(TLT)·회사채(HYG) 방향입니다. 지표가 나빠도 SPY가 올랐으면 월가가 그 지표를 산 것입니다.")
        st.dataframe(events, hide_index=True, width="stretch")
    return tape.returns


def render_components(snap) -> None:
    st.subheader("판단이 나온 구성")
    row = snap.features
    items = [
        ("돈의 가격", float(row.get("money", 0)), METRIC_HELP["돈의 가격"]),
        ("리스크 예산", float(row.get("risk", 0)), METRIC_HELP["리스크 예산"]),
        ("상대 강도", float(row.get("relative", 0)), METRIC_HELP["상대 강도"]),
        ("국면 점수", float(row.get("regime_score", 0)), METRIC_HELP["국면"]),
    ]
    cols = st.columns(4)
    for col, (title, val, hint) in zip(cols, items):
        with col:
            st.metric(title, f"{val:+.2f}", help=hint, border=True)
    st.caption(REGIME_HELP.get(str(row.get("regime")), ""))


def main() -> None:
    panel = cached_panel()
    if panel is None or panel.empty:
        st.error("일간 데이터를 불러오지 못했습니다. 네트워크 후 새로고침하세요.")
        return

    tape = cached_tape()
    snap = snapshot_from(panel, tape)
    book = decide_book(snap)

    render_hero(snap, tape)
    render_actions(book, tape.returns)
    render_meaning()
    render_validation(panel)
    live_tape_panel(panel)
    render_components(snap)

    with st.expander("데이터 범위"):
        st.write(f"일간 패널 {panel.index.min().date()} ~ {panel.index.max().date()}, 컬럼 {len(panel.columns)}개")
        st.caption("캐시: 월가/data/cache · 가상환경: 월가/.venv · 주식·백데이터와 분리")


main()
