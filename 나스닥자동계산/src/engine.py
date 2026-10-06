"""기준가 리밸런싱 시뮬레이터.

첫날 시가에 자본의 initial 만큼 산다. 기준가는 그 체결가다.
다음 날부터, 직전 종가가 기준가보다 up 이상 높으면 당일 시가에
보유 수량의 sell 만큼 팔고 기준가를 갱신한다. down 이상 낮으면
남은 현금의 buy 만큼 사고 기준가를 갱신한다.
남은 현금은 정렬된 일별 무위험 수익률로 불어난다.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

_IMPL = None


def _load_impl():
    global _IMPL
    if _IMPL is not None:
        return _IMPL

    from numba import njit, prange

    @njit(cache=False)
    def buy_spend(cash, shares, px, buy, max_weight, one_m_cost, cost):
        if buy <= 0.0 or cash <= 0.0 or px <= 0.0:
            return 0.0
        equity = cash + shares * px
        room = max_weight * equity - shares * px
        if room <= 1e-12:
            return 0.0
        denom = one_m_cost + max_weight * cost
        if denom <= 1e-12:
            return 0.0
        cap = room / denom
        spend = cash * buy
        if spend > cap:
            spend = cap
        if spend > cash:
            spend = cash
        if spend <= 1e-12:
            return 0.0
        return spend

    @njit(cache=False)
    def simulate_path(opens, closes, rfs, initial, up, down, sell, buy, cost, max_weight):
        n = opens.shape[0]
        wealth = np.empty(n, dtype=np.float64)
        weights = np.empty(n, dtype=np.float64)
        day = np.empty(n, dtype=np.int64)
        side = np.empty(n, dtype=np.int64)
        price = np.empty(n, dtype=np.float64)
        notional = np.empty(n, dtype=np.float64)
        weight_after = np.empty(n, dtype=np.float64)

        one_m_cost = 1.0 - cost
        invested = initial if initial < max_weight else max_weight
        cash = 1.0 - invested
        shares = invested / opens[0]
        anchor = opens[0]
        marked = cash + shares * closes[0]
        w0 = marked
        peak = marked
        mdd = 0.0
        sum_ex = 0.0
        sum_ex2 = 0.0
        w_sum = 0.0
        if marked > 0.0:
            w_sum = shares * closes[0] / marked
        buys = 0
        sells = 0
        n_trades = 0
        prev = marked
        wealth[0] = marked
        weights[0] = w_sum

        for t in range(1, n):
            cash *= 1.0 + rfs[t]
            px = opens[t]
            prev_close = closes[t - 1]
            if anchor > 0.0 and px > 0.0 and prev_close > 0.0:
                chg = prev_close / anchor - 1.0
                if chg >= up and sell > 0.0 and shares > 0.0:
                    qty = shares * sell
                    shares -= qty
                    gross = qty * px
                    cash += gross * one_m_cost
                    anchor = px
                    sells += 1
                    total_open = cash + shares * px
                    w_after = shares * px / total_open if total_open > 0.0 else 0.0
                    if n_trades < n:
                        day[n_trades] = t
                        side[n_trades] = -1
                        price[n_trades] = px
                        notional[n_trades] = gross
                        weight_after[n_trades] = w_after
                        n_trades += 1
                elif chg <= -down and buy > 0.0 and cash > 0.0:
                    spend = buy_spend(cash, shares, px, buy, max_weight, one_m_cost, cost)
                    if spend > 0.0:
                        shares += spend * one_m_cost / px
                        cash -= spend
                        anchor = px
                        buys += 1
                        total_open = cash + shares * px
                        w_after = shares * px / total_open if total_open > 0.0 else 0.0
                        if n_trades < n:
                            day[n_trades] = t
                            side[n_trades] = 1
                            price[n_trades] = px
                            notional[n_trades] = spend
                            weight_after[n_trades] = w_after
                            n_trades += 1

            marked = cash + shares * closes[t]
            if prev > 0.0 and marked > 0.0:
                ex = marked / prev - 1.0 - rfs[t]
                sum_ex += ex
                sum_ex2 += ex * ex
            if marked > peak:
                peak = marked
            elif peak > 0.0:
                dd = marked / peak - 1.0
                if dd < mdd:
                    mdd = dd
            if marked > 0.0:
                w_today = shares * closes[t] / marked
            else:
                w_today = 0.0
            w_sum += w_today
            weights[t] = w_today
            wealth[t] = marked
            prev = marked

        terminal = marked / w0 if w0 > 0.0 else 0.0
        avg_weight = w_sum / n
        if w0 > 0.0:
            wealth /= w0
        return (
            wealth,
            weights,
            day,
            side,
            price,
            notional,
            weight_after,
            n_trades,
            terminal,
            mdd,
            sum_ex,
            sum_ex2,
            buys,
            sells,
            avg_weight,
        )

    @njit(cache=False, parallel=True)
    def eval_grid(opens, closes, rfs, params, cost, split, max_weight):
        n_params = params.shape[0]
        n = opens.shape[0]
        out = np.zeros((n_params, 14), dtype=np.float64)
        one_m_cost = 1.0 - cost

        for i in prange(n_params):
            initial = params[i, 0]
            up = params[i, 1]
            down = params[i, 2]
            sell = params[i, 3]
            buy = params[i, 4]

            invested = initial if initial < max_weight else max_weight
            cash = 1.0 - invested
            shares = invested / opens[0]
            anchor = opens[0]
            marked = cash + shares * closes[0]
            w0 = marked
            peak = marked
            mdd = 0.0
            sum_ex = 0.0
            sum_ex2 = 0.0
            w_sum = 0.0
            if marked > 0.0:
                w_sum = shares * closes[0] / marked
            buys = 0
            sells = 0
            prev = marked

            tr_terminal = 0.0
            tr_mdd = 0.0
            tr_sum_ex = 0.0
            tr_sum_ex2 = 0.0
            tr_buys = 0.0
            tr_sells = 0.0
            tr_avg = 0.0
            snapped = False

            for t in range(1, n):
                if t == split:
                    tr_terminal = marked / w0 if w0 > 0.0 else 0.0
                    tr_mdd = mdd
                    tr_sum_ex = sum_ex
                    tr_sum_ex2 = sum_ex2
                    tr_buys = buys
                    tr_sells = sells
                    tr_avg = w_sum / split if split > 0 else 0.0
                    snapped = True

                cash *= 1.0 + rfs[t]
                px = opens[t]
                prev_close = closes[t - 1]
                if anchor > 0.0 and px > 0.0 and prev_close > 0.0:
                    chg = prev_close / anchor - 1.0
                    if chg >= up and sell > 0.0 and shares > 0.0:
                        qty = shares * sell
                        shares -= qty
                        cash += qty * px * one_m_cost
                        anchor = px
                        sells += 1
                    elif chg <= -down and buy > 0.0 and cash > 0.0:
                        spend = buy_spend(cash, shares, px, buy, max_weight, one_m_cost, cost)
                        if spend > 0.0:
                            shares += spend * one_m_cost / px
                            cash -= spend
                            anchor = px
                            buys += 1

                marked = cash + shares * closes[t]
                if prev > 0.0 and marked > 0.0:
                    ex = marked / prev - 1.0 - rfs[t]
                    sum_ex += ex
                    sum_ex2 += ex * ex
                if marked > peak:
                    peak = marked
                elif peak > 0.0:
                    dd = marked / peak - 1.0
                    if dd < mdd:
                        mdd = dd
                if marked > 0.0:
                    w_sum += shares * closes[t] / marked
                prev = marked

            terminal = marked / w0 if w0 > 0.0 else 0.0
            avg_weight = w_sum / n
            out[i, 0] = terminal
            out[i, 1] = mdd
            out[i, 2] = sum_ex
            out[i, 3] = sum_ex2
            out[i, 4] = buys
            out[i, 5] = sells
            out[i, 6] = avg_weight
            if snapped:
                out[i, 7] = tr_terminal
                out[i, 8] = tr_mdd
                out[i, 9] = tr_sum_ex
                out[i, 10] = tr_sum_ex2
                out[i, 11] = tr_buys
                out[i, 12] = tr_sells
                out[i, 13] = tr_avg
            else:
                out[i, 7] = terminal
                out[i, 8] = mdd
                out[i, 9] = sum_ex
                out[i, 10] = sum_ex2
                out[i, 11] = buys
                out[i, 12] = sells
                out[i, 13] = avg_weight

        return out

    _IMPL = (simulate_path, eval_grid)
    return _IMPL


@dataclass
class Detail:
    initial: float
    up: float
    down: float
    sell: float
    buy: float
    terminal: float
    cagr: float
    mdd: float
    sharpe: float
    calmar: float
    buys: int
    sells: int
    avg_weight: float
    wealth: np.ndarray
    weights: np.ndarray
    trades: list


def metrics_from_sums(terminal, mdd, sum_ex, sum_ex2, n_days, buys, sells, avg_weight) -> dict:
    m = n_days - 1
    years = m / 252.0 if m > 0 else 0.0
    if terminal > 0.0 and years > 0.0:
        cagr = terminal ** (1.0 / years) - 1.0
    else:
        cagr = -1.0
    if m > 1:
        var = (sum_ex2 - (sum_ex * sum_ex) / m) / (m - 1)
        mean = sum_ex / m
        sharpe = mean / np.sqrt(var) * np.sqrt(252.0) if var > 1e-18 else 0.0
    else:
        sharpe = 0.0
    if mdd < -1e-12:
        calmar = cagr / abs(mdd)
    elif cagr > 0.0:
        calmar = 1e6
    else:
        calmar = 0.0
    return {
        "terminal": float(terminal),
        "cagr": float(cagr),
        "mdd": float(mdd),
        "sharpe": float(sharpe),
        "calmar": float(calmar),
        "buys": int(buys),
        "sells": int(sells),
        "avg_weight": float(avg_weight),
        "trades": int(buys) + int(sells),
    }


def _check(opens, closes, rfs, initial, up, down, sell, buy, cost) -> None:
    if opens.shape != closes.shape or opens.shape != rfs.shape:
        raise ValueError("시가, 종가, 금리 길이가 다릅니다.")
    if opens.ndim != 1 or len(opens) < 2:
        raise ValueError("거래일이 너무 적습니다.")
    if not np.isfinite(opens).all() or not np.isfinite(closes).all() or not np.isfinite(rfs).all():
        raise ValueError("시세에 빈 값이 있습니다.")
    if np.any(opens <= 0) or np.any(closes <= 0):
        raise ValueError("가격은 0보다 커야 합니다.")
    if not 0.0 <= initial <= 1.0:
        raise ValueError("초기 비중은 0과 1 사이여야 합니다.")
    if up <= 0 or down <= 0:
        raise ValueError("오름 폭과 내림 폭은 0보다 커야 합니다.")
    if not 0.0 <= sell <= 1.0 or not 0.0 <= buy <= 1.0:
        raise ValueError("매도·매수 비율은 0과 1 사이여야 합니다.")
    if not 0.0 <= cost < 1.0:
        raise ValueError("거래 비용은 0 이상 1 미만이어야 합니다.")


def run_formula(opens, closes, rfs, initial, up, down, sell, buy, cost=0.0, dates=None, max_weight=1.0) -> Detail:
    opens = np.ascontiguousarray(opens, dtype=np.float64)
    closes = np.ascontiguousarray(closes, dtype=np.float64)
    rfs = np.ascontiguousarray(rfs, dtype=np.float64)
    _check(opens, closes, rfs, initial, up, down, sell, buy, cost)
    simulate_path, _ = _load_impl()
    (
        wealth,
        weights,
        day,
        side,
        price,
        notional,
        weight_after,
        n_trades,
        terminal,
        mdd,
        sum_ex,
        sum_ex2,
        buys,
        sells,
        avg_weight,
    ) = simulate_path(opens, closes, rfs, initial, up, down, sell, buy, cost, float(max_weight))
    stats = metrics_from_sums(terminal, mdd, sum_ex, sum_ex2, len(opens), buys, sells, avg_weight)
    stats.pop("trades", None)
    trades = []
    if initial > 0:
        open_weight = float(weights[0])
        trades.append(
            {
                "date": _date_label(dates, 0) if dates is not None else "0",
                "side": "시작",
                "price": float(opens[0]),
                "notional": float(initial),
                "weight": open_weight,
            }
        )
    for k in range(int(n_trades)):
        idx = int(day[k])
        trades.append(
            {
                "date": _date_label(dates, idx) if dates is not None else str(idx),
                "side": "매수" if int(side[k]) > 0 else "매도",
                "price": float(price[k]),
                "notional": float(notional[k]),
                "weight": float(weight_after[k]),
            }
        )
    return Detail(
        initial=float(initial),
        up=float(up),
        down=float(down),
        sell=float(sell),
        buy=float(buy),
        wealth=wealth,
        weights=weights,
        trades=trades,
        **stats,
    )


def eval_params(opens, closes, rfs, params, cost=0.0, split=None, max_weight=1.0) -> np.ndarray:
    opens = np.ascontiguousarray(opens, dtype=np.float64)
    closes = np.ascontiguousarray(closes, dtype=np.float64)
    rfs = np.ascontiguousarray(rfs, dtype=np.float64)
    params = np.ascontiguousarray(params, dtype=np.float64)
    if params.ndim != 2 or params.shape[1] != 5:
        raise ValueError("파라미터 배열은 (공식 수, 5) 형태여야 합니다.")
    if len(opens) < 2:
        raise ValueError("거래일이 너무 적습니다.")
    if split is None:
        split = len(opens)
    _, eval_grid = _load_impl()
    return eval_grid(opens, closes, rfs, params, float(cost), int(split), float(max_weight))


def kelly_fraction(closes, rfs) -> float:
    closes = np.ascontiguousarray(closes, dtype=np.float64)
    rfs = np.ascontiguousarray(rfs, dtype=np.float64)
    rets = np.diff(closes) / closes[:-1]
    excess = rets - rfs[1:]
    var = float(np.var(excess, ddof=1)) if len(excess) > 1 else 0.0
    if var <= 1e-18:
        return 0.0
    return float(np.mean(excess) / var)


def run_constant_mix(opens, closes, rfs, target, dates, cost=0.0) -> Detail:
    """월이 바뀌는 날 시가에 target 비중으로 되돌린다."""
    opens = np.ascontiguousarray(opens, dtype=np.float64)
    closes = np.ascontiguousarray(closes, dtype=np.float64)
    rfs = np.ascontiguousarray(rfs, dtype=np.float64)
    _check(opens, closes, rfs, target, 1.0, 1.0, 0.0, 0.0, cost)
    n = len(opens)
    months = pd.DatetimeIndex(pd.to_datetime(dates)).to_period("M")
    cash = 1.0 - target
    shares = target / opens[0]
    wealth = np.empty(n, dtype=np.float64)
    weights = np.empty(n, dtype=np.float64)
    marked = cash + shares * closes[0]
    wealth[0] = marked
    weights[0] = (shares * closes[0] / marked) if marked > 0 else 0.0
    prev_month = months[0]
    buys = 0
    sells = 0
    one_m_cost = 1.0 - cost
    for t in range(1, n):
        cash *= 1.0 + rfs[t]
        if months[t] != prev_month:
            px = opens[t]
            gross = cash + shares * px
            desired = target * gross
            trade = desired - shares * px
            if trade > 1e-12 and cash > 0.0 and px > 0.0:
                spend = min(cash, trade)
                shares += spend * one_m_cost / px
                cash -= spend
                buys += 1
            elif trade < -1e-12 and shares > 0.0 and px > 0.0:
                qty = min(shares, -trade / px)
                shares -= qty
                cash += qty * px * one_m_cost
                sells += 1
            prev_month = months[t]
        marked = cash + shares * closes[t]
        wealth[t] = marked
        weights[t] = (shares * closes[t] / marked) if marked > 0 else 0.0
    w0 = wealth[0]
    terminal = wealth[-1] / w0 if w0 > 0 else 0.0
    norm = wealth / w0 if w0 > 0 else wealth
    rets = np.diff(norm) / norm[:-1]
    excess = rets - rfs[1:]
    peak = np.maximum.accumulate(norm)
    mdd = float(np.min(norm / peak - 1.0))
    stats = metrics_from_sums(
        terminal,
        mdd,
        float(excess.sum()),
        float(np.square(excess).sum()),
        n,
        buys,
        sells,
        float(np.mean(weights)),
    )
    stats.pop("trades", None)
    return Detail(
        initial=float(target),
        up=0.0,
        down=0.0,
        sell=0.0,
        buy=0.0,
        wealth=norm,
        weights=weights,
        trades=[],
        **stats,
    )


def _date_label(dates, index: int) -> str:
    return pd.Timestamp(dates[index]).strftime("%Y-%m-%d")
