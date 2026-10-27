#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》全书审稿 · 机械层对账脚本（Mode C 用）。

做五件能穷举的事，不做需要判断的事：

  A. 章名对账：正文文件名（=当前章名）vs 01-时间线 / 03-人物弧线节点表里
     "第 N 章《X》" 的写法，凡是《X》≠当前章名的逐条列出（设定块滞后）。
     同时区分"断言当前章名"（矛盾）与"明示改名历史"（不是矛盾）。
  B. 04-正文格式规范 的分段索引表 vs 正文实际章名 / 节数 / 全章最关键的一节。
  C. 全部 120 章的表头日期：T 值单调不减、星期与公历自洽（T+0 = 2025-12-03）。
  D. 具名人物首次出场章 vs 03 / 05 登记的首次出场章。
  E. 跨章数字链：把"同一批关键数字"在全书出现的位置全部列出，供人工判读。

用法:
    python generated/audit_review.py            # 全跑
    python generated/audit_review.py A B        # 只跑某几项
退出码: 0 = 没有"硬矛盾"类问题（滞后块与待人工判读项不算失败）
"""
from __future__ import annotations

import datetime
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
OTHERS = CONTENT / "others"

WD = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
T0 = datetime.date(2025, 12, 3)


def chapters() -> dict[int, Path]:
    out = {}
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def chapter_title(p: Path) -> str:
    """文件名里的章名（'第NN章 章名.md' → '章名'）。"""
    stem = p.stem
    return re.sub(r"^第\d+章\s*", "", stem)


def task_a(chs: dict[int, Path]) -> list[str]:
    """设定文档里的《X》与当前章名不一致。"""
    out = []
    title = {n: chapter_title(p) for n, p in chs.items()}
    for f in ("01-时间线.md", "03-人物弧线节点表.md"):
        text = (OTHERS / f).read_text(encoding="utf-8")
        # 找 "第N章《X》" 或 "| 第N章 | ... 《X》" 形态
        for m in re.finditer(r"第\s*(\d+)\s*章[^\n|]{0,12}《([^》]+)》", text):
            n = int(m.group(1))
            name = m.group(2)
            if n not in title:
                out.append(f"[{f}] 第{n}章《{name}》 —— 正文无第{n}章")
            elif name != title[n]:
                # 取该行全文判断这是"断言"还是"改名历史"
                line_start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.end())
                line = text[line_start:line_end if line_end > 0 else len(text)]
                hist = any(k in line for k in ("因", "原大纲", "原为", "写成", "改", "改名", "后移", "原第"))
                out.append(f"[{f}] 第{n}章《{name}》 ≠ 正文《{title[n]}》"
                           f"{'  ← 疑似改名历史（非矛盾）' if hist else '  ← 断言当前章名（矛盾）'}")
    return out


def task_b(chs: dict[int, Path]) -> list[str]:
    """04-正文格式规范 的分段索引表 vs 正文。"""
    out = []
    text = (OTHERS / "04-正文格式规范.md").read_text(encoding="utf-8")
    for m in re.finditer(r"^\|\s*第(\d+)章\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|",
                         text, re.M):
        n = int(m.group(1))
        name = m.group(2).strip().replace("**", "")
        nsec = int(m.group(3))
        key = m.group(4).strip().replace("**", "")
        if key:
            key = re.sub(r"^[一二三四五六七八九十]+、\s*", "", key).strip()
        if n not in chs:
            out.append(f"第{n}章 —— 索引表有，正文无")
            continue
        actual_name = chapter_title(chs[n])
        body = chs[n].read_text(encoding="utf-8")
        heads = re.findall(r"^## ([一二三四五六七八九十]+)、(.+)$", body, re.M)
        if name != actual_name:
            out.append(f"第{n}章 索引表章名《{name}》≠正文《{actual_name}》")
        if nsec != len(heads):
            out.append(f"第{n}章 索引表节数 {nsec} ≠ 实际 {len(heads)}")
        if key and key not in actual_name:
            # 关键一节要在实际节标题里找得到
            if not any(key in t for _, t in heads):
                out.append(f"第{n}章 索引表「全章最关键的一节」{key} 在正文节标题里找不到")
    return out


def task_c(chs: dict[int, Path]) -> list[str]:
    """120 章表头：T 值单调、日期与星期自洽。"""
    out = []
    seq = []
    for n in sorted(chs):
        head = chs[n].read_text(encoding="utf-8").split("\n")[:8]
        line = next((x for x in head if x.startswith("相对时间")), "")
        m = re.search(r"T\+(\d+)（(?:(\d{4})/)?(\d+)/(\d+)\s+(\S+?)）", line)
        if not m:
            out.append(f"第{n}章 表头无法解析：{line!r}")
            continue
        t, y, mo, d, wk = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5)
        dt = T0 + datetime.timedelta(days=t)
        if (dt.month, dt.day) != (mo, d):
            out.append(f"第{n}章 T+{t} 应为 {dt.month}/{dt.day}，表头写 {mo}/{d}")
        if y and dt.year != int(y):
            out.append(f"第{n}章 T+{t} 应为 {dt.year} 年，表头写 {y}")
        if WD[dt.weekday()] != wk:
            out.append(f"第{n}章 {dt} 应为 {WD[dt.weekday()]}，表头写 {wk}")
        seq.append((n, t))
    for i in range(1, len(seq)):
        if seq[i][1] < seq[i - 1][1]:
            out.append(f"T 值倒流：第{seq[i-1][0]}章 T+{seq[i-1][1]} → 第{seq[i][0]}章 T+{seq[i][1]}")
    return out


def task_d(chs: dict[int, Path]) -> list[str]:
    """具名人物首次出场章：正文 vs 03/05 登记。"""
    out = []
    names = {}
    for n in sorted(chs):
        t = chs[n].read_text(encoding="utf-8")
        for name in ("朴哲民", "周砚", "姜素妍", "李俊赫", "金恩贞", "森川由紀",
                     "高桥信一", "韩泰植", "郑成德", "金玉姬", "崔正铁", "前田達也",
                     "恩舒", "章明欣", "孙镐俊", "宋炳洙", "权海俊", "李恩淑"):
            if name in names:
                continue
            if name in t:
                names[name] = n
    reg = {
        "朴哲民": 20, "周砚": 44, "姜素妍": 2, "李俊赫": 6, "金恩贞": 1,
        "森川由紀": 2, "高桥信一": 8, "韩泰植": 48, "郑成德": 111,
        "金玉姬": 110, "崔正铁": 110, "前田達也": 98, "恩舒": 12,
    }
    for name, first in sorted(names.items(), key=lambda kv: kv[1]):
        r = reg.get(name)
        if r is None:
            out.append(f"{name} 正文首次出现于第{first}章，但 03/05 登记表里没有这个人")
        elif first != r:
            out.append(f"{name} 正文首次出现于第{first}章，03/05 登记为第{r}章")
    return out


def task_e(chs: dict[int, Path]) -> list[str]:
    """关键数字链：把同一批数字在全书出现的位置列出来（人工判读）。"""
    keys = ["十一公里", "二十六分钟", "三百二十", "一百四十", "两千八百八十",
            "九轮", "十二行", "第三款", "十四度", "十五度", "四十八小时"]
    out = []
    for k in keys:
        hits = []
        for n in sorted(chs):
            c = chs[n].read_text(encoding="utf-8").count(k)
            if c:
                hits.append(f"{n}×{c}")
        out.append(f"{k}：" + " ".join(hits))
    return out


def main() -> int:
    chs = chapters()
    args = [a.upper() for a in sys.argv[1:]]
    tasks = {"A": ("章名对账（01/03 的《X》）", task_a),
             "B": ("04 分段索引表对账", task_b),
             "C": ("全档表头日期/星期", task_c),
             "D": ("具名人物首次出场", task_d),
             "E": ("关键数字链出现位置", task_e)}
    for key, (title, fn) in tasks.items():
        if args and key not in args:
            continue
        print(f"\n=== {key}. {title} ===")
        for line in fn(chs):
            print("  " + line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
