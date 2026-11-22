
# ================================================================ РАСПУТИН И НОВЫЕ ПЕРСОНАЖИ
_face0 = face
HAIR_R = (50, 37, 29); BEARD_R = (66, 49, 37); STRAND = (108, 84, 62)
SKIN_R = (204, 176, 150); SOCKET = (164, 136, 114)
GOLD = (214, 176, 90)
YEL2 = YEL

def blink(T, ph=0.2):
    k = (T * 0.37 + ph) % 1
    return 0.08 if k < 0.035 else 1.0

def eye_pos(x, hy, r):
    return [(x - r * 0.31, hy - r * 0.16), (x + r * 0.31, hy - r * 0.16)]

def rhead(d, x, hy, r, look=0.0, glow=0.0, eyes=1.0, seed=3, halo=0.0):
    """портрет Распутина анфас: длинные волосы на прямой пробор, глубоко посаженные светлые глаза,
    тяжёлые брови, длинный нос, усы и длинная окладистая борода"""
    lw = max(3, int(r * 0.035))
    if halo > 0:
        d.ellipse([x - r * 1.6, hy - r * 1.9, x + r * 1.6, hy + r * 0.9], outline=GOLD + (int(200 * halo),), width=max(4, int(r * 0.08)))
    # волосы сзади, падают на плечи
    P(d, [(x - r * 0.85, hy - r * 0.8), (x - r * 1.12, hy + r * 0.3), (x - r * 1.22, hy + r * 1.3), (x - r * 1.1, hy + r * 1.95),
          (x + r * 1.1, hy + r * 1.95), (x + r * 1.22, hy + r * 1.3), (x + r * 1.12, hy + r * 0.3), (x + r * 0.85, hy - r * 0.8)], HAIR_R, lw)
    # лицо
    d.ellipse([x - r * 0.76, hy - r * 1.08, x + r * 0.76, hy + r * 1.0], fill=SKIN_R, outline=INK, width=lw)
    d.chord([x - r * 0.76, hy - r * 1.08, x + r * 0.76, hy + r * 1.0], 100, 260, fill=mix(SKIN_R, (90, 66, 54), 0.13))
    # пряди: прямой пробор, волосы закрывают уши
    for s in (-1, 1):
        P(d, [(x + s * r * 0.03, hy - r * 1.13), (x + s * r * 0.55, hy - r * 1.06), (x + s * r * 0.9, hy - r * 0.62), (x + s * r * 1.02, hy + r * 0.2),
              (x + s * r * 0.98, hy + r * 1.25), (x + s * r * 0.74, hy + r * 0.95), (x + s * r * 0.69, hy - r * 0.18),
              (x + s * r * 0.47, hy - r * 0.7), (x + s * r * 0.05, hy - r * 0.93)], HAIR_R, lw)
        for j in range(4):
            LN(d, [(x + s * r * (0.12 + 0.13 * j), hy - r * 1.0), (x + s * r * (0.55 + 0.1 * j), hy - r * 0.5),
                   (x + s * r * (0.72 + 0.06 * j), hy + r * 0.3), (x + s * r * (0.76 + 0.05 * j), hy + r * 1.0)], max(2, int(r * 0.022)), STRAND)
    LN(d, [(x, hy - r * 1.12), (x, hy - r * 0.92)], max(2, int(r * 0.03)), (120, 96, 80))      # пробор
    # глубоко посаженные глаза
    for k, (ex, ey) in enumerate(eye_pos(x, hy, r)):
        s = -1 if k == 0 else 1
        d.ellipse([ex - r * 0.25, ey - r * 0.17, ex + r * 0.25, ey + r * 0.17], fill=SOCKET)
        w_, h_ = r * 0.2, r * 0.1 * max(0.05, eyes)
        if eyes > 0.15:
            up = [(ex - w_ + 2 * w_ * i / 10, ey - h_ * 0.85 * math.sin(math.pi * i / 10) ** 0.8 - s * h_ * 0.15 * (i / 10 - 0.5)) for i in range(11)]
            lo = [(ex + w_ - 2 * w_ * i / 10, ey + h_ * 0.75 * math.sin(math.pi * i / 10) ** 0.9) for i in range(11)]
            d.polygon(up + lo, fill=(236, 230, 220))
            px = ex + look * w_ * 0.4
            ir = r * 0.095
            icol = mix((140, 160, 168), (210, 236, 255), glow)
            d.ellipse([px - ir, ey - ir * 0.9, px + ir, ey + ir * 1.1], fill=icol, outline=(40, 46, 50), width=max(2, int(r * 0.015)))
            d.ellipse([px - ir * 0.42, ey - ir * 0.3, px + ir * 0.42, ey + ir * 0.54], fill=INK)
            d.ellipse([px - ir * 0.75, ey - ir * 0.45, px - ir * 0.3, ey], fill=(255, 255, 255))
            d.polygon(up + [(ex + r * 0.25 * math.cos(-math.pi * i / 16), ey + r * 0.17 * math.sin(-math.pi * i / 16)) for i in range(17)], fill=SOCKET)   # тяжёлое верхнее веко
            d.polygon(lo + [(ex + r * 0.25 * math.cos(math.pi - math.pi * i / 16), ey + r * 0.17 * math.sin(math.pi - math.pi * i / 16)) for i in range(17)], fill=SOCKET)
            d.line(up, fill=INK, width=max(3, int(r * 0.03)), joint="curve")
            d.line(lo, fill=(90, 70, 60), width=max(2, int(r * 0.012)))
            d.line([(ex - w_ * 0.9, ey - h_ * 1.5), (ex + w_ * 0.8, ey - h_ * 1.7)], fill=(130, 104, 88), width=max(2, int(r * 0.012)))   # складка века
        else:
            d.line([(ex - w_, ey), (ex + w_, ey)], fill=INK, width=max(3, int(r * 0.03)))
        LN(d, [(ex - w_ * 0.8, ey + r * 0.15), (ex + w_ * 0.8, ey + r * 0.15)], max(2, int(r * 0.015)), (150, 120, 100))  # мешки под глазами
        # брови: густые, внутренний край ниже — тяжёлый взгляд
        LN(d, [(ex - s * r * 0.2, ey - r * 0.15), (ex + s * r * 0.04, ey - r * 0.22), (ex + s * r * 0.26, ey - r * 0.24)], max(4, int(r * 0.075)), HAIR_R)
    # нос: длинный, прямой — тенью и линией сбоку
    nc = mix(SKIN_R, (120, 84, 66), 0.25)
    d.polygon([(x - r * 0.02, hy - r * 0.2), (x + r * 0.08, hy - r * 0.2), (x + r * 0.13, hy + r * 0.25), (x + r * 0.02, hy + r * 0.3)], fill=nc)
    LN(d, [(x + r * 0.06, hy - r * 0.18), (x + r * 0.12, hy + r * 0.22)], max(2, int(r * 0.02)), (120, 90, 74))
    d.arc([x - r * 0.17, hy + r * 0.22, x - r * 0.03, hy + r * 0.37], 110, 230, fill=INK, width=max(2, int(r * 0.022)))
    d.arc([x + r * 0.03, hy + r * 0.22, x + r * 0.17, hy + r * 0.37], 310, 430, fill=INK, width=max(2, int(r * 0.022)))
    for s_ in (-1, 1):
        d.ellipse([x + s_ * r * 0.07 - r * 0.03, hy + r * 0.32, x + s_ * r * 0.07 + r * 0.03, hy + r * 0.36], fill=(100, 72, 60))
    # борода
    rng_ = np.random.default_rng(seed)
    bp = [(x - r * 0.74, hy + r * 0.05), (x - r * 0.86, hy + r * 0.7), (x - r * 0.72, hy + r * 1.55), (x - r * 0.42, hy + r * 2.35),
          (x - r * 0.12, hy + r * 2.78), (x + r * 0.02, hy + r * 2.55), (x + r * 0.22, hy + r * 2.82), (x + r * 0.48, hy + r * 2.3),
          (x + r * 0.74, hy + r * 1.55), (x + r * 0.86, hy + r * 0.7), (x + r * 0.74, hy + r * 0.05), (x + r * 0.52, hy + r * 0.48),
          (x + r * 0.2, hy + r * 0.44), (x - r * 0.2, hy + r * 0.44), (x - r * 0.52, hy + r * 0.48)]
    P(d, bp, BEARD_R, lw)
    for j in range(26):
        u = rng_.uniform(-0.7, 0.7); v0 = rng_.uniform(0.5, 1.2)
        L = rng_.uniform(0.6, 1.4)
        x0_ = x + u * r; y0_ = hy + v0 * r
        x1_ = x + u * r * 0.55 + rng_.uniform(-0.08, 0.08) * r; y1_ = min(hy + (v0 + L) * r, hy + (2.7 - abs(u) * 1.6) * r)
        LN(d, [(x0_, y0_), ((x0_ + x1_) / 2 + u * r * 0.06, (y0_ + y1_) / 2), (x1_, y1_)], max(2, int(r * 0.02)), STRAND if j % 3 else (40, 30, 24))
    # губы и усы
    d.chord([x - r * 0.13, hy + r * 0.56, x + r * 0.13, hy + r * 0.7], 0, 180, fill=(140, 82, 72), outline=INK, width=max(2, lw - 2))
    for s in (-1, 1):
        P(d, [(x + s * r * 0.02, hy + r * 0.4), (x + s * r * 0.3, hy + r * 0.42), (x + s * r * 0.5, hy + r * 0.62),
              (x + s * r * 0.46, hy + r * 0.82), (x + s * r * 0.24, hy + r * 0.58), (x + s * r * 0.02, hy + r * 0.53)], HAIR_R, max(2, lw - 1))

