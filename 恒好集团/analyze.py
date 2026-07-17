# -*- coding: utf-8 -*-
# 原版(不脱敏)：大盘与客户A均展示真实绝对数值，用于对照分析。
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, json

BASE = "/Users/sumiyaliu/Documents/sumiya的AI小森林/公开/恒好集团"
OUT = os.path.join(BASE, "分析结果")
os.makedirs(OUT, exist_ok=True)

# ---------- 读取 ----------
df_big_bid = pd.read_csv(os.path.join(BASE, "大盘不同出价类型分析.csv"))
df_flow   = pd.read_csv(os.path.join(BASE, "大盘不同流量效果.csv"))
df_hh_bid = pd.read_csv(os.path.join(BASE, "恒好不同出嫁类型效果分析.csv"))
df_trend  = pd.read_csv(os.path.join(BASE, "恒好集团投放趋势.csv"))

def build_bid_table(df):
    rows=[]
    for _,r in df.iterrows():
        zt = r['广告智投类型(翻译后)']
        if pd.isna(zt) or str(zt) in ('整体','','nan'):
            rows.append({'分组':'整体','智投类型':'整体','自动出价':'-','浅层目标':'(汇总)','ROI目标':'-','是否ROI':'-',
                '消耗万':r['消耗(万元)'],'消耗占比%':r['消耗(万元)占比(%)'],'消耗环比%':r['消耗(万元)环比变化率(%)'],
                'CPM':r['竞价CPM(元)'],'CPM环比%':r['竞价CPM(元)环比变化率(%)'],'CTR%':r['ctr(%)'],'CTR环比%':r['ctr(%)环比变化率(%)'],
                'CVR%':r['浅层cvr(%)'],'CVR环比%':r['浅层cvr(%)环比变化率(%)'],'下单ROI':r['下单ROI'],'ROI环比%':r['下单ROI环比变化率(%)']})
            continue
        rows.append({'分组':str(r['广告智投类型(翻译后)']),'智投类型':str(r['广告智投类型(翻译后)']),
            '自动出价':str(r['自动出价类型(翻译后)']),'浅层目标':str(r['浅层优化目标(翻译后)']),
            'ROI目标':str(r['浅层-深层/ROI优化目标(翻译后)']),'是否ROI':str(r['是否ROI广告(翻译后)']),
            '消耗万':r['消耗(万元)'],'消耗占比%':r['消耗(万元)占比(%)'],'消耗环比%':r['消耗(万元)环比变化率(%)'],
            'CPM':r['竞价CPM(元)'],'CPM环比%':r['竞价CPM(元)环比变化率(%)'],'CTR%':r['ctr(%)'],'CTR环比%':r['ctr(%)环比变化率(%)'],
            'CVR%':r['浅层cvr(%)'],'CVR环比%':r['浅层cvr(%)环比变化率(%)'],'下单ROI':r['下单ROI'],'ROI环比%':r['下单ROI环比变化率(%)']})
    return pd.DataFrame(rows)

bid_big = build_bid_table(df_big_bid)
bid_hh  = build_bid_table(df_hh_bid)

# 整体行
big_overall = df_big_bid[df_big_bid['广告智投类型(翻译后)'].isna() | (df_big_bid['广告智投类型(翻译后)'].astype(str).isin(['整体','nan','']))].iloc[0]
hh_overall  = df_hh_bid[df_hh_bid['广告智投类型(翻译后)'].isna() | (df_hh_bid['广告智投类型(翻译后)'].astype(str).isin(['整体','nan','']))].iloc[0]

# ---------- 流量 ----------
flow = df_flow[df_flow['二级流量(仅拆分MP)']!='整体'].copy()
flow_disp = flow[['二级流量(仅拆分MP)','日均消耗(万元)','日均消耗(万元)占比(%)','下单ROI','下单单价(元)','ctr(%)','竞价CPM(元)','浅层cvr(%)']].copy()
flow_disp.columns=['二级流量','日均消耗万','消耗占比%','下单ROI','下单单价元','CTR%','CPM','CVR%']

# ---------- 恒好日趋势 ----------
trend = df_trend.copy()
trend['时间']=pd.to_datetime(trend['时间'])

# ===================== 可视化(原版，不脱敏) =====================
# 图1: 出价方式消耗结构占比(占比本身即比例)
fig1 = make_subplots(rows=1, cols=2, specs=[[{"type":"domain"},{"type":"domain"}]],
                     subplot_titles=("客户A-各出价方式消耗占比","大盘-各出价方式消耗占比"))
