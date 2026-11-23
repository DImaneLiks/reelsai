# -*- coding: utf-8 -*-
"""История 06 — «Амелия Эрхарт». Стиль референса (Сен-Жермен): штриховка, туман,
приглушённая палитра, зерно/виньетка, заголовок белый+красный, карточки с цифрами.

  python3 render_amelia.py                 # полный рендер -> output/*.mp4
  python3 render_amelia.py --frames 1,9    # тестовые кадры -> frames/
"""
import os, sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/workspace")
from ep1_build import render as R
from ep1_build.render import (W, H, FPS, YEL, text_c, F, ramp, lerp, ease, mix, clamp, camera)

TL = json.load(open(os.path.join(ROOT, "timeline.json")))
DUR = TL["total"]
OUT_DIR = "/workspace/output"; os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "История 06 - Амелия Эрхарт.mp4")
R.TL = TL
R.SPEECH = {}
for c in TL["clips"]:
    R.SPEECH.setdefault(c["speaker"], []).append(c)
R.CHUNKS.clear(); R.build_chunks()
AT = {c["id"]: c["start"] for c in TL["clips"]}
END = {c["id"]: c["start"] + c["dur"] for c in TL["clips"]}

def WS(cid, i):
    c = next(c for c in TL["clips"] if c["id"] == cid)
    return c["words"][min(i, len(c["words"]) - 1)]["s"]

# ---------------------------------------------------------------- палитра (авиация 1930-х)
INK = (22, 20, 22); OW = 5
SKY_T, SKY_B = (128, 150, 158), (58, 74, 84)     # высокое холодное небо
SEA_D = (30, 44, 52); SEA_L = (58, 84, 92)
CLOUD = (206, 208, 204)
PLANE = (168, 160, 148); PLANE_D = (96, 90, 82)
STEEL = (120, 128, 134)
GLASS = (210, 226, 232)
PAPER = (222, 210, 184)
RED = (196, 40, 34)
WHITE = (240, 236, 226)
LAMPY = (252, 206, 120)
GOLD = (214, 176, 90)
HAIR_AE = (74, 52, 40); SKIN_AE = (214, 188, 164); SKIN_AED = (168, 138, 116)
JACKET = (112, 84, 58); JACKET_D = (86, 64, 46); SCARF = (196, 190, 178)
SEA_INK = (16, 26, 32)
CAP_RED = (236, 40, 36)

def new(c):
    im = Image.new("RGB", (W, H), c); return im, ImageDraw.Draw(im, "RGBA")
def E(d, b, f, w=OW): d.ellipse(b, fill=f, outline=INK if w else None, width=w)
def P(d, pts, f, w=OW): d.polygon(pts, fill=f, outline=INK if w else None, width=w)
def RR(d, b, f, r=10, w=OW): d.rounded_rectangle(b, r, fill=f, outline=INK if w else None, width=w)
def LN(d, pts, w=OW, c=INK): d.line(pts, fill=c, width=int(w), joint="curve")

SHOTS = []
def shot(a, zoom=(1.0, 1.0), cx=None, cy=None, title=None):
    def deco(f):
        SHOTS.append(dict(a=a, f=f, zoom=zoom, cx=cx, cy=cy, title=title)); return f
    return deco

# ---------------------------------------------------------------- штриховка
_hm = Image.new("L", (W, H), 0); _hd = ImageDraw.Draw(_hm)
for k in range(-H, W, 11):
    _hd.line([(k, 0), (k + H, H)], fill=255, width=2)
HATCH = np.asarray(_hm).astype(np.float32) / 255
_hm2 = Image.new("L", (W, H), 0); _hd2 = ImageDraw.Draw(_hm2)
for k in range(0, W + H, 15):
    _hd2.line([(k, 0), (k - H, H)], fill=255, width=2)
HATCH2 = np.asarray(_hm2).astype(np.float32) / 255

def layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay, "RGBA")

def stamp(im, lay, hatch=0.45, cross=0.0, alpha=1.0):
    a = np.asarray(lay.getchannel("A")).astype(np.float32) / 255
    if alpha < 0.999:
        lay.putalpha(Image.fromarray((a * alpha * 255).astype(np.uint8)))
    im.paste(lay, (0, 0), lay)
    m = a * alpha * (HATCH * hatch + HATCH2 * cross)
    sh = Image.new("RGB", (W, H), INK)
    im.paste(sh, (0, 0), Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)))

def glow(im, x, y, rad, k=1.0, c=LAMPY):
    g = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(g)
    gd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=int(120 * k))
    g = g.filter(ImageFilter.GaussianBlur(rad * 0.45))
    im.paste(Image.new("RGB", (W, H), c), (0, 0), g)

def vgrad(d, c1, c2, y0=0, y1=H, n=24):
    for j in range(n):
        d.rectangle([0, y0 + (y1 - y0) * j / n, W, y0 + (y1 - y0) * (j + 1) / n + 1], fill=mix(c1, c2, j / (n - 1)))

def dim(im, k=0.55, tint=(40, 8, 6)):
    return Image.blend(im, Image.new("RGB", (W, H), tint), k)

def pop(T, t0, dur=0.25):
    k = ramp(T, t0, t0 + dur)
    return k * (1 + 0.25 * math.sin(math.pi * k))

def label(d, x, y, s, k, c=YEL, size=70):
    if k <= 0: return
    a = int(255 * min(1, k))
    text_c(d, (x, y), s, F(size, 9), c + (a,), stroke=8, sfill=(12, 10, 10, a))

def flash(im, k, c=(255, 250, 240)):
    if k <= 0: return im
    return Image.blend(im, Image.new("RGB", (W, H), c), min(1, k))

def headline(d, l1, l2, c2=RED, k=1.0, y=230):
    if k <= 0: return
    a = int(255 * k)
    text_c(d, (540, y), l1, F(84, 9), WHITE + (a,), stroke=8, sfill=(12, 10, 10, a))
    if l2:
        text_c(d, (540, y + 100), l2, F(84, 9), c2 + (a,), stroke=8, sfill=(12, 10, 10, a))

