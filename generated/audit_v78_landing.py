# -*- coding: utf-8 -*-
"""核对 03-人物弧线节点表 §七/§八 登记的 97-120 章落点是否在正文中成立。
做法：抽取每章登记描述里的关键名词（中文词，长度>=2），逐个在对应正文章节中查找。
"""
import os, re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

def chap(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(ROOT, pat)) if ".bak" not in p]
        if hits:
            return open(hits[0], encoding="utf-8").read()
    return ""

txt = open(os.path.join(ROOT, "others", "03-人物弧线节点表.md"), encoding="utf-8").read()
lines = txt.splitlines()

# 找 §七 §八 区块
start = None
for i, l in enumerate(lines):
    if re.search(r"^#+\s*[七八][\.、]?", l.strip()) or "§七" in l or "§八" in l:
        start = i
        break
block = lines[start:] if start is not None else lines

CN = re.compile(r"[一-鿿]{2,}")
report = []
for l in block:
    m = re.match(r"^\|\s*(?:\*\*)?(\d{3})(?:\*\*)?\s*(?:[–\-—~]?\s*(\d{3}))?", l.strip())
    if not m:
        continue
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    desc = l
    # 描述中提取候选关键词
    words = CN.findall(desc)
    cand = [w for w in words if len(w) >= 2 and w not in
            ("朴哲民","周砚","姜素妍","李俊赫","金恩贞","森川由紀","高桥信一",
             "韩泰植","郑成德","金玉姬","崔正铁","前田達也","章明欣","恩舒",
             "第三章","第一节","第二节","第三节","第四节","第五节","第六节",
             "第七节","第八节","第九节","第十节","第十一节","第十二节",
             "正文","设定","全书","本章","本章的","本章是","这一章","这一节",
             "这一段","这一句","这一行","这一栏","这一张","这一批","这一组",
             "这一条","这一次","这一份","这一页","这一栏","一个","一条","一份",
             "一次","一天","一年","一样","一个","第一个","第二个","第三个",
             "第四个","第五个","第六个","第七个","第八个","第九个","第十个",
             "已经","仍然","还是","不是","没有","不能","不会","不得","不许",
             "必须","可以","应该","当时","之后","之前","之后","现在","后来",
             "第一卷","第二卷","第三卷","第四卷","第五卷","第六卷","第七卷","第八卷",
             "状态","节点","落点","弧线","正文","全书","完成","开始","结束",
             "唯一","两个","三个","四个","五个","六个","七个","八个","九个","十个",
             "写着","写的是","写明","写成","改成","改回","记为","改成","不再",
             "不改","未动","不动","未归","牺牲","发现","确认","核对","提出",
             "推翻","后移","前移","因为","所以","如果","但是","而且","以及","或者",
             "这句话","这一行","这一节","这一处","此处","此处","以下","以上","其中",
             "同一","不同","相同","一致","不符","矛盾","冲突","问题","错误",
             "时间","数字","日期","表格","表格","材料","记录","登记","名单","编号",
             "第118","第119","第120","第117","第116","第115","第114","第113",
             "第112","第111","第110","第109","第108","第107","第106","第105",
             "第104","第103","第102","第101","第100","第99","第98","第97")]
    seen = set(); cand = [c for c in cand if not (c in seen or seen.add(c))]
    if not cand:
        continue
    body = "".join(chap(n) for n in range(lo, hi + 1))
    missing = [c for c in cand if c not in body]
    if missing:
        report.append((lo, hi, missing, l.strip()[:190]))

print("03 §七/§八 中登记落点、但关键描述词在正文找不到的条目：\n")
for lo, hi, missing, l in report:
    print("  登记 %d-%d  缺词: %s" % (lo, hi, "、".join(missing)))
    print("      %s\n" % l)
if not report:
    print("（无）")
