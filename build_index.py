#!/usr/bin/env python3
"""
build_index.py — 扫描当前目录的 HTML 文件，自动生成 index.html 门户页

使用流程：
    1. 把 HTML 拖到本目录（建议英文文件名）
    2. python3 build_index.py
    3. git add . && git commit -m "update" && git push

提取规则（按优先级）：
    标题:  <title> → 文件名 kebab-case 转 Title Case
    描述:  <meta name="description"> → body 文本前 120 字
    日期:  文件 mtime
    标签:  从文件名关键词推断
"""
import re
import html
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).parent.resolve()
EXCLUDE = {"index.html"}


def kebab_to_title(name: str) -> str:
    """kebab-case 或 snake_case → Title Case"""
    return " ".join(
        w.capitalize() for w in name.replace("_", "-").split("-") if w
    )


def extract_meta(content: str) -> tuple[str, str]:
    """
    提取 <title> 和描述。
    描述优先级: <!-- summary: ... --> > <meta name='description'> > 留空走 fallback
    """
    title_match = re.search(
        r"<title[^>]*>(.*?)</title>", content, re.DOTALL | re.IGNORECASE
    )
    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
        content,
        re.IGNORECASE,
    )
    summary_match = re.search(
        r"<!--\s*summary\s*:\s*(.+?)\s*-->", content, re.IGNORECASE | re.DOTALL
    )
    title = title_match.group(1).strip() if title_match else ""
    if summary_match:
        desc = summary_match.group(1).strip()
    elif desc_match:
        desc = desc_match.group(1).strip()
    else:
        desc = ""
    return title, desc


def fallback_desc(content: str) -> str:
    """从 body 提取前 120 字作为描述"""
    m = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    text = re.sub(r"<[^>]+>", " ", m.group(1))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 120:
        text = text[:120] + "…"
    return text


def guess_tags(filename: str) -> list[str]:
    """从文件名启发式推断标签"""
    tags = []
    rules = [
        ("双周报", ["双周报", "biweekly", "weekly"]),
        ("案例", ["案例", "case"]),
        ("复盘", ["复盘", "review"]),
        ("创意素材", ["素材", "creative"]),
        ("行业洞察", ["行业", "industry"]),
        ("诊断", ["诊断", "diagnose"]),
        ("CID 分析", ["cid"]),
        ("投放指南", ["智投", "guide"]),
    ]
    name_lower = filename.lower()
    for tag, keywords in rules:
        if any(k in filename or k in name_lower for k in keywords):
            tags.append(tag)
    if not tags:
        tags.append("公开")
    return tags


def collect_htmls() -> list[dict]:
    """扫描目录，提取每份 HTML 的元信息"""
    items = []
    for f in sorted(HERE.glob("*.html")):
        if f.name in EXCLUDE:
            continue
        stat = f.stat()
        content = f.read_text(encoding="utf-8", errors="ignore")
        title, desc = extract_meta(content)
        filename = f.stem
        display_title = (
            title
            if (title and title.lower() != filename.lower())
            else kebab_to_title(filename)
        )
        if not desc:
            desc = fallback_desc(content)
        if not desc:
            desc = f"文件 {f.name}（{stat.st_size // 1024} KB）"
        date_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
        items.append(
            {
                "filename": f.name,
                "title": display_title,
                "desc": desc,
                "date": date_str,
                "tags": guess_tags(filename),
                "mtime": stat.st_mtime,
            }
        )
    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items


def render_cards(items: list[dict]) -> str:
    parts = []
    for h in items:
        tags_html = "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in h["tags"]
        )
        date_tag = f'<span class="tag">{h["date"]}</span>'
        parts.append(
            f'\n    <a class="card" href="{html.escape(h["filename"])}">\n'
            f"      <h2>{html.escape(h['title'])}</h2>\n"
            f"      <p>{html.escape(h['desc'])}</p>\n"
            f"      {date_tag}{tags_html}\n"
            f"    </a>"
        )
    return "".join(parts) if parts else '<p class="empty">还没有公开内容，先把 HTML 拖进来再跑一次脚本。</p>'


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sumiya 公开案例 / 创意双周报</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      min-height: 100vh;
      padding: 40px 20px;
      color: #2c3e50;
    }
    .container { max-width: 800px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 50px; }
    h1 { font-size: 2.2em; margin-bottom: 8px; color: #1a2a3a; }
    .subtitle { color: #6b7c8d; font-size: 1em; }
    .empty { text-align: center; color: #95a5a6; padding: 60px 20px; background: white; border-radius: 12px; }
    .card {
      background: white;
      border-radius: 12px;
      padding: 24px 28px;
      margin-bottom: 16px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
      transition: transform 0.2s, box-shadow 0.2s;
      text-decoration: none;
      color: inherit;
      display: block;
    }
    .card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .card h2 { font-size: 1.3em; margin-bottom: 8px; color: #2c3e50; }
    .card p { color: #6b7c8d; font-size: 0.95em; line-height: 1.6; }
    .tag {
      display: inline-block;
      background: #e8f4f8;
      color: #2980b9;
      padding: 2px 10px;
      border-radius: 4px;
      font-size: 0.8em;
      margin-right: 6px;
      margin-top: 8px;
    }
    footer {
      text-align: center;
      color: #95a5a6;
      font-size: 0.85em;
      margin-top: 50px;
    }
    footer a { color: #2980b9; text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Sumiya 公开站点</h1>
      <p class="subtitle">广告创意 / 行业洞察 / 公开案例</p>
    </header>

__CARDS__

    <footer>
      <p>Hosted on <a href="https://github.com/Sumiyaliu/sumiya-public">GitHub Pages</a> · 最后更新 __BUILD_TIME__</p>
    </footer>
  </div>
</body>
</html>
"""


def main():
    items = collect_htmls()
    cards = render_cards(items)
    index_html = (
        INDEX_TEMPLATE.replace("__CARDS__", cards)
        .replace("__BUILD_TIME__", datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    out = HERE / "index.html"
    out.write_text(index_html, encoding="utf-8")
    print(f"✓ 已生成 index.html（{len(items)} 个卡片）")
    for h in items:
        print(f"  - {h['filename']:<40s}  →  {h['title']}")


if __name__ == "__main__":
    main()
