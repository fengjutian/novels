#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》第 117–120 章专项校验（第八卷卷末四章 / 全书完结四章）。

与 verify_97_116.py 同构，三件事：
  1. 卷头 / 章名 / 相对时间整行逐字一致
  2. 星期与公历日期自洽（T+0 = 2025-12-03）、T 值单调不减
  3. 本批禁写项（"夏季""夏天""确诊""同源""感染性原因待排"等）
外加两项本批专有：
  4. 新词法：新章出现、而第 1–116 章与设定文档里从未出现的 2–4 字片段
  5. 章号自指（正文里出现"第 N 章"）

用法:
    python generated/verify_117_120.py            # 全查
    python generated/verify_117_120.py 117 118    # 只查指定章
退出码: 0 = 通过, 1 = 有 FAIL
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
OTHERS = CONTENT / "others"

# 章号 -> (卷头, 章名, 相对时间整行, 季节)
SPEC = {
    117: ("# 赤潮北境 · 第八卷 雪线", "清点",
          "相对时间：T+516（2027/5/3 周一）｜春｜咸镜道方向 联合调查驻地", "春"),
    118: ("# 赤潮北境 · 第八卷 雪线", "第二次",
          "相对时间：T+522（2027/5/9 周日）｜春｜咸镜道方向 最后通道", "春"),
    119: ("# 赤潮北境 · 第八卷 雪线", "异议栏",
          "相对时间：T+530（2027/5/17 周一）｜春末｜黑龙江 哈尔滨", "春末"),
    120: ("# 赤潮北境 · 第八卷 雪线", "雪线之外",
          "相对时间：T+540（2027/5/27 周四）｜初夏｜韩国 釜山／日本 东京／黑龙江 哈尔滨", "初夏"),
}

BANNED = [
    "夏季", "夏天",
    "确诊", "法定监测确认", "综合征监测",
    "感染性原因待排",
    "同源",
]

# 本批允许出现的既有专名（用于新词法标注）
KNOWN = [
    "森川由紀", "周砚", "姜素妍", "金恩贞", "恩舒", "李俊赫", "郑成德", "朴哲民",
    "釜山", "东京", "哈尔滨", "咸镜道", "稚内",
]


def find(ch: int) -> Path | None:
    for pat in (f"第{ch:02d}章*.md", f"第{ch}章*.md"):
        hits = list(CONTENT.glob(pat))
        if hits:
            return hits[0]
    return None


def body_of(text: str) -> str:
    m = re.search(r"^## 一、", text, re.M)
    return text[m.start():] if m else ""


def check_headers(chs: list[int]) -> list[str]:
    errs = []
    for ch in chs:
        p = find(ch)
        if p is None:
            errs.append(f"ch{ch}: 找不到文件")
            continue
        head = p.read_text(encoding="utf-8").split("\n")[:10]
        want_vol, want_name, want_time, _ = SPEC[ch]
        if not head or head[0].strip() != want_vol:
            errs.append(f"ch{ch}: 卷头应为 {want_vol!r}")
        if f"### 第{ch}章 {want_name}" not in head:
            errs.append(f"ch{ch}: 章名行应为 '### 第{ch}章 {want_name}'")
        if want_time not in head:
            got = [ln for ln in head if ln.startswith("相对时间")]
            errs.append(f"ch{ch}: 相对时间应为 {want_time!r}，实际 {got[0] if got else '缺失'!r}")
    return errs


def check_banned(chs: list[int]) -> list[str]:
    errs = []
    for ch in chs:
        p = find(ch)
        if p is None:
            continue
        body = body_of(p.read_text(encoding="utf-8"))
        for w in BANNED:
            if w in body:
                errs.append(f"ch{ch}: 正文出现禁写项 {w!r}")
    return errs


