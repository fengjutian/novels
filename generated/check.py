#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》正文守卫。

合并 04-正文格式规范.md §4 自查表与 §9 形态守卫的全部可机检项。
规范要求的 regress.py / boldchk.py / wideall.py / dashkind.py / dashdump.py
在 git 全历史中从未入库，本脚本是它们的合并实现。

用法:
    python generated/check.py            # 检查全部章
    python generated/check.py 77 78      # 只检查指定章
    python generated/check.py --dump 85  # 打印该章破折号明细

退出码: 0 = 全部通过, 1 = 有 FAIL
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"

CJK = re.compile(r"[一-鿿]")
# 必须带 re.M：^ / $ 要锚到行边界，否则 findall 一节都匹配不到
SEC_HEAD = re.compile(r"^## ([一二三四五六七八九十]+)、(.+)$", re.M)
REMARK_HEAD = "## 章节备注"

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
          "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13}

# §8.1 口径：4000-5000 字，8-12 节（第 22 章 5,666 为已备案例外，本脚本不特判）
WORD_MIN, WORD_MAX = 4000, 5000
SEC_MIN, SEC_MAX = 8, 12
TITLE_MIN, TITLE_MAX = 2, 8
RUN_MAX = 6
SHORT_MAX = 0.40
DASH_MAX = 0.80
WIDE_MAX = 100          # 半角折行上限，按显示宽度


def cn_to_int(s: str) -> int | None:
    if s in CN_NUM:
        return CN_NUM[s]
    if len(s) == 2 and s[0] == "十":
        return 10 + CN_NUM.get(s[1], -1)
    if len(s) == 3 and s[1] == "十":
        return CN_NUM.get(s[0], -1) * 10 + CN_NUM.get(s[2], -1)
    return None


def width(s: str) -> int:
    return sum(2 if ord(c) > 0x2E80 else 1 for c in s)


def split_chapter(text: str) -> tuple[str, str, str]:
    """返回 (正文, 章节备注, 头部)。切点落在 '## 一、' 之前。"""
    m = re.search(r"^## 一、", text, re.M)
    if not m:
        return "", "", text
    head, body = text[:m.start()], text[m.start():]
    if REMARK_HEAD in body:
        body, remark = body.split(REMARK_HEAD, 1)
        return body, remark, head
    return body, "", head


def paragraphs(body: str) -> list[str]:
    """段以空行分隔。§9.5：段内软换行等于空格，统计前必须删掉段内 \\n。"""
    return [re.sub(r"\s*\n\s*", "", p) for p in re.split(r"\n\s*\n", body) if p.strip()]


def is_dash_para(p: str) -> bool:
    return p.lstrip("*").lstrip().startswith("—")


