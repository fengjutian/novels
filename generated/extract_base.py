#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽取 77-86 章的设定基线，长行按宽度折行后落盘，供 agent 读取。

用法: python generated/extract_base.py [章号...]
不传章号则抽取 77-86。
输出: generated/base_77_86.md
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OTHERS = ROOT / "content" / "chichao-beijing" / "others"
OUT = ROOT / "generated" / "base_77_86.md"
WIDTH = 88


def wrap(text: str, width: int = WIDTH) -> str:
    """按显示宽度折行（中文按 2 列算），保留 markdown 前缀语义。"""
    out = []
    for raw in text.split("\n"):
        if not raw.strip():
            out.append("")
            continue
        # 表格行按 | 断句，便于阅读
        if raw.startswith("|"):
            cells = raw.split("|")
            line = ""
            for c in cells:
                piece = c if c in ("",) else c
                w = len(piece) * 2
                if w > width and line:
                    out.append(line)
                    line = "  " + piece
                else:
                    line += piece
                line += "|"
            out.append(line)
            continue
        cur = ""
        cur_w = 0
        for ch in raw:
            cw = 2 if ord(ch) > 0x2E80 else 1
            if cur_w + cw > width:
                out.append(cur)
                cur, cur_w = "", 0
            cur += ch
            cur_w += cw
        out.append(cur)
    return "\n".join(out)


def main() -> int:
    chapters = [int(a) for a in sys.argv[1:]] or list(range(77, 87))
    chunks: list[str] = []
    chunks.append("# 《赤潮北境》77-86 章设定基线（自动抽取，仅供扩写参考）\n")
    chunks.append(f"> 抽取章号: {', '.join(str(c) for c in chapters)}\n")
    chunks.append("> 来源: others/01-时间线.md、others/03-人物弧线节点表.md、"
                  "others/06-术语与分类口径.md\n")

    # --- 1. 时间线逐章行（唯一覆盖 77-86 的逐章设计） ---
    tl = (OTHERS / "01-时间线.md").read_text(encoding="utf-8")
    chunks.append("\n---\n\n## 一、01-时间线.md 逐章设计\n")
    found = 0
    for c in chapters:
        m = re.search(rf"^\|\s*第{c}章\s*\|.*$", tl, re.M)
        if m:
            found += 1
            chunks.append(f"\n### 第{c}章\n\n" + wrap(m.group(0)) + "\n")
        else:
            chunks.append(f"\n### 第{c}章\n\n**[时间线中无此章条目]**\n")
    chunks.append(f"\n> 时间线命中 {found}/{len(chapters)} 章\n")

    # --- 2. 覆盖范围体检 ---
    chunks.append("\n---\n\n## 二、设定文件覆盖范围体检\n")
    for name in ("03-人物弧线节点表.md", "06-术语与分类口径.md"):
        text = (OTHERS / name).read_text(encoding="utf-8")
        nums = {int(n) for n in re.findall(r"第\s*(\d+)\s*章", text)}
        lo = [n for n in nums if n in chapters]
        chunks.append(
            f"\n- **{name}**：全文出现章号 {min(nums) if nums else '-'}–"
            f"{max(nums) if nums else '-'}，其中落在 {chapters[0]}–{chapters[-1]} 的有 "
            f"{len(lo)} 个（{sorted(lo) if lo else '无'}）\n"
        )

    # --- 3. 术语总则（与全章生效，不分章） ---
    for name, label in (("06-术语与分类口径.md", "术语与分类口径"),
                        ("02-感染者规则细则.md", "感染者规则细则")):
        text = (OTHERS / name).read_text(encoding="utf-8")
        heads = [ln for ln in text.split("\n") if re.match(r"^#{2,4} ", ln)]
        chunks.append(f"\n---\n\n## 三、{label}：全章生效的章节标题（不含正文内容）\n")
        chunks.append("\n```\n" + "\n".join(heads) + "\n```\n")

    OUT.write_text("".join(chunks), encoding="utf-8")
    print(f"written: {OUT}")
    print(f"bytes: {OUT.stat().st_size}")
    print(f"lines: {len(OUT.read_text(encoding='utf-8').splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
