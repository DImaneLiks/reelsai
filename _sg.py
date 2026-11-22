# ================================================================ ГРАФ СЕН-ЖЕРМЕН
WIG = (226, 222, 214); WIG_D = (178, 172, 164); WIG_L = (246, 244, 238)
SKIN_G = (226, 196, 172); SKIN_GD = (190, 156, 134)
BROW = (54, 40, 34)
COAT_G = (36, 40, 66); COAT_GL = (60, 66, 100)
LACE = (244, 240, 230)
DIAM = (220, 240, 255)

def sghead(d, x, hy, r, look=0.0, glow=0.0, smile=1.0, age=0.0):
    """портрет по гравюре Томассена: напудренный парик с буклями над ушами, высокий лоб,
    тёмные дугообразные брови, большие тёмные миндалевидные глаза, длинный прямой нос,
    маленький рот с тонкой полуулыбкой, мягкий округлый подбородок, гладко выбрит"""
    lw = max(3, int(r * 0.035)); thin = max(2, int(r * 0.018))
    # парик сзади (косичка-хвост закрыт)
    P(d, [(x - r * 0.95, hy - r * 0.6), (x - r * 1.05, hy + r * 0.4), (x - r * 0.9, hy + r * 0.95), (x + r * 0.9, hy + r * 0.95),
          (x + r * 1.05, hy + r * 0.4), (x + r * 0.95, hy - r * 0.6)], WIG_D, lw)
    # лицо: овальное, полноватое
    fb = [x - r * 0.78, hy - r * 1.02, x + r * 0.78, hy + r * 1.08]
    d.ellipse(fb, fill=SKIN_G, outline=INK, width=lw)
    d.chord(fb, 95, 265, fill=mix(SKIN_G, (120, 80, 64), 0.1))
    d.arc([x - r * 0.38, hy + r * 0.82, x + r * 0.38, hy + r * 1.18], 25, 155, fill=SKIN_GD, width=thin)     # второй подбородок
    for s in (-1, 1):
        d.ellipse([x + s * r * 0.45 - r * 0.18, hy + r * 0.2, x + s * r * 0.45 + r * 0.18, hy + r * 0.45], fill=mix(SKIN_G, (220, 130, 120), 0.18))
    # парик: гладкая макушка, высокий лоб
    P(d, [(x - r * 0.85, hy - r * 0.35), (x - r * 0.8, hy - r * 0.95), (x - r * 0.45, hy - r * 1.32), (x, hy - r * 1.42), (x + r * 0.45, hy - r * 1.32),
          (x + r * 0.8, hy - r * 0.95), (x + r * 0.85, hy - r * 0.35), (x + r * 0.7, hy - r * 0.5), (x + r * 0.6, hy - r * 0.78),
          (x + r * 0.3, hy - r * 0.92), (x, hy - r * 0.95), (x - r * 0.3, hy - r * 0.92), (x - r * 0.6, hy - r * 0.78), (x - r * 0.7, hy - r * 0.5)], WIG, lw)
    for j in range(6):
        u = -0.6 + j * 0.24
        LN(d, [(x + u * r * 0.7, hy - r * 0.97), (x + u * r * 1.1, hy - r * 1.3)], thin, WIG_D)
    # букли над ушами: два горизонтальных валика с каждой стороны
    for s in (-1, 1):
        for k, yy in enumerate((-0.25, 0.12)):
            cx, cy = x + s * r * 0.93, hy + yy * r
            d.rounded_rectangle([cx - r * 0.28, cy - r * 0.16, cx + r * 0.28, cy + r * 0.16], int(r * 0.16), fill=WIG, outline=INK, width=thin)
            d.chord([cx - r * 0.28, cy - r * 0.16, cx + r * 0.28, cy + r * 0.16], 20, 160, fill=WIG_D)
            d.ellipse([cx + s * r * 0.12 - r * 0.1, cy - r * 0.1, cx + s * r * 0.12 + r * 0.1, cy + r * 0.1], outline=(150, 144, 136), width=thin)
    # брови: тёмные, высокие, дугой
    for s in (-1, 1):
        ex, ey = x + s * r * 0.3, hy - r * 0.08
        LN(d, [(ex - s * r * 0.17, ey - r * 0.2), (ex, ey - r * 0.3), (ex + s * r * 0.2, ey - r * 0.25)], max(4, int(r * 0.055)), BROW)
        # глаза: большие, тёмные, миндалевидные, чуть прищур
        w_, h_ = r * 0.19, r * 0.085
        up = [(ex - w_ + 2 * w_ * i / 10, ey - h_ * math.sin(math.pi * i / 10) ** 0.8) for i in range(11)]
        lo = [(ex + w_ - 2 * w_ * i / 10, ey + h_ * 0.7 * math.sin(math.pi * i / 10)) for i in range(11)]
        d.polygon(up + lo, fill=(240, 236, 228))
        px = ex + look * w_ * 0.4
        ir = r * 0.085
        d.ellipse([px - ir, ey - ir * 0.95, px + ir, ey + ir * 0.95], fill=mix((60, 40, 30), (230, 190, 90), glow))
        d.ellipse([px - ir * 0.45, ey - ir * 0.45, px + ir * 0.45, ey + ir * 0.45], fill=INK)
        d.ellipse([px - ir * 0.7, ey - ir * 0.6, px - ir * 0.25, ey - ir * 0.15], fill=(255, 255, 255))
        d.line(up, fill=INK, width=max(3, int(r * 0.03)), joint="curve")
        d.line(lo, fill=(120, 90, 76), width=thin)
        d.arc([ex - r * 0.2, ey - r * 0.17, ex + r * 0.2, ey + r * 0.02], 200, 340, fill=SKIN_GD, width=thin)   # складка века
        if age > 0:
            LN(d, [(ex - r * 0.12, ey + r * 0.13), (ex + r * 0.12, ey + r * 0.14)], thin, SKIN_GD)
    # нос: длинный, прямой, с тенью
    nc = mix(SKIN_G, (140, 96, 80), 0.2)
    d.polygon([(x - r * 0.03, hy - r * 0.2), (x + r * 0.06, hy - r * 0.2), (x + r * 0.11, hy + r * 0.3), (x - r * 0.02, hy + r * 0.33)], fill=nc)
    LN(d, [(x + r * 0.05, hy - r * 0.18), (x + r * 0.11, hy + r * 0.26)], thin, (140, 104, 88))
    for s in (-1, 1):
        LN(d, [(x + s * r * 0.08, hy + r * 0.24), (x + s * r * 0.13, hy + r * 0.32), (x + s * r * 0.07, hy + r * 0.38)], thin, (130, 92, 78))
        d.ellipse([x + s * r * 0.05 - r * 0.03, hy + r * 0.35, x + s * r * 0.05 + r * 0.03, hy + r * 0.385], fill=(110, 74, 64))
    # рот: маленький, тонкие губы, загадочная полуулыбка
    sm = r * 0.035 * smile
    LN(d, [(x - r * 0.19, hy + r * 0.6 - sm), (x - r * 0.08, hy + r * 0.62), (x + r * 0.08, hy + r * 0.62), (x + r * 0.19, hy + r * 0.6 - sm)], max(3, int(r * 0.028)), (120, 66, 60))
    d.chord([x - r * 0.11, hy + r * 0.62, x + r * 0.11, hy + r * 0.72], 0, 180, fill=(196, 120, 110))
    for s in (-1, 1):
        d.arc([x + s * r * 0.22 - r * 0.04, hy + r * 0.55, x + s * r * 0.22 + r * 0.04, hy + r * 0.63], 0, 360, fill=SKIN_GD, width=1)
    d.arc([x - r * 0.12, hy + r * 0.78, x + r * 0.12, hy + r * 0.9], 200, 340, fill=SKIN_GD, width=thin)
    for s in (-1, 1):     # лёгкие носогубные складки — мужчина средних лет
        LN(d, [(x + s * r * 0.17, hy + r * 0.33), (x + s * r * 0.27, hy + r * 0.5), (x + s * r * 0.27, hy + r * 0.62)], thin, SKIN_GD)
    d.arc([x - r * 0.3, hy - r * 0.75, x + r * 0.3, hy - r * 0.55], 200, 340, fill=SKIN_GD, width=thin)

