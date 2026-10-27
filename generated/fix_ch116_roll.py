#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 116 章 §十二 点名场景的内部矛盾修补。

矛盾：该章 §八 写"名册上十二行，一行没划"，§十一 写"通道内人员十二名。
四十八小时无回应。状态未明"；但 §十二 的 4/29 点名写"十二个名字。划掉十一个。
第十二个没有划"，并在后面核对"划掉的行和到达的时刻"——十一行被划等于十一人
已到达，与 §八/§十一 及第 115 章（洞里那十一行始终是空的）全都冲突。

改法：以"十二行一个也没划"为准（与 §八、§十一、第 115 章一致），
只改 §十二 的算术与问答，保留该节的全部其余事实：
八点点名／名单由朝方出／郑成德念／值班的记录员主持／每天点一次／
"没有划的理由"／点在点名记录后面。

用法: python generated/fix_ch116_roll.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "content" / "chichao-beijing" / "第116章 没有人回来.md"

FIXES = [
    # (a) 算术：十二行一个也没划
    ("十二个名字。\n\n划掉十一个。\n\n第十二个没有划。\n\n李俊赫在自己的本子上把它空着。",
     "十二个名字。\n\n一个也没有划。\n\n李俊赫在自己的本子上写了十二行。\n\n十二行都空着。"),
    # (c) 谁划的／郑成德念完说什么
    ("“划掉十一个是谁划的。”\n\n“值班的记录员。”",
     "“十二行都没划，谁划的。”\n\n“没人划。”"),
    ("“他说：‘那一行留着。’”",
     "“他说：‘十二行都留着。’”"),
    # (d) 核对什么
    ("“核对什么。”\n\n“核对划掉的行和到达的时刻。”\n\n“划掉的行和时刻对得上吗。”\n\n“对得上。十一个都对得上。”\n\n“十二行里十一个划掉。划的时候是一个人一个人念吗。”\n\n“是。”",
     "“核对什么。”\n\n“核对到达的时刻。”\n\n“到达的时刻对得上吗。”\n\n“十二行都没有到达的时刻。”\n\n“为什么没有。”\n\n“因为十二行里的人一个都没有出来。”\n\n“念的时候是一个人一个人念吗。”\n\n“是。”"),
    # (e) 收尾
    ("“念完十二行以后，那一格怎么处理的。”\n\n“空着。”\n\n“以后有人问起这一格，怎么答。”\n\n“说这一行还没有划。”",
     "“念完十二行以后，那十二格怎么处理的。”\n\n“空着。”\n\n“以后有人问起这十二格，怎么答。”\n\n“说十二行都还没有划。”"),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = TARGET.read_bytes().decode("utf-8")
    for old, new in FIXES:
        n = text.count(old)
        if n != 1:
            print(f"[FAIL] 命中 {n} 次（应为 1）: {old[:40]!r}")
            return 1
        text = text.replace(old, new)
    TARGET.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    print(f"[ OK ] ch116: 修补 {len(FIXES)} 处")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
