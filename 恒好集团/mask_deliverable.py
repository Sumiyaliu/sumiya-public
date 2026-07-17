# -*- coding: utf-8 -*-
"""
将现有「恒好集团出价与流量分析_脱敏对照.xlsx」中 大盘侧 数值指标
替换为区间脱敏版本，使该文件名副其实。客户A(恒好) 列保持原值。
"""
import pandas as pd
import numpy as np
import os

BASE = "/Users/sumiyaliu/Documents/sumiya的AI小森林/公开/恒好集团"
OUT = os.path.join(BASE, "分析结果")
XL = os.path.join(OUT, "恒好集团出价与流量分析_脱敏对照.xlsx")

# ---------------- 数值解析 ----------------
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

# ---------------- 分桶 ----------------
def bin_money(v):
    v = to_num(v);  return "—" if np.isnan(v) else bin_generic(v, [0,1,5,10,20,50,100,200,500], "万")
def bin_share(v):
    v = to_num(v);  return "—" if np.isnan(v) else bin_generic(v, [0,1,3,5,10,20,50,80,100], "%", inf_label="100%")
def bin_change(v):
    v = to_num(v)
    if np.isnan(v): return "—"
    if np.isinf(v): return "新增/无对比"
    edges=[-1e9,-50,-20,-10,0,10,20,50,1e9]
    labs=["≤-50%","-50~-20%","-20~-10%","-10~0%","0~10%","10~20%","20~50%","≥50%"]
    for i in range(len(edges)-1):
        if edges[i]<v<=edges[i+1]: return labs[i]
    return "≥50%"
def bin_pct_small(v):
    v = to_num(v);  return "—" if np.isnan(v) else bin_generic(v, [0,1,3,5,10,20,40,100], "%")
def bin_roi(v):
    v = to_num(v)
    if np.isnan(v): return "—"
    if v>=3: return "≥3.0"
    lo=np.floor(v/0.2)*0.2; hi=lo+0.2
    return f"{lo:.1f}–{hi:.1f}"
def bin_yuan(v):
    v = to_num(v);  return "—" if np.isnan(v) else bin_generic(v, [0,5,10,20,30,40,50,70], "元")
def bin_egmv(v):
    v = to_num(v);  return "—" if np.isnan(v) else bin_generic(v, [0,1e4,5e4,1e5,5e5,1e6,5e6], "万", inf_label="≥500万")
def bin_generic(v, edges, unit, inf_label=None):
    for i in range(len(edges)-1):
        if edges[i]<=v<edges[i+1]:
            lo,hi=edges[i],edges[i+1]
            if unit=="万" and hi>=1e4: return f"{int(lo/1e4)}–{int(hi/1e4)}万"
            return f"{lo:g}–{hi:g}{unit}"
    return inf_label if inf_label else f"≥{edges[-1]}{unit}"

def choose_binner(col):
    c = col
    if "环比" in c: return bin_change
    if "占比" in c: return bin_share
    if "消耗(万元)" in c or "消耗万" in c: return bin_money
    if "CPM" in c: return bin_yuan
    if "下单单价" in c: return bin_yuan
    if "CTR" in c or "CVR" in c: return bin_pct_small
    if "ROI" in c: return bin_roi
    if "eGMV" in c: return bin_egmv
    if "Bias" in c or "bias" in c: return bin_change
    return None

def mask_cols(df, cols):
    df = df.copy()
    for c in cols:
        b = choose_binner(c)
        if b:
            df[c] = df[c].apply(lambda x: b(x) if pd.notna(x) else "—")
    return df

# ---------------- 读取现有交付物 ----------------
bid_big = pd.read_excel(XL, "大盘-出价方式明细")
bid_hh  = pd.read_excel(XL, "客户A-出价方式明细")
mask_bid= pd.read_excel(XL, "对照-出价方式")
trend   = pd.read_excel(XL, "客户A-投放日趋势")
mask_ov = pd.read_excel(XL, "对照-主体")
flow    = pd.read_excel(XL, "大盘-二级流量效果")

# 大盘-出价方式明细：全部指标列脱敏（无 binner 的标识列自动保留）
bid_big_m = mask_cols(bid_big, [c for c in bid_big.columns if choose_binner(c)])

# 对照-出价方式：仅脱敏 大盘_* 列
big_cols = [c for c in mask_bid.columns if c.startswith("大盘_")]
mask_bid_m = mask_cols(mask_bid, big_cols)

# 对照-主体：仅脱敏「大盘整体」行的指标列
ov_metrics = [c for c in mask_ov.columns if c != "主体" and choose_binner(c)]
mask_ov_m = mask_ov.copy()
sel = mask_ov_m["主体"].astype(str).str.contains("大盘")
for c in ov_metrics:
    b = choose_binner(c)
    mask_ov_m.loc[sel, c] = mask_ov_m.loc[sel, c].apply(lambda x: b(x) if pd.notna(x) else "—")

# 大盘-二级流量效果：全部指标列脱敏
flow_m = mask_cols(flow, [c for c in flow.columns if choose_binner(c)])

# 客户A 两个 sheet 保持原值
bid_hh_m = bid_hh
trend_m  = trend

# ---------------- 写回（覆盖同名文件） ----------------
with pd.ExcelWriter(XL, engine="openpyxl") as xl:
    bid_big_m.to_excel(xl, "大盘-出价方式明细", index=False)
    bid_hh_m.to_excel(xl, "客户A-出价方式明细", index=False)
    mask_bid_m.to_excel(xl, "对照-出价方式", index=False)
    trend_m.to_excel(xl, "客户A-投放日趋势", index=False)
    mask_ov_m.to_excel(xl, "对照-主体", index=False)
    flow_m.to_excel(xl, "大盘-二级流量效果", index=False)

print("=== 脱敏对照.xlsx 大盘侧已区间脱敏 ===")
print("大盘-出价方式明细:", bid_big_m.shape)
print("对照-出价方式 已脱敏列:", big_cols)
print("对照-主体 已脱敏行:", mask_ov_m.loc[sel, '主体'].tolist())
print("大盘-二级流量效果:", flow_m.shape)
print("输出:", XL)