def sgbody(d, fd, x, hy, r):
    """тёмно-синий бархатный камзол с золотым шитьём, кружевное жабо, бриллиантовые пуговицы"""
    P(d, [(x - r * 0.7, hy + r * 1.0), (x + r * 0.7, hy + r * 1.0), (x + r * 2.0, hy + r * 1.7), (x + r * 2.55, hy + r * 2.6),
          (x + r * 2.85, H + 50), (x - r * 2.85, H + 50), (x - r * 2.55, hy + r * 2.6), (x - r * 2.0, hy + r * 1.7)], COAT_G, 5)
    for s in (-1, 1):
        LN(fd, [(x + s * r * 0.7, hy + r * 1.1), (x + s * r * 0.95, hy + r * 2.0), (x + s * r * 1.05, H)], max(5, int(r * 0.07)), GOLD)
        LN(d, [(x + s * r * 2.0, hy + r * 1.8), (x + s * r * 2.4, H)], 4, COAT_GL)
    # жабо: каскад кружев
    fd.rectangle([x - r * 0.3, hy + r * 0.7, x + r * 0.3, hy + r * 1.15], fill=SKIN_G)
    RR(fd, [x - r * 0.45, hy + r * 1.0, x + r * 0.45, hy + r * 1.25], LACE, 8, 3)
    P(fd, [(x - r * 0.4, hy + r * 1.2), (x + r * 0.4, hy + r * 1.2), (x + r * 0.5, hy + r * 1.9), (x + r * 0.3, hy + r * 2.5),
           (x, hy + r * 2.75), (x - r * 0.3, hy + r * 2.5), (x - r * 0.5, hy + r * 1.9)], LACE, 3)
    for k in range(5):
        yy = hy + r * (1.4 + k * 0.26)
        ww = r * (0.42 - abs(k - 1.5) * 0.06)
        fd.arc([x - ww, yy - r * 0.08, x + ww, yy + r * 0.12], 20, 160, fill=(196, 190, 178), width=2)
    for j in range(4):
        by = hy + r * (2.0 + j * 0.55)
        for s in (-1, 1):
            bx = x + s * r * 1.15
            fd.polygon([(bx, by - r * 0.08), (bx + r * 0.07, by), (bx, by + r * 0.08), (bx - r * 0.07, by)], fill=DIAM, outline=INK)

