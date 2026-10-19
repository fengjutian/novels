#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重算全档篇幅，生成 04-正文格式规范.md §8.1 的表格。

§8.1 自己写着："它是一张带日期的快照：新章落地后必须重跑脚本重算，
不得再手填。" 本脚本就是那个重算器。

口径（§8.1 原文）：[一-鿿] 计数，切第一个 `## 一、` 之后到文件末尾，
不含章标题与章节备注。

用法:
    python generated/gen_sect81.py          # 打印表格
    python generated/gen_sect81.py --check  # 与规范文档现值比对，报差异
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
SPEC = CONTENT / "others" / "04-正文格式规范.md"

CJK = re.compile(r"[一-鿿]")
BANDS = [(3000, "3,000 以下"), (3600, "3,000–3,600"), (4500, "3,600–4,500"),
         (5000, "4,500–5,000"), (5500, "5,000–5,500"), (7500, "5,500–7,500")]
BAND_LOWER = [3000, 3600, 4500, 5000, 5500, 7500]


def counts() -> dict[int, int]:
    out = {}
    for f in CONTENT.glob("*.md"):
        m = re.match(r"第(\d+)章", f.name)
        if not m:
            continue
        t = f.read_text(encoding="utf-8")
        i = t.find("## 一、")
        out[int(m.group(1))] = len(CJK.findall(t[i:] if i >= 0 else t))
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    data = counts()
    total = sum(data.values())
    n = len(data)
    print(f"全档 {n} 章，合计 {total:,} 字，均值 {total // n:,}")
    print()
    for idx, (_, label) in enumerate(BANDS):
        lo = 0 if idx == 0 else BAND_LOWER[idx - 1]
        hi = BAND_LOWER[idx]
        items = sorted((c, v) for c, v in data.items() if lo <= v < hi)
        if not items:
            continue
        print(f"| {label} | "
              + "、".join(f"{c:02d} ({v:,})" for c, v in items)
              + f" | {len(items)} 章 |")

    if "--check" in sys.argv:
        spec = SPEC.read_text(encoding="utf-8")
        m = re.findall(r"(\d{2,3}) \((\d[\d,]*)\)", spec)
        stale = []
        for ch, val in m:
            c, v = int(ch), int(val.replace(",", ""))
            if c in data and data[c] != v:
                stale.append((c, v, data[c]))
        if stale:
            print(f"\n规范文档里有 {len(stale)} 处与文件对不上：")
            for c, old, new in stale:
                print(f"  第{c}章 文档写 {old:,}  实测 {new:,}  差 {new - old:+,}")
        else:
            print("\n规范文档的数值与文件全部一致。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
