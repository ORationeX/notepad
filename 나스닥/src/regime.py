"""상승·하락 판정과 기준 시점까지의 설정 탐색."""

from __future__ import annotations

import math
import os
from multiprocessing import get_context

import numpy as np
import pandas as pd

from src.features import SAMPLE_START, TRAIN_END, window_positions

UP_ROCS = (0.08, 0.15, 0.25)
DOWN_ROCS = (-0.05, -0.15)
DRAWDOWNS = (-0.12, -0.18, -0.25)
RS_MINS = (0.0, 0.05)
CONFIRMS = (10, 21)
MIN_SHARE = 0.10
MAX_SWITCHES = 25
STABLE_FLOOR = 0.75

AXES = (UP_ROCS, DOWN_ROCS, DRAWDOWNS, RS_MINS, CONFIRMS)


def _lattice(start: float, stop: float, step: float) -> tuple[float, ...]:
    count = int(round((stop - start) / step))
    return tuple(round(start + index * step, 10) for index in range(count + 1))


# 직접 조정이 아니라 이 격자를 전부 계산한다. 간격은 5%p, 확인 일수는 10과 21.
SEARCH_AXES = (
    _lattice(0.0, 0.40, 0.05),
    _lattice(-0.40, 0.0, 0.05),
    _lattice(-0.50, -0.10, 0.05),
    _lattice(-0.10, 0.20, 0.05),
    CONFIRMS,
)


def search_count(axes: tuple = SEARCH_AXES) -> int:
    total = 1
    for axis in axes:
        total *= len(axis)
    return total


def worker_count(jobs: int) -> int:
    return max(2, min(jobs, (os.cpu_count() or 2) - 1))


def classify(
    roc: np.ndarray,
    stretch: np.ndarray,
    dd: np.ndarray,
    rs: np.ndarray,
    up_roc: float,
    down_roc: float,
    decline_dd: float,
    rs_min: float,
    confirm: int,
) -> np.ndarray:
    """1은 상승, -1은 하락, 0은 아직 판정 전. 조건은 confirm일 연속일 때만 바뀐다."""
    n = len(roc)
    state = np.zeros(n, dtype=np.int8)
    current = 0
    up_run = 0
    down_run = 0
    for t in range(n):
        ready = (
            np.isfinite(roc[t])
            and np.isfinite(stretch[t])
            and np.isfinite(dd[t])
            and np.isfinite(rs[t])
        )
        if not ready:
            up_run = 0
            down_run = 0
            state[t] = current
            continue
        want_up = (
            roc[t] >= up_roc
            and stretch[t] >= 0.0
            and rs[t] >= rs_min
            and dd[t] > decline_dd
        )
        want_down = roc[t] <= down_roc or dd[t] <= decline_dd
        if want_up and current != 1:
            up_run += 1
            down_run = 0
            if up_run >= confirm:
                current = 1
                up_run = 0
        elif want_down and current != -1:
            down_run += 1
            up_run = 0
            if down_run >= confirm:
                current = -1
                down_run = 0
        else:
            up_run = 0
            down_run = 0
        state[t] = current
    return state


def classify_baseline(stretch: np.ndarray, confirm: int) -> np.ndarray:
    """200일선 위면 상승, 아래면 하락. 같은 확인 일수를 쓴다."""
    n = len(stretch)
    state = np.zeros(n, dtype=np.int8)
    current = 0
    up_run = 0
    down_run = 0
    for t in range(n):
        if not np.isfinite(stretch[t]):
            up_run = 0
            down_run = 0
            state[t] = current
            continue
        want_up = stretch[t] >= 0.0
        want_down = stretch[t] < 0.0
        if want_up and current != 1:
            up_run += 1
            down_run = 0
            if up_run >= confirm:
                current = 1
                up_run = 0
        elif want_down and current != -1:
            down_run += 1
            up_run = 0
            if down_run >= confirm:
                current = -1
                down_run = 0
        else:
            up_run = 0
            down_run = 0
        state[t] = current
    return state


