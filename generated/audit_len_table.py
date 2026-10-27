#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核对 04-正文格式规范.md §8.1 的篇幅表 vs 实测（口径：正文 `[一-鿿]`，切第一个 `## 一、` 之后）。"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
OTHERS = CONTENT / "others"

CJK = re.compile(r"[一-鿿]")


def count(n: int) -> int:
    for p in CONTENT.glob("第*.md"):
        m = re.match(r"第(\d+)章", p.name)
        if m and int(m.group(1)) == n:
            t = p.read_text(encoding="utf-8")
            i = t.find("## 一、")
            return len(CJK.findall(t[i:] if i >= 0 else t))
    return -1


def main() -> int:
    spec = (OTHERS / "04-正文格式规范.md").read_text(encoding="utf-8")
    claimed: dict[int, int] = {}
    for m in re.finditer(r"\b(\d{2}) \((\d{1,3}(?:,\d{3})*)\)", spec):
        claimed[int(m.group(1))] = int(m.group(2).replace(",", ""))
    real = {n: count(n) for n in range(1, 121)}
    diffs = []
    for n, c in sorted(claimed.items()):
        r = real.get(n, -1)
        if r < 0:
            continue
        if abs(r - c) > max(20, c * 0.02):
            diffs.append((n, c, r, r - c))
    print(f"§8.1 表内条目 {len(claimed)} 章；实测 120 章")
    print(f"总字数：表内求和 {sum(claimed.values()):,}；实测全档 {sum(real.values()):,}")
    print(f"偏差 >2% 的章：{len(diffs)}")
    for n, c, r, d in diffs:
        print(f"  第{n}章 表 {c:,} / 实测 {r:,} / 差 {d:+,}")
    print("\n表里没有、但正文已存在的章：",
          [f"{n} ({real[n]:,})" for n in sorted(real) if n not in claimed])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
