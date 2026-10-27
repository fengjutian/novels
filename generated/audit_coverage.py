# -*- coding: utf-8 -*-
"""检查 others/01、03 里逐章表对 120 章的覆盖度，以及章名对账结果汇总。"""
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

names = {n: real_name(n) for n in range(1, 121)}

def parse_table(text):
    """返回 {章号: 该行全文}"""
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*第\s*(\d+)\s*章\s*\|", line.strip())
        if m:
            out[int(m.group(1))] = line.strip()
    return out

for fn in ["01-时间线.md", "03-人物弧线节点表.md"]:
    txt = open(os.path.join(ROOT, "others", fn), encoding="utf-8").read()
    rows = parse_table(txt)
    ks = sorted(rows)
    # 连续区间
    segs = []
    if ks:
        s = p = ks[0]
        for k in ks[1:]:
            if k == p + 1:
                p = k
            else:
                segs.append((s, p)); s = p = k
        segs.append((s, p))
    print("\n===== %s =====" % fn)
    print("含『第N章』开头的表格行章号：%d 行" % len(ks))
    print("覆盖区间：" + "  ".join("%d-%d" % a if a[0] != a[1] else str(a[0])
                                   for a in segs))
    # 章名对账
    bad = []
    for n in sorted(rows):
        row = rows[n]
        rn = names.get(n)
        if not rn:
            continue
        if rn not in row:
            bad.append((n, rn, row))
    print("章名对不上的行：%d 行" % len(bad))
    for n, rn, row in bad:
        print("  第%d章 正文《%s》 | 设定行: %s" % (n, rn, row[:110]))