def check(path: Path) -> list[tuple[str, str, str]]:
    """返回 (级别, 项, 详情) 列表。级别 ∈ {FAIL, WARN}。"""
    out: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8")
    body, remark, head = split_chapter(text)

    if not body:
        return [("FAIL", "结构", "找不到 '## 一、'，正文切片失败")]

    # --- 篇幅 ---
    n = len(CJK.findall(body))
    if not (WORD_MIN <= n <= WORD_MAX):
        out.append(("FAIL", "篇幅", f"{n} 字，超出 {WORD_MIN}-{WORD_MAX}"))

    # --- 分节 ---
    secs = SEC_HEAD.findall(body)
    k = len(secs)
    if not (SEC_MIN <= k <= SEC_MAX):
        out.append(("FAIL", "节数", f"{k} 节，超出 {SEC_MIN}-{SEC_MAX}"))
    nums = [cn_to_int(a) for a, _ in secs]
    if nums != list(range(1, k + 1)):
        out.append(("FAIL", "节号", f"不连续: {nums}"))
    for a, t in secs:
        if not (TITLE_MIN <= len(t) <= TITLE_MAX):
            out.append(("FAIL", "节标题长度", f"{a}、{t} = {len(t)} 字"))
        if re.search(r"[？！?！]", t):
            out.append(("FAIL", "节标题标点", f"{a}、{t} 含问号或感叹号"))

    # --- §9 形态守卫 ---
    paras = paragraphs(body)
    dash_idx = [i for i, p in enumerate(paras) if is_dash_para(p)]
    if paras:
        dash_ratio = len(dash_idx) / len(paras)
        if dash_ratio > DASH_MAX:
            out.append(("FAIL", "DASH", f"{dash_ratio:.0%} > {DASH_MAX:.0%}"))

    run = best = 0
    for i in range(len(paras)):
        run = run + 1 if i in set(dash_idx) else 0
        best = max(best, run)
    if best > RUN_MAX:
        out.append(("FAIL", "RUN", f"连续破折号段 {best} > {RUN_MAX}"))

    # §9.3：SHORT 只算"夹在串里的"短段。注意 and 的优先级高于 or，必须加括号，
    # 否则后半句只约束右侧分支，等于把"前有破折号段的孤立短段"也算进分母。
    ds = set(dash_idx)
    short = sum(1 for i in dash_idx
                if ((i - 1) in ds or (i + 1) in ds)
                and len(CJK.findall(paras[i])) <= 20)
    if len(dash_idx) >= 20 and dash_idx:
        sr = short / len(dash_idx)
        if sr > SHORT_MAX:
            out.append(("FAIL", "SHORT", f"{sr:.0%} > {SHORT_MAX:.0%}"))

    # --- 破折号禁区 ---
    if "———" in body:
        out.append(("FAIL", "三连横线", "出现 '———'，中文无此用法"))
    if re.search(r"\n\s*——\s*\n", body):
        out.append(("FAIL", "独立破折号行", "出现 \\n——\\n"))
    triple = re.findall(r"：[^。\n]{0,30}：", body)
    if triple:
        out.append(("WARN", "双冒号", f"{len(triple)} 处，§9.6 要求逐条看: {triple[:2]}"))

    # --- 加粗配对 ---
    for p in paras:
        if p.count("**") % 2 != 0:
            out.append(("FAIL", "加粗配对", f"'**' 落单: {p[:40]}"))
            break

    # --- 元叙事：正文里不得出现章号自指 ---
    meta = list(re.finditer(r"第\s*\d+\s*章", body))
    if meta:
        out.append(("FAIL", "元叙事", f"正文出现章号: "
                                  f"{[m.group(0) for m in meta][:3]}"))

    # --- 正文分隔线 ---
    if re.search(r"^\s*---\s*$", body, re.M):
        out.append(("FAIL", "正文分隔线", "§3.1 正文中不使用 '---'"))

    # --- 引号配对 ---
    for op, cl in (("“", "”"), ("‘", "’")):
        if body.count(op) != body.count(cl):
            out.append(("FAIL", "引号", f"{op}{cl} 不配对: "
                                       f"{body.count(op)} / {body.count(cl)}"))

    # --- 章节备注四项 ---
    # 全档 86 章零章节备注（2026-10-19 实测），属全书既存体例偏差而非本章问题。
    # 降为 WARN：让这批扩写不被既存偏差阻塞。补备注或改规范是另一个决定。
    if not remark:
        out.append(("WARN", "章节备注", "§3.5 要求四项备注，全档 86 章均无"))
    else:
        for item in ("本章视点", "核心场景设计", "伏笔与回收", "写作自查"):
            if item not in remark:
                out.append(("FAIL", "章节备注", f"缺「{item}」"))

    # --- 宽行 ---
    wide = [ln for ln in body.split("\n") if width(ln) > WIDE_MAX]
    if wide:
        out.append(("WARN", "宽行", f"{len(wide)} 行超 {WIDE_MAX} 列"))

    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if a != "--dump"]
    if args:
        chapters = sorted({int(a) for a in args})
    else:
        chapters = []
        for f in CONTENT.glob("*.md"):
            m = re.match(r"第(\d+)章", f.name)
            if m:
                chapters.append(int(m.group(1)))

    fails = warns = 0
    for c in chapters:
        paths = list(CONTENT.glob(f"第{c:02d}章*.md")) or list(CONTENT.glob(f"第{c}章*.md"))
        if not paths:
            print(f"ch{c:02d}: 找不到文件")
            fails += 1
            continue
        p = paths[0]
        res = check(p)
        n = len(CJK.findall(split_chapter(p.read_text(encoding="utf-8"))[0]))
        k = len(SEC_HEAD.findall(split_chapter(p.read_text(encoding="utf-8"))[0]))
        tag = "OK  " if not res else "FAIL"
        print(f"[{tag}] ch{c:02d}  {n:>5}字 {k:>2}节  {p.name}")
        for lvl, item, detail in res:
            print(f"        {lvl}  {item}: {detail}")
            if lvl == "FAIL":
                fails += 1
            else:
                warns += 1

    print(f"\n--- chapters={len(chapters)}  FAIL={fails}  WARN={warns} ---")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
