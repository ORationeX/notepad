"""룩어헤드 없이 과거 스탠스·북을 재생하고 한눈 차트를 만든다."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go

from src.book import Book, decide_book, enlarge_tickers
from src.config import CHART_ASSETS
from src.score import Snapshot, compute_signal_frame


STANCE_COLOR = {
    "RISK_ON": "rgba(52, 211, 153, 0.16)",
    "MIXED": "rgba(148, 163, 184, 0.12)",
    "RISK_OFF": "rgba(248, 113, 113, 0.16)",
}

LINE_COLOR = {
    "SPY": "#60A5FA",
    "TLT": "#A78BFA",
    "GLD": "#FBBF24",
    "BIL": "#94A3B8",
    "북 추종": "#34D399",
    "SPY 보유": "#38BDF8",
}


@dataclass
class ValidationResult:
    prices: pd.DataFrame
    book_equity: pd.Series
    spy_equity: pd.Series
    stance: pd.Series
    kpis: dict[str, float]
    last_enlarge: list[str]
    last_stance: str


def _fridays(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    weeks = pd.Series(index, index=index).groupby(index.to_period("W-FRI")).max()
    return pd.DatetimeIndex(weeks.values)


def replay_book(panel: pd.DataFrame, signals: pd.DataFrame) -> tuple[pd.Series, pd.Series, list[str]]:
    """금요일 종가 신호 → 다음 주 확대 슬롯 동일가중. MIXED는 직전 비중 유지."""
    prices = panel[[c for c in panel.columns if c in {b["ticker"] for b in _all_tickers()}]].astype(float)
    prices = prices.ffill()
    rets = prices.pct_change().fillna(0.0)
    weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    fridays = _fridays(prices.index)
    prev_w = None
    last_enlarge: list[str] = ["SPY"]

    for i, friday in enumerate(fridays):
        if friday not in signals.index:
            continue
        row = signals.loc[friday]
        if pd.isna(row.get("score")):
            continue
        snap = Snapshot(
            asof=friday,
            regime=str(row["regime"]),
            stance=str(row["stance"]),
            score=float(row["score"]),
            daily_score=float(row["score"]),
            daily_stance=str(row["stance"]),
            overlay_note=None,
            features=row,
        )
        book: Book = decide_book(snap)
        chosen = [t for t in enlarge_tickers(book) if t in weights.columns]
        if not chosen:
            chosen = ["BIL"] if "BIL" in weights.columns else [weights.columns[0]]
        if str(row["stance"]) == "MIXED" and prev_w is not None:
            w = prev_w
        else:
            w = pd.Series(0.0, index=weights.columns)
            w.loc[chosen] = 1.0 / len(chosen)
            prev_w = w
            last_enlarge = chosen
        nxt = fridays[i + 1] if i + 1 < len(fridays) else prices.index[-1]
        mask = (prices.index > friday) & (prices.index <= nxt)
        weights.loc[mask] = w.values

    # 첫 금요일 이전: SPY 100%
    if "SPY" in weights.columns:
        first_assigned = weights.abs().sum(axis=1) > 0
        if first_assigned.any():
            start = weights.index[first_assigned][0]
            weights.loc[weights.index < start, "SPY"] = 1.0
        else:
            weights["SPY"] = 1.0

    port_ret = (weights * rets).sum(axis=1)
    equity = (1.0 + port_ret).cumprod()
    spy = (1.0 + rets.get("SPY", pd.Series(0.0, index=rets.index))).cumprod()
    return equity, spy, last_enlarge


def _all_tickers() -> list[dict]:
    from src.config import BASKETS

    return BASKETS


def _forward_mean(price: pd.Series, stance: pd.Series, label: str, horizon: int = 20) -> float:
    fwd = price.shift(-horizon) / price - 1.0
    picked = fwd[stance == label].dropna()
    if picked.empty:
        return float("nan")
    return float(picked.mean())


def _enlarge_beat_rate(panel: pd.DataFrame, signals: pd.DataFrame) -> float:
    prices = panel.ffill()
    rets = prices.pct_change()
    fridays = _fridays(prices.index)
    wins = 0
    total = 0
    for i, friday in enumerate(fridays[:-1]):
        if friday not in signals.index:
            continue
        row = signals.loc[friday]
        if pd.isna(row.get("score")):
            continue
        snap = Snapshot(
            asof=friday,
            regime=str(row["regime"]),
            stance=str(row["stance"]),
            score=float(row["score"]),
            daily_score=float(row["score"]),
            daily_stance=str(row["stance"]),
            overlay_note=None,
            features=row,
        )
        book = decide_book(snap)
        up = [t for t in enlarge_tickers(book) if t in rets.columns]
        down = [r.ticker for r in book.avoid if r.ticker in rets.columns]
        if not up or not down:
            continue
        nxt = fridays[i + 1]
        window = rets.loc[(rets.index > friday) & (rets.index <= nxt)]
        if window.empty:
            continue
        up_ret = window[up].mean(axis=1).sum()
        down_ret = window[down].mean(axis=1).sum()
        total += 1
        if up_ret > down_ret:
            wins += 1
    if total == 0:
        return float("nan")
    return wins / total


def validate(panel: pd.DataFrame, years: int = 3) -> ValidationResult:
    signals = compute_signal_frame(panel)
    end = panel.index.max()
    start = end - pd.DateOffset(years=years)
    sl_panel = panel.loc[panel.index >= start]
    sl_sig = signals.loc[signals.index >= start]
    equity, spy_eq, last_enlarge = replay_book(sl_panel, sl_sig)
    norm_cols = [c for c in CHART_ASSETS if c in sl_panel.columns]
    prices = sl_panel[norm_cols].ffill()
    prices = prices / prices.iloc[0] * 100.0
    book_eq = equity / equity.iloc[0] * 100.0
    spy_n = spy_eq / spy_eq.iloc[0] * 100.0
    stance = sl_sig["stance"].reindex(prices.index).ffill()
    spy_px = sl_panel["SPY"].ffill() if "SPY" in sl_panel.columns else prices.iloc[:, 0]
    kpis = {
        "book_vs_spy": float(book_eq.iloc[-1] / spy_n.iloc[-1] - 1.0),
        "risk_on_fwd20": _forward_mean(spy_px, stance, "RISK_ON"),
        "risk_off_fwd20": _forward_mean(spy_px, stance, "RISK_OFF"),
        "enlarge_beats_avoid": _enlarge_beat_rate(sl_panel, sl_sig),
        "book_total": float(book_eq.iloc[-1] / 100.0 - 1.0),
        "spy_total": float(spy_n.iloc[-1] / 100.0 - 1.0),
    }
    last_stance = str(stance.dropna().iloc[-1]) if stance.dropna().size else "MIXED"
    return ValidationResult(
        prices=prices,
        book_equity=book_eq,
        spy_equity=spy_n,
        stance=stance,
        kpis=kpis,
        last_enlarge=last_enlarge,
        last_stance=last_stance,
    )


def _stance_shapes(stance: pd.Series) -> list[dict]:
    shapes = []
    if stance.empty:
        return shapes
    current = None
    start = None
    prev = None
    for ts, val in stance.items():
        if val != current:
            if current is not None and start is not None and prev is not None:
                shapes.append(
                    dict(
                        type="rect",
                        xref="x",
                        yref="paper",
                        x0=start,
                        x1=prev,
                        y0=0,
                        y1=1,
                        fillcolor=STANCE_COLOR.get(current, "rgba(0,0,0,0)"),
                        line={"width": 0},
                        layer="below",
                    )
                )
            current = val
            start = ts
        prev = ts
    if current is not None and start is not None and prev is not None:
        shapes.append(
            dict(
                type="rect",
                xref="x",
                yref="paper",
                x0=start,
                x1=prev,
                y0=0,
                y1=1,
                fillcolor=STANCE_COLOR.get(current, "rgba(0,0,0,0)"),
                line={"width": 0},
                layer="below",
            )
        )
    return shapes


def build_figure(result: ValidationResult) -> go.Figure:
    fig = go.Figure()
    for col in result.prices.columns:
        fig.add_trace(
            go.Scatter(
                x=result.prices.index,
                y=result.prices[col],
                name=col,
                mode="lines",
                line=dict(width=1.4, color=LINE_COLOR.get(col, "#94A3B8")),
                hovertemplate="%{x|%Y-%m-%d}<br>" + col + " %{y:.1f}<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=result.book_equity.index,
            y=result.book_equity,
            name="북 추종",
            mode="lines",
            line=dict(width=3.0, color=LINE_COLOR["북 추종"]),
            hovertemplate="%{x|%Y-%m-%d}<br>북 추종 %{y:.1f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=result.spy_equity.index,
            y=result.spy_equity,
            name="SPY 보유",
            mode="lines",
            line=dict(width=1.8, dash="dash", color=LINE_COLOR["SPY 보유"]),
            hovertemplate="%{x|%Y-%m-%d}<br>SPY 보유 %{y:.1f}<extra></extra>",
        )
    )
    last_x = result.book_equity.index[-1]
    last_y = float(result.book_equity.iloc[-1])
    enlarge = "·".join(result.last_enlarge) if result.last_enlarge else "-"
    fig.add_annotation(
        x=last_x,
        y=last_y,
        text=f"오늘 {result.last_stance}<br>확대 {enlarge}",
        showarrow=True,
        arrowhead=2,
        ax=-80,
        ay=-40,
        font=dict(size=12, color="#F1F5F9"),
        bgcolor="rgba(30, 41, 59, 0.9)",
        bordercolor="#334155",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.6)",
        margin=dict(l=16, r=16, t=32, b=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        yaxis_title="기간 초 = 100",
        hovermode="x unified",
        shapes=_stance_shapes(result.stance),
        height=460,
    )
    return fig
