#!/usr/bin/env python3
"""
sync_public.py — 工作区白名单同步到公开站

设计原则：
1. 公开站目录完全独立于工作区（不污染、不上传工作区任何东西）
2. 白名单制：只复制你点名的文件夹，其它一概不动
3. 文件名/扩展名黑名单在复制时再过滤一次
4. 默认排除数据文件：.csv .xlsx .json .pdf .docx .pptx 等

用法：
  python3 sync_public.py --dry      # 试运行，看会复制什么
  python3 sync_public.py            # 实际同步
  python3 sync_public.py --status   # 看当前配置状态
"""
import os
import shutil
import sys
from pathlib import Path

# ── 路径配置 ──────────────────────────────────
# 工作区根目录（要从中复制内容的源）
WORKSPACE = Path("/Users/sumiyaliu/Documents/sumiya的AI小森林").resolve()

# 公开站根目录 = 本脚本所在目录（自包含，可放任何位置）
PUBLIC_DIR = Path(__file__).parent.resolve()
WHITELIST_FILE = PUBLIC_DIR / ".public_whitelist"

# ── 默认黑名单（即使在白名单文件夹内，也跳过这些文件）───
# 扩展名黑名单：所有数据/文档/压缩包
DEFAULT_DENY_EXT = {
    ".csv", ".xlsx", ".xls", ".numbers",  # 表格数据
    ".json", ".yaml", ".yml", ".toml",    # 结构化数据
    ".docx", ".doc", ".pptx", ".key",     # Office 文档
    ".pdf", ".zip", ".tar", ".gz", ".7z", # 压缩/文档
    ".sql", ".db", ".sqlite",             # 数据库
    ".env",
}
# 文件名黑名单：明确不该公开的脚本和元数据
DEFAULT_DENY_NAME = {
    ".DS_Store", "Thumbs.db",
    "deploy.sh", "build.py", "sync.sh", "cli.sh",
}
# 隐藏文件/目录 / 以 _ 开头的（约定为私有）
DEFAULT_DENY_PREFIX = {".", "_"}


def read_list(path: Path) -> list:
    """读取每行一项的列表，跳过 # 注释和空行"""
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        items.append(line)
    return items


def is_denied(name: str) -> bool:
    if any(name.startswith(p) for p in DEFAULT_DENY_PREFIX):
        return True
    ext = os.path.splitext(name)[1].lower()
    if ext in DEFAULT_DENY_EXT:
        return True
    if name in DEFAULT_DENY_NAME:
        return True
    return False


# ── 同步主流程 ──────────────────────────────────
def sync(dry: bool = False):
    whitelist = read_list(WHITELIST_FILE)
    if not whitelist:
        print("⚠️  白名单为空，请先编辑 .public_whitelist 填入要公开的文件夹")
        print(f"   路径：{WHITELIST_FILE}")
        return

    if not dry:
        # 清空公开站后重建（避免遗留过期文件）
        if PUBLIC_DIR.exists():
            for item in PUBLIC_DIR.iterdir():
                if item.name in {".git", "sync_public.py", ".public_whitelist", "README.md"}:
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    else:
        print("🔍 试运行模式（不会真的复制文件）\n")

    copied_folders = 0
    copied_files = 0
    skipped_folders = 0

    for rel in whitelist:
        src = WORKSPACE / rel
        if not src.exists():
            print(f"   ⚠️  跳过（不存在）: {rel}")
            skipped_folders += 1
            continue
        if not src.is_dir():
            print(f"   ⚠️  跳过（非目录）: {rel}")
            skipped_folders += 1
            continue

        # 统计要复制的文件数
        file_count = sum(1 for f in src.rglob("*")
                         if f.is_file() and not is_denied(f.name))

        if dry:
            print(f"   📁 将复制: {rel}  ({file_count} 个文件)")
            copied_folders += 1
            continue

        dst = PUBLIC_DIR / rel
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.rglob("*"):
            if f.is_dir():
                continue
            if is_denied(f.name):
                continue
            target = dst / f.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
            copied_files += 1
        print(f"   ✓ {rel}  ({file_count} 个文件)")

    print(f"\n{'试运行' if dry else '同步'}完成：{copied_folders} 个文件夹已处理，{skipped_folders} 个跳过"
          + (f"，共复制 {copied_files} 个文件" if not dry else ""))

    if not dry:
        print(f"\n→ 公开站位置：{PUBLIC_DIR}")
        print("→ 下一步：")
        print("   1. cd ~/Sites/sumiya-public")
        print("   2. git init && git add . && git commit -m 'init'")
        print("   3. 在 GitHub 建仓后 git push")


if __name__ == "__main__":
    if "--dry" in sys.argv:
        sync(dry=True)
    elif "--status" in sys.argv:
        print(f"工作区：  {WORKSPACE}")
        print(f"公开站：  {PUBLIC_DIR}  {'✓ 已建立' if PUBLIC_DIR.exists() else '✗ 未建立'}")
        wl = read_list(WHITELIST_FILE)
        print(f"\n白名单（{len(wl)} 项）：")
        if wl:
            for x in wl:
                print(f"  • {x}")
        else:
            print("  （空，请编辑 .public_whitelist）")
    else:
        sync(dry=False)
