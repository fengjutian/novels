#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新词法扫描：找出扩写新引入的、既不在设定文件也不在改前版本里的汉字词组。

扩写最容易出的问题是"跑偏"——为了凑字数引入设定里没有的具名人物、
新造的术语、没交代来源的地名。逐条比对 token 是最可靠的检出方式，
比正则找"人名+动作词"干净得多（后者噪声极大）。

判据：一个 token 是"新增"的，当且仅当它
  1. 出现在改后的正文里，
  2. 且不出现在全部设定文档（others/*.md）里，
  3. 且不出现在该章的 git HEAD 版本里，
  4. 且不出现在其它任何章节的正文里。
新增词极少 = 扩写没跑偏，词汇全部来自既有语料。

用法:
    python generated/newwords.py            # 扫 77-86
    python generated/newwords.py 77 78      # 扫指定章
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
OTHERS = CONTENT / "others"

HAN = re.compile(r"[一-鿿]+")

# 以这些字开头/结尾的多半是虚词碎片，不是词
STOP_HEAD = set("的了是在和与也就都而及或但很更最不没有我你他她它们这那一个之其为对从被把将向到于以之所于")
STOP_TAIL = set("的了是在和与也就都而及或但很更最不没有个之其为对从被把将向到于以")


def ngrams(text: str, lo: int = 2, hi: int = 4) -> Counter:
    """取汉字串内的 2–4 字滑窗，过滤虚词碎片。"""
    out: Counter = Counter()
    for run in HAN.findall(text):
        for n in range(lo, hi + 1):
            for i in range(len(run) - n + 1):
                g = run[i:i + n]
                if g[0] in STOP_HEAD or g[-1] in STOP_TAIL:
                    continue
                out[g] += 1
    return out


def body_of(text: str) -> str:
    i = text.find("## 一、")
    return text[i:] if i >= 0 else text


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if a.isdigit()]
    chapters = sorted({int(a) for a in args}) or list(range(77, 87))

    # 1. 已知词库：全部设定文档
    known: set[str] = set()
    for f in OTHERS.glob("*.md"):
        known |= set(ngrams(f.read_text(encoding="utf-8")))

    # 2. 已知词库：其它章节正文
    other_chapters: dict[int, str] = {}
    for f in CONTENT.glob("*.md"):
        m = re.match(r"第(\d+)章", f.name)
        if m:
            other_chapters[int(m.group(1))] = body_of(f.read_text(encoding="utf-8"))

    for c in chapters:
        # 3. 已知词库：该章改前版本（git HEAD）
        path = CONTENT / next(
            (f.name for f in CONTENT.glob(f"第{c:02d}章*.md"))
            or (f.name for f in CONTENT.glob(f"第{c}章*.md")))
        rel = f"content/chichao-beijing/{path.name}"
        r = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, cwd=ROOT)
        old = body_of(r.stdout.decode("utf-8")) if r.returncode == 0 else ""

        old_grams = set(ngrams(old))
        other_grams: set[str] = set()
        for k, t in other_chapters.items():
            if k != c:
                other_grams |= set(ngrams(t))

        new_text = path.read_text(encoding="utf-8")
        new_grams = ngrams(body_of(new_text))

        fresh = {g: v for g, v in new_grams.items()
                 if g not in known and g not in old_grams and g not in other_grams
                 and v >= 2}
        if not fresh:
            print(f"ch{c:02d}: 零新增词")
            continue
        top = sorted(fresh.items(), key=lambda kv: (-kv[1], -len(kv[0])))
        print(f"ch{c:02d}: {len(fresh)} 个新增词（频次>=2）")
        for g, v in top[:40]:
            print(f"        {g}  x{v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
