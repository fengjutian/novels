# -*- coding: utf-8 -*-
"""
《赤潮北境》审稿新增发现：「N 个字」自校失准 —— 第 2 批修复（可重放）。

背景：本书反复用"X 个字"作叙事装置（强调"每数有来源"），因此每一处"N个字"
      若紧邻一个被点名的短语，该短语的字数必须与所称数字一致。
计数标准：不计标点（依据第 42 章"一个字一个字数过"的十九个字句，全书唯一自校句）。

用法：python generated/fix_batch2.py [--dry]
"""
import os, re, glob, shutil, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(BASE, "content", "chichao-beijing")
BACKUP = os.path.join(BASE, "generated", "_fix2_backup")
DRY = "--dry" in sys.argv

def chap_path(n):
    for pat in ("第%02d章*.md" % n, "第%d章*.md" % n):
        hits = [p for p in glob.glob(os.path.join(CH, pat))
                if os.path.dirname(p) == CH and ".bak" not in p]
        if hits:
            return hits[0]
    raise SystemExit("找不到第%d章" % n)

EDITS = []
def E(ch, old, new, cnt, note):
    EDITS.append((ch, old, new, cnt, note))

# W01 第5章：引号内"与水温有关"=5 字
E(5, "听到这六个字的时候松了一口气", "听到这五个字的时候松了一口气", 1, "W01 与水温有关=5字")
# W02 第14章："合并建议"=4 字
E(14, "他报的时候写了三个字：“合并建议”", "他报的时候写了四个字：“合并建议”", 1, "W02 合并建议=4字")
# W03 第15章："不打算问，但要记。"=7 字
E(15, "这六个字是他自己的设计", "这七个字是他自己的设计", 1, "W03 不打算问但要记=7字")
# W04 第18章：5 处"那六个字"均指"感染性原因待排"（7 字）
E(18, "那六个字", "那七个字", 5, "W04 感染性原因待排=7字")
# W05 第21章："无肉眼可见病变"=7 字
E(21, "结论仍是六个字：无肉眼可见病变。", "结论仍是七个字：无肉眼可见病变。", 1, "W05 无肉眼可见病变=7字")
# W06 第23章：删掉的"不详"=2 字
E(23, "她删掉了最后那六个字。", "她删掉了最后那两个字。", 1, "W06 不详=2字")
# W07 第23章："仍在核实中"=5 字
E(23, "这六个字，是港务厅答复里写的。", "这五个字，是港务厅答复里写的。", 1, "W07 仍在核实中=5字")
# W08 第26章："釜山港、暂缓执行情况"=9 字
E(26, "追加了一行任务，六个字：釜山港、暂缓执行情况。",
     "追加了一行任务，九个字：釜山港、暂缓执行情况。", 1, "W08 釜山港暂缓执行情况=9字")
# W09 第35章："第五栏的字是我写的"=9 字（5 处）
E(35, "七个字", "九个字", 5, "W09 第五栏的字是我写的=9字")
# W10 第37章："朝方。南下。"=4 字（不计标点）—— 用长锚定，避免误伤"三百八十六个字"
E(37, "第一行上写着六个字。朝方。南下。", "第一行上写着四个字。朝方。南下。", 1, "W10 朝方南下=4字")
E(37, "他把这六个字抄了一遍", "他把这四个字抄了一遍", 1, "W10 朝方南下=4字")
# W11 第37章："第五栏的字是我写的"=9 字（3 处）
E(37, "七个字", "九个字", 3, "W11 第五栏的字是我写的=9字")
# W12 第44章："中国东北防疫工作组"=9 字（4 处）
E(44, "六个字", "九个字", 4, "W12 中国东北防疫工作组=9字")
# W13 第46章："下一批向南"=5 字
E(46, "听见无线电重复那六个字", "听见无线电重复那五个字", 1, "W13 下一批向南=5字")
# W14 第63章："样本处置需要"=6 字
E(63, "拒绝用“样本处置需要”四个字一笔带过", "拒绝用“样本处置需要”六个字一笔带过", 1, "W14 样本处置需要=6字")
# W15 第78章："被绕行，非被阻止"=7 字（3 处）
E(78, "六个字", "七个字", 3, "W15 被绕行非被阻止=7字")
# W16 第81章："口径未统一"=5 字
E(81, "括号里写的都是这六个字：口径未统一。", "括号里写的都是这五个字：口径未统一。", 1, "W16 口径未统一=5字")
# W17 第85章："朝方无请求"=5 字
E(85, "第二行是六个字：朝方无请求。", "第二行是五个字：朝方无请求。", 1, "W17 朝方无请求=5字")
# W18 第89章：原稿第七行 11 字，删"本报"2 字后 9 字
E(89, "第七行的七个字在她自己的卷宗里。", "第七行的九个字在她自己的卷宗里。", 1, "W18 第七行=9字")
# W19 第95章："缺一，不等于同一种缺"=9 字
E(95, "她在这张纸的右上角写了六个字：**“缺一，不等于同一种缺。”**",
     "她在这张纸的右上角写了九个字：**“缺一，不等于同一种缺。”**", 1, "W19 缺一不等于同一种缺=9字")
