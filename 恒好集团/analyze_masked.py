# -*- coding: utf-8 -*-
# 恒好素材版：大盘相关数字区间化展示，恒好(客户A)自身数据保持精确值。
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from mask_viz import money, share, pct_small, yuan, roi

BASE = "/Users/sumiyaliu/Documents/sumiya的AI小森林/公开/恒好集团"
OUT = os.path.join(BASE, "分析结果")
os.makedirs(OUT, exist_ok=True)

df_big_bid = pd.read_csv(os.path.join(BASE, "大盘不同出价类型分析.csv"))
df_flow   = pd.read_csv(os.path.join(BASE, "大盘不同流量效果.csv"))
df_hh_bid = pd.read_csv(os.path.join(BASE, "恒好不同出嫁类型效果分析.csv"))
df_trend  = pd.read_csv(os.path.join(BASE, "恒好集团投放趋势.csv"))

def build_bid_table(df):
    rows = []
    for _, r in df.iterrows():
        zt = r['广告智投类型(翻译后)']
        if pd.isna(zt) or str(zt) in ('整体', '', 'nan'):
            rows.append({'分组': '整体', '智投类型': '整体', '自动出价': '-',
                '消耗万': r['消耗(万元)'], '消耗占比%': r['消耗(万元)占比(%)'],
                'CPM': r['竞价CPM(元)'], 'CTR%': r['ctr(%)'], 'CVR%': r['浅层cvr(%)'], '下单ROI': r['下单ROI']})
            continue
        rows.append({'分组': str(zt), '智投类型': str(zt), '自动出价': str(r['自动出价类型(翻译后)']),
            '是否ROI': str(r['是否ROI广告(翻译后)']),
            '消耗万': r['消耗(万元)'], '消耗占比%': r['消耗(万元)占比(%)'],
            'CPM': r['竞价CPM(元)'], 'CTR%': r['ctr(%)'], 'CVR%': r['浅层cvr(%)'], '下单ROI': r['下单ROI']})
    return pd.DataFrame(rows)

bid_big = build_bid_table(df_big_bid)
bid_hh  = build_bid_table(df_hh_bid)
flow = df_flow[df_flow['二级流量(仅拆分MP)'] != '整体'].copy()
trend = df_trend.copy()
trend['时间'] = pd.to_datetime(trend['时间'])

# ===================== 图1: 出价方式消耗结构占比 =====================
# 大盘：饼图切片按真实占比绘制(结构本身非敏感数据比例)，但标签/悬浮只显示区间，不显示精确百分数
big_rows = bid_big[bid_big['分组'] != '整体']
big_labels = big_rows['智投类型'] + ' / ' + big_rows['自动出价']
big_vals = big_rows['消耗占比%'].fillna(0)
big_interval_labels = [share(v)[0] for v in big_vals]

hh_rows = bid_hh[bid_hh['分组'] != '整体']
hh_labels = hh_rows['智投类型'] + ' / ' + hh_rows['自动出价']
hh_vals = hh_rows['消耗占比%'].fillna(0)

fig1 = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]],
                      subplot_titles=("客户A-各出价方式消耗占比(精确)", "大盘-各出价方式消耗占比(区间展示)"))
fig1.add_trace(go.Pie(labels=hh_labels, values=hh_vals, hole=.4,
                       texttemplate="%{label}<br>%{percent}", title='客户A'), 1, 1)
fig1.add_trace(go.Pie(labels=big_labels, values=big_vals, hole=.4,
                       text=big_interval_labels, texttemplate="%{label}<br>%{text}",
                       hovertemplate="%{label}<br>占比区间: %{text}<extra></extra>",
                       title='大盘'), 1, 2)
fig1.update_layout(title="出价方式消耗结构占比对比（大盘为区间脱敏展示）", height=460, font=dict(size=11))

# ===================== 图2: 出价方式效果对比 =====================
cats = ['非智投/普通/下单', '非智投/投放端自动出价/下单', '非智投/普通/下单ROI']

def pick(df_sub, cat):
    for _, r in df_sub.iterrows():
        zt, zd = r['智投类型'], r['自动出价']
        is_roi = r.get('是否ROI', '')
        if cat == '非智投/普通/下单' and zt == '非智投广告' and zd == '普通' and is_roi != '是':
            return r
        if cat == '非智投/投放端自动出价/下单' and zt == '非智投广告' and zd == '投放端自动出价':
            return r
        if cat == '非智投/普通/下单ROI' and zt == '非智投广告' and zd == '普通' and is_roi == '是':
            return r
    return None

big_sub = bid_big[bid_big['分组'] != '整体']
hh_sub = bid_hh[bid_hh['分组'] != '整体']
big_picks = [pick(big_sub, c) for c in cats]
hh_picks = [pick(hh_sub, c) for c in cats]

def hh_val(lst, col):
    return [r[col] if r is not None else 0 for r in lst]

def big_val_interval(lst, col, binner):
    labels, mids = [], []
    for r in lst:
        if r is None:
            labels.append("—"); mids.append(0); continue
        lab, mid = binner(r[col])
        labels.append(lab); mids.append(mid)
    return labels, mids