def rbust(d, fd, x, hy, r):
    """плечи: чёрная поддёвка поверх светлой рубахи, нательный крест"""
    coat = (24, 24, 28)
    P(d, [(x - r * 0.55, hy + r * 0.9), (x + r * 0.55, hy + r * 0.9), (x + r * 2.0, hy + r * 1.8), (x + r * 2.55, hy + r * 2.6),
          (x + r * 2.9, H + 50), (x - r * 2.9, H + 50), (x - r * 2.55, hy + r * 2.6), (x - r * 2.0, hy + r * 1.8)], coat, 5)
    P(d, [(x - r * 0.62, hy + r * 1.0), (x + r * 0.62, hy + r * 1.0), (x + r * 0.95, H + 50), (x - r * 0.95, H + 50)], (206, 196, 174), 4)
    LN(d, [(x + r * 0.35, hy + r * 1.1), (x + r * 0.5, H)], max(4, int(r * 0.05)), (150, 40, 36))          # вышивка по вороту
    for s in (-1, 1):
        P(d, [(x + s * r * 0.62, hy + r * 1.0), (x + s * r * 1.9, hy + r * 1.8), (x + s * r * 1.3, H + 50), (x + s * r * 0.95, H + 50)], coat, 4)
        LN(d, [(x + s * r * 2.1, hy + r * 2.4), (x + s * r * 2.2, H)], 4, (54, 54, 60))
    fd.rectangle([x - r * 0.32, hy + r * 0.6, x + r * 0.32, hy + r * 1.1], fill=SKIN_R)
    # крест на цепочке
    for s in (-1, 1):
        LN(fd, [(x + s * r * 0.55, hy + r * 1.3), (x + s * r * 0.3, hy + r * 2.4), (x, hy + r * 2.95)], max(2, int(r * 0.02)), GOLD)

