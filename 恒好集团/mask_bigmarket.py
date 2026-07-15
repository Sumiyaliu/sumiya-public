# -*- coding: utf-8 -*-
"""
大盘相关指标 -> 区间数据脱敏
保留标识/结构列（出价类型、流量名称、是否ROI广告、是否置信等），
将全部数值型指标列按类型分桶为区间字符串，防止精确数值被还原。
"""
import pandas as pd
import numpy as np
import os

BASE = "/Users/sumiyaliu/Documents/sumiya的AI小森林/公开/恒好集团"
OUT = os.path.join(BASE, "分析结果")
os.makedirs(OUT, exist_ok=True)

# ---------------- 安全数值解析 ----------------
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
        if np.isnan(f):
            return np.nan
        return f
    except (TypeError, ValueError):
        return np.nan

# ---------------- 分桶函数 ----------------
def bin_money(v):
    v = to_num(v)
    if np.isnan(v):
        return "—"
    return bin_generic(v, [0, 1, 5, 10, 20, 50, 100, 200, 500], "万")

def bin_share(v):
    v = to_num(v)
    if np.isnan(v):
        return "—"
    return bin_generic(v, [0, 1, 3, 5, 10, 20, 50, 80, 100], "%", inf_label="100%")

def bin_change(v):
    v = to_num(v)
    if np.isnan(v):
        return "—"
    if np.isinf(v):
        return "新增/无对比"
    edges = [-1e9, -50, -20, -10, 0, 10, 20, 50, 1e9]
    labs = ["≤-50%", "-50~-20%", "-20~-10%", "-10~0%", "0~10%", "10~20%", "20~50%", "≥50%"]
    for i in range(len(edges) - 1):
        if edges[i] < v <= edges[i + 1]:
            return labs[i]
    return "≥50%"

def bin_pct_small(v):
    v = to_num(v)
    if np.isnan(v):
        return "—"
    return bin_generic(v, [0, 1, 3, 5, 10, 20, 40, 100], "%")

def bin_roi(v):
    v = to_num(v)
    if np.isnan(v):
        return "—"
    if v >= 3:
        return "≥3.0"
    lo = np.floor(v / 0.2) * 0.2
    hi = lo + 0.2
    return f"{lo:.1f}–{hi:.1f}"

def bin_yuan(v):
    v = to_num(v)
    if np.isnan(v):
        return "—"
    return bin_generic(v, [0, 5, 10, 20, 30, 40, 50, 70], "元")

def bin_egmv(v):
    v = to_num(v)
    if np.isnan(v):
        return "—"
    return bin_generic(v, [0, 1e4, 5e4, 1e5, 5e5, 1e6, 5e6], "万", inf_label="≥500万")

def bin_generic(v, edges, unit, inf_label=None):
    for i in range(len(edges) - 1):
        if edges[i] <= v < edges[i + 1]:
            lo, hi = edges[i], edges[i + 1]
            if unit == "万" and hi >= 1e4:
                return f"{int(lo/1e4)}–{int(hi/1e4)}万"
            return f"{lo:g}–{hi:g}{unit}"
    if inf_label:
        return inf_label
    return f"≥{edges[-1]}{unit}"

# ---------------- 列 -> 分桶器 映射 ----------------
def get_binner(col):
    c = col
    if "消耗(万元)" in c or "日均消耗(万元)" in c:
        if c.endswith("环比变化量"):
            return bin_money
        if "环比变化率" in c:
            return bin_change
        if "占比" in c:
            return bin_share
        return bin_money
    if "竞价CPM(元)" in c:
        return bin_yuan
    if "下单单价(元)" in c:
        return bin_yuan
    if "ctr(%)" in c or "浅层cvr(%)" in c or "pCVR模型 pCVR(%)" in c or "pCVR模型 CVR(%)" in c:
        if c.endswith("环比变化量"):
            return bin_pct_small
        if "环比变化率" in c:
            return bin_change
        return bin_pct_small
    if "下单ROI" in c:
        if c.endswith("环比变化量"):
            return bin_roi
        if "环比变化率" in c:
            return bin_change
        return bin_roi
    if "eGMV" in c:
        if "占比" in c:
            return bin_share
        if "环比变化率" in c:
            return bin_change
        return bin_egmv
    if "Bias" in c or "bias" in c:
        return bin_change
    if "环比变化率" in c:
        return bin_change
    return None

# 需要保留（不脱敏）的标识/结构列
def is_keep(col):
    keep_kw = ["广告智投类型", "浅层优化目标", "投放OG组合", "浅层-深层",
               "是否ROI广告", "深度辅助优化目标", "自动出价类型",
               "二级流量", "是否置信"]
    return any(k in col for k in keep_kw)

# ---------------- 处理 ----------------
def mask_df(df):
    out = pd.DataFrame()
    for col in df.columns:
        if is_keep(col):
            out[col] = df[col]
        else:
            b = get_binner(col)
            if b is None:
                out[col] = df[col]
            else:
                out[col] = df[col].apply(lambda x: b(x) if pd.notna(x) else "—")
    return out

df_bid = pd.read_csv(os.path.join(BASE, "大盘不同出价类型分析.csv"))
df_flow = pd.read_csv(os.path.join(BASE, "大盘不同流量效果.csv"))

bid_mask = mask_df(df_bid)
flow_mask = mask_df(df_flow)

# ---------------- 脱敏说明 ----------------
scheme = pd.DataFrame([
    ["金额(万元)/日均消耗(万元)", "0–1, 1–5, 5–10, 10–20, 20–50, 50–100, 100–200, 200–500, ≥500 (万)"],
    ["占比(%)", "0–1, 1–3, 3–5, 5–10, 10–20, 50–80, 80–100 (%)"],
    ["环比变化率/Bias(%)", "≤-50, -50~-20, -20~-10, -10~0, 0~10, 10~20, 20~50, ≥50 (%)，∞=新增/无对比"],
    ["CTR%/CVR%/pCVR%/CVR(%)", "0–1, 1–3, 3–5, 5–10, 10–20, 20–40, 40–100 (%)"],
    ["下单ROI", "0.2 步长区间 (如 1.6–1.8)；≥3.0"],
    ["CPM/单价(元)", "0–5, 5–10, 10–20, 20–30, 30–40, 40–50, 50–70, ≥70 (元)"],
    ["eGMV(元)", "0–1, 1–5, 5–10, 10–50, 50–100, 100–500, ≥500 (万)"],
    ["标识/结构列", "出价类型、流量名称、是否ROI广告、是否置信等 -> 不脱敏，原样保留"],
], columns=["指标类型", "区间分桶规则"])

with pd.ExcelWriter(os.path.join(OUT, "大盘指标_区间脱敏.xlsx"), engine="openpyxl") as xl:
    bid_mask.to_excel(xl, "大盘-出价方式(区间脱敏)", index=False)
    flow_mask.to_excel(xl, "大盘-二级流量(区间脱敏)", index=False)
    scheme.to_excel(xl, "脱敏说明", index=False)

print("=== 大盘指标·区间脱敏 完成 ===")
print("出价方式表:", bid_mask.shape, " 流量表:", flow_mask.shape)
print("输出:", os.path.join(OUT, "大盘指标_区间脱敏.xlsx"))
