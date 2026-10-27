#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正文里"X月X日，星期W"（汉字数词）与日历是否自洽。年份按 2025–2027 试，星期对不上的报出来。"""
import datetime
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
C = Path("D:/github/novels/content/chichao-beijing")
WD = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
      "十": 10, "十一": 11, "十二": 12}


def cn2int(s):
    if s in CN:
        return CN[s]
    if len(s) == 2 and s[0] == "十":
        return 10 + CN.get(s[1], 0)
    if len(s) == 3 and s[1] == "十":
        return CN.get(s[0], 0) * 10 + CN.get(s[2], 0)
    return None


pat = re.compile(r"([一二三四五六七八九十]+)月([一二三四五六七八九十]+)日[，,]?\s*星期([一二三四五六日天])")
for p in sorted(C.glob("第*.md"), key=lambda x: int(re.match(r"第(\d+)章", x.name).group(1))):
    n = int(re.match(r"第(\d+)章", p.name).group(1))
    t = p.read_text(encoding="utf-8")
    for m in pat.finditer(t):
        mo, d, w = cn2int(m.group(1)), cn2int(m.group(2)), WD[m.group(3)]
        if not mo or not d:
            continue
        ok = None
        for y in (2025, 2026, 2027):
            try:
                dt = datetime.date(y, mo, d)
            except ValueError:
                continue
            if dt.weekday() == w:
                ok = dt
                break
        if ok is None:
            print(f"第{n}章  「{m.group(0)}」 → 2025/2026/2027 年该日都不是星期{'一二三四五六日'[w]}")