def rcross(d, x, y, r):
    a = r * 0.06; b = r * 0.22
    RR(d, [x - a, y, x + a, y + b * 1.9], GOLD, 2, 3)
    RR(d, [x - b * 0.6, y + b * 0.4, x + b * 0.6, y + b * 0.4 + a * 2], GOLD, 2, 3)

def bust(im, x, hy, r, T, look=0.0, glow=0.0, eyes=None, hatch=0.18, halo=0.0, alpha=1.0):
    lay, ld = layer(); lay2, fd = layer()
    rbust(ld, fd, x, hy, r)
    rhead(fd, x, hy, r, look, glow, blink(T) if eyes is None else eyes, halo=halo)
    rcross(fd, x, hy + r * 2.9, r)
    stamp(im, lay, hatch, 0.0, alpha)
    if alpha < 0.999:
        lay2.putalpha(Image.fromarray((np.asarray(lay2.getchannel("A")).astype(np.float32) * alpha).astype(np.uint8)))
    im.paste(lay2, (0, 0), lay2)
    if glow > 0:
        for ex, ey in eye_pos(x, hy, r):
            glow_(im, ex, ey, r * 0.35, glow, (170, 220, 255))

def rfig(d, fd, x, feet, h, T=0.0, phase=None, pray=0.0, seed=0, look=0.0, eyes=None, face=1, **kw):
    """Распутин в полный рост: длинная чёрная поддёвка, рубаха с вышивкой, кушак, сапоги"""
    r = h * 0.075
    hy = feet - h + r * 1.4
    top = hy + r * 1.3; hip = feet - h * 0.40; sw = r * 1.5
    hem = feet - h * 0.17
    swing = 0 if phase is None else math.sin(phase)
    coat = (24, 24, 28); shirt = (206, 196, 174)
    for s, k in ((-1, 1), (1, -1)):
        fx = x + s * r * 0.5 + k * swing * r * 0.8
        P(d, [(fx - r * 0.4, hem - r * 0.4), (fx + r * 0.4, hem - r * 0.4), (fx + r * 0.42, feet - r * 0.25), (fx + face * r * 0.85, feet - r * 0.08),
              (fx + face * r * 0.85, feet + r * 0.08), (fx - r * 0.44, feet + r * 0.08)], (16, 14, 14), 3)
        LN(d, [(fx - r * 0.4, hem + r * 0.3), (fx + r * 0.4, hem + r * 0.3)], 3, (64, 60, 58))
    P(d, [(x - sw * 0.9, top), (x + sw * 0.9, top), (x + sw * 1.45, hem), (x - sw * 1.45, hem)], coat)
    P(d, [(x - r * 0.55, top), (x + r * 0.55, top), (x + r * 0.8, hip + r * 1.6), (x - r * 0.8, hip + r * 1.6)], shirt, 3)
    LN(d, [(x + r * 0.2, top + r * 0.3), (x + r * 0.2, top + r * 1.8)], max(3, int(r * 0.08)), (150, 40, 36))
    LN(d, [(x - r * 0.8, hip), (x + r * 0.8, hip)], r * 0.2, (130, 32, 28))
    LN(d, [(x + r * 0.45, hip), (x + r * 0.55, hip + r * 1.0)], max(3, int(r * 0.09)), (130, 32, 28))
    for s in (-1, 1):
        P(d, [(x + s * r * 0.5, top), (x + s * sw * 0.9, top), (x + s * sw * 1.45, hem), (x + s * r * 0.85, hem), (x + s * r * 0.85, hip + r * 1.6)], coat, 4)
        LN(d, [(x + s * sw * 0.95, top + r * 2.0), (x + s * sw * 1.25, hem - r * 0.2)], 3, (56, 56, 62))
    for s in (-1, 1):
        sh = (x + s * sw * 0.9, top + r * 0.4)
        if pray > 0 and s == face:
            hx_, hy_ = lerp(x + s * sw * 1.15, x + s * sw * 1.3, pray), lerp(hip, hy + r * 0.3, pray)
            el = (lerp(x + s * sw * 1.2, x + s * sw * 1.6, pray), lerp(top + r * 2.5, top + r * 1.6, pray))
            LN(d, [sh, el, (hx_, hy_)], r * 0.65, coat)
            hand(d, hx_, hy_, r)
            LN(d, [(hx_ - r * 0.05, hy_ - r * 0.25), (hx_ - r * 0.05, hy_ - r * 0.6)], max(3, int(r * 0.12)), SKIN)   # пальцы для благословения
        else:
            ax = x + s * sw * 1.15 - swing * s * r * 0.5
            LN(d, [sh, (ax, hip - r * 0.1)], r * 0.65, coat)
            hand(d, ax, hip, r)
    fd.rectangle([x - r * 0.3, hy + r * 0.6, x + r * 0.3, top + r * 0.2], fill=SKIN_R)
    rhead(fd, x, hy, r, look, 0.0, blink(T, seed * 0.1) if eyes is None else eyes)
    for s in (-1, 1):
        LN(fd, [(x + s * r * 0.5, top + r * 0.1), (x + s * r * 0.25, top + r * 1.0), (x, top + r * 1.6)], 2, GOLD)
    rcross(fd, x, top + r * 1.6, r)

