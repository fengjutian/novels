#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 117–120 章节标题收敛。

两处改动，均只动标题、不动正文：

1. 第 117 章 第十一节「他不在名单上」→「不在名单上」。
   依据 `04-正文格式规范.md` §2.5 规则一：全章最多一节标题带人称。
   本章第十二节「没有人派他去」保留——它是本章的信息转折点
   （名册末行不在体系名单上，本期无派遣记录）。
   原标题带「他」，第十二节也带「他」，一章两处，超标。

2. 第 118 章 第四节「第四款不管这里」→「没有第四款」。
   依据：方案正本只有三条（分工／通联／关闭），附页一张写防御阈值，
   **没有第四款**（第 106 章、第 118 章正文均如此）。原标题断言了一个
   正本里不存在的条款，与本节正文第一行「没有第四款」直接矛盾。
   改为正文原话，同时保留「无条款可管塌口」这层意思。

用法: python generated/fix_titles_117_120.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"

FIXES = [
    (117, "## 十一、他不在名单上", "## 十一、不在名单上"),
    (118, "## 四、第四款不管这里", "## 四、没有第四款"),
]


def chapter_path(ch: int) -> Path | None:
    for pat in (f"第{ch:02d}章*.md", f"第{ch}章*.md"):
        hits = list(CONTENT.glob(pat))
        if hits:
            return hits[0]
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    for ch, old, new in FIXES:
        p = chapter_path(ch)
        if p is None:
            print(f"[FAIL] ch{ch}: 找不到文件")
            return 1
        raw = p.read_bytes()
        text = raw.decode("utf-8")
        n = text.count(old + "\n")
        if n != 1:
            print(f"[FAIL] ch{ch}: {old!r} 命中 {n} 次（应为 1）")
            return 1
        text = text.replace(old + "\n", new + "\n")
        p.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"[ OK ] ch{ch}: {old} -> {new}")
    print("\n--- 共替换 %d 条节标题 ---" % len(FIXES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
