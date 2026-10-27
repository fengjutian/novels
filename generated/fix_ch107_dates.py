#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 107 章内部日期整体后移，使正文起日与表头 T+420（2027/1/27）一致。

原先正文从 1/17 起笔，表头是 1/27，读起来像日期打架。
改法：不改表头、不改任何情节与相对次序，只把四个节点整体后移十日：
    建议书 1/17 → 1/27｜出发 1/19 → 1/29｜第三项到／作废 1/23 → 2/2｜复盘 1/27 → 2/4
写回固定 UTF-8 无 BOM + LF。

用法: python generated/fix_ch107_dates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "content" / "chichao-beijing" / "第107章 他知道不够.md"

FIXES = [
    ("一月十七号，周砚把一份建议书推到桌子中间。",
     "一月二十七号，周砚把一份建议书推到桌子中间。"),
    ("一月十九日，第一支清剿分队出发。",
     "一月二十九日，第一支清剿分队出发。"),
    ("那两处十九日夜里打完了。", "那两处二十九日夜里打完了。"),
    ("二十三号，第三项到了。", "初二，第三项到了。"),
    ("发现在十九日二十二时四十分。", "发现在二十九日二十二时四十分。"),
    ("二十七号，会上要求他写一份结论。", "初四，会上要求他写一份结论。"),
    ("“二十三号触发的。”", "“初二触发的。”"),
    ("“算过是十九号。十九号它还在数。”", "“算过是二十九号。二十九号它还在数。”"),
    ("**“建议作废是二十三号。分队十九号出发。两件事各是各的。”**",
     "**“建议作废是初二。分队二十九号出发。两件事各是各的。”**"),
    ("“十九号那一天，你写没写第三项会来。”", "“二十九号那一天，你写没写第三项会来。”"),
    ("“第一行写的是十九号那天缺什么。”", "“第一行写的是二十九号那天缺什么。”"),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = TARGET.read_bytes().decode("utf-8")
    for old, new in FIXES:
        n = text.count(old)
        if n != 1:
            print(f"[FAIL] 命中 {n} 次（应为 1）: {old!r}")
            return 1
        text = text.replace(old, new)
    TARGET.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    print(f"[ OK ] ch107: 替换 {len(FIXES)} 处日期")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