KIND_COL = {"prince": (30, 30, 40), "doctor": (40, 40, 46), "tsar": (96, 98, 76), "boy": (226, 224, 214),
            "lady": (196, 190, 176), "soldier": (92, 94, 72)}
KIND_BODY = {"prince": "man", "doctor": "man", "tsar": "police", "boy": "man", "lady": "woman", "soldier": "police"}

def fig_any(d, fd=None, kind="man", **s):
    fd = fd or d
    if kind == "rasputin":
        return rfig(d, fd, **s)
    if kind in KIND_BODY:
        s.setdefault("c", KIND_COL[kind])
        vfig(d, fd=fd, kind=kind, body=KIND_BODY[kind], **s)
        if kind == "boy":                                                   # матросский воротник
            x, feet, h = s["x"], s["feet"], s["h"]; r = h * 0.075; top = feet - h + r * 2.7
            P(d, [(x - r * 1.3, top), (x + r * 1.3, top), (x + r * 1.1, top + r * 1.2), (x, top + r * 1.9), (x - r * 1.1, top + r * 1.2)], (40, 60, 110), 3)
            LN(d, [(x - r * 1.0, top + r * 1.0), (x, top + r * 1.6), (x + r * 1.0, top + r * 1.0)], 3, WHITE)
        return
    vfig(d, fd=fd, kind=kind, **s)

def face(d, x, hy, r, f, kind, seed=0, look=0.0, T=0.0):
    if kind in ("man", "woman", "police", "jack"):
        return _face0(d, x, hy, r, f, kind, seed, look, T)
    _face0(d, x, hy, r, f, "x", seed, look, T)
    hair = {"boy": (120, 86, 52), "prince": (22, 20, 22), "doctor": (176, 172, 166), "tsar": (100, 72, 48),
            "lady": HAIRS[(seed + 1) % 4], "soldier": (70, 52, 40)}[kind]
    my = hy + r * 0.58
    if kind == "lady":
        d.ellipse([x - r * 0.45, hy - r * 1.55, x + r * 0.45, hy - r * 0.85], fill=hair, outline=INK, width=3)
    d.chord([x - r * 0.9, hy - r * 1.1, x + r * 0.9, hy + r * 0.2], 180, 360, fill=hair, outline=INK, width=3)
    if kind == "prince":
        LN(d, [(x - f * r * 0.2, hy - r * 1.08), (x - f * r * 0.1, hy - r * 0.5)], 3, (70, 66, 70))
        LN(d, [(x + f * r * 0.1, my - r * 0.06), (x + f * r * 0.55, my - r * 0.1)], max(3, r * 0.07), hair)
    if kind in ("doctor", "tsar"):
        d.chord([x - r * 0.86, hy - r * 0.35, x + r * 0.86, hy + r * 1.3], 0, 180, fill=hair, outline=INK, width=3)
        P(d, [(x + f * r * 0.05, my - r * 0.12), (x + f * r * 0.62, my - r * 0.2), (x + f * r * 0.72, my + r * 0.02),
              (x + f * r * 0.35, my - r * 0.02), (x - f * r * 0.05, my)], mix(hair, INK, 0.2), 3)
    if kind == "doctor":
        ex = x + f * r * 0.12
        for s in (-1, 1):
            cx = ex + s * r * 0.32 + f * r * 0.06; cy = hy - r * 0.08
            d.ellipse([cx - r * 0.25, cy - r * 0.22, cx + r * 0.25, cy + r * 0.22], outline=INK, width=3)
    if kind in ("tsar", "soldier"):
        cap = (100, 102, 78)
        RR(d, [x - r * 0.95, hy - r * 1.55, x + r * 0.95, hy - r * 0.72], cap, 6, 3)
        d.rectangle([x - r * 0.93, hy - r * 1.0, x + r * 0.93, hy - r * 0.76], fill=(150, 40, 36) if kind == "tsar" else (80, 82, 62))
        P(d, [(x + f * r * 0.1, hy - r * 0.76), (x + f * r * 1.15, hy - r * 0.7), (x + f * r * 0.9, hy - r * 0.55), (x, hy - r * 0.62)], (20, 20, 20), 3)
        d.ellipse([x - r * 0.12, hy - r * 1.3, x + r * 0.12, hy - r * 1.06], fill=GOLD, outline=INK, width=2)
    if kind == "lady":
        d.ellipse([x + f * r * 0.22 - r * 0.14, my - r * 0.06, x + f * r * 0.22 + r * 0.14, my + r * 0.1], fill=(170, 80, 76), outline=INK, width=2)
        d.ellipse([x + f * r * 0.42 - r * 0.15, hy + r * 0.2, x + f * r * 0.42 + r * 0.15, hy + r * 0.4], fill=(222, 164, 154))

def fig_layer(specs, hatch=0.3):
    lay, ld = layer(); lay2, fdd = layer()
    for i, s in enumerate(specs):
        fig_any(ld, fd=fdd, **{"seed": i, **s})
    a = np.asarray(lay).astype(np.float32)
    m = (a[..., 3] / 255) * HATCH * hatch
    a[..., :3] = a[..., :3] * (1 - m[..., None]) + np.array(INK, np.float32) * m[..., None]
    out = Image.fromarray(a.astype(np.uint8), "RGBA")
    out.alpha_composite(lay2)
    return out

def put_layer(im, L, alpha=1.0, rot=0.0, center=None, shift=(0, 0)):
    if rot:
        L = L.rotate(rot, resample=Image.BICUBIC, center=center)
    if shift != (0, 0):
        L2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L2.paste(L, (int(shift[0]), int(shift[1])), L); L = L2
    if alpha < 0.999:
        L = L.copy(); L.putalpha(Image.fromarray((np.asarray(L.getchannel("A")).astype(np.float32) * alpha).astype(np.uint8)))
    im.paste(L, (0, 0), L)

