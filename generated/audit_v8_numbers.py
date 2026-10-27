# -*- coding: utf-8 -*-
"""第八卷（106-120）关键数字链核验：逐个数字在正文出现位置 + 章内一致性。"""
import os, re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

def chap(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat)) if ".bak" not in p]
        if hits:
            return hits[0]
    return None

# (标签, 阿拉伯/汉字写法列表, 期望出现章)
CHAIN = [
    ("朴哲民入洞 09:04",        ["09:04", "九点零四"], [114]),
    ("按第三款关闭 22:40",      ["22:40", "二十二点四十"], [114]),
    ("关闸完成 22:51",          ["22:51", "二十二点五十一"], [114]),
    ("III 型 15℃ 48 小时失能",  ["48 小时", "48小时", "四十八小时"], None),
    ("受害者记录 二十九个编号",  ["二十九"], [119, 120]),
    ("十七个签字",              ["十七个签字", "十七"], None),
    ("三行记号+两行代签=五行",   ["两行代签", "代签"], [119, 120]),
    ("缺口四十分钟",            ["四十分钟"], None),
    ("三百二十人",              ["三百二十"], [115]),
    ("九十公里",                ["九十公里"], None),
    ("雪线",                    ["雪线"], None),
]

for label, forms, expect in CHAIN:
    hits = {}
    for n in range(106, 121):
        p = chap(n)
        if not p:
            continue
        t = open(p, encoding="utf-8").read()
        c = sum(t.count(f) for f in forms)
        if c:
            hits[n] = c
    note = ""
    if expect:
        missing = [e for e in expect if e not in hits]
        note = "  <= 期望章 %s%s" % (expect, " 缺失!" if missing else " 命中")
    print("%-24s %s%s" % (label, dict(sorted(hits.items())), note))

# 章内同一单位多值粗查（人数/公里/小时）
print("\n---- 章内 '数字+单位' 一致性抽查（106-120）----")
for n in range(106, 121):
    p = chap(n)
    if not p:
        continue
    t = open(p, encoding="utf-8").read()
    for unit in ["公里", "小时", "人", "米"]:
        vals = re.findall(r"([一二三四五六七八九十百零〇两\d]{1,6})\s*%s" % unit, t)
        vals = [v for v in vals if v not in ("一","两","三","四","五","六","七","八","九","十")]
        uniq = sorted(set(vals))
        if len(uniq) >= 6:
            print("  第%03d章 「%s」取值 %d 种: %s" % (n, unit, len(uniq), "、".join(uniq[:14])))
