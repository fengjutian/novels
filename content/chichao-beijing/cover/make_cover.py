# -*- coding: utf-8 -*-
"""《赤潮北境》封面生成器
方案 A：夜海 · 第十行（冷黑 + 赤潮）
方案 B：通报 · 第十行（纸白 + 黑字 + 红章）
纯 Pillow 绘制，无外部素材。输出 1200x1600 / 600x800。
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 1600
HORIZON = 520

SERIF_HEAVY = "C:/Windows/Fonts/Source Han Serif SC Heavy (TrueType).ttf"
SERIF = "C:/Windows/Fonts/NotoSerifSC-VF.ttf"
SANS = "C:/Windows/Fonts/Noto Sans SC (TrueType).otf"
SANS_B = "C:/Windows/Fonts/Noto Sans SC Bold (TrueType).otf"

TITLE = "赤潮北境"
VOL = "第一部 · 水下"
PEN = "山月雨下"

ROW_VALS = ["3", "11", "2", "—", "4", "1", "—", "6", "2", "", "0", "—", "1", "3", "—", "2"]


def gfont(path, size):
    return ImageFont.truetype(path, size)


def draw_spaced(d, xy, text, font, fill, spacing=0, anchor_left="lt"):
    """逐字绘制并加字距，返回总宽度。"""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill, anchor=anchor_left)
        x += d.textlength(ch, font=font) + spacing
    return x - xy[0] - spacing


# ---------------------------------------------------------------- 方案 A
def a_gradient():
    stops = [
        (0.00, (5, 7, 10)),
        (0.16, (7, 9, 13)),
        (0.27, (16, 12, 14)),
        (0.320, (46, 18, 17)),
        (0.345, (13, 23, 26)),
        (0.55, (8, 19, 24)),
        (0.72, (13, 15, 18)),
        (0.86, (44, 14, 12)),
        (1.00, (62, 16, 12)),
    ]
    ys = np.linspace(0, 1, H)
    pos = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=float)
    out = np.zeros((H, 3))
    for c in range(3):
        out[:, c] = np.interp(ys, pos, cols[:, c])
    return Image.fromarray(np.repeat(out[:, None, :], W, axis=1).astype(np.uint8), "RGB")


def a_glow(img, center, radius, color, strength=140):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    for r, s in ((radius, 0.30), (radius * 0.62, 0.5), (radius * 0.34, 0.85)):
        a = int(strength * s)
        d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=tuple(int(c * a / 255) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.45))
    return Image.fromarray(np.clip(np.asarray(img, float) + np.asarray(layer, float), 0, 255).astype(np.uint8), "RGB")


def a_horizon(img):
    """海平线：一条极细的亮线 + 上方一段被压扁的赤色雾带"""
    band = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(band)
    d.rectangle([0, HORIZON - 58, W, HORIZON + 8], fill=(132, 38, 24))
    band = band.filter(ImageFilter.GaussianBlur(30))
    img = Image.fromarray(np.clip(np.asarray(img, float) + np.asarray(band, float) * 0.72, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    d.line([0, HORIZON, W, HORIZON], fill=(140, 58, 44), width=2)
    return img


def a_noise(img, amount=6.5, seed=20251103):
    arr = np.asarray(img, dtype=np.float32)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, amount, (H, W, 1))
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8), "RGB")


def a_vignette(img, power=1.7, strength=0.5):
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = W / 2, H * 0.46
    d = np.sqrt(((xx - cx) / (W * 0.72)) ** 2 + ((yy - cy) / (H * 0.72)) ** 2)
    mask = np.clip(1.0 - strength * (d ** power), 0, 1)[..., None]
    return Image.fromarray((np.asarray(img, float) * mask).astype(np.uint8), "RGB")


def a_table(img, y0=986, y1=1508, header=True):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, x1 = 96, 1104
    n = 16
    step = (y1 - y0) / n
    fnum = gfont(SANS, 17)
    fval = gfont(SANS, 17)
    fzero = gfont(SANS_B, 58)
    flabel = gfont(SERIF, 19)

    # 表头
    if header:
        fh = gfont(SANS, 13)
        d.text((x0 + 2, y0 - 26), "序号", font=fh, fill=(255, 255, 255, 55), anchor="lm")
        d.text((x0 + 130, y0 - 26), "单位", font=fh, fill=(255, 255, 255, 55), anchor="lm")
        d.text((x1 - 2, y0 - 26), "例数", font=fh, fill=(255, 255, 255, 55), anchor="rm")
        d.line([x0, y0 - 10, x1, y0 - 10], fill=(255, 255, 255, 62), width=1)

    for i in range(n):
        y = y0 + i * step
        zero_row = (i == 9)
        if zero_row:
            d.line([x0, y, x1, y], fill=(200, 88, 58, 130), width=2)
        else:
            d.line([x0, y, x1, y], fill=(255, 255, 255, 42), width=1)
        d.text((x0 + 2, y + step * 0.5), f"{i+1:02d}", font=fnum, fill=(255, 255, 255, 88), anchor="lm")
        if zero_row:
            d.text((x0 + 130, y + step * 0.5), "仁川", font=flabel, fill=(226, 110, 76, 225), anchor="lm")
            d.text((x1 - 2, y + step * 0.5), "0", font=fzero, fill=(236, 118, 78, 248), anchor="rm")
    d.line([x0, y1, x1, y1], fill=(255, 255, 255, 42), width=1)

    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def a_type(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 竖排主标题
    ft = gfont(SERIF_HEAVY, 176)
    x, y, gap = 884, 92, 26
    for ch in TITLE:
        d.text((x, y), ch, font=ft, fill=(238, 235, 228, 255), anchor="lt")
        y += 176 + gap

    # 卷次 + 细线
    fv = gfont(SERIF, 31)
    d.text((1104, 868), VOL, font=fv, fill=(216, 208, 198, 200), anchor="rt")
    d.line([938, 902, 1104, 902], fill=(196, 78, 48, 200), width=2)

    # 左上角学名 / 时间锚点
    fs = gfont(SANS, 15)
    d.text((96, 92), "PSEUDOVIBRIO  RUBESCENS", font=fs, fill=(255, 255, 255, 105), anchor="lt")
    d.text((96, 120), "T-30  /  第一卷", font=fs, fill=(255, 255, 255, 68), anchor="lt")

    # 引语（置于夜空，避免与赤潮底色打架）
    fq = gfont(SERIF, 31)
    d.text((96, 300), "它不通过空气传播，", font=fq, fill=(228, 220, 209, 158), anchor="lt")
    d.text((96, 348), "也不通过体液传播。", font=fq, fill=(228, 220, 209, 158), anchor="lt")
    d.text((96, 396), "只通过你今晚吃的那条鱼。", font=fq, fill=(228, 220, 209, 158), anchor="lt")

    # 署名
    fa = gfont(SANS, 30)
    w = draw_spaced(d, (96, 1538), PEN, fa, (236, 230, 220, 215), spacing=8)
    fsmall = gfont(SANS, 18)
    d.text((96 + w + 22, 1548), "著", font=fsmall, fill=(236, 230, 220, 120), anchor="lt")

    layer = layer.filter(ImageFilter.GaussianBlur(0.3))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def a_table_frag(img):
    """只露出的那一行：第十行，仁川，零。表格从画面下缘裁掉，暗示后面还有。"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, x1 = 96, 1104
    y = 1408

    for yy in (1472, 1536, 1600):
        d.line([x0, yy, x1, yy], fill=(255, 255, 255, 34), width=1)

    d.line([x0, y, x1, y], fill=(255, 255, 255, 78), width=1)
    d.line([x0, y, x0 + 96, y], fill=(206, 92, 60, 235), width=4)

    fh = gfont(SANS, 21)
    d.text((x0 + 116, y - 14), "第 10 行", font=fh, fill=(255, 255, 255, 120), anchor="lb")
    fl = gfont(SERIF, 23)
    d.text((x0 + 248, y - 14), "仁川", font=fl, fill=(228, 116, 80, 240), anchor="lb")
    fnote = gfont(SANS, 15)
    d.text((x1, y - 16), "例数", font=fnote, fill=(255, 255, 255, 90), anchor="rb")

    fzero = gfont(SANS_B, 104)
    d.text((x1 + 6, y - 30), "0", font=fzero, fill=(232, 114, 74, 245), anchor="rb")

    layer = layer.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def build_a(variant=1):
    img = a_gradient()
    img = a_glow(img, (620, 1530), 780, (152, 40, 22), 150)
    img = a_glow(img, (240, 596), 380, (110, 28, 18), 55)
    img = a_horizon(img)
    img = a_noise(img, 6.5)
    if variant == 1:
        img = a_table(img, 986, 1508, header=True)
    elif variant == 2:
        img = a_table(img, 566, 1476, header=False)
    elif variant == 3:
        img = a_table(img, 746, 1486, header=True)
    else:
        img = a_table_frag(img)
    img = a_type(img)
    img = a_vignette(img)
    img = a_noise(img, 2.8, seed=7)
    return img


