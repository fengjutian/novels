# -*- coding: utf-8 -*-
"""复核第31-70章深读 agent 报出的引文与行号，并自行核算字数。"""
import os, re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

def chap(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat)) if ".bak" not in p]
        if hits:
            return open(hits[0], encoding="utf-8").read().splitlines()
    return None

def others(fn):
    return open(os.path.join(ROOT, "others", fn), encoding="utf-8").read().splitlines()

CHECKS = [
    ("B1-38-二月十二日",   38, 175, "十四天后的日期是二月十二日"),
    ("B1-38-只管十四天",   38, 165, "最后批下来的临时编号只管十四天"),
    ("B1-38-十四格表",     38, 211, "她拿到一张十四格的表"),
    ("B2-32-节标题",       32,   9, "## 一、停课第二天"),
    ("B2-32-停课第二天",   32,  11, "停课第二天，金恩贞仍在六点四十分醒来"),
    ("B2-32-第三个早上",   32,  14, "停课以后这是第三个早上"),
    ("B3-42-节标题",       42,  45, "## 二、第十个早上"),
    ("B3-42-第十个早上",   42,  53, "今天是第十个早上"),
    ("B3-42-十个早上",     42,  57, "这十个早上里，那一栏一次也没有被填过"),
    ("B4-56-车上29人",     56,  11, "车上二十九人，其中十一名儿童"),
    ("B4-56-27人",         56,  71, "只剩二十七人能够自己走进门"),
    ("B4-56-29人确认",     56,  79, "二十九人最终全部确认存活"),
    ("B5-44-末行19字",     44, 313, "最后一行那十九个字今天一个字也没有动"),
    ("B5-42-两版不是两行", 42, 524, "版面是两版，不是两行"),
    ("B5-42-19字在第四版", 42, 459, "十九个字那一句在第四版，位置没有动"),
    ("B6-42-二十一个字",   42, 461, "二十一个字"),
    ("B6-42-数过二十一",   42, 465, "一个字一个字数过。二十一。"),
    ("B6-42-同一句",       42, 463, "同一个词写在两张纸上的时候，不写在纸上的同一个位置"),
    ("B7-37-传真五次",     37,  12, "传真机一共响了五次"),
    ("B8-42-第二十四次",   42, 371, "稿子第二十四次登出"),
    ("B8-42-第二十四张",   42, 396, "今天这张是第二十四张"),
    ("B9-36-连续七天",     36,  11, "三个连续七天未变的地名"),
    ("B10-61-11/8",        61,  37, "第一次广播后，桥对面升起十一块白布。第三次只剩八块"),
    ("B10-61-页边",        61,  69, "把十一、八、九三个数字按广播时间写下"),
    ("B10-61-第四次六",    61,  87, "第四次广播时，桥北只升起六块白布"),
    ("B11-31-第九天",      31, 431, "今天是第九天"),
    ("B12-39-前六张",      39,  11, "前六张的纸角上都印着三个字"),
]

bad = 0
for tag, n, ln, frag in CHECKS:
    lines = chap(n)
    if lines is None:
        print("%-20s [章缺失]" % tag); bad += 1; continue
    if ln > len(lines):
        print("%-20s 第%03d章 行%d 超出 %d  *** 需复核 ***" % (tag, n, ln, len(lines)))
        bad += 1; continue
    actual = lines[ln - 1]
    if frag in actual:
        print("%-20s 第%03d章 行%-4d OK" % (tag, n, ln))
    else:
        real = [i + 1 for i, l in enumerate(lines) if frag in l]
        print("%-20s 第%03d章 行%d 不符 *** 实现在 %s ***" % (tag, n, ln, real))
        print("      行%d: %s" % (ln, actual.strip()[:110]))
        bad += 1

print("\n不符/需复核：%d / %d\n" % (bad, len(CHECKS)))

# ---- 自行核算第42章那句的实际字数 ----
print("---- 第42章 句长核算 ----")
for n, ln in [(42, 463), (42, 465)]:
    lines = chap(n)
    s = lines[ln - 1].strip()
    # 取引号内正文
    m = re.search(r"[“\"](.+?)[”\"]", s)
    body = m.group(1) if m else s
    han = [c for c in body if re.match(r"[一-鿿]", c)]
    print("  第%03d章 行%d: %s" % (n, ln, body))
    print("     汉字数=%d  含标点总长=%d" % (len(han), len(body)))

# ---- 对照：第42章"十九个字"那一句 ----
print("\n---- 第42章 十九个字对照句 ----")
for i, l in enumerate(chap(42), 1):
    if "十九个字" in l and ("写" in l or "一句" in l):
        print("  行%d: %s" % (i, l.strip()[:120]))

# ---- 设定块行号核对 ----
print("\n---- 设定块 ----")
O = [("01-136-朴哲民第四次出场", "01-时间线.md", 136, "朴哲民第四次出场"),
     ("01-132-第六次", "01-时间线.md", 132, "第六次"),
     ("01-158-第十六个早上", "01-时间线.md", 158, "第十六个早上"),
     ("06-250-第八个早上", "06-术语与分类口径.md", 250, "忠清北道日报第八个早上"),
     ("06-246-第38章新立", "06-术语与分类口径.md", 246, "第 38 章新立的三条纪律"),
     ("04-286-第42章索引", "04-正文格式规范.md", 286, "第42章"),
     ("03-277-第43章旧名", "03-人物弧线节点表.md", 277, "第43章《七个空格》"),
     ("03-280-第46章旧名", "03-人物弧线节点表.md", 280, "第46章《不给你看》")]
for tag, f, ln, frag in O:
    lines = others(f)
    if ln > len(lines):
        print("%-22s %s 行%d 超出 %d *** 需复核 ***" % (tag, f, ln, len(lines))); continue
    if frag in lines[ln - 1]:
        print("%-22s %s 行%-4d OK" % (tag, f, ln))
    else:
        real = [i + 1 for i, l in enumerate(lines) if frag in l]
        print("%-22s %s 行%d 不符 *** 实现在 %s ***" % (tag, f, ln, real))
        print("      行%d: %s" % (ln, lines[ln - 1].strip()[:110]))
