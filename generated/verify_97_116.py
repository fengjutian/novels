#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》第 97–116 章专项校验。

check.py 负责通用格式；本脚本负责 check.py 管不到的四件事：
  1. 卷头 / 章名 / 相对时间三行与 BRIEF_97_116.md 的表逐字一致
  2. 星期与日期自洽、日期单调不减、卷界同日体例（105/106 同日）
  3. 本批禁写项（"夏季""确诊""同源""感染性原因待排"等）
  4. 新词法：新章里出现、而第 1–96 章与设定文档里从未出现的 2–4 字词
     ——用来抓"扩写跑偏"和"凭空造了新实体"

用法:
    python generated/verify_97_116.py            # 全查
    python generated/verify_97_116.py 97 98      # 只查指定章
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
    97: ("# 赤潮北境 · 第七卷 档案", "第二组",
         "相对时间：T+350（11/18 周三）｜初冬｜韩国 釜山", "初冬"),
    98: ("# 赤潮北境 · 第七卷 档案", "流量计",
         "相对时间：T+355（11/23 周一）｜初冬｜日本 北海道 稚内", "初冬"),
    99: ("# 赤潮北境 · 第七卷 档案", "对照表",
         "相对时间：T+360（11/28 周六）｜初冬｜日本 北海道 稚内 废弃研究设施", "初冬"),
    100: ("# 赤潮北境 · 第七卷 档案", "交出去",
          "相对时间：T+365（12/3 周四）｜冬｜韩国 釜山", "冬"),
    101: ("# 赤潮北境 · 第七卷 档案", "第十一封",
          "相对时间：T+370（12/8 周二）｜冬｜日本 北海道 稚内 前沿", "冬"),
    102: ("# 赤潮北境 · 第七卷 档案", "先清哪一段",
          "相对时间：T+380（12/18 周五）｜冬｜黑龙江 哈尔滨", "冬"),
    103: ("# 赤潮北境 · 第七卷 档案", "来源",
          "相对时间：T+390（12/28 周一）｜深冬｜韩国 釜山", "深冬"),
    104: ("# 赤潮北境 · 第七卷 档案", "没发出去的那份",
          "相对时间：T+400（2027/1/7 周四）｜深冬｜黑龙江 哈尔滨", "深冬"),
    105: ("# 赤潮北境 · 第七卷 档案", "一百二十公分",
          "相对时间：T+410（2027/1/17 周日）｜深冬｜黑龙江 哈尔滨 前沿", "深冬"),
    106: ("# 赤潮北境 · 第八卷 雪线", "分区",
          "相对时间：T+410（2027/1/17 周日）｜深冬｜黑龙江 哈尔滨", "深冬"),
    107: ("# 赤潮北境 · 第八卷 雪线", "他知道不够",
          "相对时间：T+420（2027/1/27 周三）｜深冬｜黑龙江 哈尔滨", "深冬"),
    108: ("# 赤潮北境 · 第八卷 雪线", "一整版",
          "相对时间：T+430（2027/2/6 周六）｜冬｜韩国 釜山", "冬"),
    109: ("# 赤潮北境 · 第八卷 雪线", "十一份",
          "相对时间：T+440（2027/2/16 周二）｜冬｜日本 东京", "冬"),
    110: ("# 赤潮北境 · 第八卷 雪线", "六个人",
          "相对时间：T+450（2027/2/26 周五）｜冬｜咸镜道方向 山区", "冬"),
    111: ("# 赤潮北境 · 第八卷 雪线", "社会骚乱",
          "相对时间：T+460（2027/3/8 周一）｜早春｜咸镜道方向 联合调查驻地", "早春"),
    112: ("# 赤潮北境 · 第八卷 雪线", "第一夜",
          "相对时间：T+480（2027/3/28 周日）｜早春｜黑龙江 东北核心区 前沿", "早春"),
    113: ("# 赤潮北境 · 第八卷 雪线", "三万一千",
          "相对时间：T+490（2027/4/7 周三）｜春｜黑龙江 东北核心区 前沿", "春"),
    114: ("# 赤潮北境 · 第八卷 雪线", "最后通道",
          "相对时间：T+500（2027/4/17 周六）｜春｜咸镜道方向 最后通道", "春"),
    115: ("# 赤潮北境 · 第八卷 雪线", "带出来的人",
          "相对时间：T+508（2027/4/25 周日）｜春｜咸镜道方向 最后通道", "春"),
    116: ("# 赤潮北境 · 第八卷 雪线", "没有人回来",
          "相对时间：T+512（2027/4/29 周四）｜春｜黑龙江 东北核心区 前沿", "春"),
}

# 本批禁写项：BRIEF §2.2 与 06 术语口径
BANNED = [
    "夏季", "夏天", "盛夏避难",
    "确诊", "法定监测确认", "综合征监测",
    "感染性原因待排",
    "同源",
]

# 本批允许新增的具名人物与地名（BRIEF §2.3）
ALLOWED_NEW_NAMES = [
    "前田達也", "金玉姬", "崔正铁", "郑成德",
    "稚内", "北海道", "咸镜道",
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
        lines = p.read_text(encoding="utf-8").split("\n")
        head = lines[:10]
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
                errs.append(f"ch{ch}: 正文出现禁写项 {w!r}")
    return errs


def check_dates(chs: list[int]) -> list[str]:
    """T 值单调不减 + 卷界同日体例（105/106 同日）。"""
    errs = []
    seq = []
    for ch in sorted(SPEC):
        w = re.search(r"T\+(\d+)", SPEC[ch][2])
        seq.append((ch, int(w.group(1))))
    for i in range(1, len(seq)):
        if seq[i][1] < seq[i - 1][1]:
            errs.append(f"T 值倒流: ch{seq[i-1][0]} -> ch{seq[i][0]}")
    # 星期与公历日期自洽（T+0 = 2025-12-03）
    import datetime
    t0 = datetime.date(2025, 12, 3)
    wd = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for ch in sorted(SPEC):
        line = SPEC[ch][2]
        m = re.search(r"T\+(\d+)（(.*?)）", line)
        if not m:
            errs.append(f"ch{ch}: 相对时间行无法解析")
            continue
        t = int(m.group(1))
        inner = m.group(2)
        d2 = re.match(r"(?:(\d{4})/)?(\d+)/(\d+) (.+)$", inner)
        if not d2:
            errs.append(f"ch{ch}: 相对时间行无法解析: {inner!r}")
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


def old_corpus() -> str:
    """第 1–96 章 + 全部设定文档，作为'已存在语料'。"""
    parts = []
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m and 1 <= int(m.group(1)) <= 96:
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
        mark = "  ← 已登记新增实体" if g in ALLOWED_NEW_NAMES else ""
        print(f"  {g}  x{c}{mark}")

    print(f"\n--- chapters={len(chs)}  FAIL={fails}  新词条目={len(words)} ---")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
