# 公开站点

> 这里放对外公开的 HTML 报告 / 案例 / 创意双周报等。

**访问地址**：<https://Sumiyaliu.github.io/sumiya-public/>

## 目录

- `传统滋补百宝箱3.0.html` — 传统滋补投放百宝箱 V3.0（保底版）
- `case-paper-1440/` — 1440 横版标杆案例纸内页集
- `sync_public.py` — 工作区白名单同步脚本
- `.public_whitelist` — 公开站白名单配置

## 发布新报告的标准流程

```bash
# 1. 把 HTML 拖到本目录
# 2. 提交 + 推送
git add . && git commit -m "update: 新增 xxx 报告" && git push

# 3. 1 分钟后 GitHub Pages 自动部署生效
```

## 注意事项

- 不放客户名 / 投放数据 / 未脱敏内容
- HTML 引用的图片放在同目录的相对路径下
- 仓库是 Public，发内容前请过一遍敏感词