def sgbust(im, x, hy, r, T, look=0.0, glow=0.0, hatch=0.15, alpha=1.0, smile=1.0, sparkle=1.0):
    lay, ld = layer(); lay2, fd = layer()
    sgbody(ld, fd, x, hy, r)
    sghead(fd, x, hy, r, look, glow, smile)
    stamp(im, lay, hatch, 0.0, alpha)
    if alpha < 0.999:
        lay2.putalpha(Image.fromarray((np.asarray(lay2.getchannel("A")).astype(np.float32) * alpha).astype(np.uint8)))
    im.paste(lay2, (0, 0), lay2)
    if glow > 0:
        for s in (-1, 1):
            glow_(im, x + s * r * 0.3, hy - r * 0.08, r * 0.4, glow, (255, 210, 120))
    if sparkle > 0:
        d = ImageDraw.Draw(im, "RGBA")
        for j in range(4):
            ph = (T * 0.9 + j * 0.27) % 1
            if ph < 0.25:
                bx = x + (-1) ** j * r * 1.15; by = hy + r * (2.0 + j * 0.55)
                k = math.sin(ph / 0.25 * math.pi) * sparkle
                s_ = r * 0.25 * k
                d.line([(bx - s_, by), (bx + s_, by)], fill=(255, 255, 255, int(230 * k)), width=3)
                d.line([(bx, by - s_), (bx, by + s_)], fill=(255, 255, 255, int(230 * k)), width=3)

def sgfig(d, fd, x, feet, h, T=0.0, face=1, look=0.0, seed=0, **kw):
    """граф в полный рост: камзол до колен, белые чулки, туфли с пряжками"""
    r = h * 0.075
    hy = feet - h + r * 1.4
    top = hy + r * 1.25; hem = feet - h * 0.3; sw = r * 1.4
    for s in (-1, 1):
        fx = x + s * r * 0.45
        LN(d, [(fx, hem - r), (fx, feet - r * 0.2)], r * 0.55, (232, 228, 220))
        P(d, [(fx - r * 0.35, feet - r * 0.25), (fx + face * r * 0.75, feet - r * 0.15), (fx + face * r * 0.75, feet + r * 0.05), (fx - r * 0.35, feet + r * 0.05)], (20, 18, 18), 3)
        bx0, bx1 = sorted((fx + face * r * 0.1, fx + face * r * 0.35)); d.rectangle([bx0, feet - r * 0.28, bx1, feet - r * 0.1], fill=GOLD)
    P(d, [(x - sw, top), (x + sw, top), (x + sw * 1.3, hem), (x - sw * 1.3, hem)], COAT_G)
    for s in (-1, 1):
        LN(d, [(x + s * r * 0.4, top + r * 0.3), (x + s * r * 0.55, hem)], max(4, int(r * 0.1)), GOLD)
        sh = (x + s * sw, top + r * 0.4)
        LN(d, [sh, (x + s * sw * 1.2, top + r * 2.4), (x + s * sw * 1.15, top + r * 3.6)], r * 0.6, COAT_G)
        fd.ellipse([x + s * sw * 1.15 - r * 0.3, top + r * 3.5, x + s * sw * 1.15 + r * 0.3, top + r * 4.1], fill=SKIN_G, outline=INK, width=3)
        RR(fd, [x + s * sw * 1.15 - r * 0.35, top + r * 3.25, x + s * sw * 1.15 + r * 0.35, top + r * 3.55], LACE, 4, 2)
    fd.rectangle([x - r * 0.3, hy + r * 0.7, x + r * 0.3, top + r * 0.2], fill=SKIN_G)
    for k in range(3):
        yy = top + r * k * 0.4; ww = r * (0.45 - k * 0.08)
        P(fd, [(x - ww, yy), (x + ww, yy), (x, yy + r * 0.55)], LACE, 2)
    sghead(fd, x, hy, r, look)