def check_dates(chs: list[int]) -> list[str]:
    errs = []
    seq = [(ch, int(re.search(r"T\+(\d+)", SPEC[ch][2]).group(1))) for ch in sorted(SPEC)]
    for i in range(1, len(seq)):
        if seq[i][1] < seq[i - 1][1]:
            errs.append(f"T 值倒流: ch{seq[i-1][0]} -> ch{seq[i][0]}")
    t0 = datetime.date(2025, 12, 3)
    wd = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for ch in sorted(SPEC):
        line = SPEC[ch][2]
        m = re.search(r"T\+(\d+)（(.*?)）", line)
        if not m:
            errs.append(f"ch{ch}: 相对时间行无法解析")
            continue
        t = int(m.group(1))
        d2 = re.match(r"(?:(\d{4})/)?(\d+)/(\d+) (.+)$", m.group(2))
        if not d2:
            errs.append(f"ch{ch}: 相对时间行无法解析: {m.group(2)!r}")
            continue
        year, mm, dd, week = d2.group(1), int(d2.group(2)), int(d2.group(3)), d2.group(4)
        d = t0 + datetime.timedelta(days=t)
        if (d.month, d.day) != (mm, dd):
            errs.append(f"ch{ch}: T+{t} 应为 {d.month}/{d.day}，文件写 {mm}/{dd}")
        if year and d.year != int(year):
            errs.append(f"ch{ch}: T+{t} 应为 {d.year} 年")
        if wd[d.weekday()] != week:
            errs.append(f"ch{ch}: {d} 应为 {wd[d.weekday()]}，文件写 {week}")
    return errs


def check_selfref(chs: list[int]) -> list[str]:
    errs = []
    for ch in chs:
        p = find(ch)
        if p is None:
            continue
        body = body_of(p.read_text(encoding="utf-8"))
        for m in re.finditer(r"第\s*\d+\s*章", body):
            errs.append(f"ch{ch}: 正文出现章号自指 {m.group(0)!r}")
    return errs


def old_corpus() -> str:
    """第 1–116 章 + 全部设定文档，作为'已存在语料'。"""
    parts = []
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m and 1 <= int(m.group(1)) <= 116:
            parts.append(p.read_text(encoding="utf-8"))
    for p in sorted(OTHERS.glob("*.md")):
        parts.append(p.read_text(encoding="utf-8"))
    return "".join(parts)


def new_words(chs: list[int], min_count: int = 2) -> list[tuple[str, int]]:
    old = old_corpus()
    new = ""
    for ch in chs:
        p = find(ch)
        if p:
            new += body_of(p.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for run in re.findall(r"[一-鿿]{2,}", new):
        for n in (2, 3, 4):
            for i in range(len(run) - n + 1):
                g = run[i:i + n]
                counts[g] = counts.get(g, 0) + 1
    out = [(g, c) for g, c in counts.items() if c >= min_count and g not in old]
    grams = {g for g, _ in out}
    longest = sorted(grams, key=len, reverse=True)
    out = [(g, c) for g, c in out
           if not any(g != h and g in h and counts[h] >= c for h in longest)]
    out.sort(key=lambda x: (-x[1], x[0]))
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = [int(a) for a in sys.argv[1:]]
    chs = args or sorted(SPEC)

    fails = 0
    for label, errs in (("表头", check_headers(chs)),
                        ("禁写项", check_banned(chs)),
                        ("日期", check_dates(chs)),
                        ("章号自指", check_selfref(chs))):
        if errs:
            for e in errs:
                print(f"[FAIL] {label}: {e}")
            fails += 1
        else:
            print(f"[ OK ] {label}: 通过")

    print("\n--- 新词法（新章出现、旧语料零次的 2–4 字片段，出现 >=2 次）---")
    words = new_words(sorted(SPEC))
    if not words:
        print("（零新增）")
    for g, c in words[:40]:
        mark = "  ← 已登记/既有专名" if g in KNOWN else ""
        print(f"  {g}  x{c}{mark}")

    print(f"\n--- chapters={len(chs)}  FAIL={fails}  新词条目={len(words)} ---")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
