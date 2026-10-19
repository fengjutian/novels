# -*- coding: utf-8 -*-
"""扫描正文中「X个字 / X行 / X个词 / X句话」等自报计数，与实际字符串长度比对。
只读，不修改任何章节文件。
"""
import re
import sys
import glob
import os

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "content", "chichao-beijing")

CN_NUM = {
    "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6,
    "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12,
    "十三": 13, "十四": 14, "十五": 15, "十六": 16, "十七": 17,
    "十八": 18, "十九": 19, "二十": 20, "二十一": 21, "二十二": 22,
    "二十三": 23, "二十四": 24, "二十五": 25,
}

# 「这/那/一共/共计/总共/数/写/输/读/改/划掉 + 可选汉字 + 中文数字 + 个字」
PAT = re.compile(
    r'“([^”]{1,20})”[^。！？\n]{0,6}?([一二两三四五六七八九十]+)\s*个字'
)

# 跨行型：提示框「上面写着五个字：」后跟下一行的裸字符串
PAT2 = re.compile(
    r'(?:写着|写着：|写着:)\s*([一二两三四五六七八九十]+)\s*个字[：:]?\s*$'
)


def count_chars(s):
    """统计字符串的 CJK 字符数。"""
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def is_ascii_word(s):
    """纯拉丁/数字内容，不适用「X个字」的汉字计数判据。"""
    return count_chars(s) == 0


def main():
    files = sorted(glob.glob(os.path.join(BASE, "第*.md")))
    bad = []
    skipped = []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
        name = os.path.basename(path)
        for idx, line in enumerate(lines, 1):
            for m in PAT.finditer(line):
                quoted, num = m.group(1), m.group(2)
                if num not in CN_NUM:
                    continue
                if is_ascii_word(quoted):
                    skipped.append((name, idx, quoted, num))
                    continue
                actual = count_chars(quoted)
                claimed = CN_NUM[num]
                if actual != claimed:
                    bad.append((name, idx, quoted, num, claimed, actual))
            # 跨行：这一行以「写着五个字：」结尾，下一行是被计数的裸字符串
            m2 = PAT2.search(line.rstrip("\n"))
            if m2 and idx < len(lines):
                num = m2.group(1)
                if num not in CN_NUM:
                    continue
                nxt = lines[idx].strip().strip("“”\"'")
                if not nxt or is_ascii_word(nxt):
                    continue
                actual = count_chars(nxt)
                claimed = CN_NUM[num]
                if actual != claimed:
                    bad.append((name, idx + 1, nxt, num, claimed, actual))

    out = []
    for name, idx, quoted, num, claimed, actual in bad:
        out.append("%s:%d  声称「%s」为 %s，实际 %d 字  ->  应改为「%d」"
                   % (name, idx, quoted, num, actual, claimed))
    out.append("---")
    out.append("扫描 %d 章，发现错算 %d 处" % (len(files), len(bad)))
    if skipped:
        out.append("")
        out.append("跳过（拉丁文本，不适用汉字计数判据）:")
        for name, idx, quoted, num in skipped:
            out.append("  %s:%d  「%s」=%s" % (name, idx, quoted, num))
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