def figures(im, specs, hatch=0.3, alpha=1.0):
    put_layer(im, fig_layer(specs, hatch), alpha)

glow_ = glow

# ---------------------------------------------------------------- фоны
def vgrad(d, c1, c2, y0=0, y1=H, n=24):
    for j in range(n):
        d.rectangle([0, y0 + (y1 - y0) * j / n, W, y0 + (y1 - y0) * (j + 1) / n + 1], fill=mix(c1, c2, j / (n - 1)))

def snow(d, T, n=90, k=1.0):
    for i in range(n):
        x = (i * 137.5 + math.sin(T * 0.7 + i) * 30) % W
        y = (i * 251 + T * (70 + (i % 5) * 22)) % H
        s = 3 + i % 4
        d.ellipse([x - s, y - s, x + s, y + s], fill=(236, 238, 240, int(190 * k)))

def izba(d, x, base, s=1.0, lit=True, snowy=True):
    w, h = 400 * s, 300 * s
    d.rectangle([x, base - h, x + w, base], fill=(104, 76, 54), outline=INK, width=5)
    for j in range(1, 8):
        LN(d, [(x, base - h * j / 8), (x + w, base - h * j / 8)], 3, (70, 50, 36))
    P(d, [(x - 30 * s, base - h), (x + w / 2, base - h - 220 * s), (x + w + 30 * s, base - h)], (78, 58, 44), 5)
    if snowy:
        P(d, [(x - 40 * s, base - h + 6), (x + w / 2, base - h - 230 * s), (x + w + 40 * s, base - h + 6), (x + w / 2, base - h - 170 * s)], (232, 234, 238), 4)
    for c_ in (0, 1):
        wx = x + 70 * s + c_ * 180 * s; wy = base - h + 80 * s
        RR(d, [wx - 14 * s, wy - 24 * s, wx + 104 * s, wy + 134 * s], (210, 216, 222), 6, 4)                 # резные наличники
        RR(d, [wx, wy, wx + 90 * s, wy + 110 * s], (230, 180, 100) if lit else (36, 40, 44), 3, 3)
        LN(d, [(wx + 45 * s, wy), (wx + 45 * s, wy + 110 * s)], 3); LN(d, [(wx, wy + 55 * s), (wx + 90 * s, wy + 55 * s)], 3)

def birch(d, x, base, h):
    LN(d, [(x, base), (x + 6, base - h)], 22, (226, 222, 214))
    for j in range(7):
        y = base - 40 - j * h / 8
        LN(d, [(x - 9, y), (x + 4, y + 6)], 6, (40, 36, 34))
    for j in range(4):
        y = base - h * (0.5 + j * 0.12)
        LN(d, [(x + 4, y), (x + 4 + (-1) ** j * 90, y - 80)], 5, (60, 52, 44))

def village(T, snowy=True):
    im, d = new((170, 176, 182))
    vgrad(d, (116, 128, 142), (190, 192, 192), 0, 1150)
    if not snowy:
        vgrad(d, (130, 150, 160), (200, 196, 170), 0, 1150)
    pts = [(0, 1150)] + [(k * 60, 1030 - (k % 3) * 40 - (k * 37) % 60) for k in range(20)] + [(W, 1150)]
    P(d, pts, (58, 72, 66) if snowy else (70, 90, 60), 0)
    # церковь с луковичным куполом
    d.rectangle([760, 780, 900, 1060], fill=(214, 210, 200), outline=INK, width=4)
    P(d, [(752, 780), (830, 660), (908, 780)], (90, 110, 90), 4)
    E(d, [790, 560, 870, 680], (196, 160, 80), 4)
    LN(d, [(830, 560), (830, 500)], 5); LN(d, [(810, 520), (850, 520)], 5)
    d.rectangle([0, 1150, W, H], fill=(226, 228, 232) if snowy else (104, 118, 70))
    LN(d, [(0, 1150), (W, 1150)], 5)
    izba(d, 60, 1260, 0.95, True, snowy)
    izba(d, 640, 1210, 0.7, False, snowy)
    birch(d, 520, 1300, 640); birch(d, 980, 1290, 560)
    if snowy:
        snow(d, T)
    return im, d

def palace(T, wall=(38, 58, 50)):
    im, d = new(wall)
    for k in range(3):
        x = 60 + k * 340
        RR(d, [x, 380, x + 280, 1180], mix(wall, (0, 0, 0), 0.15), 4, 0)
        d.rectangle([x, 380, x + 280, 1180], outline=GOLD, width=6)
    RR(d, [380, 520, 700, 900], (60, 44, 32), 4, 8)                         # портрет в раме
    d.rectangle([380, 520, 700, 900], outline=GOLD, width=10)
    for s, x0 in ((1, 0), (-1, W)):                                          # шторы
        P(d, [(x0, 300), (x0 + s * 230, 300), (x0 + s * 160, 900), (x0 + s * 240, 1400), (x0, 1400)], (130, 30, 34), 5)
        for j in range(3):
            LN(d, [(x0 + s * (40 + j * 55), 320), (x0 + s * (30 + j * 50), 1380)], 4, (96, 20, 24))
    glow(im, 540, 250, 420, 0.6, (250, 210, 140)); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 1250, W, H], fill=(92, 62, 40)); LN(d, [(0, 1250), (W, 1250)], 6)
    for k in range(14):
        LN(d, [(k * 90 - 200, H), (k * 90 + 100, 1250)], 3, (70, 46, 30))
    return im, d