def tag(d, s="ТАЙНЫ ИСТОРИИ · XX ВЕК"):
    f = F(30, 9); w = f.getlength(s)
    d.rounded_rectangle([44, 70, 44 + w + 64, 122], 26, fill=(12, 10, 10, 200))
    d.ellipse([62, 88, 78, 104], fill=RED)
    d.text((90, 97), s, font=f, fill=(240, 236, 226), anchor="lm")

def fact(d, big, small, k, c=YEL, y=880):
    if k <= 0: return
    a = int(255 * k)
    text_c(d, (540, y), big, F(150, 9), c + (a,), stroke=10, sfill=(12, 10, 10, a))
    if small:
        text_c(d, (540, y + 130), small, F(52, 9), WHITE + (a,), stroke=6, sfill=(12, 10, 10, a))

def clouds(im, T, n=7, y0=300, k=0.8, spd=14.0, sea=False):
    """облачные валуны; если sea — плоские облачные ленты над горизонтом"""
    lay, ld = layer()
    for j in range(n):
        x = ((T * spd * (0.6 + j % 3) + j * 313) % (W + 900)) - 450
        y = y0 + j * 150 + math.sin(T * 0.3 + j) * 14
        col = CLOUD + (int(150 * k),)
        rr = 150 - j % 3 * 22
        for dx, dy, s in ((-rr, 8, 0.75), (0, -10, 1.0), (rr, 6, 0.8)):
            rad = rr * s
            ld.ellipse([x + dx - rad, y + dy - rad * 0.45, x + dx + rad, y + dy + rad * 0.45], fill=col)
    if sea:
        lay = lay.filter(ImageFilter.GaussianBlur(18))
    im.paste(lay, (0, 0), lay)

def rain(d, T, n=110, k=1.0):
    rng = np.random.default_rng(3)
    for i in range(n):
        x = (i * 173.3 + math.sin(T * 0.9 + i) * 20) % W
        y = (i * 271 + T * (900 + (i % 7) * 160)) % H
        ln_ = 26 + i % 3 * 12
        d.line([(x, y), (x - 6, y + ln_)], fill=(210, 220, 226, int(110 * k)), width=2)

def sea_bg(T, horizon=1150, storm=0.0):
    im, d = new(mix(SEA_D, (18, 24, 30), 0.3))
    vgrad(d, mix(SKY_B, (20, 24, 30), 0.3 + 0.4 * storm), mix(SEA_D, (10, 16, 20), 0.2), 0, horizon)
    d.rectangle([0, horizon, W, H], fill=SEA_D)
    # волны — штрихами
    for row in range(26):
        y = horizon + 18 + row * 30
        amp = 8 + row * 1.6
        ph = T * (0.8 + row * 0.05)
        pts = [(x, y + math.sin(x / 130 + ph) * amp * 0.25) for x in range(-40, W + 80, 90)]
        wdt = 2 + row // 6
        col = mix(SEA_D, SEA_L, max(0.05, 0.5 - row * 0.017)) * 255 if False else mix(SEA_D, SEA_L, max(0.05, 0.5 - row * 0.017))
        d.line(pts, fill=col, width=int(wdt))
    fog_(im, T, 0.5 + 0.5 * storm, horizon - 260)
    return im, d

def fog_(im, T, k=0.5, y0=900):
    f = Image.new("L", (W, H), 0); fd = ImageDraw.Draw(f)
    for j in range(7):
        y = y0 + j * 120 + math.sin(T * 0.4 + j) * 20
        x = ((T * (18 + j * 6) + j * 300) % (W + 900)) - 450
        fd.ellipse([x - 600, y - 70, x + 600, y + 70], fill=int(90 * k))
    f = f.filter(ImageFilter.GaussianBlur(40))
    im.paste(Image.new("RGB", (W, H), (176, 184, 182)), (0, 0), f)

# ---------------------------------------------------------------- самолёт Lockheed Electra 10E
def plane_layer(d, x, y, s, T, tilt=0.0, prop=1.0, lights=1.0, broken=0.0):
    """вид 3/4 спереди-сбоку: двухмоторный, фюзеляж, крылья, хвост; пропеллеры — размытые диски"""
    rot = math.degrees(tilt)
    body = mix(PLANE, PLANE_D, 0.25)
    # крыло дальнее
    P(d, [(x - s * 1.9, y - s * 0.05), (x - s * 0.4, y - s * 0.28), (x + s * 0.2, y - s * 0.2), (x - s * 1.5, y + s * 0.12)], PLANE_D, 4)
    # фюзеляж
    d.ellipse([x - s * 1.7, y - s * 0.34, x + s * 1.05, y + s * 0.34], fill=body, outline=INK, width=5)
    LN(d, [(x - s * 1.6, y + s * 0.05), (x + s * 0.9, y + s * 0.05)], 3, PLANE_D)
    # хвост
    P(d, [(x - s * 1.55, y - s * 0.1), (x - s * 1.95, y - s * 0.75), (x - s * 1.35, y - s * 0.7), (x - s * 1.2, y - s * 0.2)], body, 4)
    P(d, [(x - s * 1.75, y - s * 0.02), (x - s * 2.05, y - s * 0.06), (x - s * 1.6, y + s * 0.12)], body, 3)
    # кабина
    E(d, [x + s * 0.25, y - s * 0.3, x + s * 0.62, y - s * 0.06], GLASS, 3)
    LN(d, [(x + s * 0.36, y - s * 0.3), (x + s * 0.36, y - s * 0.06)], 2, INK)
    # окна
    for j in range(4):
        E(d, [x - s * 0.75 + j * s * 0.28, y - s * 0.14, x - s * 0.62 + j * s * 0.28, y - s * 0.0], GLASS, 2)
    # крыло ближнего плеча
    P(d, [(x - s * 0.5, y + s * 0.05), (x + s * 0.35, y - s * 0.1), (x + s * 1.75, y + s * 0.5), (x + s * 0.6, y + s * 0.62)], PLANE, 5)
    # моторы + пропеллеры
    for sx, sy in ((x + s * 0.62, y + s * 0.18), (x - s * 0.62, y - s * 0.34)):
        E(d, [sx - s * 0.2, sy - s * 0.14, sx + s * 0.2, sy + s * 0.14], PLANE_D, 3)
        if prop > 0:
            for q in range(3):
                ang = T * 22 + q * 2.09
                d.line([(sx + math.cos(ang) * s * 0.55, sy + math.sin(ang) * s * 0.55 * 0.35),
                        (sx - math.cos(ang) * s * 0.55, sy - math.sin(ang) * s * 0.55 * 0.35)],
                       fill=(40, 38, 36, 220), width=4)
            d.ellipse([sx - s * 0.55, sy - s * 0.2, sx + s * 0.55, sy + s * 0.2], outline=(60, 58, 56, 90), width=2)
    if lights > 0:
        for lx, ly in ((x + s * 1.0, y), (x - s * 1.9, y - s * 0.6)):
            d.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=(255, 90, 70, int(255 * lights)))
    if broken > 0:
        LN(d, [(x - s * 0.3, y - s * 0.3), (x + s * 0.1, y + s * 0.1), (x - s * 0.05, y + s * 0.3)], 4, (30, 20, 18))

