"""인과적(뒤만 보는) 개별 신호. rolling은 중심을 쓰지 않는다."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import SLOPE_WINDOW, Z_MIN, Z_WINDOW


def rolling_z(series: pd.Series, window: int = Z_WINDOW, min_periods: int = Z_MIN) -> pd.Series:
    mean = series.rolling(window, min_periods=min_periods).mean()
    std = series.rolling(window, min_periods=min_periods).std(ddof=0)
    z = (series - mean) / std.replace(0, np.nan)
    return z.clip(-2.5, 2.5)


def pct_change_n(series: pd.Series, n: int = SLOPE_WINDOW) -> pd.Series:
    return series.pct_change(n)


def diff_n(series: pd.Series, n: int = SLOPE_WINDOW) -> pd.Series:
    return series.diff(n)


def clip_score(series: pd.Series) -> pd.Series:
    return series.clip(-2.0, 2.0)


def build_feature_frame(panel: pd.DataFrame) -> pd.DataFrame:
    """패널 컬럼에서 레짐·스코어에 쓰는 피처만 만든다. 전부 인과적."""
    out = pd.DataFrame(index=panel.index)
    spy = panel.get("SPY")
    qqq = panel.get("QQQ")
    iwm = panel.get("IWM")
    rsp = panel.get("RSP")
    tlt = panel.get("TLT")
    hyg = panel.get("HYG")
    lqd = panel.get("LQD")
    gld = panel.get("GLD")
    uup = panel.get("UUP")
    xlu = panel.get("XLU")
    xlf = panel.get("XLF")
    dgs2 = panel.get("DGS2")
    curve = panel.get("T10Y2Y")
    real = panel.get("DFII10")
    hy = panel.get("BAMLH0A0HYM2")
    dollar = panel.get("DTWEXBGS")
    if dollar is None or dollar.dropna().empty:
        dollar = uup
    vix = panel["VIX"] if "VIX" in panel.columns else panel.get("VIXCLS")
    icsa = panel.get("ICSA")
    cpi = panel.get("CPIAUCSL")
    bei = panel.get("T10YIE")

    out["spy_21"] = pct_change_n(spy) if spy is not None else np.nan
    out["qqq_21"] = pct_change_n(qqq) if qqq is not None else np.nan
    out["iwm_21"] = pct_change_n(iwm) if iwm is not None else np.nan
    out["rsp_21"] = pct_change_n(rsp) if rsp is not None else np.nan
    out["tlt_21"] = pct_change_n(tlt) if tlt is not None else np.nan
    out["hyg_21"] = pct_change_n(hyg) if hyg is not None else np.nan
    out["lqd_21"] = pct_change_n(lqd) if lqd is not None else np.nan
    out["gld_21"] = pct_change_n(gld) if gld is not None else np.nan
    out["uup_21"] = pct_change_n(uup) if uup is not None else np.nan
    out["xlu_21"] = pct_change_n(xlu) if xlu is not None else np.nan
    out["xlf_21"] = pct_change_n(xlf) if xlf is not None else np.nan
    out["dgs2_chg"] = diff_n(dgs2) if dgs2 is not None else np.nan
    out["real_chg"] = diff_n(real) if real is not None else np.nan
    out["curve"] = curve
    out["hy_chg"] = diff_n(hy) if hy is not None else np.nan
    out["hy_level"] = hy
    out["dollar_chg"] = pct_change_n(dollar) if dollar is not None else np.nan
    out["vix"] = vix
    out["icsa_chg"] = pct_change_n(icsa, 20) if icsa is not None else np.nan
    if cpi is not None:
        monthly = cpi.resample("ME").last().dropna()
        yoy = monthly.pct_change(12)
        out["cpi_yoy"] = yoy.reindex(out.index, method="ffill")
        out["cpi_yoy_chg"] = diff_n(out["cpi_yoy"], 63)
    else:
        out["cpi_yoy"] = np.nan
        out["cpi_yoy_chg"] = np.nan
    out["bei_chg"] = diff_n(bei) if bei is not None else np.nan

    # 돈의 가격: 금리·실질금리·달러가 내려가면 리스크온
    out["money"] = clip_score(
        (
            -rolling_z(out["dgs2_chg"].fillna(0))
            - rolling_z(out["real_chg"].fillna(0))
            - rolling_z(out["dollar_chg"].fillna(0))
            + rolling_z(out["curve"].fillna(0)) * 0.35
        )
        / 3.35
    )

    # 리스크 예산: 스프레드·VIX 하락, 폭 확대가 플러스
    breadth = pd.Series(0.0, index=out.index)
    if spy is not None and rsp is not None:
        breadth = rolling_z((out["rsp_21"] - out["spy_21"]).fillna(0))
    small = pd.Series(0.0, index=out.index)
    if qqq is not None and iwm is not None:
        small = rolling_z((out["iwm_21"] - out["qqq_21"]).fillna(0))
    hy_level = out["hy_level"].ffill() if "hy_level" in out.columns else pd.Series(index=out.index, dtype=float)
    vix_s = out["vix"].ffill() if "vix" in out.columns else pd.Series(index=out.index, dtype=float)
    out["risk"] = clip_score(
        (
            -rolling_z(out["hy_chg"].fillna(0))
            - rolling_z(hy_level)
            - rolling_z(vix_s)
            + breadth * 0.45
            + small * 0.35
        )
        / 3.8
    )

    growth_vs_def = pd.Series(0.0, index=out.index)
    if qqq is not None and xlu is not None:
        growth_vs_def = rolling_z((out["qqq_21"] - out["xlu_21"]).fillna(0))
    liq = pd.Series(0.0, index=out.index)
    if spy is not None and tlt is not None:
        both_up = np.sign(out["spy_21"].fillna(0)) + np.sign(out["tlt_21"].fillna(0))
        liq = rolling_z(pd.Series(both_up, index=out.index).astype(float))
    out["relative"] = clip_score((growth_vs_def + liq * 0.5 + small * 0.4) / 1.9)

    out["growth_weak"] = out["icsa_chg"].fillna(0) > 0.02
    out["inflation_hot"] = (out["cpi_yoy_chg"].fillna(0) > 0) | (
        (out["bei_chg"].fillna(0) > 0) & (out["dollar_chg"].fillna(0) > 0)
    )
    out["stocks_up"] = out["spy_21"].fillna(0) > 0
    out["yields_down"] = out["dgs2_chg"].fillna(0) < 0
    out["credit_worse"] = out["hy_chg"].fillna(0) > 0
    return out
