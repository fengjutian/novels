#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打印各章的分段标题索引，供 `others/04-正文格式规范.md` §八 表格使用。

用法:
    python generated/sect_index.py            # 第 1 章起全部
    python generated/sect_index.py 97 116     # 只看这个区间的章
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
          "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13}
SEC_HEAD = re.compile(r"^## ([一二三四五六七八九十]+)、(.+)$", re.M)
CJK = re.compile(r"[一-鿿]")
PERSON_WORDS = ("他", "她", "我", "你")


def cn(s: str) -> int:
    if s in CN_NUM:
        return CN_NUM[s]
    if len(s) == 2 and s[0] == "十":
        return 10 + CN_NUM.get(s[1], -1)
    if len(s) == 3 and s[1] == "十":
        return CN_NUM.get(s[0], -1) * 10 + CN_NUM.get(s[2], -1)
    return -1


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = [int(a) for a in sys.argv[1:]]
    lo, hi = (args[0], args[-1]) if args else (1, 999)
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if not m:
            continue
        ch = int(m.group(1))
        if not (lo <= ch <= hi):
            continue
        text = p.read_text(encoding="utf-8")
        body = re.search(r"^## 一、", text, re.M)
        if not body:
            continue
        body = text[body.start():]
        secs = SEC_HEAD.findall(body)
        n = len(CJK.findall(body))
        titles = [t for _, t in secs]
        person = [t for t in titles if t[0] in PERSON_WORDS]
        print(f"| 第{ch}章 | {p.stem.split('章 ', 1)[1]} | {len(secs)} | {n} | "
              f"{'、'.join(person) if person else '—'} |")
        print(f"    标题：{' / '.join(f'{cn(a)}、{t}' for a, t in secs)}")


if __name__ == "__main__":
    main()
