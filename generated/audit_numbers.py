#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设定块引用的数字 vs 正文里有没有这个数（汉字数词与阿拉伯数词两种写法都查）。

对 01-时间线.md 的逐章表、06-术语与分类口径.md 的逐章块逐行做：
  · 从设定行里抽出"看起来是正文里的量"的数字（跳过章号、T 值、日期、节号、比例分母）
  · 转成汉字数词，两种写法都在对应章节正文里找
  · 找不到 → 报告"设定块引用的数在正文里查无此数"

用法: python generated/audit_numbers.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
OTHERS = CONTENT / "others"

D = "零一二三四五六七八九"


def to_cn(n: int) -> str:
    if n == 0:
        return "零"
    if n < 10:
        return D[n]
    if n < 20:
        return "十" + (D[n % 10] if n % 10 else "")
    if n < 100:
        return D[n // 10] + "十" + (D[n % 10] if n % 10 else "")
    if n < 1000:
        s = D[n // 100] + "百"
        r = n % 100
        if r == 0:
            return s
        if r < 10:
            return s + "零" + D[r]
        return s + to_cn(r)
    if n < 10000:
        s = D[n // 1000] + "千"
        r = n % 1000
        if r == 0:
            return s
        if r < 100:
            return s + "零" + to_cn(r)
        return s + to_cn(r)
    return str(n)


def chapters() -> dict[int, str]:
    out = {}
    for p in CONTENT.glob("第*.md"):
        m = re.match(r"第(\d+)章", p.name)
        if not m:
            continue
        t = p.read_text(encoding="utf-8")
        i = t.find("## 一、")
        out[int(m.group(1))] = t[i:] if i >= 0 else t
    return out


SKIP_CONTEXT = re.compile(r"(T[+-]|第\s*\d+\s*章|年|月|日|/|\d\.\d)")


def numbers_in(line: str) -> list[int]:
    vals = []
    for m in re.finditer(r"\d[\d,]*", line):
        tok = m.group(0)
        ctx = line[max(0, m.start() - 6):m.end() + 6]
        if SKIP_CONTEXT.search(ctx):
            continue
        try:
            v = int(tok.replace(",", ""))
        except ValueError:
            continue
        if v >= 10 and v <= 999999:
            vals.append(v)
    return vals


def main() -> int:
    chs = chapters()
    total = 0
    for fname, rowpat in (("01-时间线.md", r"^\|\s*第(\d+)章\s*\|"),
                          ("06-术语与分类口径.md", r"^\|\s*第\s*(\d+)\s*章\s*\|")):
        text = (OTHERS / fname).read_text(encoding="utf-8")
        print(f"\n=== {fname} ===")
        for line in text.split("\n"):
            m = re.match(rowpat, line)
            if not m:
                continue
            n = int(m.group(1))
            if n not in chs:
                continue
            body = chs[n]
            miss = []
            for v in numbers_in(line):
                forms = {str(v), f"{v:,}", to_cn(v)}
                if not any(f in body for f in forms):
                    miss.append(v)
            if miss:
                total += len(miss)
                print(f"  第{n}章 设定块里的数在正文查无此数: {sorted(set(miss))}")
    print(f"\n--- 合计 {total} 处 ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
