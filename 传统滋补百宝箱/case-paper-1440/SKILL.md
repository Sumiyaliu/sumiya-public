---
name: case-paper-1440
description: Generate a 1440px-wide single-page Chinese "案例纸 / 能力升级介绍" HTML using the bundled template. Use this skill when the user asks to produce a horizontal case study / capability launch / industry showcase one-pager in the style of `case.html`, with sections like 能力介绍 / 行业案例 / 搭建步骤 / 海量扶持. Trigger on requests such as "做一张案例纸"、"生成能力升级介绍页"、"按这个版式再出一份"、"输出 1440 横版案例 HTML"。
---

# 案例纸 1440 横版生成器

## Overview

Produce a polished 1440px-wide horizontal single-page HTML (案例纸) covering a capability upgrade or industry case study. The skill bundles a fully-styled HTML template plus a layout specification, so output keeps consistent typography, color, KPI grid, Chart.js trend chart, and 海量扶持 area across runs.

## When To Use

Trigger this skill whenever the user requests any of the following:

- "做一张/生成一份案例纸 / 案例介绍页 / 能力升级介绍页"
- "按这个版式再出一份 …"、"参考 case.html 改成 …"
- Producing a horizontal one-pager with sections: 能力介绍、行业案例、搭建步骤、海量扶持 / 资源申请
- Output target is a single self-contained HTML file (1440 wide) that opens directly in a browser

Do NOT use this skill for: vertical posters / PPT / 长图文 / mobile-first pages.

## Workflow

### Step 1 · Collect the inputs

Ask only what is missing; reuse anything already provided. Required pieces:

1. **主标题**（含 1–2 个高亮数字短语，例如「+4倍」「+7.5万/天」）
2. **行业 / 客户类型**（写入右上角 badge）
3. **能力定义**（一句话概念）+ **适用客户/条件**
4. **升级前 vs 升级后**对比文案
5. **案例背景** + **痛点 N 条**（每条 1 行短句）
6. **趋势数据**：x 轴标签（如「第 1 天」…）+ 两条折线的数值数组
7. **6 个 KPI**：数值 + 单位 + 一行说明（颜色可选 red/green/orange/purple/cyan）
8. **搭建步骤**：步骤一子步骤（标题 + 截图文件名）、步骤二说明文案
9. **海量扶持**：时间、提报方式、扶持要求；可选二维码
10. **图片资源**：列出每张截图对应的本地文件路径或文件名

如果用户提供得不全，先用合理占位（标注 TODO），避免阻塞产出。

### Step 2 · Read the layout spec

Before writing, read `references/layout-spec.md` to align on grid, colors, class names, image grid column adjustment rules, and chart wiring details. Follow that spec strictly — do not invent new class names.

### Step 3 · Produce the HTML

1. Copy `assets/template.html` to the user's target path (default: workspace root, filename like `case.html` or what the user specifies).
2. Edit the copy in place using targeted replacements; do NOT rewrite the whole file.
3. Map collected inputs into the template:
   - Header `<h1>` 内的高亮数字用 `<span class="hl">…</span>`。
   - `.case-bg-row` 图片数量若 ≠ 2，需同步调整 CSS `grid-template-columns`（每张缩略图 92px，最后一列 1fr）。
   - 痛点条目放进 `.pain-list`，每条用 `<span class="pain-item">（n）…<b>关键词</b></span>`。
   - KPI 数字颜色通过 `.num` 上追加 `red / green / orange / purple / cyan` 任一类控制。
   - Chart.js 数据替换 `labels` 与两条 `datasets[*].data / label`，颜色与图例样式保持原状。
   - 步骤二标题随能力命名变化（例如「直播账户勾选商品聚合页」）。
   - 海量扶持中"提报方式"按客户要求落「主体名称 / 账户ID / 行业经理」等措辞。
4. 同步在输出文件旁建立或复用 `images/` 目录，放好引用的截图与二维码。

### Step 4 · Sanity check before delivery

确认以下要点后再交付：

- [ ] 标题里至少 1 处使用 `.hl` 高亮关键数字
- [ ] `.case-bg-row` 的 `grid-template-columns` 与实际图片数量一致
- [ ] 痛点条数与 `.pain-list` 中编号一致
- [ ] KPI 共 6 张，数值含 `.unit` 单位
- [ ] Chart.js 两条折线 label 用中文双引号引用能力名（如 `"…能力名"消耗（万元）`）
- [ ] 所有 `<img src="images/…">` 文件实际存在
- [ ] 文件 1440 宽度下能完整渲染，无横向滚动

## Resources

### assets/

- `assets/template.html` — 完整的样式 + 结构 + Chart.js 脚本模板。**始终复制后再改**，不要在原文件上编辑。模板自带 `<style>` 与示例数据，可作为"骨架"直接使用。

### references/

- `references/layout-spec.md` — 详细的版式规范：画布、配色、类名、栅格、图表与文案规则。**Step 2 必读**，编辑模板前对照确认。

模板内的图片引用路径为 `images/imgX.png`，套用时请同步准备同名图片或调整引用。
