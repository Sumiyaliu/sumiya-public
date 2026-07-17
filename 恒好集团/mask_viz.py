# -*- coding: utf-8 -*-
"""
供图表/报告使用：返回 (区间标签, 代表值/区间中点)。
代表值仅用于图表高度示意，展示时以区间标签为准，不展示精确原始值。
"""
import numpy as np

def to_num(v):
    if v is None:
        return np.nan
    if isinstance(v, str):
        s = v.strip()
        if s in ("∞", "inf", "Inf", "+∞", "INF"):
            return np.inf
        if s in ("", "—", "NaN", "nan"):
            return np.nan
        try:
            return float(s)
        except ValueError:
            return np.nan
    try:
        f = float(v)
        return np.nan if np.isnan(f) else f
    except (TypeError, ValueError):
        return np.nan

def _generic(v, edges, unit, unit_div=1, inf_label=None):
    v = to_num(v)
    if np.isnan(v):
        return "—", 0
    for i in range(len(edges) - 1):
        if edges[i] <= v < edges[i + 1]:
            lo, hi = edges[i], edges[i + 1]
            mid = (lo + hi) / 2 / unit_div
            if unit_div > 1:
                label = f"{int(lo/unit_div)}–{int(hi/unit_div)}{unit}"
            else:
                label = f"{lo:g}–{hi:g}{unit}"
            return label, mid
    lo = edges[-1]
    label = inf_label if inf_label else f"≥{lo}{unit}"
    return label, lo * 1.15 / unit_div

def money(v):
    return _generic(v, [0, 1, 5, 10, 20, 50, 100, 200, 500, 1e6], "万")

def share(v):
    return _generic(v, [0, 1, 3, 5, 10, 20, 50, 80, 100, 1e6], "%", inf_label="100%")

def pct_small(v):
    return _generic(v, [0, 1, 3, 5, 10, 20, 40, 100, 1e6], "%")

def yuan(v):
    return _generic(v, [0, 5, 10, 20, 30, 40, 50, 70, 1e6], "元")

def roi(v):
    v = to_num(v)
    if np.isnan(v):
        return "—", 0
    if v >= 3:
        return "≥3.0", 3.1
    lo = np.floor(v / 0.2) * 0.2
    hi = lo + 0.2
    return f"{lo:.1f}–{hi:.1f}", lo + 0.1