# ---------------------------------------------------------------- 方案 B
def b_paper():
    base = np.zeros((H, W, 3), dtype=np.float32)
    base[:, :] = (238, 232, 220)
    yy, xx = np.mgrid[0:H, 0:W]
    # 纸纹与轻微受光不匀
    shade = 1.0 - 0.10 * ((xx / W - 0.35) ** 2 + (yy / H - 0.3) ** 2)
    base *= shade[..., None]
    rng = np.random.default_rng(11)
    base += rng.normal(0, 3.2, (H, W, 1))
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    # 纤维
    fib = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(fib)
    for _ in range(2600):
        x, y = rng.integers(0, W), rng.integers(0, H)
        d.line([x, y, x + rng.integers(2, 9), y + rng.integers(-1, 2)], fill=int(rng.integers(6, 18)))
    fib = fib.filter(ImageFilter.GaussianBlur(0.4))
    img = Image.fromarray(np.clip(np.asarray(img, float) - np.asarray(fib, float)[..., None], 0, 255).astype(np.uint8), "RGB")
    return img


def b_stamp(img, cx, cy, r):
    """红色印章：双圈 + 竖排'赤潮' + 旋转"""
    s = Image.new("RGBA", (r * 3, r * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    red = (176, 44, 32, 210)
    c = r * 1.5
    d.ellipse([c - r, c - r, c + r, c + r], outline=red, width=int(r * 0.09))
    d.ellipse([c - r * 0.86, c - r * 0.86, c + r * 0.86, c + r * 0.86], outline=red, width=max(2, int(r * 0.03)))
    f = gfont(SERIF_HEAVY, int(r * 0.62))
    d.text((c, c - r * 0.30), "赤", font=f, fill=red, anchor="mm")
    d.text((c, c + r * 0.30), "潮", font=f, fill=red, anchor="mm")
    # 做旧：随机擦除
    rng = np.random.default_rng(5)
    arr = np.asarray(s).astype(np.float32)
    alpha = arr[..., 3] / 255.0
    holes = rng.random((r * 3, r * 3)) < 0.055
    alpha *= (~holes)
    arr[..., 3] = alpha * 255
    s = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    s = s.rotate(-7, resample=Image.BICUBIC, expand=False)
    img.paste(s, (int(cx - r * 1.5), int(cy - r * 1.5)), s)
    return img


def b_table(img):
    d = ImageDraw.Draw(img)
    x0, x1 = 96, 1104
    y0, y1 = 604, 1352
    n = 16
    step = (y1 - y0) / n
    ink = (26, 22, 20)
    fnum = gfont(SANS, 18)
    fval = gfont(SANS, 18)
    fzero = gfont(SANS_B, 52)
    flabel = gfont(SERIF, 20)

    for i in range(n):
        y = y0 + i * step
        zero_row = (i == 9)
        d.line([x0, y, x1, y], fill=(ink if zero_row else (150, 140, 128)), width=3 if zero_row else 1)
        d.text((x0 + 2, y + step * 0.5), f"{i+1:02d}", font=fnum, fill=(96, 88, 78), anchor="lm")
        if zero_row:
            d.text((x0 + 132, y + step * 0.5), "仁川", font=flabel, fill=(150, 26, 18), anchor="lm")
            d.text((x1 - 2, y + step * 0.5), "0", font=fzero, fill=(150, 26, 18), anchor="rm")
        elif ROW_VALS[i]:
            d.text((x1 - 2, y + step * 0.5), ROW_VALS[i], font=fval, fill=(70, 64, 58), anchor="rm")
    d.line([x0, y1, x1, y1], fill=(150, 140, 128), width=1)
    return img


def b_type(img):
    d = ImageDraw.Draw(img)
    ink = (20, 17, 15)

    fs = gfont(SANS, 16)
    d.text((96, 88), "赤潮拟菌  /  PSEUDOVIBRIO RUBESCENS", font=fs, fill=(120, 110, 98), anchor="lt")
    d.text((1104, 88), "通报 001", font=fs, fill=(120, 110, 98), anchor="rt")
    d.line([96, 122, 1104, 122], fill=(60, 54, 48), width=2)

    ft = gfont(SERIF_HEAVY, 156)
    x, y = 92, 176
    for ch in TITLE:
        d.text((x, y), ch, font=ft, fill=ink, anchor="lt")
        x += 156 + 14

    fv = gfont(SERIF, 34)
    d.text((96, 404), VOL, font=fv, fill=(70, 62, 54), anchor="lt")
    d.line([96, 462, 460, 462], fill=(150, 26, 18), width=3)

    fq = gfont(SERIF, 27)
    d.text((96, 494), "它不通过空气传播，也不通过体液传播。只通过你今晚吃的那条鱼。", font=fq, fill=(64, 57, 50), anchor="lt")

    fa = gfont(SANS, 34)
    w = draw_spaced(d, (96, 1488), PEN, fa, (30, 26, 23), spacing=10)
    fsmall = gfont(SANS, 19)
    d.text((96 + w + 22, 1500), "著", font=fsmall, fill=(90, 82, 74), anchor="lt")

    # 页脚编号
    d.text((1104, 1498), "T-30", font=gfont(SANS, 18), fill=(130, 120, 108), anchor="rt")
    return img


def build_b():
    img = b_paper()
    img = b_type(img)
    img = b_table(img)
    img = b_stamp(img, 1010, 300, 82)
    return img


# ---------------------------------------------------------------- 输出
def main():
    which = (sys.argv[1] if len(sys.argv) > 1 else "a4").lower()
    tag = which.upper()
    if which in ("a", "a1", "a4"):
        img = build_a(4)
        tag = "夜海"
    elif which == "a2":
        img = build_a(2)
        tag = "夜海2"
    elif which == "a3":
        img = build_a(3)
        tag = "夜海3"
    elif which == "a4":
        img = build_a(4)
        tag = "夜海"
    elif which == "b":
        img = build_b()
        tag = "通报"
    else:
        raise SystemExit("usage: a | a2 | a3 | a4 | b")
    png = f"cover_{tag}_1200x1600.png"
    jpg = f"cover_{tag}_600x800.jpg"
    img.save(png)
    img.resize((600, 800), Image.LANCZOS).save(jpg, quality=93)
    print("saved", png, jpg)


if __name__ == "__main__":
    main()
