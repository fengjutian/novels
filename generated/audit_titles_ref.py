# -*- coding: utf-8 -*-
"""扫描 others/*.md 中所有《...》章名引用，与正文 120 个章名比对，找出失效引用。"""
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
valid = set(v for v in names.values() if v)
# 已知旧章名候选：从 .bak_phase* 目录里提取所有历史章名
old_names = set()
for d in glob.glob(os.path.join(ROOT, ".bak_phase*")):
    for p in glob.glob(os.path.join(d, "第*.md")):
        base = os.path.basename(p)[:-3]
        nm = re.sub(r"^第\d+章\s*", "", base)
        if nm and nm not in valid:
            old_names.add(nm)

print("正文现行章名 %d 个；历史(.bak)章名 %d 个\n" % (len(valid), len(old_names)))

for fn in sorted(glob.glob(os.path.join(ROOT, "others", "*.md"))):
    txt = open(fn, encoding="utf-8").read()
    lines = txt.splitlines()
    bad = []
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r"《([^》]{1,20})》", line):
            nm = m.group(1)
            if nm in valid:
                continue
            tag = ""
            if nm in old_names:
                tag = "[旧章名]"
            elif not re.search(r"[一-鿿]", nm):
                tag = "[非章名]"
            bad.append((i, nm, tag, line.strip()[:150]))
    if bad:
        print("===== %s  （失效/可疑引用 %d 处） =====" % (os.path.basename(fn), len(bad)))
        for i, nm, tag, line in bad:
            print("  L%-4d %s %s" % (i, nm, tag))
            print("        %s" % line)
        print()