_fig_any0 = fig_any
def fig_any(d, fd=None, kind="man", **s):
    if kind == "count":
        return sgfig(d, fd or d, **s)
    if kind == "oldlady":
        old = HAIRS[:]
        for i in range(4): HAIRS[i] = (200, 198, 194)
        try:
            return _fig_any0(d, fd, kind="lady", **s)
        finally:
            HAIRS[:] = old
    return _fig_any0(d, fd, kind=kind, **s)

# ---------------------------------------------------------------- фоны и предметы
def salon(T, wall=(70, 54, 46)):
    im, d = new(wall)
    vgrad(d, mix(wall, (20, 14, 12), 0.4), wall, 0, 1300)
    for j in range(5):
        x = 60 + j * 220
        RR(d, [x, 380, x + 160, 1150], mix(wall, (110, 90, 70), 0.4), 6, 4)
        d.rectangle([x + 18, 400, x + 142, 1130], outline=GOLD + (120,), width=3)
    glow(im, 540, 480, 420, 0.6, (250, 200, 120)); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 1300, W, H], fill=(84, 60, 44)); LN(d, [(0, 1300), (W, 1300)], 6)
    for k in range(8):
        LN(d, [(k * 150 - 300, H), (540 + (k - 3.5) * 60, 1300)], 3, (66, 46, 34))
    return im, d

def frame_portrait(im, x, y, w, h, T, r, year=None, alpha=1.0, ka=1.0):
    """портрет графа в золотой раме"""
    d = ImageDraw.Draw(im, "RGBA")
    RR(d, [x - w / 2 - 22, y - h / 2 - 22, x + w / 2 + 22, y + h / 2 + 22], GOLD, 8, 5)
    d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=(52, 40, 34))
    im2 = im.copy()
    sgbust(im2, x, y - h * 0.08, r, T, hatch=0.12, sparkle=0)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=int(255 * alpha))
    im.paste(im2, (0, 0), m)
    d = ImageDraw.Draw(im, "RGBA")
    if year:
        label(d, x, y + h / 2 + 70, year, ka, YEL, 72)

def violin(d, x, y, s=1.0):
    c = (150, 76, 34)
    d.ellipse([x - 70 * s, y, x + 70 * s, y + 130 * s], fill=c, outline=INK, width=4)
    d.ellipse([x - 55 * s, y - 100 * s, x + 55 * s, y + 10 * s], fill=c, outline=INK, width=4)
    LN(d, [(x, y - 260 * s), (x, y + 110 * s)], 10 * s, (30, 22, 18))
    d.ellipse([x - 16 * s, y - 290 * s, x + 16 * s, y - 250 * s], fill=(30, 22, 18))
    for s_ in (-1, 1):
        d.arc([x + s_ * 22 * s - 10 * s, y - 20 * s, x + s_ * 22 * s + 10 * s, y + 40 * s], 0, 360, fill=INK, width=3)

def flask(d, x, y, s=1.0, c=(120, 220, 140), a=255):
    P(d, [(x - 22 * s, y - 120 * s), (x + 22 * s, y - 120 * s), (x + 22 * s, y - 50 * s), (x + 90 * s, y + 80 * s), (x - 90 * s, y + 80 * s), (x - 22 * s, y - 50 * s)], (210, 226, 230, int(a * 0.7)), 4)
    P(d, [(x - 55 * s, y + 15 * s), (x + 55 * s, y + 15 * s), (x + 86 * s, y + 76 * s), (x - 86 * s, y + 76 * s)], c + (a,), 0)
    RR(d, [x - 28 * s, y - 140 * s, x + 28 * s, y - 118 * s], (120, 90, 60), 3, 3)

def diamond(d, x, y, s=1.0, crack=0.0):
    pts = [(x - 160 * s, y - 40 * s), (x - 90 * s, y - 120 * s), (x + 90 * s, y - 120 * s), (x + 160 * s, y - 40 * s), (x, y + 170 * s)]
    P(d, pts, DIAM, 5)
    for p in [(x - 90 * s, y - 120 * s), (x + 90 * s, y - 120 * s)]:
        LN(d, [p, (x, y - 40 * s)], 3, (150, 180, 200))
    LN(d, [(x - 160 * s, y - 40 * s), (x + 160 * s, y - 40 * s)], 3, (150, 180, 200))
    for xx in (-90, 0, 90):
        LN(d, [(x + xx * s, y - 40 * s), (x, y + 170 * s)], 3, (150, 180, 200))
    if crack > 0:
        LN(d, [(x - 100 * s, y - 100 * s), (x - 40 * s, y - 40 * s), (x - 60 * s, y + 10 * s), (x + 10 * s, y + 70 * s)], 6, (40, 40, 50, int(255 * crack)))