hh_ctr = hh_val(hh_picks, 'CTR%'); hh_cvr = hh_val(hh_picks, 'CVR%'); hh_roi = hh_val(hh_picks, '下单ROI')
big_ctr_lab, big_ctr_mid = big_val_interval(big_picks, 'CTR%', pct_small)
big_cvr_lab, big_cvr_mid = big_val_interval(big_picks, 'CVR%', pct_small)
big_roi_lab, big_roi_mid = big_val_interval(big_picks, '下单ROI', roi)

fig2 = make_subplots(rows=1, cols=3, subplot_titles=("CTR", "浅层CVR", "下单ROI"))
fig2.add_trace(go.Bar(name='大盘(区间)', x=cats, y=big_ctr_mid, text=big_ctr_lab, textposition='outside',
                       marker_color='#4C78A8', hovertemplate="%{x}<br>大盘CTR区间: %{text}<extra></extra>"), 1, 1)
fig2.add_trace(go.Bar(name='客户A', x=cats, y=hh_ctr, text=[f"{v:.2f}%" for v in hh_ctr], textposition='outside',
                       marker_color='#F58518'), 1, 1)
fig2.add_trace(go.Bar(name='大盘(区间)', x=cats, y=big_cvr_mid, text=big_cvr_lab, textposition='outside',
                       marker_color='#4C78A8', showlegend=False,
                       hovertemplate="%{x}<br>大盘CVR区间: %{text}<extra></extra>"), 1, 2)
fig2.add_trace(go.Bar(name='客户A', x=cats, y=hh_cvr, text=[f"{v:.2f}%" for v in hh_cvr], textposition='outside',
                       marker_color='#F58518', showlegend=False), 1, 2)
fig2.add_trace(go.Bar(name='大盘(区间)', x=cats, y=big_roi_mid, text=big_roi_lab, textposition='outside',
                       marker_color='#4C78A8', showlegend=False,
                       hovertemplate="%{x}<br>大盘ROI区间: %{text}<extra></extra>"), 1, 3)
fig2.add_trace(go.Bar(name='客户A', x=cats, y=hh_roi, text=[f"{v:.2f}" for v in hh_roi], textposition='outside',
                       marker_color='#F58518', showlegend=False), 1, 3)
fig2.update_layout(title="出价方式效果对比 (大盘为区间脱敏展示，客户A为精确值)", barmode='group', height=460, font=dict(size=10))
fig2.update_yaxes(title_text="%", row=1, col=1); fig2.update_yaxes(title_text="%", row=1, col=2)
fig2.update_yaxes(title_text="ROI", row=1, col=3)

# ===================== 图3: 恒好日趋势（仅客户A数据，无需脱敏） =====================
fig3 = make_subplots(specs=[[{"secondary_y": True}]])
fig3.add_trace(go.Bar(x=trend['时间'], y=trend['消耗(万元)'], name='消耗(万元)', marker_color='#72B7B2'), secondary_y=False)
fig3.add_trace(go.Scatter(x=trend['时间'], y=trend['下单ROI'], name='下单ROI', mode='lines+markers', marker_color='#E45756'), secondary_y=True)
fig3.update_layout(title="客户A(恒好)投放日趋势 (消耗 & 下单ROI)", height=420, font=dict(size=11))
fig3.update_yaxes(title_text="消耗(万元)", secondary_y=False)
fig3.update_yaxes(title_text="下单ROI", secondary_y=True)

# ===================== 图4: 大盘二级流量效果（区间展示） =====================
flow_names = flow['二级流量(仅拆分MP)'].tolist()
cost_lab, cost_mid = [], []
roi_lab, roi_mid = [], []
for _, r in flow.iterrows():
    l, m = money(r['日均消耗(万元)']); cost_lab.append(l); cost_mid.append(m)
    l, m = roi(r['下单ROI']); roi_lab.append(l); roi_mid.append(m)

fig4 = make_subplots(specs=[[{"secondary_y": True}]])
fig4.add_trace(go.Bar(x=flow_names, y=cost_mid, text=cost_lab, textposition='outside',
                       name='日均消耗(区间)', marker_color='#54A24B',
                       hovertemplate="%{x}<br>日均消耗区间: %{text}<extra></extra>"), secondary_y=False)
fig4.add_trace(go.Scatter(x=flow_names, y=roi_mid, text=roi_lab, mode='lines+markers+text', textposition='top center',
                           name='下单ROI(区间)', marker_color='#B279A2',
                           hovertemplate="%{x}<br>下单ROI区间: %{text}<extra></extra>"), secondary_y=True)
fig4.update_layout(title="大盘二级流量效果 (日均消耗 & 下单ROI，区间脱敏展示)", height=460, font=dict(size=10))
fig4.update_yaxes(title_text="日均消耗(万元，区间中值示意)", secondary_y=False)
fig4.update_yaxes(title_text="下单ROI(区间中值示意)", secondary_y=True)

fig1.write_html(os.path.join(OUT, "图1_出价结构对比.html"))
fig2.write_html(os.path.join(OUT, "图2_出价效果对比.html"))
fig3.write_html(os.path.join(OUT, "图3_恒好日趋势.html"))
fig4.write_html(os.path.join(OUT, "图4_流量效果.html"))

print("=== 图表已按恒好素材要求重新生成（大盘区间脱敏，客户A精确） ===")