def plane_im(im, x, y, s, T, **kw):
    lay, ld = layer(); plane_layer(ld, x, y, s, T, **kw)
    stamp(im, lay, 0.35)

# ---------------------------------------------------------------- портрет Амелии
def ae_head(d, x, hy, r, look=0.0, glow_=0.0, alpha=1.0):
    """круглое лицо, короткие волнистые тёмные волосы, спокойный взгляд — по фото 1930-х"""
    lw = max(3, int(r * 0.04)); thin = max(2, int(r * 0.02))
    fb = [x - r * 0.8, hy - r, x + r * 0.8, hy + r * 1.05]
    d.ellipse(fb, fill=SKIN_AE, outline=INK, width=lw)
    d.chord(fb, 95, 265, fill=mix(SKIN_AE, (120, 84, 66), 0.12))
    # волосы: пробор слева, волны до ушей
    P(d, [(x - r * 0.95, hy + r * 0.1), (x - r * 1.0, hy - r * 0.55), (x - r * 0.55, hy - r * 1.2), (x + r * 0.2, hy - r * 1.28),
          (x + r * 0.9, hy - r * 0.85), (x + r * 0.98, hy + r * 0.15), (x + r * 0.72, hy - r * 0.15), (x + r * 0.5, hy - r * 0.55),
          (x + r * 0.1, hy - r * 0.72), (x - r * 0.3, hy - r * 0.6), (x - r * 0.62, hy - r * 0.25), (x - r * 0.72, hy + r * 0.2)], HAIR_AE, lw)
    for j in range(5):
        u = -0.5 + j * 0.3
        LN(d, [(x + u * r * 0.6, hy - r * 0.62), (x + u * r * 1.05, hy - r * 1.05)], thin, mix(HAIR_AE, (20, 16, 14), 0.4))
    # глаза
    for s in (-1, 1):
        ex, ey = x + s * r * 0.34, hy - r * 0.05
        w_, h_ = r * 0.17, r * 0.09
        d.ellipse([ex - w_, ey - h_, ex + w_, ey + h_], fill=(244, 240, 232), outline=INK, width=thin)
        px = ex + look * w_ * 0.4
        ir = r * 0.075
        d.ellipse([px - ir, ey - ir, px + ir, ey + ir], fill=mix((70, 52, 40), (230, 190, 90), glow_))
        d.ellipse([px - ir * 0.45, ey - ir * 0.45, px + ir * 0.45, ey + ir * 0.45], fill=INK)
        d.ellipse([px - ir * 0.7, ey - ir * 0.6, px - ir * 0.2, ey - ir * 0.15], fill=(255, 255, 255))
        d.arc([ex - w_, ey - h_ * 1.2, ex + w_, ey + h_ * 0.4], 200, 340, fill=INK, width=max(3, int(r * 0.035)))
        LN(d, [(ex - w_ * 1.1, ey - h_ * 2.1), (ex + w_ * 1.1, ey - h_ * 1.9)], max(3, int(r * 0.045)), HAIR_AE)
    # нос, рот
    LN(d, [(x + r * 0.02, hy - r * 0.05), (x + r * 0.05, hy + r * 0.3), (x - r * 0.03, hy + r * 0.34)], thin, SKIN_AED)
    LN(d, [(x - r * 0.16, hy + r * 0.6), (x, hy + r * 0.66), (x + r * 0.16, hy + r * 0.6)], max(3, int(r * 0.03)), (150, 84, 76))
    d.arc([x - r * 0.12, hy + r * 0.56, x + r * 0.12, hy + r * 0.7], 340, 20, fill=(196, 120, 110), width=thin)
    d.arc([x - r * 0.28, hy + r * 0.85, x + r * 0.28, hy + r * 1.1], 200, 340, fill=SKIN_AED, width=thin)

