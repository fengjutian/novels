#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《赤潮北境》第 3 轮机械审计 —— 专查前两轮未覆盖的维度。

维度：
  A. 标点与引号形态一致性（直引号 / 半角标点 / 破折号形态 / 省略号）
  B. 正文内 `---`（04 §3.1 禁止）与 `———` 三连、破折号单独成行（§9.6）
  C. 章内时间链：逐章抽取"X点(X分)"时刻，检查是否单调/倒退
  D. 段落级重复：跨章或章内完全相同的正文段落
  E. 章内相邻重复句 / 连续重复段
  F. 阿拉伯数字混入正文（本书正文数字一律中文数字）
  G. 计量单位口径混用（公里/千米、米/公尺、摄氏/华氏）
  H. 结构件缺失：〔本章完〕、卷首行、章节信息块
  I. 规范文件引用了不存在的设定文件（00-统一地理表）

用法: python generated/audit_round3.py [A B C ...]
"""
from __future__ import annotations

import io
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "chichao-beijing"
OTHERS = CONTENT / "others"

CN_NUM = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
}


def cn2int(s: str):
    """中文数字转 int，支持 十一 / 二十 / 二十三 / 三十一 / 一百二十三。"""
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if "百" in s:
        a, _, b = s.partition("百")
        hi = cn2int(a) if a else 1
        return hi * 100 + (cn2int(b) if b else 0)
    if "十" in s:
        a, _, b = s.partition("十")
        hi = cn2int(a) if a else 1
        if hi is None:
            return None
        lo = cn2int(b) if b else 0
        if lo is None:
            return None
        return hi * 10 + lo
    if len(s) == 1 and s in CN_NUM:
        return CN_NUM[s]
    return None


def chapters() -> dict[int, Path]:
    out = {}
    for p in sorted(CONTENT.glob("第*.md")):
        m = re.match(r"第(\d+)章", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def load(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def body_of(text: str) -> str:
    """正文部分：切第一个 '## 一、' 之后。"""
    i = text.find("## 一、")
    return text[i:] if i >= 0 else text


def lines_of(p: Path) -> list[tuple[int, str]]:
    return list(enumerate(load(p).split("\n"), 1))


# ---------- A. 标点与引号 ----------
def task_a(chs):
    out = []
    straight_q = []      # 直双引号 "
    straight_a = []      # 直单引号 '
    halfcomma = []       # 半角逗号后跟汉字
    halfperiod = []      # 半角句点
    bracket_kinds = defaultdict(list)   # 「」『』 vs “”
    ellipsis_wrong = []  # 单点省略 …
    em_dash_kinds = defaultdict(list)   # —— / ―― / ——
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            s = line
            if '"' in s:
                straight_q.append(f"第{n}章 L{ln}: {s.strip()[:60]}")
            if "'" in s:
                straight_a.append(f"第{n}章 L{ln}: {s.strip()[:60]}")
            if re.search(r"[\u4e00-\u9fff],", s):
                halfcomma.append(f"第{n}章 L{ln}: {s.strip()[:60]}")
            if re.search(r"[\u4e00-\u9fff]\.(?!\d)", s):
                halfperiod.append(f"第{n}章 L{ln}: {s.strip()[:60]}")
            if "「" in s or "『" in s:
                bracket_kinds["直角引号"].append(f"第{n}章 L{ln}")
            if "…" in s and "……" not in s:
                ellipsis_wrong.append(f"第{n}章 L{ln}: {s.strip()[:60]}")
            for pat, key in ((r"———", "三连横线"), (r"――", "U+2015 双横线"),
                             (r"—(?!—)", "单个横线"), (r"———", "四连横线")):
                if re.search(pat, s):
                    em_dash_kinds[key].append(f"第{n}章 L{ln}: {s.strip()[:60]}")
    for label, arr in (("直双引号 \"", straight_q), ("直单引号 '", straight_a),
                       ("半角逗号接汉字", halfcomma), ("半角句点接汉字", halfperiod),
                       ("单点省略号", ellipsis_wrong)):
        out.append(f"[{label}] {len(arr)} 处")
        for x in arr[:8]:
            out.append(f"    {x}")
    for k, arr in em_dash_kinds.items():
        out.append(f"[破折号形态 {k}] {len(arr)} 处")
        for x in arr[:8]:
            out.append(f"    {x}")
    if bracket_kinds.get("直角引号"):
        out.append(f"[直角引号「」] {len(bracket_kinds['直角引号'])} 处")
        for x in bracket_kinds["直角引号"][:8]:
            out.append(f"    {x}")
    return out


# ---------- B. 正文内 --- / 三连 / 破折号单独成行 ----------
def task_b(chs):
    out = []
    sep = []       # 正文中的 ---
    dashline = []  # 单独一行只含破折号
    three = []     # ———
    for n, p in sorted(chs.items()):
        text = load(p)
        body = body_of(text)
        base = text[: text.find(body)] if body in text else ""
        blines = body.split("\n")
        offset = base.count("\n")
        for i, line in enumerate(blines, start=1):
            st = line.strip()
            if st == "---":
                sep.append(f"第{n}章 L{i + offset}: 正文内 ---")
            if re.fullmatch(r"—{1,3}\s*", st):
                dashline.append(f"第{n}章 L{i + offset}: {st}")
            if "———" in line:
                three.append(f"第{n}章 L{i + offset}: {st[:60]}")
    out.append(f"[正文内 ---] {len(sep)} 处")
    for x in sep[:15]:
        out.append(f"    {x}")
    out.append(f"[破折号单独成行] {len(dashline)} 处")
    for x in dashline[:15]:
        out.append(f"    {x}")
    out.append(f"[——— 三连] {len(three)} 处")
    for x in three[:15]:
        out.append(f"    {x}")
    return out


# ---------- C. 章内时间链 ----------
TIME_RE = re.compile(r"([零〇一二两三四五六七八九十百]+)点([零〇一二两三四五六七八九十]+)?分?")
# 时刻词前缀，决定该时刻属于哪一天/哪一时段
PERIODS = [("凌晨", 0), ("早上", 1), ("上午", 1), ("中午", 2), ("下午", 3),
           ("傍晚", 4), ("晚上", 5), ("夜里", 5), ("夜", 5), ("晚", 5), ("清晨", 1)]


def minute_of(h, m):
    base = h * 60
    if m is None:
        return base
    mi = cn2int(m) if isinstance(m, str) else m
    if mi is None:
        return base
    if mi >= 60:
        mi = mi % 60
    return base + mi


def task_c(chs):
    out = []
    for n, p in sorted(chs.items()):
        text = load(p)
        body = body_of(text)
        base = text[: text.find(body)] if body in text else ""
        offset = base.count("\n")
        hits = []
        for i, line in enumerate(body.split("\n"), start=1):
            if line.startswith("## "):
                continue
            for m in TIME_RE.finditer(line):
                h = cn2int(m.group(1))
                if h is None or h > 24:
                    continue
                hh = h % 24
                mm = cn2int(m.group(2)) if m.group(2) else None
                # 判周期
                ctx = line[max(0, m.start() - 6): m.start()]
                per = None
                for word, base_h in PERIODS:
                    if word in ctx:
                        per = base_h
                        break
                hits.append((i + offset, m.group(0), hh, minute_of(hh, mm), per, line.strip()[:50]))
        # 只看带明确"点…分"或上下文带周期词的
        seq = [(ln, g, mi, per) for (ln, g, hh, mi, per, _s) in hits if mi is not None]
        if len(seq) < 2:
            continue
        # 单调性检查：同章内，同一时段内的时刻应递增
        regress = []
        prev = None
        for ln, g, mi, per in seq:
            if prev and per == prev[2] and mi < prev[1]:
                regress.append((ln, g, prev[0], per))
            prev = (ln, mi, per, g)
        if regress:
            out.append(f"第{n}章 时序倒退 {len(regress)} 处")
            for ln, g, pg, per in regress[:6]:
                out.append(f"    L{ln}: {g} 出现在 {pg} 之后（同段={per}）")
    return out


# ---------- D. 段落级重复 ----------
def task_d(chs):
    out = []
    seen = defaultdict(list)
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            s = line.strip()
            if len(s) < 25 or s.startswith("#") or s.startswith("---") or s.startswith("**〔"):
                continue
            seen[s].append(f"第{n}章 L{ln}")
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    out.append(f"完全相同的正文段落（≥25字）：{len(dups)} 组")
    for k, v in sorted(dups.items(), key=lambda kv: -len(kv[1]))[:20]:
        out.append(f"    {len(v)}× {'; '.join(v[:5])}")
        out.append(f"        {k[:70]}")
    return out


# ---------- E. 相邻重复句 ----------
def task_e(chs):
    out = []
    for n, p in sorted(chs.items()):
        text = load(p)
        body = body_of(text)
        base = text[: text.find(body)] if body in text else ""
        offset = base.count("\n")
        blines = body.split("\n")
        paras = [(i + offset, l.strip()) for i, l in enumerate(blines, 1)
                 if l.strip() and not l.startswith("#") and not l.startswith("---")]
        for i in range(len(paras) - 1):
            a, b = paras[i][1], paras[i + 1][1]
            if a == b:
                out.append(f"第{n}章 L{paras[i][0]}: 相邻两段完全相同")
        # 同段内重复句
        for ln, s in paras:
            sents = [x for x in re.split(r"[。！？]", s) if len(x.strip()) >= 12]
            for k in range(len(sents) - 1):
                if sents[k].strip() == sents[k + 1].strip():
                    out.append(f"第{n}章 L{ln}: 同段内相邻两句重复：{sents[k].strip()[:40]}")
    return out


# ---------- F. 阿拉伯数字混入正文 ----------
def task_f(chs):
    out = []
    for n, p in sorted(chs.items()):
        body = body_of(load(p))
        base = load(p)
        offset = (base[: base.find(body)] if body in base else "").count("\n")
        for i, line in enumerate(body.split("\n"), 1):
            st = line.strip()
            if not st or st.startswith("#"):
                continue
            # 允许：T+NN 表头、编号如 0327-0447、III 型、章节引用
            hits = re.findall(r"\d+", st)
            if hits:
                out.append(f"第{n}章 L{i + offset}: {st[:70]}")
    out.append(f"正文含阿拉伯数字的行：{len(out)} 行")
    return out[:60]


# ---------- G. 计量单位口径 ----------
UNITS = {
    "公里": "千米", "千米": "公里",
    "公尺": "米", "摄氏度": "℃", "华氏": "℉",
    "公升": "升", "公斤": "千克", "公吨": "吨",
}


def task_g(chs):
    out = []
    for n, p in sorted(chs.items()):
        for ln, line in lines_of(p):
            s = line.strip()
            for a, b in UNITS.items():
                if a in s:
                    out.append(f"第{n}章 L{ln}: 用「{a}」（建议口径「{b}」）: {s[:60]}")
    out.append(f"单位口径候选：{len(out)} 行")
    return out[:40]


# ---------- H. 结构件 ----------
def task_h(chs):
    out = []
    miss_end = []
    miss_vol = []
    miss_info = []
    for n, p in sorted(chs.items()):
        text = load(p)
        if "〔本章完〕" not in text:
            miss_end.append(n)
        if not re.match(r"^# 赤潮北境 · 第[一二三四五六七八]卷", text):
            miss_vol.append(n)
        if "**相对时间：" not in text:
            miss_info.append(n)
    out.append(f"缺 〔本章完〕 的章：{len(miss_end)} {miss_end}")
    out.append(f"卷首行格式不符的章：{len(miss_vol)} {miss_vol}")
    out.append(f"缺章节信息块的章：{len(miss_info)} {miss_info}")
    return out


# ---------- I. 设定文件引用完整性 ----------
def task_i(chs):
    out = []
    for f in sorted(OTHERS.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"`(0\d-[^`]+\.md)`", text):
            name = m.group(1)
            if not (OTHERS / name).exists():
                line = text[: m.start()].count("\n") + 1
                out.append(f"{f.name} L{line}: 引用了不存在的设定文件 {name}")
    return out


def main() -> int:
    chs = chapters()
    args = [a.upper() for a in sys.argv[1:]]
    tasks = {
        "A": ("标点与引号形态", task_a),
        "B": ("正文内 --- / 破折号形态", task_b),
        "C": ("章内时间链单调性", task_c),
        "D": ("段落级重复", task_d),
        "E": ("相邻重复句/段", task_e),
        "F": ("正文阿拉伯数字", task_f),
        "G": ("计量单位口径", task_g),
        "H": ("结构件完整性", task_h),
        "I": ("设定文件引用完整性", task_i),
    }
    for key, (title, fn) in tasks.items():
        if args and key not in args:
            continue
        print(f"\n=== {key}. {title} ===")
        for line in fn(chs):
            print("  " + line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