def bed(im, d, x, y, s, T, drop=0.0, sick=1.0):
    RR(d, [x - 330 * s, y - 330 * s, x + 330 * s, y + 40 * s], (110, 76, 50), 20, 5)             # изголовье
    RR(d, [x - 280 * s, y - 120 * s, x + 280 * s, y + 60 * s], (238, 236, 228), 30, 4)            # подушка
    fd_lay, fd = layer()
    face(fd, x, y - 40 * s, 95 * s, 1, "boy", 0, -0.3, T)
    im.paste(fd_lay, (0, 0), fd_lay); d = ImageDraw.Draw(im, "RGBA")
    if sick > 0:                                                             # бледность
        d.ellipse([x - 84 * s, y - 140 * s, x + 84 * s, y + 60 * s], fill=(200, 210, 220, int(50 * sick)))
    P(d, [(x - 380 * s, y + 40 * s), (x + 380 * s, y + 40 * s), (x + 430 * s, y + 620 * s), (x - 430 * s, y + 620 * s)], (176, 190, 206), 5)
    for j in range(4):
        LN(d, [(x - 300 * s + j * 200 * s, y + 80 * s), (x - 330 * s + j * 220 * s, y + 600 * s)], 3, (140, 154, 172))
    RR(d, [x - 400 * s, y + 60 * s, x + 400 * s, y + 150 * s], (220, 216, 204), 12, 4)             # отворот простыни
    hx, hy_ = x + 130 * s, y + 120 * s
    d.ellipse([hx - 40 * s, hy_ - 30 * s, hx + 40 * s, hy_ + 34 * s], fill=SKIN, outline=INK, width=3)
    if drop > 0:
        rr = 26 * s * drop
        P(d, [(hx, hy_ + 30 * s), (hx - rr, hy_ + 30 * s + rr * 1.6), (hx + rr, hy_ + 30 * s + rr * 1.6)], (170, 20, 16), 0)
        d.ellipse([hx - rr, hy_ + 30 * s + rr * 0.9, hx + rr, hy_ + 30 * s + rr * 2.9], fill=(170, 20, 16))
    return d

def lampada(im, d, x, y, T):
    RR(d, [x - 70, y - 200, x + 70, y - 20], (180, 140, 70), 6, 4)                   # икона
    RR(d, [x - 50, y - 180, x + 50, y - 40], (120, 70, 40), 4, 3)
    d.ellipse([x - 20, y - 160, x + 20, y - 120], fill=GOLD)
    E(d, [x - 26, y + 10, x + 26, y + 60], (170, 30, 26), 3)
    glow(im, x, y + 20, 120, 0.7 + 0.15 * math.sin(T * 9), (250, 120, 70))
    return ImageDraw.Draw(im, "RGBA")

def cellar(T):
    im, d = new((60, 52, 46))
    for row in range(16):
        for k in range(8):
            x = k * 150 + (75 if row % 2 else 0) - 75; y = 300 + row * 70
            d.rectangle([x, y, x + 146, y + 66], fill=(70 + (k * 7 + row * 3) % 14, 62, 54), outline=(44, 38, 34), width=3)
    for cx in (270, 810):                                                    # своды
        d.chord([cx - 330, 120, cx + 330, 860], 180, 360, fill=(46, 40, 36))
        d.arc([cx - 330, 120, cx + 330, 860], 180, 360, fill=INK, width=8)
    d.rectangle([0, 1300, W, H], fill=(52, 44, 40)); LN(d, [(0, 1300), (W, 1300)], 6)
    glow(im, 540, 900, 520, 0.8, (250, 190, 110))
    return im, ImageDraw.Draw(im, "RGBA")

def table(d, y=1150, w=820):
    P(d, [(540 - w / 2, y), (540 + w / 2, y), (540 + w / 2 + 40, y + 190), (540 - w / 2 - 40, y + 190)], (236, 230, 216), 5)
    for k in range(9):
        LN(d, [(540 - w / 2 - 30 + k * (w + 60) / 8, y + 190), (540 - w / 2 - 30 + k * (w + 60) / 8 + 10, y + 240)], 4, (200, 194, 180))
    d.rectangle([540 - w / 2 - 40, y + 190, 540 + w / 2 + 40, y + 250], fill=(226, 220, 206), outline=INK, width=4)

def cake(d, x, y, s=1.0, poison=0.0):
    P(d, [(x - 60 * s, y), (x + 60 * s, y), (x + 48 * s, y - 70 * s), (x - 48 * s, y - 70 * s)], mix((200, 150, 120), (150, 180, 110), poison * 0.5), 4)
    d.chord([x - 52 * s, y - 110 * s, x + 52 * s, y - 40 * s], 180, 360, fill=(246, 230, 226), outline=INK, width=4)
    E(d, [x - 14 * s, y - 128 * s, x + 14 * s, y - 100 * s], (190, 30, 40), 3)
    for j in range(3):
        LN(d, [(x - 40 * s + j * 40 * s, y - 8 * s), (x - 40 * s + j * 40 * s, y - 62 * s)], 2, (160, 110, 90))

def wineglass(d, x, y, s=1.0, fill=1.0):
    P(d, [(x - 55 * s, y - 230 * s), (x + 55 * s, y - 230 * s), (x + 40 * s, y - 120 * s), (x, y - 95 * s), (x - 40 * s, y - 120 * s)], (210, 220, 224, 120), 4)
    if fill > 0:
        P(d, [(x - 50 * s, y - 200 * s), (x + 50 * s, y - 200 * s), (x + 40 * s, y - 122 * s), (x, y - 100 * s), (x - 40 * s, y - 122 * s)], (120, 20, 34), 0)
    LN(d, [(x, y - 95 * s), (x, y - 10 * s)], 6 * s)
    d.ellipse([x - 45 * s, y - 16 * s, x + 45 * s, y + 6 * s], fill=(210, 220, 224), outline=INK, width=4)

