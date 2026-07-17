# 公开站 · 使用说明

工作区里有些内容想分享到公网（GitHub Pages），有些不能。
这个目录是**独立于工作区**的"公开站"，只同步白名单内的文件夹。

## 三个原则

1. **白名单制**：只复制你点名的文件夹（`.public_whitelist`），其它一概不动
2. **黑名单再过滤**：复制时跳过 `.csv` `.xlsx` `.json` `.pdf` `.docx` 等数据/文档文件
3. **完全独立**：这个目录可以单独 `git init`，**不会**把工作区任何其它东西带上去

## 标准流程

### 第 1 步：编辑白名单
打开 `.public_whitelist`，把想公开的文件夹前的 `#` 去掉。

### 第 2 步：试运行
```bash
python3 sync_public.py --dry
```
列出哪些文件夹、几个文件会被复制。**不会真的复制**。

### 第 3 步：实际同步
```bash
python3 sync_public.py
```
把白名单内的文件夹复制到本目录。

### 第 4 步：首次推到 GitHub
```bash
cd ~/Sites/sumiya-public
git init
git add .
git commit -m "init: 公开站 v1"
```
然后去 https://github.com/new 建一个仓库（建议 Public），再：
```bash
git remote add origin https://github.com/你的用户名/你的仓库.git
git branch -M main
git push -u origin main
```
最后在 GitHub 仓库页 → **Settings** → **Pages** → Source 选 `main` / `(root)` → **Save**。
1-2 分钟后即可访问 `https://你的用户名.github.io/你的仓库/`

### 第 5 步：日常更新
```bash
cd ~/Sites/sumiya-public
python3 sync_public.py     # 重新同步
git add .
git commit -m "update: ..."
git push                   # 1-2 分钟后 GitHub Pages 自动更新
```

## 查看当前状态
```bash
python3 sync_public.py --status
```

## 重要提醒

- 复制前**先看一遍每个文件夹的内容**，确认没有客户名、内部代号、未脱敏数据
- 复制后**先在本地打开 HTML 看看**，确认没有引用工作区路径的图片
- HTML 里引用图片请用**相对路径**（如 `./img/banner.png`），不要用 `/Users/.../...`
- 推送前**先检查 diff**：`git status` 和 `git diff --stat`