# W20/W21 第104章："第六栏以下无实质内容"=10 字（2 处）
E(104, "他把这七个字看了三遍。", "他把这十个字看了三遍。", 1, "W20 第六栏以下无实质内容=10字")
E(104, "所以“第六栏以下无实质内容”这七个字，与原件不符。",
      "所以“第六栏以下无实质内容”这十个字，与原件不符。", 1, "W21 同上")
# W22 第104章："按转引本交"=5 字
E(104, "备注栏他写了六个字：**“按转引本交。”**", "备注栏他写了五个字：**“按转引本交。”**", 1, "W22 按转引本交=5字")
# W23 第106章："制高观察哨，前移六米"=9 字
E(106, "那个点旁边写着六个字：", "那个点旁边写着九个字：", 1, "W23 制高观察哨前移六米=9字")
# W24 第109章："我知道"=3 字
E(109, "他把“我知道”四个字写成了“与原始材料无关”。",
      "他把“我知道”三个字写成了“与原始材料无关”。", 1, "W24 我知道=3字")
# W25 第109章："与本人无关"=5 字
E(109, "写完他把“与本人无关”四个字划掉了。", "写完他把“与本人无关”五个字划掉了。", 1, "W25 与本人无关=5字")
# W26/W27 第111章："聚集性社会骚乱"=7 字（2 处）
E(111, "归类一栏写的是六个字。", "归类一栏写的是七个字。", 1, "W26 聚集性社会骚乱=7字")
E(111, "“六个字不看解释，别人会不懂。”", "“七个字不看解释，别人会不懂。”", 1, "W27 同上")

# ---------------------------------------------------------------- 执行
def load(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom

def save(path, txt, bom):
    data = txt.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)

groups = {}
for ch, old, new, cnt, note in EDITS:
    groups.setdefault(chap_path(ch), []).append((old, new, cnt, note))

print("=" * 74)
print("「N个字」自校失准修复  共 %d 条" % len(EDITS))
print("=" * 74)

errors, plans = [], []
for p, items in groups.items():
    txt, bom = load(p)
    ok = True
    for old, new, cnt, note in items:
        got = txt.count(old)
        if got != cnt:
            errors.append("  [%s] 命中 %d 次（期望 %d）：%s" %
                          (os.path.basename(p), got, cnt, note))
            ok = False
            continue
        txt = txt.replace(old, new)
    if ok:
        plans.append((p, bom, txt, len(items)))

if errors:
    print("\n断言失败，未写盘：")
    for e in errors:
        print(e)
    sys.exit(1)

if DRY:
    print("\n--dry：断言全部通过。%d 处改动，涉及 %d 个文件。" % (len(EDITS), len(plans)))
    for p, _, _, n in plans:
        print("   %-36s %d 处" % (os.path.basename(p), n))
    sys.exit(0)

if os.path.isdir(BACKUP):
    shutil.rmtree(BACKUP)
os.makedirs(BACKUP)
for p in groups:
    shutil.copy2(p, os.path.join(BACKUP, os.path.basename(p)))
print("\n已备份 %d 个文件到 generated/_fix2_backup/" % len(groups))

for p, bom, txt, n in plans:
    save(p, txt, bom)
    print("  写入 %-36s %d 处" % (os.path.basename(p), n))

print("\n完成：%d 处改动，%d 个文件。" % (len(EDITS), len(plans)))
