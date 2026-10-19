#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""原文保全校验：扩写只许插入，不许删改。

**这个脚本是被一次真实事故逼出来的。**
2026-10-19 扩写第 77 章时，重写整章导致原文五段（"共有十九个"那一整组，
含 19／十八厘米／布纹三个关键细节）被静默删除。字数校验和新词法校验
**全部是绿的**——删掉的段落里有设定文件里的关键数字，
是新词法扫描查不出来的漏。

所以必须有一条独立的尺子：原文每一段是否还在。
判据按段落而非按行，因为折行不算改内容（§9.5：段内软换行等于空格）。

用法:
    python generated\verify_preserve.py            # 77-86
    python generated\verify_preserve.py 77 84
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"

# 本批开工前的最后一个提交 = 全部 10 章的原始压缩稿
BASELINE = "04c4477"


def norm(p: str) -> str:
    """归一化：删段内换行与多余空白，只比内容不比排版。"""
    return re.sub(r"\s+", "", p)


def body_of(t: str) -> str:
    i = t.find("## 一、")
    return t[i:] if i >= 0 else t


def path_of(ch: int) -> Path:
    for pat in (f"第{ch:02d}章*.md", f"第{ch}章*.md"):
        for f in CONTENT.glob(pat):
            return f
    raise SystemExit(f"找不到第{ch}章")


def git_show(rel: str, ref: str) -> str:
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], capture_output=True, cwd=ROOT)
    return r.stdout.decode("utf-8") if r.returncode == 0 else ""


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if a.isdigit()]
    chapters = sorted({int(a) for a in args}) or list(range(77, 87))

    total_missing = 0
    for ch in chapters:
        p = path_of(ch)
        rel = p.relative_to(ROOT).as_posix()
        old = git_show(rel, BASELINE)
        if not old:
            print(f"ch{ch:02d}: 基线 {BASELINE} 中无此文件，跳过")
            continue
        cur = norm(body_of(p.read_text(encoding="utf-8")))

        old_paras = [q.strip() for q in re.split(r"\n\s*\n", body_of(old)) if q.strip()]
        missing = []
        for q in old_paras:
            if q.startswith("## "):
                # 节标题：允许因长度不合规而被改名，只要求序号还在
                if norm(q) not in cur:
                    missing.append(q)
                continue
            if norm(q) not in cur:
                missing.append(q)

        if missing:
            total_missing += len(missing)
            print(f"ch{ch:02d} {p.name}: 丢失 {len(missing)}/{len(old_paras)} 段")
            for q in missing:
                print(f"      MISSING: {q[:70]}")
        else:
            print(f"ch{ch:02d} {p.name}: 原文 {len(old_paras)} 段全部保留")

    print()
    print("=" * 56)
    print(f"丢失段落合计: {total_missing}")
    print("=" * 56)
    return 1 if total_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
