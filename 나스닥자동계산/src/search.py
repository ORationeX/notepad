"""리밸런싱 다섯 숫자의 격자 탐색."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.engine import eval_params

GRID_VERSION = 6

# 2%–30%는 1% 간격이다. 그 위는 간격을 넓혀 40% 경계에 1위가 붙지 않게 한다.
_FINE_BANDS = np.round(np.linspace(0.02, 0.30, 29), 2)
_WIDE_BANDS = np.array([0.35, 0.40, 0.45, 0.50, 0.60, 0.80, 1.00, 1.50, 2.00])
INITIALS = np.round(np.linspace(0.05, 1.0, 20), 2)
UPS = np.concatenate([_FINE_BANDS, _WIDE_BANDS])
DOWNS = np.concatenate([_FINE_BANDS, _WIDE_BANDS])
SELLS = np.round(np.linspace(0.05, 1.0, 20), 2)
BUYS = np.round(np.linspace(0.05, 1.0, 20), 2)
LEADER_KEEP = 40
STABLE_FLOOR = 0.75

OBJECTIVES = {
    "최종 수익": "terminal",
    "수익 ÷ 낙폭": "calmar",
    "샤프": "sharpe",
}


def initials_for(max_weight: float) -> np.ndarray:
    capped = INITIALS[INITIALS <= float(max_weight) + 1e-9]
    if capped.size == 0:
        return np.array([round(float(max_weight), 2)], dtype=np.float64)
    return capped


def grid_count(initials=INITIALS, ups=UPS, downs=DOWNS, sells=SELLS, buys=BUYS) -> int:
    return int(len(initials) * len(ups) * len(downs) * len(sells) * len(buys))


def grid_summary(max_weight: float = 1.0) -> str:
    initials = initials_for(max_weight)
    return (
        f"초기 비중 {pct_text(float(initials[0]))}–{pct_text(float(initials[-1]))}는 5% 간격, "
        "오름·내림 폭은 2–30%가 1% 간격이고 35–200%는 더 넓은 간격, "
        "매도·매수 비율 5–100%는 5% 간격입니다. "
        f"모두 {grid_count(initials=initials):,}개입니다. "
        f"사는 금액은 투자 비중 {pct_text(float(max_weight))}에서 멈춥니다."
    )


def build_params(initials=INITIALS, ups=UPS, downs=DOWNS, sells=SELLS, buys=BUYS) -> np.ndarray:
    axes = [np.asarray(values, dtype=np.float64) for values in (initials, ups, downs, sells, buys)]
    lengths = [len(values) for values in axes]
    total = int(np.prod(lengths))
    grid = np.empty((total, 5), dtype=np.float64)
    index = np.arange(total)
    for column in range(4, -1, -1):
        size = lengths[column]
        grid[:, column] = axes[column][index % size]
        index //= size
    return grid


def holdout_split(n_days: int) -> int | None:
    """뒤 30%를 검증 구간으로 남긴다. 앞뒤가 너무 짧으면 나누지 않는다."""
    if n_days < 252 * 2:
        return None
    split = int(n_days * 0.7)
    if split < 252 or n_days - split < 126:
        return None
    return split


def _axis(center: float, step: float, lo: float, hi: float) -> list[float]:
    values = [min(hi, max(lo, center + offset * step)) for offset in (-1, 0, 1)]
    return sorted({round(v, 6) for v in values})


def neighborhood(seed: np.ndarray, lock_initial: bool = False) -> np.ndarray:
    initial = [round(float(seed[0]), 6)] if lock_initial else _axis(float(seed[0]), 0.05, 0.05, 1.0)
    up = _axis(float(seed[1]), 0.01, 0.02, 0.40)
    down = _axis(float(seed[2]), 0.01, 0.02, 0.40)
    sell = _axis(float(seed[3]), 0.05, 0.05, 1.0)
    buy = _axis(float(seed[4]), 0.05, 0.05, 1.0)
    return build_params(initial, up, down, sell, buy)


def _metrics_arrays(terminal, mdd, sum_ex, sum_ex2, n_days, buys, sells, avg_weight) -> dict[str, np.ndarray]:
    """metrics_from_sums와 같은 식을 공식 배열에 한 번에 적용한다."""
    count = len(terminal)
    m = n_days - 1
    years = m / 252.0 if m > 0 else 0.0
    cagr = np.full(count, -1.0, dtype=np.float64)
    if years > 0.0:
        positive = terminal > 0.0
        cagr[positive] = np.power(terminal[positive], 1.0 / years) - 1.0
    sharpe = np.zeros(count, dtype=np.float64)
    if m > 1:
        var = (sum_ex2 - (sum_ex * sum_ex) / m) / (m - 1)
        mean = sum_ex / m
        stable = var > 1e-18
        sharpe[stable] = mean[stable] / np.sqrt(var[stable]) * np.sqrt(252.0)
    calmar = np.zeros(count, dtype=np.float64)
    deep = mdd < -1e-12
    calmar[deep] = cagr[deep] / np.abs(mdd[deep])
    calm = (~deep) & (cagr > 0.0)
    calmar[calm] = 1e6
    buys_i = buys.astype(np.int32)
    sells_i = sells.astype(np.int32)
    return {
        "terminal": np.asarray(terminal, dtype=np.float64),
        "cagr": cagr,
        "mdd": np.asarray(mdd, dtype=np.float64),
        "sharpe": sharpe,
        "calmar": calmar,
        "buys": buys_i,
        "sells": sells_i,
        "avg_weight": np.asarray(avg_weight, dtype=np.float64),
        "trades": buys_i + sells_i,
    }


def _frame_from_raw(params: np.ndarray, raw: np.ndarray, n_days: int, split: int) -> pd.DataFrame:
    train_days = split if 0 < split < n_days else n_days
    full = _metrics_arrays(raw[:, 0], raw[:, 1], raw[:, 2], raw[:, 3], n_days, raw[:, 4], raw[:, 5], raw[:, 6])
    train = _metrics_arrays(
        raw[:, 7], raw[:, 8], raw[:, 9], raw[:, 10], train_days, raw[:, 11], raw[:, 12], raw[:, 13]
    )
    data = {
        "initial": params[:, 0],
        "up": params[:, 1],
        "down": params[:, 2],
        "sell": params[:, 3],
        "buy": params[:, 4],
    }
    data.update(full)
    for key, value in train.items():
        data[f"train_{key}"] = value
    return pd.DataFrame(data)


def neighbor_floor(values: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
    """각 칸과, 축을 한 눈금만 옮긴 이웃 가운데 가장 낮은 값."""
    grid = np.asarray(values, dtype=np.float64).reshape(shape)
    floor = grid.copy()
    for axis in range(grid.ndim):
        for shift in (-1, 1):
            shifted = np.full(shape, np.inf, dtype=np.float64)
            src = [slice(None)] * grid.ndim
            dst = [slice(None)] * grid.ndim
            if shift < 0:
                src[axis] = slice(None, -1)
                dst[axis] = slice(1, None)
            else:
                src[axis] = slice(1, None)
                dst[axis] = slice(None, -1)
            shifted[tuple(dst)] = grid[tuple(src)]
            floor = np.minimum(floor, shifted)
    return floor.reshape(-1)


def prefer_stable(table: pd.DataFrame, score_col: str) -> pd.DataFrame:
    """한 눈금만 옮겨도 최종 금액이 4분의 3 미만이 되는 공식은 1위에서 빼 둔다."""
    train = str(score_col).startswith("train_")
    floor_col = "train_floor" if train else "floor"
    term_col = "train_terminal" if train else "terminal"
    if floor_col not in table.columns or table.empty:
        return table
    stable = table[table[floor_col] >= table[term_col] * STABLE_FLOOR]
    if stable.empty:
        return table
    return stable


def _top_index(score, terminal, trades, up, down, mask, keep: int) -> np.ndarray:
    available = int(np.count_nonzero(mask))
    if available == 0:
        return np.empty(0, dtype=np.int64)
    take = min(keep, available)
    if take == available:
        pool = np.flatnonzero(mask)
    elif available == len(mask):
        pool = np.argpartition(np.asarray(score), -take)[-take:]
    else:
        usable = np.array(score, dtype=np.float64, copy=True)
        usable[~mask] = -np.inf
        pool = np.argpartition(usable, -take)[-take:]
    order = np.lexsort(
        (
            -down[pool],
            -up[pool],
            trades[pool],
            -terminal[pool],
            -score[pool],
        )
    )
    return pool[order[:take]]


def select_leaders(
    params: np.ndarray,
    raw: np.ndarray,
    n_days: int,
    split: int,
    keep: int = LEADER_KEEP,
    floor: np.ndarray | None = None,
    train_floor: np.ndarray | None = None,
    min_trades: int = 0,
    train_min_trades: int = 0,
) -> pd.DataFrame:
    """순위표와 1위에 쓰이는 앞자리만 남긴다. 전체 표는 수백만 행이라 화면에 두지 않는다."""
    train_days = split if 0 < split < n_days else n_days
    full = _metrics_arrays(raw[:, 0], raw[:, 1], raw[:, 2], raw[:, 3], n_days, raw[:, 4], raw[:, 5], raw[:, 6])
    train = _metrics_arrays(
        raw[:, 7], raw[:, 8], raw[:, 9], raw[:, 10], train_days, raw[:, 11], raw[:, 12], raw[:, 13]
    )
    initial = params[:, 0]
    up = params[:, 1]
    down = params[:, 2]
    full_active = (full["buys"] >= 1) & (full["sells"] >= 1)
    train_active = (train["buys"] >= 1) & (train["sells"] >= 1)
    initial_30 = np.isclose(initial, 0.30, atol=1e-4)
    full_masks = [
        np.ones(len(params), dtype=bool),
        full_active,
        initial_30,
        initial_30 & full_active,
    ]
    train_masks = [
        np.ones(len(params), dtype=bool),
        train_active,
        initial_30,
        initial_30 & train_active,
    ]
    if floor is not None:
        stable = floor >= full["terminal"] * STABLE_FLOOR
        full_masks.extend([stable, stable & full_active, stable & initial_30, stable & initial_30 & full_active])
    if train_floor is not None:
        train_stable = train_floor >= train["terminal"] * STABLE_FLOOR
        train_masks.extend(
            [train_stable, train_stable & train_active, train_stable & initial_30, train_stable & initial_30 & train_active]
        )
    if min_trades > 0:
        frequent = full["trades"] >= min_trades
        full_masks.extend([frequent, frequent & full_active])
        if floor is not None:
            full_masks.extend([frequent & stable, frequent & stable & full_active, frequent & stable & initial_30])
    if train_min_trades > 0:
        train_frequent = train["trades"] >= train_min_trades
        train_masks.extend([train_frequent, train_frequent & train_active])
        if train_floor is not None:
            train_masks.extend(
                [train_frequent & train_stable, train_frequent & train_stable & train_active, train_frequent & train_stable & initial_30]
            )
    chosen = []
    for name in ("terminal", "calmar", "sharpe"):
        for mask in full_masks:
            chosen.append(_top_index(full[name], full["terminal"], full["trades"], up, down, mask, keep))
        for mask in train_masks:
            chosen.append(_top_index(train[name], train["terminal"], train["trades"], up, down, mask, keep))
    selected = np.unique(np.concatenate(chosen))
    frame = _frame_from_raw(params[selected], raw[selected], n_days, split)
    if floor is not None:
        frame["floor"] = floor[selected]
    if train_floor is not None:
        frame["train_floor"] = train_floor[selected]
    return frame


def eligible_rows(
    table: pd.DataFrame,
    score_col: str,
    min_trades: int = 0,
    buys_col: str = "buys",
    sells_col: str = "sells",
    initial: float | None = None,
    active_only: bool = True,
) -> pd.DataFrame:
    sub = table
    if initial is not None:
        sub = sub[np.isclose(sub["initial"], initial, atol=1e-4)]
    if sub.empty:
        return sub
    sub = prefer_stable(sub, score_col)
    if active_only:
        active = sub[(sub[buys_col] >= 1) & (sub[sells_col] >= 1)]
        if not active.empty:
            sub = active
    trades_col = "train_trades" if str(score_col).startswith("train_") else "trades"
    if min_trades > 0 and trades_col in sub.columns and not sub.empty:
        frequent = sub[sub[trades_col] >= min_trades]
        if not frequent.empty:
            sub = frequent
        else:
            most = sub[trades_col].max()
            sub = sub[sub[trades_col] == most]
    return sub


def pick(
    table: pd.DataFrame,
    score_col: str,
    buys_col: str = "buys",
    sells_col: str = "sells",
    initial: float | None = None,
    min_trades: int = 0,
) -> pd.Series:
    sub = eligible_rows(table, score_col, min_trades=min_trades, buys_col=buys_col, sells_col=sells_col, initial=initial)
    if sub.empty:
        raise ValueError("고를 공식이 없습니다.")
    terminal_col = "train_terminal" if score_col.startswith("train_") else "terminal"
    trades_col = "train_trades" if score_col.startswith("train_") else "trades"
    up_col = "up"
    down_col = "down"
    ranked = sub.sort_values(
        [score_col, terminal_col, trades_col, up_col, down_col],
        ascending=[False, False, True, False, False],
        kind="mergesort",
    )
    return ranked.iloc[0]


def search_table(
    opens,
    closes,
    rfs,
    cost: float = 0.0,
    split: int | None = None,
    params: np.ndarray | None = None,
    on_progress=None,
    max_weight: float = 1.0,
    min_trades: int = 0,
    train_min_trades: int = 0,
) -> pd.DataFrame:
    """슬라이더와 같은 간격의 격자를 모두 계산한다.

    결과가 수백만 줄이면 1위와 순위표에 나오는 앞자리만 돌려준다.
    비교한 개수는 grid_count와 같다.
    """
    n_days = len(opens)
    if split is None or split <= 0 or split >= n_days:
        split_arg = n_days
    else:
        split_arg = int(split)
    if params is None:
        used_initials = initials_for(max_weight)
        base = build_params(initials=used_initials)
        shape = (len(used_initials), len(UPS), len(DOWNS), len(SELLS), len(BUYS))
    else:
        base = np.ascontiguousarray(params, dtype=np.float64)
        shape = None
    count = int(base.shape[0])
    raw = np.empty((count, 14), dtype=np.float64)
    step = 1_000_000 if count > 1_000_000 else count
    for start in range(0, count, step):
        end = min(start + step, count)
        raw[start:end] = eval_params(
            opens, closes, rfs, base[start:end], cost=cost, split=split_arg, max_weight=max_weight
        )
        if on_progress is not None:
            on_progress(0.9 * end / count, f"{end:,} / {count:,}개 공식")
    if on_progress is not None:
        on_progress(0.95, "금액이 큰 공식을 고르는 중")
    floor = neighbor_floor(raw[:, 0], shape) if shape is not None else None
    train_floor = neighbor_floor(raw[:, 7], shape) if shape is not None else None
    if count > 2000:
        frame = select_leaders(
            base,
            raw,
            n_days,
            split_arg,
            floor=floor,
            train_floor=train_floor,
            min_trades=min_trades,
            train_min_trades=train_min_trades,
        )
    else:
        frame = _frame_from_raw(base, raw, n_days, split_arg)
        if floor is not None:
            frame["floor"] = floor
            frame["train_floor"] = train_floor
    if on_progress is not None:
        on_progress(1.0, f"{count:,}개 공식을 비교했습니다")
    return frame


def pct_text(value: float) -> str:
    percent = value * 100.0
    if abs(percent - round(percent)) < 0.05:
        return f"{percent:.0f}%"
    return f"{percent:.1f}%"


def describe(row) -> str:
    return (
        f"시작할 때 자본의 {pct_text(row['initial'])}를 산다. "
        f"직전 종가가 기준가보다 {pct_text(row['up'])} 이상 높으면 다음 시가에 보유 수량의 {pct_text(row['sell'])}를 팔고, "
        f"{pct_text(row['down'])} 이상 낮으면 다음 시가에 남은 현금의 {pct_text(row['buy'])}를 산다. "
        f"체결되면 그 가격이 새 기준가다."
    )


def short_name(row) -> str:
    return (
        f"초기 {pct_text(row['initial'])} · "
        f"+{pct_text(row['up'])}에 {pct_text(row['sell'])} 매도 · "
        f"-{pct_text(row['down'])}에 {pct_text(row['buy'])} 매수"
    )


def save_table(path: Path, key: str, table: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(path, index=False)
    path.with_suffix(".json").write_text(json.dumps({"key": key}, ensure_ascii=False), encoding="utf-8")


def load_table(path: Path, key: str) -> pd.DataFrame | None:
    path = Path(path)
    meta_path = path.with_suffix(".json")
    if not path.exists() or not meta_path.exists():
        return None
    try:
        saved = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if saved.get("key") != key:
        return None
    return pd.read_parquet(path)