labels_hh  = bid_hh[bid_hh['分组']!='整体']['智投类型']+' / '+bid_hh[bid_hh['分组']!='整体']['自动出价']
vals_hh   = bid_hh[bid_hh['分组']!='整体']['消耗占比%'].fillna(0)
labels_big = bid_big[bid_big['分组']!='整体']['智投类型']+' / '+bid_big[bid_big['分组']!='整体']['自动出价']
vals_big  = bid_big[bid_big['分组']!='整体']['消耗占比%'].fillna(0)
fig1.add_trace(go.Pie(labels=labels_hh, values=vals_hh, hole=.4, title='客户A'),1,1)
fig1.add_trace(go.Pie(labels=labels_big, values=vals_big, hole=.4, title='大盘'),1,2)
fig1.update_layout(title="出价方式消耗结构占比对比", height=420, font=dict(size=11))

# 图2: 出价方式效果对比(大盘 vs 客户A，真实绝对数值)
cats=['非智投/普通/下单','非智投/投放端自动出价/下单','非智投/普通/下单ROI']
def val(df_map,cat):
    for (zt,zd),r in df_map.items():
        roi = r.get('是否ROI','')
        if cat=='非智投/普通/下单' and zt=='非智投广告' and zd=='普通' and roi!='是': return r
        if cat=='非智投/投放端自动出价/下单' and zt=='非智投广告' and zd=='投放端自动出价': return r
        if cat=='非智投/普通/下单ROI' and zt=='非智投广告' and zd=='普通' and roi=='是': return r
    return None
b_map={(r['智投类型'],r['自动出价']):r for _,r in bid_big[bid_big['分组']!='整体'].iterrows()}
h_map={(r['智投类型'],r['自动出价']):r for _,r in bid_hh[bid_hh['分组']!='整体'].iterrows()}
b_vals=[val(b_map,c) for c in cats]; h_vals=[val(h_map,c) for c in cats]
def s(lst,col): return [ (r[col] if r is not None else 0) for r in lst]
b_c,s_c = s(b_vals,'CTR%'), s(h_vals,'CTR%')
b_v,s_v = s(b_vals,'CVR%'), s(h_vals,'CVR%')
b_r,s_r = s(b_vals,'下单ROI'), s(h_vals,'下单ROI')
fig2 = make_subplots(rows=1, cols=3, subplot_titles=("CTR (%)","浅层CVR (%)","下单ROI"))
fig2.add_trace(go.Bar(name='大盘',x=cats,y=b_c,marker_color='#4C78A8'),1,1)
fig2.add_trace(go.Bar(name='客户A',x=cats,y=s_c,marker_color='#F58518'),1,1)
fig2.add_trace(go.Bar(name='大盘',x=cats,y=b_v,marker_color='#4C78A8'),1,2)
fig2.add_trace(go.Bar(name='客户A',x=cats,y=s_v,marker_color='#F58518'),1,2)
fig2.add_trace(go.Bar(name='大盘',x=cats,y=b_r,marker_color='#4C78A8'),1,3)
fig2.add_trace(go.Bar(name='客户A',x=cats,y=s_r,marker_color='#F58518'),1,3)
fig2.update_layout(title="出价方式效果对比 (大盘 vs 客户A)",barmode='group',height=420,font=dict(size=10))

# 图3: 恒好日趋势
fig3 = make_subplots(specs=[[{"secondary_y": True}]])
fig3.add_trace(go.Bar(x=trend['时间'],y=trend['消耗(万元)'],name='消耗(万元)',marker_color='#72B7B2'),secondary_y=False)
fig3.add_trace(go.Scatter(x=trend['时间'],y=trend['下单ROI'],name='下单ROI',mode='lines+markers',marker_color='#E45756'),secondary_y=True)
fig3.update_layout(title="客户A(恒好)投放日趋势 (消耗 & 下单ROI)",height=420,font=dict(size=11))
fig3.update_yaxes(title_text="消耗(万元)",secondary_y=False)
fig3.update_yaxes(title_text="下单ROI",secondary_y=True)

# 图4: 大盘二级流量效果(真实绝对数值)
fig4 = make_subplots(specs=[[{"secondary_y": True}]])
fig4.add_trace(go.Bar(x=flow_disp['二级流量'],y=flow_disp['日均消耗万'],name='日均消耗(万元)',marker_color='#54A24B'),secondary_y=False)
fig4.add_trace(go.Scatter(x=flow_disp['二级流量'],y=flow_disp['下单ROI'],name='下单ROI',mode='lines+markers',marker_color='#B279A2'),secondary_y=True)
fig4.update_layout(title="大盘二级流量效果 (日均消耗 & 下单ROI)",height=420,font=dict(size=10))
fig4.update_yaxes(title_text="日均消耗(万元)",secondary_y=False)
fig4.update_yaxes(title_text="下单ROI",secondary_y=True)