def chateau(d, x, base, s=1.0):
    c = (210, 204, 186)
    d.rectangle([x - 380 * s, base - 260 * s, x + 380 * s, base], fill=c, outline=INK, width=5)
    for k in range(-3, 4):
        RR(d, [x + k * 100 * s - 26 * s, base - 200 * s, x + k * 100 * s + 26 * s, base - 110 * s], (60, 70, 80), 3, 3)
    for k, hh in ((-1, 1.0), (0, 1.3), (1, 1.0)):
        tx = x + k * 300 * s
        d.rectangle([tx - 70 * s, base - (260 + 140 * hh) * s, tx + 70 * s, base - 260 * s], fill=c, outline=INK, width=5)
        P(d, [(tx - 90 * s, base - (260 + 140 * hh) * s), (tx, base - (260 + 320 * hh) * s), (tx + 90 * s, base - (260 + 140 * hh) * s)], (66, 72, 84), 5)
    for k in (-2, -1, 1, 2):
        tx = x + k * 150 * s
        LN(d, [(tx, base - 260 * s), (tx, base - 330 * s)], 14 * s, (66, 72, 84))

def coin(d, x, y, rr, gold=0.0):
    c = mix((170, 96, 56), (240, 196, 70), gold)
    d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c, outline=INK, width=5)
    d.ellipse([x - rr * 0.8, y - rr * 0.8, x + rr * 0.8, y + rr * 0.8], outline=mix(c, INK, 0.3), width=4)
    text_c(d, (x, y), "XII", F(int(rr * 0.6), 9), mix(c, INK, 0.45))

def tomb(d, x, base, s=1.0, text="1784"):
    P(d, [(x - 140 * s, base), (x - 140 * s, base - 260 * s), (x - 100 * s, base - 330 * s), (x + 100 * s, base - 330 * s), (x + 140 * s, base - 260 * s), (x + 140 * s, base)], (150, 150, 146), 5)
    LN(d, [(x, base - 300 * s), (x, base - 160 * s)], 14 * s, (90, 90, 88)); LN(d, [(x - 50 * s, base - 260 * s), (x + 50 * s, base - 260 * s)], 14 * s, (90, 90, 88))
    text_c(d, (x, base - 90 * s), text, F(int(54 * s), 9), (70, 70, 68))

def book(d, x, y, w, h, title=None, lines=8):
    RR(d, [x - w / 2 - 14, y - h / 2 - 10, x + w / 2 + 14, y + h / 2 + 14], (90, 50, 34), 8, 5)
    d.rectangle([x - w / 2, y - h / 2, x - 4, y + h / 2], fill=PAPER, outline=INK, width=3)
    d.rectangle([x + 4, y - h / 2, x + w / 2, y + h / 2], fill=PAPER, outline=INK, width=3)
    for side in (-1, 1):
        for j in range(lines):
            yy = y - h / 2 + 60 + j * (h - 100) / lines
            x0 = x + side * 30 if side > 0 else x - w / 2 + 30
            LN(d, [(x0, yy), (x0 + w / 2 - 70 - (j % 3) * 30, yy)], 4, (150, 130, 110))
    if title:
        text_c(d, (x - w / 4, y - h / 2 + 30), title, F(30, 9), INK)

def compass_square(d, x, y, s=1.0, c=GOLD):
    LN(d, [(x - 120 * s, y + 100 * s), (x, y - 120 * s), (x + 120 * s, y + 100 * s)], 14 * s, c)
    LN(d, [(x - 130 * s, y - 10 * s), (x, y + 110 * s), (x + 130 * s, y - 10 * s)], 14 * s, c)
    text_c(d, (x, y + 10 * s), "G", F(int(60 * s), 9), c)

# ================================================================ СЦЕНЫ
def fogs(im, T, k=0.6):
    lay, ld = layer()
    for j in range(7):
        x = (j * 210 + T * (30 + j * 8)) % (W + 400) - 200
        y = 1150 + (j % 3) * 110
        ld.ellipse([x - 340, y - 70, x + 340, y + 70], fill=(200, 206, 210, int(70 * k)))
    lay = lay.filter(ImageFilter.GaussianBlur(30))
    im.paste(lay, (0, 0), lay)

@shot(0.0, zoom=(1.45, 1.3), cx=540, cy=900, title=("ОН", "НЕ СТАРЕЛ", RED))
def s_hook(T, t):
    im, d = new((26, 18, 16))
    g = 0.7 + 0.3 * ramp(T, WS("L01", 2) - 0.05, WS("L01", 2) + 0.15)
    glow(im, 540, 880, 640, 0.9, (160, 100, 40))
    sgbust(im, 540, 900, 210, T, glow=g * (0.85 + 0.15 * math.sin(T * 9)))
    im = flash(im, 0.5 * (1 - ramp(T, WS("L01", 2), WS("L01", 2) + 0.25)) * (T > WS("L01", 2)), (255, 230, 170))
    return im

