# -*- coding: utf-8 -*-
"""改动前后逐项对比 check.py 的检查结果，确认是否引入新的 FAIL。"""
import os, sys, io, glob, shutil, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("chk", os.path.join(BASE, "generated", "check.py"))
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

CUR = os.path.join(BASE, "content", "chichao-beijing")
BAK1 = os.path.join(BASE, "generated", "_fix1_backup")
BAK2 = os.path.join(BASE, "generated", "_fix2_backup")

def bak_for(name):
    p1 = os.path.join(BAK1, name)
    p2 = os.path.join(BAK2, name)
    if os.path.exists(p2):
        return p2
    if os.path.exists(p1):
        return p1
    return None

cur_files = [os.path.basename(p) for p in glob.glob(os.path.join(CUR, "第*.md"))
             if os.path.dirname(p) == CUR]

new_fail = 0
fixed_fail = 0
same = 0
details = []

for name in sorted(cur_files):
    b = bak_for(name)
    if not b:
        continue
    cur_p = os.path.join(CUR, name)
    res_cur = chk.check(Path(cur_p))
    res_bak = chk.check(Path(b))
    def norm(rs):
        out = []
        for lvl, item, det in rs:
            # 细节里的行号/字数会随改动变化，只比 (lvl, item)
            out.append((lvl, item))
        return sorted(out)
    c = norm(res_cur); k = norm(res_bak)
    fc = [x for x in c if x[0] == "FAIL"]
    fk = [x for x in k if x[0] == "FAIL"]
    added = [x for x in fc if x not in fk]
    removed = [x for x in fk if x not in fc]
    if added:
        new_fail += len(added)
        details.append(("新增", name, added))
    if removed:
        fixed_fail += len(removed)
        details.append(("消失", name, removed))
    if not added and not removed:
        same += 1

print("对比 %d 个改动过的文件：" % len([n for n in cur_files if bak_for(n)]))
print("  检查项完全一致的文件：%d" % same)
print("  新增 FAIL：%d 项" % new_fail)
print("  消失 FAIL：%d 项" % fixed_fail)
print()
for kind, name, items in details:
    print("  [%s] %s" % (kind, name))
    for lvl, item in items:
        print("        %s %s" % (lvl, item))