def window_stats(
    state: np.ndarray,
    ret: np.ndarray,
    rf: np.ndarray,
    start_i: int,
    end_i: int,
) -> dict:
    """보유는 전날 상태를 따른다. 상승이 아니면 현금이다."""
    labels = state[start_i : end_i + 1]
    previous = state[start_i - 1 : end_i]
    judged = labels != 0
    judged_count = int(np.count_nonzero(judged))
    ups = int(np.count_nonzero(labels == 1))
    downs = int(np.count_nonzero(labels == -1))
    switches = int(np.count_nonzero(judged & (labels != previous)))
    position = (previous == 1).astype(np.float64)
    asset = np.where(np.isfinite(ret[start_i : end_i + 1]), ret[start_i : end_i + 1], 0.0)
    cash = np.where(np.isfinite(rf[start_i : end_i + 1]), rf[start_i : end_i + 1], 0.0)
    growth_path = np.cumprod(1.0 + position * asset + (1.0 - position) * cash)
    terminal = float(growth_path[-1])
    peak = np.maximum.accumulate(growth_path)
    mdd = float(np.min(growth_path / peak - 1.0))
    years = len(labels) / 252.0
    if terminal > 0.0 and years > 0.0:
        cagr = terminal ** (1.0 / years) - 1.0
    else:
        cagr = -1.0
    if mdd < -1e-12:
        calmar = cagr / abs(mdd)
    elif cagr > 0.0:
        calmar = 1e6
    else:
        calmar = 0.0
    return {
        "terminal": terminal,
        "cagr": float(cagr),
        "mdd": mdd,
        "calmar": float(calmar),
        "up_share": float(ups / judged_count) if judged_count else 0.0,
        "down_share": float(downs / judged_count) if judged_count else 0.0,
        "switches": switches,
    }


def _neighbor_floor(values: np.ndarray, shape: tuple[int, ...]) -> np.ndarray:
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


def _arrays(features: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "roc": features["roc"].to_numpy(dtype=np.float64),
        "stretch": features["stretch"].to_numpy(dtype=np.float64),
        "dd": features["dd"].to_numpy(dtype=np.float64),
        "rs": features["rs"].to_numpy(dtype=np.float64),
        "ret": features["ret"].to_numpy(dtype=np.float64),
        "rf": features["rf"].to_numpy(dtype=np.float64),
    }


def _bounds(
    features: pd.DataFrame,
    train_end: pd.Timestamp | None = None,
) -> tuple[tuple[int, int], tuple[int, int]]:
    index = pd.DatetimeIndex(features.index)
    end = TRAIN_END if train_end is None else pd.Timestamp(train_end).normalize()
    train = window_positions(index, SAMPLE_START, end)
    holdout = window_positions(index, end + pd.Timedelta(days=1), None)
    return train, holdout


def _score_one(data: dict[str, np.ndarray], params: tuple, train: tuple[int, int], holdout: tuple[int, int]):
    up_roc, down_roc, decline_dd, rs_min, confirm = params
    confirm = int(confirm)
    state = classify(
        data["roc"],
        data["stretch"],
        data["dd"],
        data["rs"],
        float(up_roc),
        float(down_roc),
        float(decline_dd),
        float(rs_min),
        confirm,
    )
    train_stats = window_stats(state, data["ret"], data["rf"], *train)
    test_stats = window_stats(state, data["ret"], data["rf"], *holdout)
    row = {
        "up_roc": float(up_roc),
        "down_roc": float(down_roc),
        "decline_dd": float(decline_dd),
        "rs_min": float(rs_min),
        "confirm": confirm,
        "train_calmar": train_stats["calmar"],
        "train_terminal": train_stats["terminal"],
        "train_mdd": train_stats["mdd"],
        "train_cagr": train_stats["cagr"],
        "train_up": train_stats["up_share"],
        "train_down": train_stats["down_share"],
        "train_switches": train_stats["switches"],
        "test_calmar": test_stats["calmar"],
        "test_terminal": test_stats["terminal"],
        "test_mdd": test_stats["mdd"],
        "test_cagr": test_stats["cagr"],
    }
    return row, train_stats["terminal"]