fig1.write_html(os.path.join(OUT,"图1_出价结构对比.html"))
fig2.write_html(os.path.join(OUT,"图2_出价效果对比.html"))
fig3.write_html(os.path.join(OUT,"图3_恒好日趋势.html"))
fig4.write_html(os.path.join(OUT,"图4_流量效果.html"))

# ===================== Excel(原版，不脱敏) =====================
bid_big_m = bid_big[bid_big['分组']!='整体'].copy()
bid_hh_m  = bid_hh[bid_hh['分组']!='整体'].copy()
def to_mask(df_big_sub, df_hh_sub):
    rows=[]
    for _,hr in df_hh_sub.iterrows():
        zt, zd = hr['智投类型'], hr['自动出价']
        br = df_big_sub[(df_big_sub['智投类型']==zt)&(df_big_sub['自动出价']==zd)]
        br = br.iloc[0] if len(br) else None
        row={'出价方式':f"{zt}/{zd}"}
        row['客户A_消耗占比%']=hr['消耗占比%']
        row['大盘_消耗占比%']= br['消耗占比%'] if br is not None else np.nan
        for c,lab in [('CTR%','CTR'),('CVR%','CVR'),('下单ROI','下单ROI'),('CPM','CPM')]:
            row[f'客户A_{lab}']=hr[c]
            row[f'大盘_{lab}']= br[c] if br is not None else np.nan
        rows.append(row)
    return pd.DataFrame(rows)

mask_bid = to_mask(bid_big_m, bid_hh_m)

mask_overall = pd.DataFrame([
    {'主体':'客户A(恒好集团)','消耗(万元)':hh_overall['消耗(万元)'],'竞价CPM(元)':hh_overall['竞价CPM(元)'],'CTR(%)':hh_overall['ctr(%)'],'浅层CVR(%)':hh_overall['浅层cvr(%)'],'下单ROI':hh_overall['下单ROI']},
    {'主体':'大盘整体','消耗(万元)':big_overall['消耗(万元)'],'竞价CPM(元)':big_overall['竞价CPM(元)'],'CTR(%)':big_overall['ctr(%)'],'浅层CVR(%)':big_overall['浅层cvr(%)'],'下单ROI':big_overall['下单ROI']},
])

flow_mask = flow_disp[['二级流量','消耗占比%','下单ROI','下单单价元','CTR%','CPM','CVR%']].copy()
flow_mask.columns=['二级流量','消耗占比%','下单ROI','下单单价元','CTR%','CPM','CVR%']

with pd.ExcelWriter(os.path.join(OUT,"恒好集团出价与流量分析_脱敏对照.xlsx"), engine='openpyxl') as xl:
    bid_big.to_excel(xl,'大盘-出价方式明细',index=False)
    bid_hh.to_excel(xl,'客户A-出价方式明细',index=False)
    mask_bid.to_excel(xl,'对照-出价方式',index=False)
    trend.to_excel(xl,'客户A-投放日趋势',index=False)
    mask_overall.to_excel(xl,'对照-主体',index=False)
    flow_mask.to_excel(xl,'大盘-二级流量效果',index=False)

# summary(供报告，含真实数值)
summary = {
 'hh_overall':{'cost':hh_overall['消耗(万元)'],'cpm':hh_overall['竞价CPM(元)'],'ctr':hh_overall['ctr(%)'],'cvr':hh_overall['浅层cvr(%)'],'roi':hh_overall['下单ROI']},
 'big_overall':{'cost':big_overall['消耗(万元)'],'cpm':big_overall['竞价CPM(元)'],'ctr':big_overall['ctr(%)'],'cvr':big_overall['浅层cvr(%)'],'roi':big_overall['下单ROI']},
 'hh_cost_share':hh_overall['消耗(万元)']/big_overall['消耗(万元)']*100,
 'mask_bid':mask_bid.to_dict('records'),
 'flow_mask':flow_mask.to_dict('records'),
}
with open(os.path.join(OUT,"summary.json"),'w',encoding='utf-8') as f:
    json.dump(summary,f,ensure_ascii=False,indent=2,default=str)

print("=== DONE (原版·不脱敏) ===")
print(f"客户A消耗: {hh_overall['消耗(万元)']:.1f}万 | 大盘消耗: {big_overall['消耗(万元)']:.1f}万 | 占比: {hh_overall['消耗(万元)']/big_overall['消耗(万元)']*100:.1f}%")
print("输出:", OUT)