def vial(d, x, y, s=1.0, tilt=0.0):
    RR(d, [x - 60 * s, y - 150 * s, x + 60 * s, y + 60 * s], (60, 120, 70), 20, 5)
    RR(d, [x - 22 * s, y - 220 * s, x + 22 * s, y - 145 * s], (60, 120, 70), 6, 5)
    RR(d, [x - 28 * s, y - 250 * s, x + 28 * s, y - 214 * s], (140, 100, 70), 6, 4)
    RR(d, [x - 46 * s, y - 100 * s, x + 46 * s, y + 20 * s], (226, 218, 194), 6, 3)       # этикетка с черепом
    d.ellipse([x - 24 * s, y - 88 * s, x + 24 * s, y - 40 * s], fill=INK)
    d.rectangle([x - 14 * s, y - 46 * s, x + 14 * s, y - 28 * s], fill=INK)
    for s_ in (-1, 1):
        d.ellipse([x + s_ * 10 * s - 7 * s, y - 72 * s, x + s_ * 10 * s + 7 * s, y - 58 * s], fill=(226, 218, 194))
    for s_ in (-1, 1):
        LN(d, [(x - 30 * s, y - 20 * s + s_ * 10 * s), (x + 30 * s, y - 20 * s - s_ * 10 * s)], 5 * s)
    d.ellipse([x - 40 * s, y - 130 * s, x - 22 * s, y - 112 * s], fill=(160, 220, 170, 160))

def revolver(d, x, y, s=1.0, f=1):
    m = (54, 56, 62)
    RR(d, [min(x, x + f * 230 * s), y - 22 * s, max(x, x + f * 230 * s), y + 10 * s], m, 4, 4)            # ствол
    RR(d, [x - 30 * s, y - 40 * s, x + 50 * s, y + 34 * s], (70, 72, 78), 10, 4)                         # барабан
    for j in range(3):
        LN(d, [(x - 20 * s + j * 28 * s, y - 34 * s), (x - 20 * s + j * 28 * s, y + 28 * s)], 3)
    P(d, [(x - 30 * s, y - 10 * s), (x - f * 90 * s, y + 10 * s), (x - f * 120 * s, y + 140 * s), (x - f * 60 * s, y + 150 * s), (x - f * 20 * s, y + 34 * s)], (90, 60, 40), 4)
    d.arc([x - f * 20 * s - 30 * s, y + 10 * s, x - f * 20 * s + 30 * s, y + 70 * s], 0, 180, fill=INK, width=int(5 * s) + 1)

def knife(d, x, y, s=1.0, f=1):
    P(d, [(x, y - 14 * s), (x + f * 170 * s, y - 4 * s), (x + f * 200 * s, y + 6 * s), (x, y + 14 * s)], (200, 206, 210), 4)
    RR(d, [min(x, x - f * 110 * s), y - 18 * s, max(x, x - f * 110 * s), y + 18 * s], (80, 56, 40), 8, 4)

def moika(T):
    im, d = new((26, 32, 46))
    vgrad(d, (18, 22, 34), (52, 60, 76), 0, 1000)
    d.rectangle([0, 520, W, 1150], fill=(194, 158, 96), outline=INK, width=6)                  # жёлтый фасад
    P(d, [(260, 520), (540, 360), (820, 520)], (210, 176, 112), 6)
    for k in range(7):
        x = 80 + k * 150
        RR(d, [x, 560, x + 34, 1150], (232, 226, 210), 4, 3)                                    # колонны
    for row in range(2):
        for k in range(6):
            x = 140 + k * 150; y = 640 + row * 250
            RR(d, [x, y, x + 60, y + 150], (240, 190, 100) if (k + row) % 3 else (40, 36, 40), 4, 4)
    d.rectangle([0, 1150, W, 1290], fill=(96, 94, 92)); LN(d, [(0, 1150), (W, 1150)], 5)    # гранитная набережная
    for k in range(18):
        LN(d, [(k * 64, 1110), (k * 64, 1150)], 6, (30, 30, 34))
    LN(d, [(0, 1110), (W, 1110)], 6, (30, 30, 34))
    d.rectangle([0, 1290, W, H], fill=(196, 206, 214))                                       # лёд реки
    for k in range(6):
        LN(d, [(k * 200, 1290 + (k % 3) * 80), (k * 200 + 160, 1360 + (k % 2) * 90)], 3, (150, 164, 178))
    gas_lamp(im, d, 180, 1170, 0.9); gas_lamp(im, d, 900, 1170, 0.9)
    d = ImageDraw.Draw(im, "RGBA")
    snow(d, T, 70)
    return im, d