def ae_bust(im, x, hy, r, T, look=0.0, glow_=0.0, alpha=1.0, scarf_k=1.0):
    """бюст: пилотская куртка + шарф"""
    lay, ld = layer()
    # плечи/куртка
    P(ld, [(x - r * 2.1, H + 50), (x - r * 1.9, hy + r * 1.5), (x - r * 0.7, hy + r * 1.05), (x + r * 0.7, hy + r * 1.05),
           (x + r * 1.9, hy + r * 1.5), (x + r * 2.1, H + 50)], JACKET, 6)
    for s in (-1, 1):
        LN(ld, [(x + s * r * 0.55, hy + r * 1.15), (x + s * r * 0.85, hy + r * 2.2)], max(5, int(r * 0.06)), JACKET_D)
    ld.rounded_rectangle([x - r * 0.85, hy + r * 1.0, x + r * 0.85, hy + r * 1.35], int(r * 0.2), fill=JACKET_D, outline=INK, width=4)
    # шарф
    sw = int(255 * scarf_k)
    P(ld, [(x - r * 0.55, hy + r * 1.05), (x + r * 0.55, hy + r * 1.05), (x + r * 0.4, hy + r * 1.45), (x - r * 0.4, hy + r * 1.45)],
      SCARF + (sw,), 3)
    tailx = x - r * 1.5 + math.sin(T * 1.7) * r * 0.25
    P(ld, [(x - r * 0.4, hy + r * 1.3), (x - r * 0.1, hy + r * 1.42), (tailx + r * 0.3, hy + r * 2.6 + math.cos(T * 1.3) * r * 0.2),
           (tailx - r * 0.2, hy + r * 2.5)], SCARF + (sw,), 3)
    ae_head(ld, x, hy, r, look)
    stamp(im, lay, 0.22, 0.0, alpha)
    if glow_ > 0:
        for s in (-1, 1):
            glow(im, x + s * r * 0.34, hy - r * 0.05, r * 0.5, glow_, (255, 210, 120))

# ---------------------------------------------------------------- карты и артефакты
def map_bg(T, k=1.0):
    im, d = new(PAPER)
    rng = np.random.default_rng(5)
    for j in range(30):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        d.ellipse([x, y, x + rng.uniform(20, 90), y + rng.uniform(20, 90)], fill=(196, 182, 152, 60))
    # берега (стилизованные острова Океании)
    def blob(cx, cy, rx, ry, seed):
        rg = np.random.default_rng(seed)
        pts = []
        for a in range(0, 360, 24):
            rr = 1 + rg.uniform(-0.22, 0.22)
            pts.append((cx + math.cos(math.radians(a)) * rx * rr, cy + math.sin(math.radians(a)) * ry * rr))
        P(d, pts, mix(PAPER, (150, 130, 96), 0.5), 4)
    blob(240, 560, 130, 90, 1); blob(760, 420, 170, 110, 2); blob(880, 900, 120, 150, 3)
    blob(300, 1300, 200, 130, 4); blob(700, 1600, 150, 90, 5)
    # сетка меридианов
    for j in range(7):
        d.line([(j * 180 + 30, 0), (j * 180 - 60, H)], fill=(120, 100, 70, 90), width=2)
        d.line([(0, j * 300 + 60), (W, j * 300 - 40)], fill=(120, 100, 70, 90), width=2)
    return im, d

def route_arc(d, p0, p1, k, bow=0.25, c=RED, w=7):
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - bow * abs(p1[0] - p0[0])
    pts = []
    for t in np.linspace(0, 1, 40):
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * mx + t ** 2 * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * my + t ** 2 * p1[1]
        pts.append((x, y))
    n_ = max(2, int(len(pts) * clamp(k)))
    d.line(pts[:n_], fill=c, width=int(w), joint="curve")
    if k >= 1:
        d.ellipse([p1[0] - 12, p1[1] - 12, p1[0] + 12, p1[1] + 12], outline=c, width=4)

def radio_room(T):
    """тёмная радиорубка: аппарат, лампа, осциллирующая волна"""
    im, d = new((26, 24, 26))
    vgrad(d, (36, 32, 30), (16, 14, 14), 0, 1500)
    d.rectangle([0, 1500, W, H], fill=(44, 34, 28))
    # стол с аппаратурой
    RR(d, [150, 1050, 930, 1420], (70, 58, 46), 18, 6)
    RR(d, [220, 900, 560, 1080], (52, 50, 54), 10, 5)
    for j in range(4):
        E(d, [260 + j * 70, 940, 300 + j * 70, 980], (140, 120, 90), 3)
    RR(d, [620, 880, 880, 1080], (60, 54, 50), 10, 5)
    # зелёный глазок передатчика
    blinkk = 0.5 + 0.5 * math.sin(T * 7)
    E(d, [700, 950, 740, 990], mix((30, 60, 40), (90, 220, 120), blinkk), 2)
    glow(im, 720, 970, 160, 0.5 * blinkk, (120, 220, 140))
    d = ImageDraw.Draw(im, "RGBA")
    # лампа
    LN(d, [(540, 300), (540, 420)], 8, (30, 28, 26))
    P(d, [(500, 420), (580, 420), (560, 480), (520, 480)], (40, 38, 36), 3)
    glow(im, 540, 500, 300, 0.8, LAMPY)
    d = ImageDraw.Draw(im, "RGBA")
    return im, d

def photo_frame(d, x, y, w, h, rot=0.0, cap=None):
    fr = Image.new("RGBA", (w + 40, h + 90), PAPER + (255,))
    fd = ImageDraw.Draw(fr)
    fd.rectangle([20, 20, w + 20, h + 50], fill=(60, 56, 50))
    if rot:
        fr = fr.rotate(rot, expand=True, resample=Image.BICUBIC)
    return fr

# ================================================================ ШОТЫ
@shot(AT["L01"] - 0.05, zoom=(1.06, 1.0), cx=540, cy=900, title=("ОНА ИСЧЕЗЛА", "НАД ОКЕАНОМ", RED))
def s_hook(T, t):
    im, d = sea_bg(T, 1150, storm=ramp(T, AT["L01"], AT["L01"] + 2))
    clouds(im, T, 8, 200, 0.9)
    # силуэт самолёта уходит в шторм и растворяется
    ka = 1 - ramp(T, WS("L01", 1), WS("L01", 3) + 0.6)
    if ka > 0.02:
        lay, ld = layer()
        plane_layer(ld, 540 + (1 - ka) * 260, 620 - (1 - ka) * 160, 130, T, prop=ka, lights=ka)
        a = np.asarray(lay.getchannel("A")).astype(np.float32) / 255
        lay.putalpha(Image.fromarray((a * ka * 255).astype(np.uint8)))
        im.paste(Image.new("RGB", (W, H), SEA_INK), (0, 0), lay)
    d = ImageDraw.Draw(im, "RGBA")
    rain(d, T, 130, ramp(T, AT["L01"] + 0.5, AT["L01"] + 2))
    if T > WS("L01", 4):   # «и через тридцать лет» — карточка с цифрой
        fact(d, "30", "ЛЕТ СПУСТЯ ЕЁ ВИДЕЛИ ЖИВОЙ", pop(T, WS("L01", 4), 0.4), YEL, 760)
    if T > WS("L01", 7):
        label(d, 540, 1180, "В ЧУЖОМ ГОРОДЕ", pop(T, WS("L01", 7), 0.35), WHITE, 64)
    return im