_WORKER: dict = {}


def _init_worker(data: dict[str, np.ndarray], train: tuple[int, int], holdout: tuple[int, int]) -> None:
    _WORKER["data"] = data
    _WORKER["train"] = train
    _WORKER["holdout"] = holdout


def _score_batch(params: list[tuple]) -> tuple[list[dict], list[float]]:
    rows = []
    terminals = []
    for item in params:
        row, terminal = _score_one(_WORKER["data"], item, _WORKER["train"], _WORKER["holdout"])
        rows.append(row)
        terminals.append(terminal)
    return rows, terminals


def _param_grid(axes: tuple) -> list[tuple]:
    params = []
    for slot in np.ndindex(*(len(axis) for axis in axes)):
        params.append(tuple(axis[index] for axis, index in zip(axes, slot)))
    return params


def _run_grid(
    data: dict[str, np.ndarray],
    axes: tuple,
    train: tuple[int, int],
    holdout: tuple[int, int],
    parallel: bool,
) -> tuple[list[dict], list[float]]:
    params = _param_grid(axes)
    if not parallel or len(params) < 32:
        rows = []
        terminals = []
        for item in params:
            row, terminal = _score_one(data, item, train, holdout)
            rows.append(row)
            terminals.append(terminal)
        return rows, terminals
    processes = worker_count(len(params))
    size = math.ceil(len(params) / processes)
    batches = [params[start : start + size] for start in range(0, len(params), size)]
    context = get_context("spawn")
    with context.Pool(
        processes=len(batches),
        initializer=_init_worker,
        initargs=(data, train, holdout),
    ) as pool:
        parts = pool.map(_score_batch, batches)
    rows = []
    terminals = []
    for part_rows, part_terminals in parts:
        rows.extend(part_rows)
        terminals.extend(part_terminals)
    return rows, terminals


def evaluate(
    features: pd.DataFrame,
    train_end: pd.Timestamp | None = None,
    axes: tuple | None = None,
    parallel: bool = False,
) -> tuple[pd.DataFrame, dict[int, dict], dict]:
    """격자 전부와 확인 일수별 200일선 기준선, 매수 보유.

    train_end까지의 성적으로 고르고, 그 다음 날부터는 예측이다.
    parallel이면 설정 하나씩을 여러 프로세스에 나눠 계산한다.
    """
    data = _arrays(features)
    train, holdout = _bounds(features, train_end)
    used = AXES if axes is None else axes
    shape = tuple(len(axis) for axis in used)
    rows, terminals = _run_grid(data, used, train, holdout, parallel)
    floor = _neighbor_floor(np.asarray(terminals), shape)
    frame = pd.DataFrame(rows)
    own = frame["train_terminal"].to_numpy(dtype=np.float64)
    frame["stable"] = (own > 0.0) & (floor >= own * STABLE_FLOOR)
    baselines = {}
    for confirm in used[4]:
        confirm = int(confirm)
        state = classify_baseline(data["stretch"], confirm)
        baselines[confirm] = {
            "confirm": confirm,
            "train": window_stats(state, data["ret"], data["rf"], *train),
            "test": window_stats(state, data["ret"], data["rf"], *holdout),
        }
    held = np.ones(len(features), dtype=np.int8)
    buyhold = {
        "train": window_stats(held, data["ret"], data["rf"], *train),
        "test": window_stats(held, data["ret"], data["rf"], *holdout),
    }
    return frame, baselines, buyhold


def _eligible(row: pd.Series, baseline_calmar: float) -> bool:
    return bool(
        row["train_up"] >= MIN_SHARE
        and row["train_down"] >= MIN_SHARE
        and int(row["train_switches"]) <= MAX_SWITCHES
        and float(row["train_calmar"]) > baseline_calmar
    )


