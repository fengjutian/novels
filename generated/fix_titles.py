#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 97–116 章节标题收敛（`04-正文格式规范.md` §2.5 规则一：全章最多一节标题带人称）。

只做精确字符串替换，每条替换断言命中一次；写回时固定 UTF-8 无 BOM + LF。

用法: python generated/fix_titles.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"

# (章, 旧标题行, 新标题行)  —— 保留每章唯一的"信息转折点"人称标题，其余改成具体名词
FIXES = [
    # 第97章：保留「她划掉的那一句」（本章转折）
    (97, "## 九、她拒绝过的那一次", "## 九、那一次拒绝"),
    (97, "## 十、她要的那张纸", "## 十、那份原件"),
    # 第98章：保留「她带走的东西」
    (98, "## 二、她自己的设备", "## 二、自带的设备"),
    # 第99章：保留「她带出来的两页」
    (99, "## 十一、她烧掉的一页", "## 十一、烧掉的一页"),
    # 第100章：保留「她接了」
    (100, "## 五、她只看一遍", "## 五、只看一遍"),
    (100, "## 八、她不补", "## 八、不补"),
    # 第101章：保留「她签过的那一次」
    (101, "## 四、她回来晚了", "## 四、回来晚了"),
    # 第102章：保留「他签的是哪一段」
    (102, "## 九、他先问的是几号", "## 九、先问的是几号"),
    # 第103章：保留「她写完的」
    (103, "## 八、她自己的那一段", "## 八、自己那一段"),
    # 第104章：保留「他不能证明」
    (104, "## 五、他写的那一行", "## 五、写的那一行"),
    (104, "## 六、他自己写错的一处", "## 六、写错的一处"),
    # 第109章：保留「他没有回答」
    (109, "## 四、他自己写的那一行", "## 四、写的那一行"),
    (109, "## 十、他划掉了", "## 十、划掉的那一行"),
    (109, "## 十一、他再列一张", "## 十一、第二张表"),
    # 第110章：保留「她怕的不是这个」
    (110, "## 二、她进山", "## 二、进山"),
    # 第111章：保留「他说我判错了」
    (111, "## 一、他签过的那张表", "## 一、那张表"),
    (111, "## 十二、他的成本", "## 十二、两个成本"),
    # 第115章：保留「他没有出来」
    (115, "## 四、她出来了", "## 四、抱孩子的女人"),
    (115, "## 十一、他们出去了", "## 十一、出去的人"),
]


def chapter_path(ch: int) -> Path | None:
    for pat in (f"第{ch:02d}章*.md", f"第{ch}章*.md"):
        hits = list(CONTENT.glob(pat))
        if hits:
            return hits[0]
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    by_chapter: dict[int, list[tuple[str, str]]] = {}
    for ch, old, new in FIXES:
        by_chapter.setdefault(ch, []).append((old, new))

    total = 0
    for ch, pairs in sorted(by_chapter.items()):
        p = chapter_path(ch)
        if p is None:
            print(f"[FAIL] ch{ch}: 找不到文件")
            return 1
        raw = p.read_bytes()
        text = raw.decode("utf-8")
        for old, new in pairs:
            n = text.count(old + "\n")
            if n != 1:
                print(f"[FAIL] ch{ch}: {old!r} 命中 {n} 次（应为 1）")
                return 1
            text = text.replace(old + "\n", new + "\n")
            total += 1
        # 固定写回：UTF-8 无 BOM，LF
        p.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"[ OK ] ch{ch}: 替换 {len(pairs)} 条标题")
    print(f"\n--- 共替换 {total} 条节标题 ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
