#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》第 4 轮机械审计：术语权限与判定树执行。

维度：
  W. 叙述者权限越权：按 06 §三 的权限表，检查每个视点人物是否说了不该说的口径词
  X. 禁写术语全局复查（06 §二 规则三/四 + 报告 F-7 已列的禁写清单）
  Y. 02 判定树执行：III 型判定三问是否在正文被完整引用或违反
  Z. 机构名/地名在正文内部的一致性（同一机构不同章不同名）
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
OTHERS = CONTENT / "others"

# 06 §三 权限表
PROHIBITED = {
    "疑似病例": ["市场管理课", "护工", "普通市民", "基层医员"],
    "进入法定监测程序": ["记者", "道里/郡里医员", "市场管理课", "护工", "普通市民", "基层医员"],
    "感染性原因待排": ["记者", "疾控医员", "市场管理课", "护工", "普通市民"],
}

# 视点 → 角色（03-人物弧线节点表 + 04 各章备注）
ROLE = {
    "姜素妍": "记者",
    "章明欣": "基层医员",
    "李恩淑": "护工",
    "朴成洙": "市场管理课",
    "朴宰勋": "疾控医员",
}

BANNED = ["确诊", "法定监测确认", "综合征监测", "夏季", "夏天", "感染性原因待排"]


def chapters() -> dict[int, Path]:
    out = {}
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def load(p):
    return p.read_text(encoding="utf-8")


def chapter_viewpoint(text):
    """从章名/节标题猜视点：取本章出现频次最高的角色名。"""
    counts = defaultdict(int)
    for name in ROLE:
        counts[name] = text.count(name)
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]


def task_w(chs):
    out = []
    for n, p in sorted(chs.items()):
        text = load(p)
        vp = chapter_viewpoint(text)
        if vp is None:
            continue
        role = ROLE[vp]
        for term, forbidden_roles in PROHIBITED.items():
            if role not in forbidden_roles:
                continue
            for ln, line in enumerate(text.split("\n"), 1):
                if term in line and line.strip():
                    out.append(f"第{n}章 L{ln} 视点≈{vp}({role}) 出现「{term}」: {line.strip()[:80]}")
    out.append(f"权限越权候选：{len(out)} 行")
    return out


def task_x(chs):
    out = []
    for term in BANNED:
        rows = []
        for n, p in sorted(chs.items()):
            for ln, line in enumerate(load(p).split("\n"), 1):
                if term in line:
                    rows.append((n, ln, line.strip()[:70]))
        if rows:
            out.append(f"「{term}」{len(rows)} 处")
            for r in rows[:8]:
                out.append(f"    第{r[0]}章 L{r[1]}: {r[2]}")
    return out


def task_y(chs):
    """III 型判定三问：正文提到判定时，三项是否齐备。"""
    out = []
    q = {
        "冲刺": ["冲刺", "跑"],
        "低温": ["零下三十", "-30", "负三十", "低温"],
        "失能": ["失能", "四十八小时"],
    }
    for n, p in sorted(chs.items()):
        text = load(p)
        if "III 型" not in text and "III型" not in text:
            continue
        # 找含"III 型"的判定段
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if re.search(r"III\s*型", line) and re.search(r"判定|确认|认定|类型", line):
                window = "\n".join(lines[max(0, i - 6): i + 10])
                missing = [k for k, alts in q.items()
                           if not any(a in window for a in alts)]
                if missing:
                    out.append(f"第{n}章 L{i+1}: III 型判定附近缺 {missing} | {line.strip()[:70]}")
    out.append(f"III 型判定上下文缺项候选：{len(out)} 行")
    return out


def task_z(chs):
    """机构名一致性：找出正文里反复出现的机构/纸面名称清单，人工判读。"""
    out = []
    pat = re.compile(r"([一-鿿]{2,12}(?:日报|通报|表格|名单|决定书|方案|附页|回执|登记本|值班表|指令|通报书|公告|会议|亭|部|厅|局|所|中心|工作组|指挥部|委员会|联络组|观察哨|监测点))")
    buckets = defaultdict(list)
    for n, p in sorted(chs.items()):
        for ln, line in enumerate(load(p).split("\n"), 1):
            for m in pat.finditer(line):
                buckets[m.group(1)].append((n, ln))
    # 只列出在 3 章以上出现的，且有多个近义变体的
    for name, locs in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        if len(locs) >= 3:
            chs_hit = sorted({x[0] for x in locs})
            out.append(f"{name}：{len(locs)} 处 / {len(chs_hit)} 章  首见第{chs_hit[0]}章 末见第{chs_hit[-1]}章")
    return out


def main() -> int:
    chs = chapters()
    args = [a.upper() for a in sys.argv[1:]]
    tasks = {
        "W": ("叙述者术语权限", task_w),
        "X": ("禁写术语复查", task_x),
        "Y": ("III 型判定三问", task_y),
        "Z": ("机构名清单", task_z),
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
