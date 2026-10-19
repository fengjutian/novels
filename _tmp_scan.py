import pathlib, re

files = ['第94章 排在后面.md', '第95章 各缺一环.md', '第96章 三个时间.md']
for f in files:
    p = pathlib.Path('content/chichao-beijing') / f
    t = p.read_text(encoding='utf-8')
    print(f, 'ascii_single:', t.count(chr(39)), 'ascii_double:', t.count(chr(34)))
    for m in re.finditer(r".{0,14}" + re.escape(chr(39)) + r".{0,20}", t):
        print('    ', repr(m.group()))
