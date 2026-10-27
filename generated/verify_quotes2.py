# -*- coding: utf-8 -*-
"""批量复核第二批引文（第71-96章 agent 报的 P2/P3 + 01设定块冲突）。"""
import os, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

def chap(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat))
                if ".bak" not in p]
        if hits:
            return open(hits[0], encoding="utf-8").read()
    return None

def others(name):
    return open(os.path.join(ROOT, "others", name), encoding="utf-8").read()

CHECKS = [
    ("C-79章-差四天", 79, "四天"),
    ("C-79章-七月十一", 79, "七月十一"),
    ("C-79章-七月十七", 79, "七月十七"),
    ("C-78章-处置十四", 78, "处置十四"),
    ("C-78章-处置零", 78, "处置零"),
    ("C-78章-前天", 78, "前天"),
    ("C-78章-41小时", 78, "41 小时"),
    ("C-78章-四十七小时", 78, "四十七小时"),
    ("C-73章-三行", 73, "三行"),
    ("C-73章-五行", 73, "五行"),
    ("C-73章-六行", 73, "六行"),
    ("C-73章-两个月前", 73, "两个月前"),
    ("C-74章-二月十六日", 74, "二月十六日"),
    ("C-74章-二月二十四日", 74, "二月二十四日"),
    ("C-75章-第八次", 75, "第八次"),
    ("C-75章-第七次", 75, "第七次"),
    ("C-86章-二百五十三", 86, "二百五十三"),
    ("C-86章-五百七十一", 86, "五百七十一"),
    ("C-83章-三个月", 83, "三个月"),
    ("C-83章-三年多", 83, "三年多"),
    ("C-83章-八十九", 83, "八十九"),
    ("C-88章-十一天", 88, "十一天"),
    ("C-88章-九度", 88, "九度"),
    ("C-88章-第一格", 88, "第一格"),
    ("C-85章-二十二行", 85, "二十二行"),
    ("C-82章-只有这一行", 82, "只有这一行"),
    ("C-92章-二十号回执", 92, "二十号"),
    ("C-92章-二十四号", 92, "二十四号"),
    ("C-93章-十二天", 93, "十二天"),
    ("C-93章-待合并", 93, "待合并"),
    ("C-71章-六天", 71, "六天"),
    ("C-71章-五十一份", 71, "五十一份"),
]

for tag, n, frag in CHECKS:
    txt = chap(n)
    if txt is None:
        print("%-24s [章缺失]" % tag); continue
    cnt = txt.count(frag)
    print("%-24s 第%03d章 命中%2d  %s" % (tag, n, cnt, "OK" if cnt else "*** 未命中 ***"))

print("\n---- others ----")
OTH = [
    ("O-01-83章-91%", "01-时间线.md", "91%"),
    ("O-01-88章-9度区间", "01-时间线.md", "9℃"),
    ("O-01-87章-核心区外十九户", "01-时间线.md", "核心区外十九户"),
    ("O-01-81章-2101", "01-时间线.md", "2101"),
    ("O-01-84章-3个月前", "01-时间线.md", "3 个月前"),
    ("O-02-76章当场可做", "02-感染者规则细则.md", "第 76"),
]
for tag, f, frag in OTH:
    t = others(f)
    c = t.count(frag)
    print("%-24s %-22s 命中%2d  %s" % (tag, f, c, "OK" if c else "*** 未命中 ***"))
