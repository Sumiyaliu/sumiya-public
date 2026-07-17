# 案例纸 1440 横版版式规范

本文档说明 `assets/template.html` 模板的版式结构、视觉规范与数据填充约定，便于在产出同款风格的"能力升级 / 投放案例 / 业务介绍"单页时严格遵循。

## 画布

- 宽度固定 `1440px`，最小高 `900px`，外层 `.page` 圆角 18px，带渐变背景与左右上下两个径向光晕。
- 字体优先 PingFang SC / 微软雅黑。主色：深蓝 `#1e3a8a`，主蓝 `#2563eb`，青 `#06b6d4`，绿 `#10b981`，警示红 `#dc2626`，强调黄 `#fde68a`。
- 整页采用左右两列（`grid-template-columns: 1fr 1.18fr`），右列略宽以容纳搭建步骤。

## 顶部 Header

- 渐变背景：`linear-gradient(135deg, #1e3a8a, #2563eb, #06b6d4)`。
- 左右各一个磨砂胶囊 `.badge`，正中 `<h1>` 主标题。
- 标题中的关键数字 / 短语用 `<span class="hl">` 包裹，会变为高亮黄 `#fde68a`。同一标题可放多个 `hl`（如「+4倍」「+7.5万/天」）。

## 主体两列布局

### 左列（建议顺序）

1. **Section 1 · 能力介绍**
   - `.intro-text`：蓝底卡片，一句话概念定义。
   - `.apply-text`：黄底卡片，写明"适用客户/适用条件"，左侧带 `.apply-tag` 标签。
   - `.compare`：升级前 / 箭头 / 升级后 三栏对比卡。
   - `.alert`：底部黄色虚线提示框，写注意事项。

2. **Section 2 · 行业投放案例**
   - `.case-bg-row`：左侧若干张直播间/产品截图缩略图（`.case-bg`，高 ≈210px），右侧 `.case-side` 写背景与痛点。
   - 图片数量改变时，需同步调整 `.case-bg-row` 的 `grid-template-columns`（92px ×N + 1fr）。
   - `.pain-list`：红底卡片列出痛点，每条用「（1）（2）（3）」编号，关键词用 `<b>` 加粗。
   - `.highlight-title`：左侧蓝色短竖条 + 加粗标题，用于章节中的小节标题。
   - `.chart-card`：嵌入 Chart.js 折线图，展示消耗 / 起量趋势。
   - `.kpi-grid`：3×2 的 6 个 KPI 卡片。`.kpi .num` 提供颜色修饰类 `red / green / orange / purple / cyan`，副单位用 `.unit`。

### 右列（建议顺序）

3. **Section 3 · 如何搭建**
   - 由若干 `.step-block` 组成，每个 `.step-head` 带 `.step-tag`（橙红渐变）或 `.step-tag.blue`（蓝青渐变）。
   - 步骤一常包含多张子步骤截图，使用 `.substeps > .substep`（左 220px 标题 + 右截图）。
   - 步骤二常并排两张说明图，使用 `.step2-imgs`（两列）+ `.step2-img-card`。
   - `.step2-info ul li`：蓝色三角形项目符。

4. **Section 4 · 海量扶持 / 资源申请**
   - 使用 `.support-block`（暖橙黄背景），右侧带 `.qrcode-box` 二维码。
   - 每条 `.support-item` 左侧固定宽度橙红标签 `.lbl`，右侧文案。常见项：扶持时间、提报方式、扶持要求。

## 图表（Chart.js）

- 模板底部 `<script>` 中以 Chart.js 渲染折线图，两条数据集（总消耗 + 能力消耗），自带 `datalabels-lite` 插件在节点上方绘制数值标签。
- 修改时只需替换 `labels`、`datasets[*].data` 与 `datasets[*].label`。颜色保持 `#2563eb` / `#10b981` 双色。
- 图例中如需引用某个能力名，使用中文双引号包裹（如 `"直播表达多品聚合"消耗（万元）`）。

## 图片资源约定

- 模板默认引用 `images/` 同级目录下的图片（`img1.png` ~ `img7.png`、`img4a.png`、`img4b.png`、`qrcode.png`）。
- 套用模板时，应在输出 HTML 同级建立 `images/` 文件夹，并按相同文件名放置或更新引用路径。

## 文案与强调规则

- 数字 / 倍数 / 涨幅在标题中用 `<span class="hl">`；正文中用 `<b style="color:#dc2626;">`（重点红）或保持 `<b>`（深蓝默认）。
- 段落字号区间：正文 12.5–13px，副标题 13.5–14px，section 标题 17px，主标题 24px。
- 关键短句尽量做"标签 + 内容"结构，避免长段落。