def river(T, hole=0.0):
    im, d = new((22, 26, 38))
    vgrad(d, (14, 16, 26), (46, 54, 70), 0, 1100)
    d.ellipse([760, 260, 900, 400], fill=(220, 222, 210)); glow(im, 830, 330, 220, 0.6, (200, 210, 220)); d = ImageDraw.Draw(im, "RGBA")
    P(d, [(0, 900), (0, 820), (300, 760), (540, 740), (780, 760), (W, 820), (W, 900)], (20, 22, 30), 0)  # мост
    for k in range(4):
        d.chord([k * 300 - 60, 840, k * 300 + 200, 1100], 180, 360, fill=(46, 54, 70))
    d.rectangle([0, 1000, W, H], fill=(190, 200, 210))
    for k in range(9):
        LN(d, [(k * 140 - 60, 1040 + (k % 4) * 110), (k * 140 + 90, 1100 + (k % 3) * 150), (k * 140 + 40, 1240 + (k % 2) * 140)], 3, (140, 154, 170))
    if hole > 0:
        cx, cy = 540, 1250
        for j in range(3):
            rr = (90 + j * 70) * hole + (T * 40 % 70)
            d.ellipse([cx - rr * 1.6, cy - rr * 0.5, cx + rr * 1.6, cy + rr * 0.5], outline=(120, 140, 160, int(150 / (j + 1))), width=4)
        E(d, [cx - 240 * hole, cy - 80 * hole, cx + 240 * hole, cy + 80 * hole], (14, 20, 28), 6)
        for j in range(10):
            a = j / 10 * 2 * math.pi
            P(d, [(cx + math.cos(a) * 240 * hole, cy + math.sin(a) * 80 * hole), (cx + math.cos(a + 0.2) * 300 * hole, cy + math.sin(a + 0.2) * 110 * hole),
                  (cx + math.cos(a + 0.35) * 240 * hole, cy + math.sin(a + 0.35) * 80 * hole)], (220, 228, 236), 3)
    snow(d, T, 50, 0.7)
    return im, d

def flames(d, x, y, w, h, T, n=9):
    for j in range(n):
        u = (j / (n - 1) - 0.5) * 2
        fx = x + u * w * 0.5
        hh = h * (1 - abs(u) * 0.55) * (0.8 + 0.2 * math.sin(T * 11 + j * 1.7))
        sway = math.sin(T * 7 + j) * w * 0.04
        for c_, k in (((210, 70, 30), 1.0), ((240, 150, 40), 0.7), ((252, 220, 120), 0.4)):
            P(d, [(fx - w * 0.09 * k * 1.4, y), (fx + sway, y - hh * k), (fx + w * 0.09 * k * 1.4, y)], c_, 0)

def fire_bg(T):
    im, d = new((14, 14, 18))
    vgrad(d, (10, 10, 16), (36, 26, 26), 0, 1300)
    for k in range(9):
        x = k * 140 - 40; hh = 700 + (k * 97) % 300
        P(d, [(x, 1300), (x + 70, 1300 - hh), (x + 140, 1300)], (16, 20, 20), 0)
    d.rectangle([0, 1300, W, H], fill=(30, 26, 24))
    glow(im, 540, 1050, 700, 1.0, (230, 110, 40))
    return im, ImageDraw.Draw(im, "RGBA")

def union_jack(d, x, y, w, h, a=255):
    d.rectangle([x, y, x + w, y + h], fill=(30, 40, 110, a))
    for p in (((x, y), (x + w, y + h)), ((x + w, y), (x, y + h))):
        d.line(p, fill=(240, 240, 240, a), width=int(h * 0.2)); d.line(p, fill=(190, 30, 40, a), width=int(h * 0.07))
    d.rectangle([x + w / 2 - h * 0.17, y, x + w / 2 + h * 0.17, y + h], fill=(240, 240, 240, a))
    d.rectangle([x, y + h / 2 - h * 0.17, x + w, y + h / 2 + h * 0.17], fill=(240, 240, 240, a))
    d.rectangle([x + w / 2 - h * 0.1, y, x + w / 2 + h * 0.1, y + h], fill=(190, 30, 40, a))
    d.rectangle([x, y + h / 2 - h * 0.1, x + w, y + h / 2 + h * 0.1], fill=(190, 30, 40, a))

def frost(im, k):
    if k <= 0: return im
    f = Image.new("RGB", (W, H), (200, 226, 240))
    m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
    rng_ = np.random.default_rng(5)
    for j in range(40):
        side = j % 4
        x0 = [0, W, rng_.uniform(0, W), rng_.uniform(0, W)][side]; y0 = [rng_.uniform(0, H), rng_.uniform(0, H), 0, H][side]
        pts = [(x0, y0)]
        for _ in range(5):
            x0 += rng_.uniform(-120, 120) + (W / 2 - x0) * 0.12; y0 += rng_.uniform(-120, 120) + (H / 2 - y0) * 0.08
            pts.append((x0, y0))
        md.line(pts, fill=255, width=5)
    m = Image.fromarray((np.asarray(m).astype(np.float32) * k * 0.9).astype(np.uint8))
    edge = Image.fromarray(((1 - VIG) * 255 * 1.4 * k).clip(0, 160).astype(np.uint8))
    im.paste(f, (0, 0), edge); im.paste(Image.new("RGB", (W, H), (236, 246, 252)), (0, 0), m)
    return im

def pop(T, t0, dur=0.25):
    k = ramp(T, t0, t0 + dur)
    return k * (1 + 0.25 * math.sin(math.pi * k))

def icon_layer(fn, cx, cy, sc):
    """рисуем иконку на прозрачном слое и масштабируем вокруг центра"""
    lay, ld = layer(); fn(ld)
    if abs(sc - 1) > 1e-3 and sc > 0.01:
        lay = lay.resize((max(1, int(W * sc)), max(1, int(H * sc))), Image.BICUBIC)
        L2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L2.paste(lay, (int(cx - cx * sc), int(cy - cy * sc)), lay); lay = L2
    return lay

def label(d, x, y, s, k, c=YEL, size=70):
    if k <= 0: return
    a = int(255 * min(1, k))
    text_c(d, (x, y), s, F(size, 9), c + (a,), stroke=8, sfill=(12, 10, 10, a))

def flash(im, k, c=(255, 250, 240)):
    if k <= 0: return im
    return Image.blend(im, Image.new("RGB", (W, H), c), min(1, k))

