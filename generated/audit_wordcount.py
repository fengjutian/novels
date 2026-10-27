# -*- coding: utf-8 -*-
"""
全书「N 个字」自校：每一处"N个字"若紧邻一个引号短语，核算其实际汉字数并比对。
本书反复用"X个字"作为叙事装置（强调"每数有来源"），故每一处都必须与实际字数相符。
"""
import os, re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

CN_NUM = {"零":0,"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,
          "十":10,"百":100}
def cn2int(s):
    if s.isdigit():
        return int(s)
    if s in CN_NUM:
        return CN_NUM[s]
    m = re.fullmatch(r"([一二两三四五六七八九])?十([一二三四五六七八九])?", s)
    if m:
        a = CN_NUM.get(m.group(1) or "一", 1)
        b = CN_NUM.get(m.group(2) or "", 0)
        return a * 10 + b
    return None

# 数字 + 个字
NUMWORD = re.compile(r"([0-9]{1,3}|[零一二两三四五六七八九十百]{1,4})\s*个\s*字")
# 引号短语（中文双引号 / 弯引号 / 单引号）
QUOTES = re.compile(r"[“\"]([^”\"]{1,40})[”\"]")

def han(s):
    return len(re.findall(r"[一-鿿]", s))

rows = []
for n in range(1, 121):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat))
                if os.path.dirname(p) == ROOT]
        if hits:
            path = hits[0]; break
    else:
        continue
    lines = open(path, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines, 1):
        qs = [(m.start(), m.end(), m.group(1)) for m in QUOTES.finditer(line)]
        for m in NUMWORD.finditer(line):
            val = cn2int(m.group(1))
            if val is None or val < 2 or val > 30:
                continue
            # 最近的前置引号（在前 30 字内结束）
            prev = [q for q in qs if 0 <= m.start() - q[1] <= 30]
            nxt = [q for q in qs if 0 <= q[0] - m.end() <= 30]
            target = None; rel = ""
            if prev:
                q = prev[-1]; target = q[2]; rel = "前"
            elif nxt:
                q = nxt[0]; target = q[2]; rel = "后"
            if target is None:
                continue
            h = han(target)
            if h == val:
                continue
            # 排除"整段话字数"型用法（引号内超过 12 字且不像是短术语）
            if h > 12:
                continue
            rows.append((n, i, val, h, rel, target, line.strip()))

print("「N个字」与实际短语字数不符的条目：共 %d 处\n" % len(rows))
cur = None
for n, i, val, h, rel, target, line in rows:
    if n != cur:
        print("---- 第%d章 ----" % n); cur = n
    print("  L%-4d 声称 %d 字 / 实际 %d 字  「%s」（引号在%s）" % (i, val, h, target, rel))
    print("        %s" % line[:150])
