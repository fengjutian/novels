# -*- coding: utf-8 -*-
"""后几十章字数核验：按章列出汉字数，并对照 04 §2.3 的 4,000-5,000 窗口。"""
import os, re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

def chap_lines(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat)) if ".bak" not in p]
        if hits:
            return open(hits[0], encoding="utf-8").read().splitlines()
    return None

def han_count(n):
    lines = chap_lines(n)
    if lines is None:
        return None
    # 切第一个 "## 一、" 之后
    start = 0
    for i, l in enumerate(lines):
        if re.match(r"^##\s*[一二三四五六七八九十]+、", l):
            start = i + 1
            break
    body = "\n".join(lines[start:])
    return len(re.findall(r"[一-鿿]", body)), len(re.findall(r"^##\s*[一二三四五六七八九十]+、", "\n".join(lines), re.M))

rows = []
for n in range(1, 121):
    c = han_count(n)
    if c:
        rows.append((n, c[0], c[1]))

LO, HI = 4000, 5000
print("章号   字数   节数  判定")
print("-" * 46)
for n, c, s in rows:
    if n < 61:
        continue
    flag = "OK" if LO <= c <= HI else ("低 %d" % (LO - c) if c < LO else "高 %d" % (c - HI))
    print("%3d  %6d  %4d  %s" % (n, c, s, flag))

def stat(lo, hi, label):
    sub = [r for r in rows if lo <= r[0] <= hi]
    tot = sum(r[1] for r in sub)
    ok = [r for r in sub if LO <= r[1] <= HI]
    under = [r for r in sub if r[1] < LO]
    over = [r for r in sub if r[1] > HI]
    print("\n%s (%d-%d, %d 章)" % (label, lo, hi, len(sub)))
    print("  合计 %d 字，章均 %d 字" % (tot, tot // len(sub)))
    print("  达标 %d 章 / 欠字数 %d 章 / 超字数 %d 章" % (len(ok), len(under), len(over)))
    if under:
        print("  欠字章节: " + ", ".join("%d(%d)" % (r[0], r[1]) for r in under))
    if over:
        print("  超字章节: " + ", ".join("%d(%d)" % (r[0], r[1]) for r in over))
    return under

u1 = stat(61, 75, "第五卷《北境》")
u2 = stat(76, 90, "第六卷《过冬》")
u3 = stat(91, 105, "第七卷《档案》")
u4 = stat(106, 120, "第八卷《雪线》")
u5 = stat(76, 120, "后 45 章合计")
u6 = stat(41, 80, "第 41-80 章")

print("\n---- 全书 ----")
tot = sum(r[1] for r in rows)
print("120 章合计 %d 字，章均 %d 字" % (tot, tot // 120))
ok = [r for r in rows if LO <= r[1] <= HI]
print("达标 %d 章（%.1f%%）" % (len(ok), 100.0 * len(ok) / 120))
print("最低 %d 章 %d 字；最高 %d 章 %d 字"
      % (min(rows, key=lambda r: r[1])[0], min(r[1] for r in rows),
         max(rows, key=lambda r: r[1])[0], max(r[1] for r in rows)))
