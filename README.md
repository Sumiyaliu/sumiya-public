# 公开站点

> 这里放对外公开的 HTML 报告 / 案例 / 创意双周报等。

**访问地址**：<https://Sumiyaliu.github.io/sumiya-public/>

## 目录

- `index.html` — 门户页（站点首页，**自动生成**）
- `build_index.py` — 自动构建脚本
- `creative-biweekly-report.html` — 传统滋补 & 保健食品创意双周报

## 发布新报告的标准流程

```bash
# 1. 把 HTML 拖到本目录（用英文文件名，如 report-2026-07.html）
# 2. 在 HTML 顶部加一段 summary 注释（可选但推荐）
cat my-report.html | head -3
#   <!DOCTYPE html>
#   <!-- summary: 这份报告讲了什么（一句话） -->
#   <html>...

# 3. 跑脚本，重新生成门户页
python3 build_index.py

# 4. 提交 + 推送
git add . && git commit -m "update: 新增 xxx 报告" && git push

# 5. 1 分钟后 GitHub Pages 自动部署生效
```

## build_index.py 提取规则

| 字段 | 来源 | 优先级 |
|---|---|---|
| 标题 | `<title>` 或 文件名（kebab→Title） | `<title>` 优先 |
| 描述 | `<!-- summary: ... -->` → `<meta name="description">` → body 前 120 字 | summary 注释优先 |
| 日期 | 文件 mtime | — |
| 标签 | 文件名关键词推断 | — |

## 命名规范

- HTML 文件名用**英文 / 拼音**（如 `case-xxx.html`、`report-2026-07.html`）
- 描述想自定义：在 HTML 顶部加 `<!-- summary: 一句话描述 -->`

## 注意事项

- 不放客户名 / 投放数据 / 未脱敏内容
- HTML 引用的图片放在同目录的相对路径下
- 仓库是 Public，发内容前请过一遍敏感词