@shot(AT["L02"] - 0.1, zoom=(1.0, 1.1), cx=540, cy=820, title=("ПЕРВАЯ ЖЕНЩИНА", "В ОДИНОЧНОМ ПЕРЕЛЁТЕ", RED))
def s_record(T, t):
    im, d = new(mix(SKY_T, SKY_B, 0.4))
    vgrad(d, SKY_T, mix(SKY_B, (30, 40, 48), 0.5), 0, 1500)
    clouds(im, T, 6, 260, 0.7, spd=60)
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 1500, W, H], fill=mix(SEA_D, (20, 30, 38), 0.4))
    for row in range(10):
        y = 1520 + row * 40
        d.line([(x, y + math.sin(x / 150 + T * 0.6 + row) * 6) for x in range(-40, W + 80, 100)],
               fill=mix(SEA_D, SEA_L, max(0.05, 0.4 - row * 0.03)), width=2 + row // 4)
    # самолёт летит слева направо с лёгким креном
    x = 140 + 380 * ease(ramp(t, 0, 4))
    plane_im(im, x, 760 + math.sin(T * 1.3) * 18, 170, T, tilt=math.sin(T * 0.8) * 0.04, lights=1.0)
    lay, ld = layer()
    ld.line([(x - 200, 760 + math.sin(T * 1.3) * 18), (x - 620, 780 + math.sin(T * 1.3) * 18)], fill=(230, 230, 230, 120), width=26)
    lay = lay.filter(ImageFilter.GaussianBlur(10)); im.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(im, "RGBA")
    if T > WS("L02", 2):
        label(d, 540, 1120, "1932 · АТЛАНТИКА", pop(T, WS("L02", 2), 0.4), YEL, 76)
    return im

@shot(AT["L03"] - 0.1, zoom=(1.0, 1.06), cx=540, cy=960, title=("1937", "КРУГОСВЕТНЫЙ РЕЙС", RED))
def s_map(T, t):
    im, d = map_bg(T)
    LA = (170, 420); SP = (330, 1290); PG = (880, 900)   # Лос-Анджелес, Сан-Хосе(Панама стилиз.), Лаэ
    k1 = ramp(T, WS("L03", 0), WS("L03", 3))
    route_arc(d, LA, SP, k1, 0.2)
    k2 = ramp(T, WS("L03", 3), WS("L03", 6))
    route_arc(d, SP, PG, k2, -0.22)
    label(d, LA[0] + 120, LA[1] - 60, "ЛОС-АНДЖЕЛЕС", k1, (70, 50, 30), 40)
    label(d, PG[0] - 60, PG[1] - 90, "ЛАЭ · НОВАЯ ГВИНЕЯ", k2, (70, 50, 30), 40)
    # пунктир маршрута вокруг света
    if k2 >= 1:
        for j in range(14):
            a_ = math.radians(j * 26 - 60)
            d.ellipse([540 + math.cos(a_) * 430 - 4, 960 + math.sin(a_) * 430 - 4,
                       540 + math.cos(a_) * 430 + 4, 960 + math.sin(a_) * 430 + 4], fill=(120, 100, 70, 160))
    # самолётик идёт по маршруту
    pp = min(k1, 1) if k1 < 1 else 1
    if k2 > 0:
        mx, my = (SP[0] + PG[0]) / 2, (SP[1] + PG[1]) / 2 + 0.22 * abs(PG[0] - SP[0])
        tt_ = k2
        px = (1 - tt_) ** 2 * SP[0] + 2 * (1 - tt_) * tt_ * mx + tt_ ** 2 * PG[0]
        py = (1 - tt_) ** 2 * SP[1] + 2 * (1 - tt_) * tt_ * my + tt_ ** 2 * PG[1]
        plane_im(im, px, py, 60, T, prop=1)
    else:
        mx, my = (LA[0] + SP[0]) / 2, (LA[1] + SP[1]) / 2 - 0.2 * abs(SP[0] - LA[0])
        tt_ = k1
        px = (1 - tt_) ** 2 * LA[0] + 2 * (1 - tt_) * tt_ * mx + tt_ ** 2 * SP[0]
        py = (1 - tt_) ** 2 * LA[1] + 2 * (1 - tt_) * tt_ * my + tt_ ** 2 * SP[1]
        plane_im(im, px, py, 60, T, prop=1)
    d = ImageDraw.Draw(im, "RGBA")
    if T > WS("L03", 9):
        label(d, 540, 1560, "САМЫЙ ОПАСНЫЙ РЕЙС", pop(T, WS("L03", 9), 0.35), RED, 72)
    return im

@shot(AT["L04"] - 0.1, zoom=(1.02, 1.0), cx=540, cy=900, title=("ПОСЛЕДНИЙ", "РАДИОВЫЗОВ", RED))
def s_radio(T, t):
    im, d = radio_room(T)
    a = WS("L04", 5)                      # «был коротким» — включается голос
    kw = ramp(T, a - 0.2, a + 0.4)
    # эфирная волна на экране-осциллографе
    RR(d, [620, 880, 880, 1080], (18, 26, 20), 10, 4)
    pts = []
    for xx_ in range(630, 876, 6):
        amp = 34 * kw * (0.4 + 0.6 * abs(math.sin(T * 3 + xx_ * 0.05)))
        pts.append((xx_, 980 + math.sin(xx_ * 0.12 + T * 9) * amp))
    d.line(pts, fill=(120, 230, 140, int(220 * max(0.15, kw))), width=3)
    # цитата — белая «телеграфная» строка
    qc = WS("L04", 7)
    if T > qc:
        kk = pop(T, qc, 0.35)
        d.rounded_rectangle([90, 560, 990, 760], 20, fill=(12, 10, 10, int(200 * kk)))
        text_c(d, (540, 620), "«МЫ ЛЕТИМ НИЗКО,", F(46, 9), WHITE + (int(255 * kk),))
        text_c(d, (540, 700), "НО ВАС НЕ ВИДИМ»", F(46, 9), CAP_RED + (int(255 * kk),))
    if T > WS("L04", 1):
        label(d, 540, 1620, "2 июля 1937 · 08:16", ramp(T, WS("L04", 1), WS("L04", 3)), YEL, 52)
    return im

@shot(AT["L05"] - 0.1, zoom=(1.0, 1.08), cx=540, cy=1000, title=("ЗАГАДКА", "№1", YEL))
def s_search(T, t):
    im, d = sea_bg(T, 900, storm=0.25)
    clouds(im, T, 5, 120, 0.7, spd=25)
    d = ImageDraw.Draw(im, "RGBA")
    # корабли — тёмные силуэты, бинокль-лучи
    for (bx, bs) in ((260, 90), (700, 120), (980, 70)):
        yb = 1180 + (bs - 90)
        P(d, [(bx - bs, yb), (bx + bs, yb), (bx + bs * 0.7, yb + 26), (bx - bs * 0.7, yb + 26)], SEA_INK, 3)
        LN(d, [(bx, yb), (bx, yb - bs * 0.7)], max(4, bs // 20), SEA_INK)
        LN(d, [(bx - bs * 0.3, yb - bs * 0.7), (bx + bs * 0.3, yb - bs * 0.7)], 3, SEA_INK)
    # лучи поиска
    kb = ramp(T, WS("L05", 1), WS("L05", 3))
    for j in range(3):
        ang = -0.5 + j * 0.4 + math.sin(T * 0.5 + j) * 0.25
        lay, ld = layer()
        x0, y0 = 260 + j * 360, 1150
        ld.polygon([(x0, y0), (x0 + math.cos(ang) * 900, y0 - 800), (x0 + math.cos(ang) * 900 + 120, y0 - 800)],
                   fill=(250, 230, 160, int(50 * kb)))
        lay = lay.filter(ImageFilter.GaussianBlur(8)); im.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(im, "RGBA")
    if T > WS("L05", 3):
        fact(d, "17", "ДНЕЙ ПОИСКОВ · НИ ОБЛОМКА", pop(T, WS("L05", 3), 0.4), YEL, 620)
    return im

@shot(AT["L06"] - 0.1, zoom=(1.04, 1.0), cx=540, cy=900, title=("ЗАГАДКА", "№2", YEL))
def s_photo(T, t):
    im, d = new((34, 30, 28))
    vgrad(d, (48, 42, 38), (20, 18, 16), 0, H)
    # «фотография»: светлая рамка, внутри — фигура в женском платье и шляпке
    fx, fy, fw, fh = 190, 560, 700, 900
    rot = math.sin(T * 0.5) * 1.2
    ph = Image.new("RGBA", (fw, fh), PAPER + (255,))
    pd = ImageDraw.Draw(ph)
    pd.rectangle([26, 26, fw - 26, fh - 90], fill=(96, 104, 96))
    # улица: намёк на дома
    for j in range(4):
        pd.rectangle([50 + j * 160, 120, 50 + j * 160 + 120, 460], fill=(78, 84, 80))
    # фигура
    cx, feet = fw // 2, fh - 130
    pd.polygon([(cx - 70, feet), (cx + 70, feet), (cx + 40, feet - 260), (cx - 40, feet - 260)], fill=(58, 52, 50))
    pd.ellipse([cx - 34, feet - 380, cx + 34, feet - 280], fill=(150, 138, 122))
    pd.ellipse([cx - 44, feet - 396, cx + 44, feet - 360], fill=(40, 34, 30))   # шляпка
    pd.ellipse([cx - 26, feet - 372, cx + 26, feet - 336], fill=(168, 150, 132))
    ph = ph.rotate(rot, expand=True, resample=Image.BICUBIC)
    im.paste(ph, (fx, fy), ph)
    d = ImageDraw.Draw(im, "RGBA")
    glow(im, 540, 950, 500, 0.35, LAMPY)
    d = ImageDraw.Draw(im, "RGBA")
    a = WS("L06", 5)
    if T > a:                                   # красная обводка «похожа на неё»
        kk = ramp(T, a, a + 0.5)
        d.rounded_rectangle([fx - 10, fy - 10, fx + fw + 10, fy + fh + 10], 14, outline=CAP_RED + (int(230 * kk),), width=8)
    if T > WS("L06", 7):
        label(d, 540, 1620, "ЯПОНИЯ · 1930-е", pop(T, WS("L06", 7), 0.35), WHITE, 60)
    if T > WS("L06", 10):
        label(d, 540, 470, "В ЖЕНСКОМ ПЛАТЬЕ", pop(T, WS("L06", 10), 0.35), YEL, 64)
    return im

@shot(AT["L07"] - 0.1, zoom=(1.0, 1.1), cx=540, cy=980, title=("ЗАГАДКА", "№3", YEL))
def s_skull(T, t):
    im, d = new((30, 28, 30))
    vgrad(d, (52, 48, 46), (18, 16, 16), 0, 1500)
    d.rectangle([0, 1500, W, H], fill=(60, 52, 44))
    # череп на столе — экспонат
    cx, cy, r = 540, 950, 220
    lay, ld = layer()
    ld.ellipse([cx - r * 0.8, cy - r, cx + r * 0.8, cy + r * 0.55], fill=(216, 208, 190), outline=INK, width=6)
    ld.polygon([(cx - r * 0.45, cy + r * 0.3), (cx + r * 0.45, cy + r * 0.3), (cx + r * 0.3, cy + r * 0.8), (cx - r * 0.3, cy + r * 0.8)],
               fill=(206, 198, 180))
    for s in (-1, 1):
        ld.ellipse([cx + s * r * 0.38 - r * 0.2, cy - r * 0.3, cx + s * r * 0.38 + r * 0.2, cy + r * 0.05], fill=(24, 22, 22))
    ld.polygon([(cx - r * 0.08, cy + r * 0.05), (cx + r * 0.08, cy + r * 0.05), (cx, cy + r * 0.3)], fill=(24, 22, 22))
    for j in range(6):
        x0 = cx - r * 0.3 + j * r * 0.12
        ld.rectangle([x0, cy + r * 0.5, x0 + r * 0.08, cy + r * 0.68], fill=(226, 218, 200), outline=INK)
    stamp(im, lay, 0.4)
    d = ImageDraw.Draw(im, "RGBA")
    glow(im, cx, cy - 100, 420, 0.5, (240, 230, 200))
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 540, 470, "1990 · ОСТРОВ ГАРНДРИ", ramp(T, WS("L07", 1), WS("L07", 4)), WHITE, 56)
    if T > WS("L07", 7):
        label(d, 540, 1350, "ЧЕРЕП АМЕЛИИ?", pop(T, WS("L07", 7), 0.35), YEL, 76)
    a = WS("L07", 11)                            # «экспертиза опровергла» — красный штамп
    if T > a:
        kk = pop(T, a, 0.3)
        st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([300, 1520, 780, 1650], 12, outline=CAP_RED + (int(240 * kk),), width=9)
        text_c(sd, (540, 1585), "ОПРОВЕРГНУТО", F(58, 9), CAP_RED + (int(240 * kk),))
        st = st.rotate(-4, resample=Image.BICUBIC)
        im.paste(st, (0, 0), st)
    return im

@shot(AT["L08"] - 0.1, zoom=(1.0, 1.08), cx=540, cy=1100, title=("ПОКАЗАНИЕ", "МОЛЯК", RED))
def s_sub(T, t):
    im, d = new((16, 26, 34))
    vgrad(d, (30, 52, 64), (8, 14, 20), 0, 700)       # вода сверху
    d.rectangle([0, 700, W, H], fill=(10, 18, 24))    # глубина
    # луч света из-под воды
    lay, ld = layer()
    for j in range(5):
        a_ = -1.2 + j * 0.25 + math.sin(T * 0.4) * 0.06
        ld.polygon([(540, 1900), (540 + math.cos(a_) * 1400, 1900 + math.sin(a_) * 1400),
                    (540 + math.cos(a_ + 0.08) * 1400, 1900 + math.sin(a_ + 0.08) * 1400)],
                   fill=(120, 180, 190, 40))
    lay = lay.filter(ImageFilter.GaussianBlur(12)); im.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(im, "RGBA")
    # пузырьки
    rng = np.random.default_rng(9)
    for i in range(40):
        x = float(rng.integers(0, W)); y = (float(rng.integers(0, 1900)) - T * (60 + i * 3)) % 1900
        s = 3 + i % 4
        d.ellipse([x - s, y - s, x + s, y + s], outline=(180, 210, 220, 90), width=2)
    # силуэт субмарины
    sb, sd = layer()
    x0, y0 = 540 + math.sin(T * 0.3) * 60, 1050
    sd.ellipse([x0 - 340, y0 - 70, x0 + 340, y0 + 70], fill=(12, 16, 18, 255))
    sd.rectangle([x0 - 40, y0 - 130, x0 + 60, y0 - 60], fill=(12, 16, 18, 255))
    sd.polygon([(x0 + 330, y0 - 40), (x0 + 430, y0 - 90), (x0 + 430, y0 + 90), (x0 + 330, y0 + 40)], fill=(12, 16, 18, 255))
    im.paste(sb, (0, 0), sb)
    d = ImageDraw.Draw(im, "RGBA")
    # перископный взгляд: самолёт на поверхности
    if T > WS("L08", 5):
        kk = pop(T, WS("L08", 5), 0.4)
        circ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(circ)
        cd.ellipse([300, 300, 780, 780], fill=(0, 0, 0, 0), outline=(220, 214, 190, int(200 * kk)), width=6)
        plane_layer(cd, 540, 540, 90, T, prop=kk)
        cd.line([(300, 540), (780, 540)], fill=(220, 214, 190, int(90 * kk)), width=2)
        cd.line([(540, 300), (540, 780)], fill=(220, 214, 190, int(90 * kk)), width=2)
        im.paste(circ, (0, 0), circ)
        d = ImageDraw.Draw(im, "RGBA")
        label(d, 540, 880, "САМОЛЁТ НА ВОДЕ", kk, WHITE, 56)
    if T > WS("L08", 0):
        label(d, 540, 1620, "«Я ВИДЕЛ ЭТО САМ»", ramp(T, WS("L08", 0), WS("L08", 2)), YEL, 60)
    return im

@shot(AT["L09"] - 0.1, zoom=(1.05, 1.0), cx=540, cy=800, title=("ГИБЕЛЬ", "ИЛИ ПЛЕН?", RED))
def s_ask(T, t):
    im, d = new((24, 20, 28))
    glow(im, 540, 760, 640, 0.8, (120, 90, 60))
    ae_bust(im, 540, 700, 175, T, look=0.0, glow_=ramp(T, WS("L09", 0), WS("L09", 2)),
            alpha=1 - ramp(T, END["L09"] - 0.3, END["L09"] + 0.3))
    d = ImageDraw.Draw(im, "RGBA")
    label(d, 250, 1150, "МОРЕ?", pop(T, WS("L09", 0), 0.3), RED, 66)
    label(d, 820, 1150, "ПЛЕН?", pop(T, WS("L09", 3), 0.3), WHITE, 66)
    if T > WS("L09", 6):
        label(d, 540, 1300, "ПИШИТЕ В КОММЕНТАРИЯХ", pop(T, WS("L09", 6), 0.35), YEL, 56)
    return im

@shot(END["L09"] + 0.3, title=None)
def s_end(T, t):
    im, d = new((14, 12, 12))
    k = ramp(T, END["L09"] + 0.3, END["L09"] + 0.8)
    text_c(d, (540, 820), "ТАЙНЫ ИСТОРИИ", F(96, 9), mix((14, 12, 12), RED, k))
    text_c(d, (540, 950), "АМЕЛИЯ ЭРХАРТ", F(56, 9), mix((14, 12, 12), WHITE, k))
    k2 = ramp(T, END["L09"] + 1.0, END["L09"] + 1.5)
    d.rounded_rectangle([230, 1060, 850, 1160], 26, fill=mix((14, 12, 12), (44, 40, 38), k2))
    text_c(d, (540, 1110), "Новые выпуски в профиле", F(44, 10), mix((14, 12, 12), WHITE, k2))
    return im

# ---------------------------------------------------------------- субтитры (как в референсе)
def caption_wr(img, T):
    ch = None
    for c in R.CHUNKS:
        if c["s"] <= T < c["e"]: ch = c
    if not ch: return
    words = ch["words"]
    clean = [w.strip(".,!?«»—–: ").lower() for w in words]
    cand = [i for i, w in enumerate(clean) if w not in R.STOP and len(w) > 2]
    hi = max(cand, key=lambda i: len(clean[i])) if cand else None
    if len(words) == 1: hi = 0 if cand else None
    k = ramp(T, ch["s"], ch["s"] + 0.12)
    sc = 0.82 + 0.18 * k + 0.08 * math.sin(math.pi * k)
    f = F(max(10, int(96 * sc)), 9)
    parts = [w.replace("—", "–").replace("«", "").replace("»", "").upper() for w in words]
    sp = f.getlength(" ")
    widths = [f.getlength(p) for p in parts]
    tw = sum(widths) + sp * (len(parts) - 1)
    if tw > 980:
        f = F(max(10, int(96 * sc * 980 / tw)), 9)
        sp = f.getlength(" "); widths = [f.getlength(p) for p in parts]; tw = sum(widths) + sp * (len(parts) - 1)
    a = int(255 * min(1, k * 1.5))
    y = 1490
    sh, sd = layer()
    x = 540 - tw / 2
    for i, p in enumerate(parts):
        sd.text((x, y + 8), p, font=f, fill=(0, 0, 0, int(a * 0.7)), anchor="lm", stroke_width=12, stroke_fill=(0, 0, 0, int(a * 0.7)))
        x += widths[i] + sp
    band = sh.crop((0, y - 150, W, y + 150)).filter(ImageFilter.GaussianBlur(8))
    img.paste(band, (0, y - 150), band)
    d = ImageDraw.Draw(img, "RGBA")
    x = 540 - tw / 2
    for i, p in enumerate(parts):
        col = CAP_RED if i == hi else (255, 255, 255)
        d.text((x, y), p, font=f, fill=col + (a,), anchor="lm", stroke_width=8, stroke_fill=(10, 8, 8, a))
        x += widths[i] + sp
R.caption = caption_wr
SHOTS.sort(key=lambda s: s["a"])
for s, nx in zip(SHOTS, SHOTS[1:] + [dict(a=DUR)]):
    s["b"] = nx["a"]

# ---------------------------------------------------------------- обработка «старой плёнки»
rng = np.random.default_rng(21)
GR = [np.array(Image.fromarray((rng.standard_normal((H // 2, W // 2)) * 12).astype(np.float32)).resize((W, H), Image.BILINEAR))
      for _ in range(4)]
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.62 * np.clip(((xx - W / 2) / (W * 0.68)) ** 2 + ((yy - H / 2) / (H * 0.64)) ** 2, 0, 1) ** 1.1).astype(np.float32)
PAPERT = np.array(Image.fromarray((rng.random((H // 6, W // 6)) * 16).astype(np.float32)).resize((W, H), Image.BICUBIC))
PAPERT += np.array(Image.fromarray((rng.random((H // 40, W // 40)) * 14).astype(np.float32)).resize((W, H), Image.BICUBIC))
LUM = np.array([0.3, 0.59, 0.11], np.float32)
TINT = np.array([1.0, 0.99, 0.94], np.float32)

def grade(im, n):
    a = np.asarray(im).astype(np.float32)
    l = a @ LUM
    a = a * 0.65 + l[..., None] * 0.35
    a = (a * TINT + 6)
    a = a - PAPERT[..., None] + GR[(n // 2) % 4][..., None]
    a = a * VIG[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def frame(T, n):
    R.NOW[0] = T
    sh = SHOTS[0]
    for s in SHOTS:
        if s["a"] <= T: sh = s
    im = sh["f"](T, T - sh["a"])
    k = ease((T - sh["a"]) / max(0.01, sh["b"] - sh["a"]))
    z = lerp(sh["zoom"][0], sh["zoom"][1], k)
    z *= 1 + 0.025 * (1 - ramp(T - sh["a"], 0, 0.18))
    im = camera(im, z, sh["cx"] or W / 2, sh["cy"] or H / 2)
    im = grade(im, n)
    d = ImageDraw.Draw(im, "RGBA")
    if sh["title"]:
        l1, l2, c2 = sh["title"]
        headline(d, l1, l2, c2, ramp(T, sh["a"], sh["a"] + 0.2))
    if T < END["L09"]:
        tag(d)
    R.caption(im, T)
    return im

def main():
    args = sys.argv[1:]
    if args and args[0] == "--frames":
        os.makedirs(os.path.join(ROOT, "frames"), exist_ok=True)
        for x in args[1].split(","):
            T = float(x)
            frame(T, int(T * FPS)).save(os.path.join(ROOT, "frames", f"a_{T:05.1f}.png"))
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", os.path.join(ROOT, "mix_loud.wav"), "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        p.stdin.write(frame(n / FPS, n).tobytes())
        if n % 300 == 0: print(f"{n / FPS:5.1f}s / {DUR}", flush=True)
    p.stdin.close(); p.wait()
    print("готово:", OUT)

if __name__ == "__main__":
    main()