@shot(WS("L01", 3) - 0.1, zoom=(1.1, 1.0), cx=540, cy=1000, title=("ЕГО ВИДЕЛИ", "ПОСЛЕ СМЕРТИ", RED))
def s_hook2(T, t):
    im, d = new((30, 34, 40))
    vgrad(d, (18, 22, 30), (60, 64, 70), 0, 1350)
    d.rectangle([0, 1350, W, H], fill=(44, 50, 40)); LN(d, [(0, 1350), (W, 1350)], 5)
    d.ellipse([820, 520, 940, 640], fill=(220, 224, 228))
    tomb(d, 540, 1500, 1.5, "† 1784")
    t_c = WS("L01", 12)
    if T > t_c:
        k = ramp(T, t_c, t_c + 0.15)
        LN(d, [(470, 1050), (520, 1150), (490, 1260), (560, 1400)], 7, (30, 30, 30, int(255 * k)))
    fogs(im, T, 0.7)
    spots = [(WS("L01", 5), 230, 1420, "1789"), (WS("L01", 6), 860, 1380, "1793"), (WS("L01", 9), 540, 1470, "1821")]
    for j, (t0, x, feet, yr) in enumerate(spots):
        if T > t0:
            nxt = spots[j + 1][0] if j + 1 < len(spots) else 99
            a_ = ramp(T, t0, t0 + 0.12) * (1 - 0.6 * ramp(T, nxt, nxt + 0.15))
            put_layer(im, fig_layer([dict(kind="count", x=x, feet=feet, h=620 if j < 2 else 760, T=T, face=1 if x < 540 else -1)], 0.3), a_)
            d = ImageDraw.Draw(im, "RGBA")
            label(d, x, feet - (700 if j < 2 else 850), yr, pop(T, t0), YEL, 84)
    for t0, _, _, _ in spots:
        im = flash(im, 0.35 * (1 - ramp(T, t0, t0 + 0.15)) * (T > t0), (220, 230, 255))
    im = flash(im, 0.5 * (1 - ramp(T, t_c, t_c + 0.25)) * (T > t_c), (255, 250, 240))
    return im

@shot(AT["L03"] - 0.1, zoom=(1.0, 1.12), cx=540, cy=950, title=("ГРАФ", "СЕН-ЖЕРМЕН", YEL))
def s_name(T, t):
    im, d = salon(T)
    sgbust(im, 540, 860, 190, T)
    a = WS("L03", 6)
    if T > a:
        im = dim(im, 0.4 * ramp(T, a, a + 0.3), (10, 8, 8))
        for j, (s_, w) in enumerate((("ИМЯ", 6), ("РОДИНА", 8), ("ВОЗРАСТ", 11))):
            t0 = WS("L03", w) - 0.1
            if T > t0:
                x = 200 + j * 340
                lay = icon_layer(lambda ld, s_=s_, x=x: (ld.rounded_rectangle([x - 150, 1120, x + 150, 1290], 12, fill=PAPER, outline=INK, width=4),
                                                         text_c(ld, (x, 1165), s_, F(40, 9), INK), text_c(ld, (x, 1235), "?", F(80, 9), RED)), x, 1200, pop(T, t0))
                put_layer(im, lay)
    return im

@shot(AT["L05"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=1000, title=("«Я ВИДЕЛ", "КЛЕОПАТРУ»", YEL))
def s_cleo(T, t):
    im, d = new((200, 170, 110))
    vgrad(d, (230, 180, 110), (200, 150, 90), 0, 1250)
    glow(im, 540, 520, 300, 0.8, (255, 230, 160)); d = ImageDraw.Draw(im, "RGBA")
    for (px, ph, pw) in ((250, 420, 360), (700, 520, 460), (1000, 300, 260)):
        P(d, [(px - pw, 1250), (px, 1250 - ph), (px + pw, 1250)], (196, 156, 96), 5)
        LN(d, [(px, 1250 - ph), (px + pw * 0.35, 1250)], 3, (150, 116, 70))
    d.rectangle([0, 1250, W, H], fill=(210, 176, 120)); LN(d, [(0, 1250), (W, 1250)], 5)
    im = dim(im, 0.35 * ramp(T, WS("L05", 3), WS("L05", 3) + 0.4), (40, 30, 30))
    sgbust(im, 540, 1150, 150, T, look=0.4, glow=0.3)
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 270, 640, "КЛЕОПАТРА", pop(T, WS("L05", 1)), WHITE, 56)
    label(d, 810, 760, "ХРИСТОС", pop(T, WS("L05", 3)), WHITE, 56)
    return im

