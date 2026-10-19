#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把正文里的 ASCII 直引号/单引号还原为中文引号。

背景：2026-10-19 第 78 章的扩写提交（869229e）在转换过程中把**原文的**
中文引号一并改成了 ASCII，导致同一章内两种引号混排。原文（该章 HEAD
之前的版本）实测 ASCII 双引号 = 0，全部为中文引号，因此本章可以整体
按出现顺序还原。

本脚本只在"该章原文为纯中文引号"时才对全文生效，其余情况仅报告不动手。

用法:
    python generated/fix_quotes.py 78
    python generated\fix_quotes.py 78 --dry
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"


def path_of(ch: int) -> Path:
    for pat in (f"第{ch:02d}章*.md", f"第{ch}章*.md"):
        for f in CONTENT.glob(pat):
            return f
    raise SystemExit(f"找不到第{ch}章")


def orig_of(path: Path, ref: str = "7ecf253") -> str:
    rel = path.relative_to(ROOT).as_posix()
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], capture_output=True, cwd=ROOT)
    return r.stdout.decode("utf-8") if r.returncode == 0 else ""


def convert(text: str) -> tuple[str, int]:
    """逐行把 ASCII 双/单引号按出现顺序交替换成中文引号。"""
    out, n = [], 0
    for line in text.split("\n"):
        buf, open_d, open_s = [], True, True
        for ch in line:
            if ch == '"':
                buf.append("“" if open_d else "”")
                open_d = not open_d
                n += 1
            elif ch == "'":
                buf.append("‘" if open_s else "’")
                open_s = not open_s
                n += 1
            else:
                buf.append(ch)
        out.append("".join(buf))
    return "\n".join(out), n


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    dry = "--dry" in sys.argv
    for a in sys.argv[1:]:
        if not a.isdigit():
            continue
        ch = int(a)
        p = path_of(ch)
        old = orig_of(p)
        cur = p.read_text(encoding="utf-8")
        o_ascii, c_ascii = old.count('"'), cur.count('"')
        print(f"ch{ch:02d} {p.name}")
        print(f"    原文(7ecf253) ASCII 双引号 = {o_ascii}   当前 = {c_ascii}")
        if o_ascii != 0:
            print(f"    跳过：原文含 ASCII 引号，整体转换不安全")
            continue
        new, n = convert(cur)
        left = new.count('"') + new.count("'")
        print(f"    将转换 {n} 个引号，剩余 ASCII = {left}")
        if left:
            print(f"    警告：仍有未配对的 ASCII 引号，请人工检查")
        if dry:
            print("    （--dry，未写入）")
        else:
            p.write_text(new, encoding="utf-8")
            print("    已写入")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
