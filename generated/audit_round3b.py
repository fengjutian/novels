#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》第 3 轮机械审计 · 第二批：排版层与配对层。

维度：
  J. 数字与汉字之间的半角空格（中文正文排版错误），分章统计
  K. 引号配对（中文双引号 “” 是否成对）
  L. 括号配对（半角 () 与全角（）混用与未闭合）
  M. 千分位逗号 / 冒号半角 / 连字符
  N. 日文假名与西文混排处的空格（中文正文里的日文段落是否规范）
  O. 章内加粗 ** 跨段开合
  P. 表格列数不一致（markdown 表格）
  Q. 连续空行 / 行尾空格
  R. 章节信息块与 04 §3.4 模板的逐项差异
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


def chapters() -> dict[int, Path]:
    out = {}
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def load(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def body_of(text: str) -> tuple[str, int]:
    i = text.find("## 一、")
    if i < 0:
        return text, 0
    return text[i:], text[:i].count("\n")


def lines_of(p: Path):
    return list(enumerate(load(p).split("\n"), 1))


CJK = r"\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff"
FULL = r"\uff00-\uffef"


# ---------- J. 数字与汉字之间的空格 ----------
def task_j(chs):
    out = []
    pat = re.compile(rf"(?<=[0-9]) +(?=[{CJK}])")
    per = defaultdict(list)
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            s = line
            if s.startswith("#"):
                continue
            for m in pat.finditer(s):
                per[n].append((ln, s.strip()[:70]))
    tot = sum(len(v) for v in per.values())
    out.append(f"数字与汉字之间的半角空格：全书 {tot} 处，分布在 {len(per)} 章")
    for n in sorted(per):
        out.append(f"    第{n}章 {len(per[n])} 处   例：L{per[n][0][0]} {per[n][0][1]}")
    return out


# ---------- K. 引号配对 ----------
def task_k(chs):
    out = []
    bad = []
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            if line.count("“") != line.count("”"):
                bad.append((n, ln, line.strip()[:70]))
    out.append(f"引号不成对的行：{len(bad)} 行")
    for x in bad[:20]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    return out


# ---------- L. 括号 ----------
def task_l(chs):
    out = []
    half = []
    unclosed = []
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            if "(" in line or ")" in line:
                half.append((n, ln, line.strip()[:70]))
            if line.count("（") != line.count("）") or line.count("(") != line.count(")"):
                unclosed.append((n, ln, line.strip()[:70]))
    out.append(f"使用半角括号 () 的行：{len(half)} 行")
    for x in half[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    out.append(f"括号不配对的行：{len(unclosed)} 行")
    for x in unclosed[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    return out


# ---------- M. 千分位 / 半角冒号 / 连字符 ----------
def task_m(chs):
    out = []
    thou = []
    halfcolon = []
    hyphen = []
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            s = line.strip()
            if re.search(r"\d,\d", s):
                thou.append((n, ln, s[:70]))
            if re.search(rf"[\u4e00-\u9fff]:", s) or re.search(r":(?=[{CJK}])", s):
                halfcolon.append((n, ln, s[:70]))
            if re.search(r"[\u4e00-\u9fff]-[A-Za-z0-9\u4e00-\u9fff]", s):
                hyphen.append((n, ln, s[:70]))
    out.append(f"千分位逗号数字：{len(thou)} 行")
    for x in thou[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    out.append(f"半角冒号接中文：{len(halfcolon)} 行")
    for x in halfcolon[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    out.append(f"半角连字符夹中文：{len(hyphen)} 行")
    for x in hyphen[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    return out


# ---------- N. 日文假名段落中的空格 ----------
def task_n(chs):
    out = []
    hits = defaultdict(int)
    ex = {}
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            if re.search(r"[\u3040-\u309f\u30a0-\u30ff]", line):
                hits[n] += 1
                ex.setdefault(n, []).append((ln, line.strip()[:70]))
    out.append(f"含日文假名的行：{sum(hits.values())} 行，分布在 {len(hits)} 章")
    for n in sorted(hits):
        out.append(f"    第{n}章 {hits[n]} 行")
    # 检查这些行里 汉字与假名 之间是否有空格
    gap = []
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            if re.search(r"[\u3040-\u309f\u30a0-\u30ff]", line) and re.search(
                    rf"[{CJK}] +[{CJK}]", line):
                gap.append((n, ln, line.strip()[:70]))
    out.append(f"日文行中汉字之间有空格：{len(gap)} 行")
    for x in gap[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    return out


# ---------- O. 加粗跨段 ----------
def task_o(chs):
    out = []
    bad = []
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            if line.count("**") % 2 != 0:
                bad.append((n, ln, line.strip()[:70]))
    out.append(f"加粗标记不成对的行：{len(bad)} 行")
    for x in bad[:20]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]}")
    return out


# ---------- P. 表格列数 ----------
def task_p(chs):
    out = []
    for n, p in sorted(chs.items()):
        block = []
        for ln, line in lines_of(p):
            if line.strip().startswith("|"):
                block.append((ln, line.strip()))
            else:
                if len(block) >= 2:
                    cols = [len(b.split("|")) for _, b in block]
                    if len(set(cols)) > 1:
                        out.append(f"第{n}章 L{block[0][0]}–L{block[-1][0]}: "
                                   f"表格列数不一致 {sorted(set(cols))}")
                        for bl, b in block:
                            out.append(f"      L{bl}: {b[:80]}")
                block = []
    return out


# ---------- Q. 空行 / 行尾空格 ----------
def task_q(chs):
    out = []
    trail = []
    multi = []
    for n, p in sorted(chs.items()):
        lines = load(p).split("\n")
        for ln, line in enumerate(lines, 1):
            if line != line.rstrip():
                trail.append((n, ln, line[:60]))
        run = 0
        for ln, line in enumerate(lines, 1):
            if line.strip() == "":
                run += 1
                if run == 3:
                    multi.append((n, ln))
            else:
                run = 0
    out.append(f"行尾多余空格的行：{len(trail)} 行")
    for x in trail[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}: {x[2]!r}")
    out.append(f"连续 3 个以上空行的位置：{len(multi)} 处")
    for x in multi[:15]:
        out.append(f"    第{x[0]}章 L{x[1]}")
    return out


# ---------- R. 章节信息块与 04 §3.4 模板比对 ----------
def task_r(chs):
    out = []
    forms = defaultdict(list)
    for n, p in sorted(chs.items()):
        text = load(p)
        head = text.split("\n")[:10]
        line = next((x for x in head if "相对时间" in x), "")
        # 归一化：把数字、日期都换成占位
        norm = re.sub(r"[0-9]+", "N", line)
        forms[norm].append(n)
    out.append(f"表头形态种类：{len(forms)}")
    for k in sorted(forms, key=lambda k: -len(forms[k])):
        out.append(f"    {len(forms[k]):3d} 章  {k}")
        out.append(f"        章号：{forms[k]}")
    return out


def main() -> int:
    chs = chapters()
    args = [a.upper() for a in sys.argv[1:]]
    tasks = {
        "J": ("数字与汉字间的空格", task_j),
        "K": ("引号配对", task_k),
        "L": ("括号", task_l),
        "M": ("千分位/冒号/连字符", task_m),
        "N": ("日文行排版", task_n),
        "O": ("加粗配对", task_o),
        "P": ("表格列数", task_p),
        "Q": ("空行/行尾空格", task_q),
        "R": ("章节信息块形态", task_r),
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
