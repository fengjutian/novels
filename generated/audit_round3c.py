#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》第 3 轮机械审计 · 第三批：计数链与相对时长。

维度：
  S. "第N次/第N遍/第N个早上/第N天/第N轮" 计数链：按关键词聚类，检出跳号/倒退/自相矛盾
  T. 相对时长表述（"三天后""两个月前""半个月"）与章间实际日期差是否可核
  U. "合计/总共/一共"句前的分项加总是否成立（抽出后人工判读）
  V. 跨章"数量—单位"对：同一物件在两章的数量不一致
"""
from __future__ import annotations

import io
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"

CN = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
      "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "百": 100}


def cn2int(s):
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if "百" in s:
        a, _, b = s.partition("百")
        hi = cn2int(a) if a else 1
        return hi * 100 + (cn2int(b) if b else 0)
    if "十" in s:
        a, _, b = s.partition("十")
        hi = cn2int(a) if a else 1
        lo = cn2int(b) if b else 0
        return hi * 10 + lo
    if len(s) == 1 and s in CN:
        return CN[s]
    return None


NUMCH = "零〇一二两三四五六七八九十百千"


def chapters() -> dict[int, Path]:
    out = {}
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def load(p):
    return p.read_text(encoding="utf-8")


# ---------- S. 计数链 ----------
def task_s(chs):
    out = []
    # 模式：第<数>次 / 第<数>遍 / 第<数>个早上 / 第<数>天 / 第<数>轮 / 第<数>行
    pat = re.compile(rf"第([{NUMCH}]+)(次|遍|个早上|天|轮|行|号|本|张|封|页|句|条|份|箱|块|段)")
    buckets = defaultdict(list)
    for n, p in sorted(chs.items()):
        for ln, line in enumerate(load(p).split("\n"), 1):
            for m in pat.finditer(line):
                v = cn2int(m.group(1))
                if v is None:
                    continue
                # 上下文关键词：取前 12 字
                ctx = line[max(0, m.start() - 14): m.start()]
                buckets[(m.group(2), ctx[-6:])].append((n, ln, v, line.strip()[:80]))
    # 按单位分组，检查同一单位簇内的数值序列
    for unit in sorted({k[0] for k in buckets}):
        # 把同单位的簇合并
        items = []
        for (u, ctx), lst in buckets.items():
            if u == unit:
                items.extend(lst)
        if len(items) < 3:
            continue
        items.sort()
        seq = [(n, ln, v, t) for (n, ln, v, t) in items]
        vals = [v for _, _, v, _ in seq]
        if max(vals) - min(vals) <= 1:
            continue
        # 找跳号：把同章内/相邻章的值排序，检测缺失
        out.append(f"=== 单位「{unit}」 共 {len(seq)} 处，值域 {min(vals)}–{max(vals)}")
        prev_by_ch = {}
        for n, ln, v, t in seq:
            out.append(f"    第{n}章 L{ln}: 第{v}{unit}  | {t}")
    return out


# ---------- T. 相对时长 ----------
DUR = re.compile(rf"([{NUMCH}]+)(天|周|个月|年)前")
DUR2 = re.compile(rf"([{NUMCH}]+)(天|周|个月|年)后")


def task_t(chs):
    out = []
    hits = defaultdict(list)
    for n, p in sorted(chs.items()):
        for ln, line in enumerate(load(p).split("\n"), 1):
            for m in DUR.finditer(line):
                v = cn2int(m.group(1))
                if v is None:
                    continue
                unit = m.group(2)
                days = {"天": 1, "周": 7, "个月": 30, "年": 365}[unit]
                hits[n].append((ln, v * days, m.group(0), line.strip()[:80]))
    for n in sorted(hits):
        for ln, d, s, t in hits[n]:
            out.append(f"第{n}章 L{ln}: {s}（≈{d}天）  {t}")
    return out


# ---------- U. 加总核对 ----------
def task_u(chs):
    out = []
    # 抓 "X，Y，Z。合计 N" / "A 加 B 等于 C" / "X 加 Y 是 Z"
    cn_map = CN
    pat_add = re.compile(rf"([{NUMCH}]+)\s*加\s*([{NUMCH}]+)\s*(?:等于|是|＝|=)\s*([{NUMCH}]+)")
    for n, p in sorted(chs.items()):
        for ln, line in enumerate(load(p).split("\n"), 1):
            for m in pat_add.finditer(line):
                a, b, c = (cn2int(m.group(i)) for i in (1, 2, 3))
                if None in (a, b, c):
                    continue
                if a + b != c:
                    out.append(f"第{n}章 L{ln}: {m.group(0)}  → {a}+{b}={a+b}≠{c}  | {line.strip()[:80]}")
    return out


def main() -> int:
    chs = chapters()
    args = [a.upper() for a in sys.argv[1:]]
    tasks = {
        "S": ("计数链", task_s),
        "T": ("相对时长", task_t),
        "U": ("加总核对", task_u),
    }
    for key, (title, fn) in tasks.items():
        if args and key not in args:
            continue
        print(f"\n=== {key}. {title} ===")
        for line in fn(chs):
            print("  " + line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
