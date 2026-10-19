import pathlib, re

FILES = ['第94章 排在后面.md', '第95章 各缺一环.md', '第96章 三个时间.md']


def convert(text):
    out = []
    d_open = True
    s_open = True
    for ch in text:
        if ch == '"':
            out.append('\u201c' if d_open else '\u201d')
            d_open = not d_open
        elif ch == "'":
            out.append('\u2018' if s_open else '\u2019')
            s_open = not s_open
        else:
            out.append(ch)
    return ''.join(out), d_open, s_open


for f in FILES:
    p = pathlib.Path('content/chichao-beijing') / f
    raw = p.read_bytes()
    text = raw.decode('utf-8')
    new, d_bad, s_bad = convert(text)
    assert d_bad, (f, 'odd double quotes')
    assert s_bad, (f, 'odd single quotes')
    p.write_bytes(new.encode('utf-8'))
    print(f, 'converted; ascii_d=', new.count('"'), 'ascii_s=', new.count("'"),
          'cn_open=', new.count('\u201c'), 'cn_close=', new.count('\u201d'),
          'sopen=', new.count('\u2018'), 'sclose=', new.count('\u2019'))
