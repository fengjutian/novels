# -*- coding: utf-8 -*-
"""全书具名人物跨章出现序列：找长时间消失后复现、卷间断线等人物状态异常。"""
import os, re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

NAMES = ["朴哲民","周砚","姜素妍","李俊赫","金恩贞","森川由紀","高桥信一",
         "韩泰植","郑成德","金玉姬","崔正铁","前田達也","章明欣","宋炳洙",
         "孙镐俊","李恩淑","朴在勋","罗淑姬","金恩植","崔正鐵","柳成贤",
         "尹道勋","河正浩","车美兰","南秀英","金敏哲","朴成浩","徐正浩"]

def chap_text(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat)) if ".bak" not in p]
        if hits:
            return open(hits[0], encoding="utf-8").read()
    return ""

texts = {}
for n in range(1, 121):
    texts[n] = chap_text(n)

VOL = {}
for n in range(1, 121):
    VOL[n] = (n - 1) // 15 + 1

print("%-6s %-6s %s" % ("人物", "首见", "出现章序列（按卷分组）"))
print("-" * 100)
report = []
for nm in NAMES:
    seq = [n for n in range(1, 121) if nm in texts[n]]
    if not seq:
        continue
    # 按卷聚合
    byvol = {}
    for n in seq:
        byvol.setdefault(VOL[n], []).append(n)
    seg = " | ".join("卷%d:%s" % (v, ",".join(str(x) for x in byvol[v])) for v in sorted(byvol))
    print("%-6s 第%3d章 %s" % (nm, seq[0], seg))
    # 长间隔
    for a, b in zip(seq, seq[1:]):
        if b - a > 15:
            report.append("  ! %s：第%d章之后空 %d 章，到第%d章复现"
                          % (nm, a, b - a - 1, b))
    # 卷间断线
    vs = sorted(byvol)
    for v1, v2 in zip(vs, vs[1:]):
        if v2 - v1 > 1:
            last = byvol[v1][-1]; first = byvol[v2][0]
            report.append("  ~ %s：卷%d 结束于第%d章，卷%d 首次出现于第%d章"
                          % (nm, v1, last, v2, first))
    if len(seq) <= 3:
        report.append("  * %s 全书仅出现于第%s章" % (nm, ",".join(map(str, seq))))

print("\n===== 异常候选 =====")
for r in report:
    print(r)