@shot(AT["L04"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=1050, title=("ЭЛИКСИР", "БЕССМЕРТИЯ", RED))
def s_elixir(T, t):
    im, d = salon(T, (56, 40, 40))
    sgbust(im, 540, 820, 140, T, look=0.3)
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 1180, W, H], fill=(230, 224, 210)); LN(d, [(0, 1180), (W, 1180)], 5)
    for x in (220, 540, 860):
        d.ellipse([x - 140, 1230, x + 140, 1330], fill=(250, 248, 244), outline=INK, width=4)
        d.ellipse([x - 80, 1250, x + 80, 1310], fill=(170, 96, 60) if x != 540 else (250, 248, 244))
    a = WS("L04", 11)
    if T > a:
        k = ramp(T, a, a + 0.4)
        glow(im, 700, 1000, 220, k, (150, 255, 170))
        put_layer(im, icon_layer(lambda ld: flask(ld, 700, 1040, 0.8, (110, 230, 140)), 700, 1040, pop(T, a)))
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 540, 640, "НЕ ЕЛ НИ КРОШКИ", ramp(T, WS("L04", 4), WS("L04", 4) + 0.3), WHITE, 56)
    return im

@shot(AT["L02"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=1000, title=("ЧЕРЕЗ 50 ЛЕТ", "ТО ЖЕ ЛИЦО", RED))
def s_same(T, t):
    im, d = salon(T)
    t50 = WS("L02", 9)
    old = T > t50
    figures(im, [dict(kind="oldlady" if old else "lady", x=300, feet=1880, h=860 if old else 900, T=T, face=1, seed=1, c=(90, 80, 90) if old else (150, 60, 70))], 0.25)
    figures(im, [dict(kind="count", x=760, feet=1900, h=1080, T=T, face=-1, look=-0.5)], 0.22)
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 300, 820, "1760" if old else "1710", 1.0, RED if old else YEL, 110)
    if T > WS("L02", 13):
        label(d, 760, 600, "ТОТ ЖЕ ВОЗРАСТ", pop(T, WS("L02", 13)), WHITE, 60)
    im = flash(im, 0.6 * (1 - ramp(T, t50, t50 + 0.3)) * old, (255, 250, 240))
    return im