def choice_from_row(row: pd.Series, source: str = "격자") -> dict:
    return {
        "source": source,
        "up_roc": float(row["up_roc"]),
        "down_roc": float(row["down_roc"]),
        "decline_dd": float(row["decline_dd"]),
        "rs_min": float(row["rs_min"]),
        "confirm": int(row["confirm"]),
        "stable": bool(row["stable"]) if "stable" in row.index else False,
        "train": {
            "terminal": float(row["train_terminal"]),
            "cagr": float(row["train_cagr"]),
            "mdd": float(row["train_mdd"]),
            "calmar": float(row["train_calmar"]),
            "up_share": float(row["train_up"]),
            "down_share": float(row["train_down"]),
            "switches": int(row["train_switches"]),
        },
        "test": {
            "terminal": float(row["test_terminal"]),
            "cagr": float(row["test_cagr"]),
            "mdd": float(row["test_mdd"]),
            "calmar": float(row["test_calmar"]),
        },
    }


def choose(grid: pd.DataFrame, baselines: dict[int, dict]) -> dict:
    """앞 구간 칼마가 같은 확인 일수의 기준선보다 높은 안정 설정. 없으면 기준선."""
    base_calmar = grid["confirm"].map(lambda days: baselines[int(days)]["train"]["calmar"])
    eligible = grid.apply(lambda row: _eligible(row, float(base_calmar.loc[row.name])), axis=1)
    pool = grid.loc[eligible]
    stable = pool.loc[pool["stable"]]
    use = stable if not stable.empty else pool
    if use.empty:
        confirm = max(baselines, key=lambda days: baselines[days]["train"]["calmar"])
        picked = baselines[confirm]
        return {
            "source": "기준선",
            "up_roc": None,
            "down_roc": None,
            "decline_dd": None,
            "rs_min": None,
            "confirm": confirm,
            "stable": True,
            "train": picked["train"],
            "test": picked["test"],
        }
    ranked = use.sort_values(
        ["train_calmar", "train_switches", "train_terminal"],
        ascending=[False, True, False],
        kind="mergesort",
    )
    return choice_from_row(ranked.iloc[0])


def state_for(features: pd.DataFrame, choice: dict) -> np.ndarray:
    if choice["source"] == "기준선":
        stretch = features["stretch"].to_numpy(dtype=np.float64)
        return classify_baseline(stretch, int(choice["confirm"]))
    return classify(
        features["roc"].to_numpy(dtype=np.float64),
        features["stretch"].to_numpy(dtype=np.float64),
        features["dd"].to_numpy(dtype=np.float64),
        features["rs"].to_numpy(dtype=np.float64),
        float(choice["up_roc"]),
        float(choice["down_roc"]),
        float(choice["decline_dd"]),
        float(choice["rs_min"]),
        int(choice["confirm"]),
    )


def describe(choice: dict) -> str:
    days = int(choice["confirm"])
    if choice["source"] == "기준선":
        return (
            f"종가가 200일 이동평균 위면 상승, 아래면 하락입니다. "
            f"같은 방향이 {days}일 연속일 때만 바꿉니다. "
            "격자 안에서는 이 기준선보다 앞 구간의 칼마가 높은 설정이 없었습니다."
        )
    return (
        f"1년 수익률이 {choice['up_roc'] * 100:.0f}% 이상이고 200일선 위이며, "
        f"나스닥이 S&P보다 126일 동안 {choice['rs_min'] * 100:.0f}%p 이상 앞서고, "
        f"고점 대비 낙폭이 {choice['decline_dd'] * 100:.0f}%보다 얕으면 상승입니다. "
        f"1년 수익률이 {choice['down_roc'] * 100:.0f}% 이하이거나 "
        f"낙폭이 {choice['decline_dd'] * 100:.0f}% 이하면 하락입니다. "
        f"같은 신호가 {days}일 연속일 때만 바꿉니다."
    )
