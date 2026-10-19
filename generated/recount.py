#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》正文篇幅实测（04-正文格式规范.md §8.1 口径）。

口径（照抄 §8.1）：[一-鿿] 计数，切第一个 '## 一、' 之后到文件末尾
（本书各章正文末尾即章末，无〔本章完〕标记），不含章标题与章节备注。

用法:
    python generated/recount.py          # 分档汇总 + 总计
    python generated/recount.py --table   # 输出 §8.1 的 Markdown 行
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
CJK = re.compile(r"[一-鿿]")

BANDS = [(3000, 3600), (3600, 4500), (4500, 5000), (5000, 5500), (5500, 7500)]


def count(p: Path) -> int:
    text = p.read_text(encoding="utf-8")
    m = re.search(r"^## 一、", text, re.M)
    body = text[m.start():] if m else ""
    body = body.split("## 章节备注", 1)[0]
    return len(CJK.findall(body))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m:
            rows.append((int(m.group(1)), count(p)))
    rows.sort()
    total = sum(c for _, c in rows)

    if "--table" in sys.argv:
        for n, c in rows:
            if n >= 87:
                print(f"| 第{n}章 | {c:,} |")
        return 0

    print(f"章节数：{len(rows)}   合计：{total:,}   均值：{total // len(rows):,}")
    print(f"最短：第{min(rows, key=lambda r: r[1])[0]}章 "
          f"{min(c for _, c in rows):,}   "
          f"最长：第{max(rows, key=lambda r: r[1])[0]}章 "
          f"{max(c for _, c in rows):,}")

    lo = [(n, c) for n, c in rows if c < 3000]
    print(f"\n< 3,000：{len(lo)} 章")
    print("  " + "、".join(f"{n} ({c:,})" for n, c in lo))
    for lo_b, hi_b in BANDS:
        band = [(n, c) for n, c in rows if lo_b <= c < hi_b]
        print(f"\n{lo_b:,}–{hi_b:,}：{len(band)} 章")
        print("  " + "、".join(f"{n} ({c:,})" for n, c in band))
    hi = [(n, c) for n, c in rows if c >= 7500]
    if hi:
        print(f"\n>= 7,500：{len(hi)} 章  " + "、".join(f"{n} ({c:,})" for n, c in hi))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