@shot(AT["L06"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=1050, title=("1784", "СМЕРТЬ?", RED))
def s_death(T, t):
    im, d = new((40, 44, 48))
    vgrad(d, (30, 34, 40), (70, 72, 74), 0, 1350)
    d.rectangle([0, 1350, W, H], fill=(50, 56, 44)); LN(d, [(0, 1350), (W, 1350)], 5)
    d.ellipse([780, 300, 900, 420], fill=(220, 224, 228))
    tomb(d, 540, 1450, 1.4, "1784")
    for x in (150, 930):
        LN(d, [(x, 1350), (x, 800)], 18, (30, 28, 26))
        for j in range(4):
            LN(d, [(x, 900 + j * 90), (x + (-1) ** j * 120, 820 + j * 90)], 8, (30, 28, 26))
    label(d, 540, 640, "ЭККЕРНФЁРДЕ, ГЕРМАНИЯ", ramp(T, WS("L06", 9), WS("L06", 9) + 0.3), WHITE, 46)
    return im

@shot(AT["L07"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=1000, title=("1785", "ОН СНОВА ЗДЕСЬ", RED))
def s_masons(T, t):
    im, d = new((30, 26, 30))
    glow(im, 540, 900, 520, 0.6, (120, 90, 60))
    d = ImageDraw.Draw(im, "RGBA")
    RR(d, [190, 500, 890, 1340], PAPER, 6, 6)
    text_c(d, (540, 570), "СПИСОК ГОСТЕЙ", F(46, 9), INK)
    names = ["Месмер", "Калиостро", "Лавуазье?", "…", "СЕН-ЖЕРМЕН", "…"]
    for j, n in enumerate(names):
        y = 660 + j * 80
        c = RED if n == "СЕН-ЖЕРМЕН" else (90, 80, 70)
        text_c(d, (540, y), n, F(44 if c == RED else 38, 9 if c == RED else 10), c)
    a = WS("L07", 4)
    if T > a:
        k = ramp(T, a, a + 0.3)
        d.rounded_rectangle([300, 940, 780, 1020], 30, outline=RED + (int(255 * k),), width=8)
    if T > WS("L07", 11):
        put_layer(im, icon_layer(lambda ld: compass_square(ld, 540, 1220, 0.8), 540, 1220, pop(T, WS("L07", 11))))
    return im

@shot(AT["L08"] - 0.2, zoom=(1.0, 1.06), cx=540, cy=1000, title=("ЗАГАДКА", "№1", YEL))
def s_grave(T, t):
    im, d = new((44, 46, 46))
    vgrad(d, (34, 36, 40), (70, 70, 66), 0, 1300)
    d.rectangle([0, 1300, W, H], fill=(56, 60, 44)); LN(d, [(0, 1300), (W, 1300)], 5)
    book(d, 540, 820, 700, 420, "ЦЕРКОВНАЯ КНИГА", 6)
    a = WS("L08", 4)
    if T > a:
        d.rounded_rectangle([580, 760, 860, 840], 20, outline=RED + (int(255 * ramp(T, a, a + 0.3)),), width=7)
    b = WS("L08", 8)
    if T > b:
        k = pop(T, b)
        label(d, 540, 1200, "МОГИЛА: ?", k, RED, 90)
    return im

@shot(AT["L09"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=1000, title=("ЗАГАДКА", "№2", YEL))
def s_coin(T, t):
    im, d = salon(T, (50, 40, 34))
    figures(im, [dict(kind="prince", x=180, feet=1950, h=1000, T=T, face=1, look=0.6, c=(120, 40, 40))], 0.25)
    sgbust(im, 820, 900, 120, T, look=-0.4, sparkle=0)
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 200, 760, "КАЗАНОВА", pop(T, WS("L09", 2)), WHITE, 56)
    a = WS("L09", 6); g = ramp(T, a, WS("L09", 10) + 0.2)
    if g > 0.3:
        glow(im, 600, 1250, 260, g, (255, 210, 90)); d = ImageDraw.Draw(im, "RGBA")
    coin(d, 600, 1250, 130, g)
    return im

@shot(AT["L10"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=1000, title=("ЗАГАДКА", "№3", YEL))
def s_archive(T, t):
    im, d = new((40, 32, 28))
    for row in range(5):
        y = 500 + row * 230
        d.rectangle([60, y + 180, 1020, y + 200], fill=(90, 62, 40), outline=INK, width=3)
        for j in range(11):
            x = 80 + j * 86
            RR(d, [x, y + 20 + (j % 3) * 10, x + 70, y + 180], [(150, 120, 72), (120, 100, 70), (160, 140, 100)][(j + row) % 3], 3, 3)
    d.rectangle([380, 1180, 700, 1270], fill=PAPER, outline=INK, width=4)
    text_c(d, (540, 1225), "ДЕЛО: СЕН-ЖЕРМЕН", F(26, 9), INK)
    a = WS("L10", 9)
    k = ramp(T, a - 0.2, END["L10"])
    if k > 0:
        glow(im, 540, 1500, 700, k, (250, 120, 40)); d = ImageDraw.Draw(im, "RGBA")
        flames(d, 540, 1700, 1100, 700 * k, T, 12)
        im = dim(im, 0.25 * k, (60, 10, 0))
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 540, 1100, "НАПОЛЕОН III", ramp(T, WS("L10", 2), WS("L10", 2) + 0.3), WHITE, 56)
    if T > WS("L10", 11):
        label(d, 540, 950, "1871", pop(T, WS("L10", 11)), RED, 120)
    return im

@shot(AT["L11"] - 0.2, zoom=(1.0, 1.08), cx=540, cy=900, title=("КЕМ", "ОН БЫЛ?", YEL))
def s_ask(T, t):
    im, d = new((26, 20, 30))
    glow(im, 540, 820, 620, 0.85, (120, 90, 60))
    g = ramp(T, WS("L11", 6), WS("L11", 7) + 0.3)
    sgbust(im, 540, 740, 170, T, glow=g, alpha=1 - ramp(T, END["L11"] - 0.3, END["L11"] + 0.3))
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 250, 1150, "МОШЕННИК?", pop(T, WS("L11", 0)), RED, 60)
    label(d, 830, 1150, "АЛХИМИК?", pop(T, WS("L11", 1)), WHITE, 60)
    label(d, 540, 1290, "БЕССМЕРТНЫЙ?", pop(T, WS("L11", 7)), YEL, 66)
    return im

@shot(END["L11"] + 0.3, title=None)
def s_end(T, t):
    im, d = new((14, 12, 12))
    k = ramp(T, END["L11"] + 0.3, END["L11"] + 0.8)
    text_c(d, (540, 820), "ТАЙНЫ ИСТОРИИ", F(96, 9), mix((14, 12, 12), RED, k))
    text_c(d, (540, 950), "ГРАФ СЕН-ЖЕРМЕН", F(56, 9), mix((14, 12, 12), WHITE, k))
    k2 = ramp(T, END["L11"] + 1.0, END["L11"] + 1.5)
    d.rounded_rectangle([230, 1060, 850, 1160], 26, fill=mix((14, 12, 12), (44, 40, 38), k2))
    text_c(d, (540, 1110), "Новые выпуски в профиле", F(44, 10), mix((14, 12, 12), WHITE, k2))
    return im
