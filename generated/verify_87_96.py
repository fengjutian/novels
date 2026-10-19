#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》第 87–96 章专项校验。

check.py 负责通用格式；本脚本负责 check.py 管不到的四件事：
  1. 卷头 / 章名 / 相对时间三行与 BRIEF_87_96.md 的表逐字一致
  2. 星期与季节正确，十章日期单调不减
  3. 本批禁写项（"夏季" 等）
  4. 新词法：新章里出现、而第 1–86 章与设定文档里从未出现的 2–4 字词
     ——用来抓"扩写跑偏"和"凭空造了新实体"

用法:
    python generated/verify_87_96.py            # 全查
    python generated/verify_87_96.py 88 89      # 只查指定章（仍拿全批做对照）
退出码: 0 = 通过, 1 = 有 FAIL
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
OTHERS = CONTENT / "others"

CJK = re.compile(r"[一-鿿]")

# 章号 -> (卷头, 章名, 相对时间整行, 季节)
SPEC = {
    87: ("# 赤潮北境｜第六卷 过冬", "以油为准",
         "相对时间：T+256（9/24 周一）｜初秋｜黑龙江 哈尔滨", "初秋"),
    88: ("# 赤潮北境｜第六卷 过冬", "六天",
         "相对时间：T+261（9/29 周六）｜初秋｜辽宁 丹东 前沿", "初秋"),
    89: ("# 赤潮北境｜第六卷 过冬", "没有主语的话",
         "相对时间：T+271（10/9 周二）｜初秋｜韩国 釜山", "初秋"),
    90: ("# 赤潮北境｜第六卷 过冬", "同一个数",
         "相对时间：T+281（10/19 周五）｜初秋｜吉林 延边 前沿", "初秋"),
    91: ("# 赤潮北境｜第七卷 档案", "处理中",
         "相对时间：T+281（10/19 周五）｜深秋｜日本 宫城", "深秋"),
    92: ("# 赤潮北境｜第七卷 档案", "各自成立",
         "相对时间：T+286（10/24 周三）｜深秋｜日本 东京", "深秋"),
    93: ("# 赤潮北境｜第七卷 档案", "经办人",
         "相对时间：T+291（10/29 周一）｜深秋｜日本 东京", "深秋"),
    94: ("# 赤潮北境｜第七卷 档案", "排在后面",
         "相对时间：T+296（11/3 周六）｜初冬｜黑龙江 哈尔滨", "初冬"),
    95: ("# 赤潮北境｜第七卷 档案", "各缺一环",
         "相对时间：T+301（11/8 周四）｜初冬｜韩国 釜山 地下诊所", "初冬"),
    96: ("# 赤潮北境｜第七卷 档案", "三个时间",
         "相对时间：T+306（11/13 周二）｜初冬｜黑龙江 哈尔滨", "初冬"),
}

# 本批禁写项：BRIEF §〇 已裁定第 88 章旧摘要"夏季到来"作废
BANNED = ["夏季", "夏天", "盛夏避难"]

# 新增具名人物白名单（本批只允许一个，见 BRIEF §2.3）
ALLOWED_NEW_NAMES = ["藤田茂"]


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
        lines = p.read_text(encoding="utf-8").split("\n")
        head = [ln for ln in lines[:10]]
        want_vol, want_name, want_time, _ = SPEC[ch]
        if not head or head[0].strip() != want_vol:
            errs.append(f"ch{ch}: 卷头应为 {want_vol!r}，实际 {head[0].strip()!r}" if head
                        else f"ch{ch}: 文件为空")
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
                errs.append(f"ch{ch}: 正文出现禁写项 {w!r}（BRIEF §〇 已裁定作废）")
    return errs


def check_dates(chs: list[int]) -> list[str]:
    """日期单调不减 + 星期与日期自洽。"""
    errs = []
    seq = []
    for ch in sorted(SPEC):
        w = re.search(r"T\+\d+（(\d+)/(\d+) 周.", SPEC[ch][2])
        m, d = int(w.group(1)), int(w.group(2))
        seq.append((ch, m, d))
    for i in range(1, len(seq)):
        if (seq[i][1], seq[i][2]) < (seq[i - 1][1], seq[i - 1][2]):
            errs.append(f"日期倒流: ch{seq[i-1][0]} -> ch{seq[i][0]}")
    # 第 90/91 章同为 10/19，允许（卷界同日，与第30/31章同体例）
    return errs


def old_corpus() -> str:
    """第 1–86 章 + 全部设定文档，作为"已存在语料"。"""
    parts = []
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m and 1 <= int(m.group(1)) <= 86:
            parts.append(p.read_text(encoding="utf-8"))
    for p in sorted(OTHERS.glob("*.md")):
        parts.append(p.read_text(encoding="utf-8"))
    return "".join(parts)


def new_words(chs: list[int], min_count: int = 2) -> list[tuple[str, int]]:
    """新章里 >=min_count 次、而旧语料 0 次的 2–4 字片段。"""
    old = old_corpus()
    new = ""
    for ch in chs:
        p = find(ch)
        if p:
            new += body_of(p.read_text(encoding="utf-8"))
    # 只保留连续汉字串
    runs = re.findall(r"[一-鿿]{2,}", new)
    counts: dict[str, int] = {}
    for run in runs:
        for n in (2, 3, 4):
            for i in range(len(run) - n + 1):
                g = run[i:i + n]
                counts[g] = counts.get(g, 0) + 1
    out = []
    for g, c in counts.items():
        if c >= min_count and g not in old:
            out.append((g, c))
    # 折叠子片段：若 g 是某个更长片段 g2 的子串且 count(g) <= count(g2)，丢掉 g。
    # 目的是把"可容 / 可容纳 / 可容纳人 / 容纳人 / 纳人"合并成一条，
    # 否则一个词会刷出五行看起来像五个新词的条目。
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
                        ("日期", check_dates(chs))):
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
        mark = "  ← 需人工确认是否为新具名实体" if g in ALLOWED_NEW_NAMES else ""
        print(f"  {g}  x{c}{mark}")

    print(f"\n--- chapters={len(chs)}  FAIL={fails}  新词条目={len(words)} ---")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
