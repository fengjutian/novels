# -*- coding: utf-8 -*-
"""生成 01/03/04 中所有『第N章《X》』引用的对照表，标出与正文章名不符者。"""
import os, re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

def real_name(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat)) if ".bak" not in p]
        if hits:
            base = os.path.basename(hits[0])[:-3]
            return re.sub(r"^第\d+章\s*", "", base)
    return None

NAME = {n: real_name(n) for n in range(1, 121)}
VALID = set(v for v in NAME.values() if v)

pat = re.compile(r"第\s*(\d+)\s*章\s*《([^》]{1,24})》")
total = 0
for fn in sorted(glob.glob(os.path.join(ROOT, "others", "*.md"))):
    base = os.path.basename(fn)
    if base.startswith("02") or base.startswith("05"):
        continue
    lines = open(fn, encoding="utf-8").read().splitlines()
    hits = []
    for i, l in enumerate(lines, 1):
        for m in pat.finditer(l):
            n, nm = int(m.group(1)), m.group(2)
            if nm in VALID:
                continue
            hits.append((i, n, nm, NAME.get(n)))
    if hits:
        print("\n===== %s  (%d 处不符) =====" % (base, len(hits)))
        for i, n, nm, real in hits:
            total += 1
            print("  L%-4d 第%d章《%s》  ->  应为《%s》" % (i, n, nm, real))
print("\n合计不符引用：%d 处" % total)
