# -*- coding: utf-8 -*-
"""История 05 — «Граф Сен-Жермен».
Стиль референса: штриховка, вытянутые фигуры с тенью на лицах, туман, газовые фонари,
приглушённая палитра, зерно, виньетка, заголовок сцены сверху (белый + красный), карточки с цифрами.

  /Users/dmitrijpostnov/Documents/reels/.venv/bin/python render.py               # полный рендер
  /Users/dmitrijpostnov/Documents/reels/.venv/bin/python render.py --frames 1,9  # кадры -> frames/
"""
import os, sys, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REELS = "/Users/dmitrijpostnov/Documents/reels"
sys.path.insert(0, os.path.join(REELS, "ep1_build"))
import render as R
from render import (W, H, FPS, YEL, text_c, F, ramp, lerp, ease, mix, clamp, camera)

TL = json.load(open(os.path.join(ROOT, "timeline.json")))
DUR = TL["total"]
OUT = os.path.join(os.path.dirname(ROOT), "История 05 - Сен-Жермен.mp4")
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

# ---------------------------------------------------------------- палитра
INK = (22, 20, 22); OW = 5
NIGHT = (34, 44, 48); NIGHT2 = (24, 30, 34)
BRICK, BRICK_D = (78, 58, 50), (58, 44, 40)
STONE = (62, 64, 64); STONE_L = (80, 82, 80)
LAMP = (252, 206, 120)
SKIN = (206, 186, 164); SKIN_D = (150, 130, 112)
COAT = (52, 52, 58); COAT2 = (74, 62, 52); DRESS = (92, 56, 52); DRESS2 = (70, 74, 84)
POLICE = (34, 40, 66)
PAPER = (222, 210, 184)
RED = (196, 40, 34); BLOOD_TXT = (170, 30, 26)
WHITE = (240, 236, 226)

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
    """кладём слой с фигурами и штрихуем его внутри силуэта (как в референсе)"""
    a = np.asarray(lay.getchannel("A")).astype(np.float32) / 255
    if alpha < 0.999:
        lay.putalpha(Image.fromarray((a * alpha * 255).astype(np.uint8)))
    im.paste(lay, (0, 0), lay)
    m = a * alpha * (HATCH * hatch + HATCH2 * cross)
    sh = Image.new("RGB", (W, H), INK)
    im.paste(sh, (0, 0), Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)))

# ---------------------------------------------------------------- викторианские персонажи (детализированные, с лицами)
HAIRS = [(46, 34, 28), (92, 62, 40), (120, 96, 70), (30, 28, 30)]
SHIRT = (226, 220, 204)

def face(d, x, hy, r, face_dir, kind, seed=0, look=0.0, T=0.0):
    """лицо поверх штриховки: глаза с белками и зрачками, брови, нос, рот"""
    f = face_dir
    jack = kind == "jack"
    sk = (176, 168, 160) if jack else SKIN
    hair = HAIRS[seed % len(HAIRS)]
    # волосы сзади / причёска
    if kind == "woman":
        d.ellipse([x - f * r * 0.9 - r * 0.5, hy - r * 0.5, x - f * r * 0.9 + r * 0.5, hy + r * 0.5], fill=hair, outline=INK, width=3)
    d.ellipse([x - r * 0.88, hy - r * 1.05, x + r * 0.88, hy + r * 1.05], fill=sk, outline=INK, width=4)
    d.chord([x - r * 0.88, hy - r * 1.05, x + r * 0.88, hy + r * 1.05], 90 if f > 0 else 270, 270 if f > 0 else 450,
            fill=mix(sk, (90, 70, 60), 0.12))                                            # тень на дальней стороне
    d.ellipse([x - f * r * 0.86 - r * 0.16, hy - r * 0.05, x - f * r * 0.86 + r * 0.16, hy + r * 0.38], fill=mix(sk, (90, 70, 60), 0.3), outline=INK, width=3)  # ухо
    if kind in ("man", "police", "jack"):
        d.chord([x - r * 0.9, hy - r * 1.1, x + r * 0.9, hy + r * 0.2], 180, 360, fill=hair)        # волосы
        LN(d, [(x - f * r * 0.74, hy - r * 0.35), (x - f * r * 0.7, hy + r * 0.1)], r * 0.1, hair)  # бакенбарды
    elif kind == "woman":
        d.chord([x - r * 0.92, hy - r * 1.1, x + r * 0.92, hy + r * 0.1], 180, 360, fill=hair)
    # глаза
    ex = x + f * r * 0.12
    for k, s in enumerate((-1, 1)):
        cx = ex + s * r * 0.32 + f * r * 0.06; cy = hy - r * 0.08
        w_, h_ = r * (0.2 if (s == -f) else 0.24), r * 0.17
        d.ellipse([cx - w_, cy - h_, cx + w_, cy + h_], fill=(244, 240, 232), outline=INK, width=3)
        px = cx + f * w_ * 0.35 + look * w_ * 0.3
        d.ellipse([px - h_ * 0.62, cy - h_ * 0.62, px + h_ * 0.62, cy + h_ * 0.62], fill=(60, 50, 44) if not jack else (120, 20, 16))
        d.ellipse([px - h_ * 0.28, cy - h_ * 0.28, px + h_ * 0.28, cy + h_ * 0.28], fill=INK)
        d.ellipse([px - h_ * 0.5, cy - h_ * 0.55, px - h_ * 0.15, cy - h_ * 0.2], fill=(255, 255, 255))
        d.line([(cx - w_ * 1.05, cy - h_ * 0.3), (cx + w_ * 1.05, cy - h_ * 0.3)], fill=sk if not jack else (150, 140, 134), width=1)
        d.arc([cx - w_, cy - h_, cx + w_, cy + h_], 200, 340, fill=INK, width=4)                  # верхнее веко
        by = cy - h_ * 2.0
        ang = (0.35 if jack else 0.12) * s * (1 if f > 0 else -1)
        LN(d, [(cx - w_ * 1.1, by - ang * r * 0.3), (cx + w_ * 1.1, by + ang * r * 0.3)], r * 0.09, hair)  # брови
    # нос
    nx = x + f * r * 0.55
    LN(d, [(x + f * r * 0.35, hy - r * 0.05), (nx + f * r * 0.12, hy + r * 0.3), (x + f * r * 0.36, hy + r * 0.36)], 4)
    # рот / усы
    my = hy + r * 0.58
    if kind in ("police",) or (kind == "man" and seed % 2 == 0) or jack:
        P(d, [(x + f * r * 0.05, my - r * 0.12), (x + f * r * 0.62, my - r * 0.2), (x + f * r * 0.75, my - r * 0.02),
              (x + f * r * 0.35, my - r * 0.04), (x - f * r * 0.05, my)], hair, 3)
    if jack:
        d.arc([x + f * r * 0.05 - r * 0.35, my - r * 0.35, x + f * r * 0.05 + r * 0.35, my + r * 0.12], 20, 160, fill=INK, width=4)  # ухмылка
    elif kind == "woman":
        d.ellipse([x + f * r * 0.22 - r * 0.14, my - r * 0.06, x + f * r * 0.22 + r * 0.14, my + r * 0.1], fill=(160, 70, 66), outline=INK, width=2)
        d.ellipse([x + f * r * 0.42 - r * 0.15, hy + r * 0.2, x + f * r * 0.42 + r * 0.15, hy + r * 0.4], fill=(220, 160, 150))
    else:
        LN(d, [(x + f * r * 0.05, my + r * 0.05), (x + f * r * 0.45, my + r * 0.02)], 4)
    # головной убор
    if kind in ("man", "jack"):
        hc = (14, 14, 16)
        RR(d, [x - r * 0.72, hy - r * 2.5, x + r * 0.72, hy - r * 0.62], hc, 5, 3)
        d.rectangle([x - r * 0.72, hy - r * 0.95, x + r * 0.72, hy - r * 0.72], fill=(90, 20, 18) if jack else (60, 56, 52))
        RR(d, [x - r * 1.3, hy - r * 0.78, x + r * 1.3, hy - r * 0.55], hc, 6, 3)
        if jack:                                                                        # тень полей шляпы на лице
            d.chord([x - r * 0.88, hy - r * 1.05, x + r * 0.88, hy + r * 0.2], 180, 360, fill=(10, 10, 12, 120))
    elif kind == "woman":
        bc = [(60, 44, 40), (70, 60, 80), (90, 70, 50)][seed % 3]
        d.chord([x - r * 1.2, hy - r * 1.5, x + r * 1.2, hy + r * 0.25], 180, 360, fill=bc, outline=INK, width=4)
        d.arc([x - r * 1.25, hy - r * 1.3, x + r * 1.25, hy + r * 0.35], 175, 365, fill=mix(bc, INK, 0.4), width=max(3, int(r * 0.12)))
        LN(d, [(x - f * r * 0.9, hy + r * 0.45), (x - f * r * 1.0, hy + r * 1.2)], 4, (170, 60, 56))
    elif kind == "police":
        P(d, [(x - r * 0.85, hy - r * 0.5), (x - r * 0.68, hy - r * 1.7), (x, hy - r * 2.2), (x + r * 0.68, hy - r * 1.7),
              (x + r * 0.85, hy - r * 0.5)], POLICE, 4)
        LN(d, [(x - r * 1.0, hy - r * 0.5), (x + r * 1.0, hy - r * 0.5)], r * 0.15, (20, 22, 40))
        P(d, [(x, hy - r * 1.55), (x + r * 0.22, hy - r * 1.25), (x, hy - r * 0.95), (x - r * 0.22, hy - r * 1.25)], (200, 186, 130), 2)

def hand(d, x, y, r, glove=False):
    c = (20, 18, 20) if glove else SKIN
    d.ellipse([x - r * 0.32, y - r * 0.28, x + r * 0.32, y + r * 0.36], fill=c, outline=INK, width=3)

def vfig(d, x, feet, h, kind="man", T=0.0, phase=None, face=1, lantern=False, c=None, fd=None, seed=0, look=0.0, body=None):
    """вытянутая детализированная фигура. kind: man | woman | police | jack;  face: 1 вправо, -1 влево"""
    f = face; fd = fd or d
    kind_f = kind; kind = body or kind
    r = h * 0.075
    hy = feet - h + r * 1.4
    neck = hy + r * 1.0; top = hy + r * 1.3
    hip = feet - h * 0.40
    sw = r * 1.4
    swing = 0 if phase is None else math.sin(phase)
    col = c or {"man": [COAT2, COAT, (66, 70, 60), (84, 66, 70)][seed % 4], "woman": [DRESS, (64, 70, 90), (90, 80, 60)][seed % 3],
                "police": POLICE, "jack": (16, 16, 18)}[kind]
    dk = mix(col, INK, 0.35)
    # ноги и обувь
    if kind != "woman":
        for s, k in ((-1, 1), (1, -1)):
            fx = x + s * r * 0.45 + k * swing * r * 0.9
            LN(d, [(x + s * r * 0.45, hip), (fx, feet - r * 0.25)], r * 0.62, (36, 34, 38) if kind != "police" else (24, 26, 44))
            P(d, [(fx - r * 0.35, feet - r * 0.4), (fx + f * r * 0.75, feet - r * 0.15), (fx + f * r * 0.8, feet + r * 0.05),
                  (fx - r * 0.35, feet + r * 0.05)], (18, 16, 16), 3)
            LN(d, [(fx, feet - r * 0.33), (fx + f * r * 0.4, feet - r * 0.2)], 3, (90, 86, 84))
    if kind == "jack":                                                                  # плащ: красная подкладка сзади
        P(d, [(x - sw * 0.9, top), (x + sw * 0.9, top), (x + sw * 2.0, hip + r * 2.2), (x - sw * 2.0, hip + r * 2.2)], (110, 18, 16))
        P(d, [(x - sw * 0.9, top), (x + sw * 0.9, top), (x + sw * 1.75, hip + r * 2.0), (x - sw * 1.75, hip + r * 2.0)], col)
        for s in (-1, 1):
            LN(d, [(x + s * sw * 0.4, top + r * 0.6), (x + s * sw * 1.1, hip + r * 1.9)], 3, (50, 50, 56))
        P(d, [(x - sw * 0.75, top - r * 0.4), (x - sw * 0.2, top + r * 0.9), (x - sw * 0.95, top + r * 0.5)], col, 3)   # стоячий воротник
        P(d, [(x + sw * 0.75, top - r * 0.4), (x + sw * 0.2, top + r * 0.9), (x + sw * 0.95, top + r * 0.5)], col, 3)
        P(d, [(x - r * 0.3, top), (x + r * 0.3, top), (x, top + r * 0.9)], SHIRT, 3)
        bx = x + f * sw * 1.5
        RR(d, [bx - r * 0.8, hip - r * 0.2, bx + r * 0.8, hip + r * 0.9], (60, 36, 26), 8, 3)       # саквояж
        d.arc([bx - r * 0.4, hip - r * 0.6, bx + r * 0.4, hip + r * 0.2], 180, 360, fill=INK, width=5)
        hand(d, bx, hip - r * 0.45, r, glove=True)
        cx_ = x - f * sw * 1.4
        LN(d, [(cx_, hip - r * 0.3), (cx_ - f * r * 0.3, feet)], 7, (40, 30, 24))                     # трость
        d.ellipse([cx_ - r * 0.22, hip - r * 0.6, cx_ + r * 0.22, hip - r * 0.2], fill=(190, 170, 110), outline=INK, width=3)
        hand(d, cx_, hip - r * 0.3, r, glove=True)
    elif kind == "woman":
        P(d, [(x - sw * 0.9, hip - r), (x + sw * 0.9, hip - r), (x + sw * 1.75 + swing * r * 0.3, feet),
              (x - sw * 1.75 + swing * r * 0.3, feet)], col)                                          # юбка
        for j in range(4):
            xx_ = x - sw * 0.6 + j * sw * 0.4
            LN(d, [(xx_, hip - r * 0.5), (xx_ + (xx_ - x) * 0.7, feet - r * 0.2)], 3, dk)
        P(d, [(x - sw * 0.6, hip - r * 0.9), (x + sw * 0.6, hip - r * 0.9), (x + sw * 0.9, feet - r * 1.3), (x - sw * 0.9, feet - r * 1.3)],
          (196, 186, 166), 3)                                                                           # фартук
        P(d, [(x - sw * 0.8, top), (x + sw * 0.8, top), (x + sw * 0.85, hip - r), (x - sw * 0.85, hip - r)], dk)   # корсаж
        sc = [(110, 80, 70), (90, 96, 110), (120, 100, 80)][seed % 3]
        P(d, [(x - sw * 1.1, top + r * 0.1), (x + sw * 1.1, top + r * 0.1), (x + sw * 0.4, top + r * 2.6), (x, top + r * 3.2),
              (x - sw * 0.4, top + r * 2.6)], sc)                                                       # шаль
        for j in range(7):
            fx_ = x - sw * 0.4 + j * sw * 0.13
            LN(d, [(fx_, top + r * 2.7 + abs(j - 3) * -r * 0.1), (fx_, top + r * 3.2 + abs(j - 3) * -r * 0.1)], 2, dk)
        for s in (-1, 1):
            ax = x + s * sw * 0.55 - swing * s * r * 0.3
            LN(d, [(x + s * sw * 1.0, top + r * 0.5), (ax, hip - r * 0.6)], r * 0.55, sc)
            hand(d, ax, hip - r * 0.5, r)
    else:
        coat_bot = hip + r * (1.9 if kind == "man" else 1.2)
        P(d, [(x - sw * 0.85, top), (x + sw * 0.85, top), (x + sw * 1.15, coat_bot), (x - sw * 1.15, coat_bot)], col)
        LN(d, [(x, top + r * 1.6), (x, coat_bot)], 3, dk)
        P(d, [(x - r * 0.42, top), (x + r * 0.42, top), (x, top + r * 1.3)], SHIRT, 3)                 # рубашка
        if kind == "man":
            sc = [(140, 40, 36), (60, 70, 100), (110, 100, 70), (40, 60, 50)][seed % 4]
            P(d, [(x - r * 0.25, top + r * 0.1), (x + r * 0.25, top + r * 0.1), (x + r * 0.12, top + r * 0.9), (x - r * 0.12, top + r * 0.9)], sc, 2)
            for s in (-1, 1):                                                                         # лацканы
                P(d, [(x + s * r * 0.42, top), (x + s * sw * 0.8, top + r * 0.3), (x + s * r * 0.15, top + r * 1.8)], dk, 3)
        else:                                                                                          # полиция: ремень, пуговицы, номер
            LN(d, [(x - sw * 1.0, hip - r * 0.2), (x + sw * 1.0, hip - r * 0.2)], r * 0.3, (20, 20, 22))
            RR(d, [x - r * 0.25, hip - r * 0.38, x + r * 0.25, hip - r * 0.02], (200, 186, 130), 3, 2)
            for j in range(4):
                yb = top + r * 0.6 + j * r * 0.75
                d.ellipse([x - r * 0.1, yb - r * 0.1, x + r * 0.1, yb + r * 0.1], fill=(200, 186, 130))
            P(d, [(x - sw * 0.85, top), (x + sw * 0.85, top), (x + sw * 0.6, top + r * 0.5), (x - sw * 0.6, top + r * 0.5)], dk, 3)
            if kind_f == "police": text_c(d, (x - f * sw * 0.5, top + r * 0.28), "H", F(max(10, int(r * 0.35)), 9), (200, 186, 130))
        for j in range(3):
            yb = top + r * 1.9 + j * r * 0.7
            if kind == "man": d.ellipse([x + r * 0.15, yb - r * 0.08, x + r * 0.31, yb + r * 0.08], fill=(30, 28, 26))
        for s in (-1, 1):                                                                             # руки с манжетами
            if lantern and s == f: continue
            ax = x + s * sw * 1.05 - swing * s * r * 0.5
            LN(d, [(x + s * sw * 0.9, top + r * 0.4), (ax, hip - r * 0.1)], r * 0.62, col)
            LN(d, [(ax - r * 0.25, hip - r * 0.35), (ax + r * 0.25, hip - r * 0.35)], 4, SHIRT if kind == "man" else dk)
            hand(d, ax, hip, r)
    if lantern:
        lx, ly = x + f * sw * 1.4, hip + r * 0.5
        LN(d, [(x + f * sw * 0.9, top + r * 0.4), (lx, ly - r * 1.0)], r * 0.6, col)
        hand(d, lx, ly - r * 1.0, r)
        LN(d, [(lx, ly - r * 1.0), (lx, ly - r * 0.6)], 3)
        RR(d, [lx - r * 0.5, ly - r * 0.6, lx + r * 0.5, ly + r * 0.7], LAMP, 6, 3)
        LN(d, [(lx - r * 0.5, ly), (lx + r * 0.5, ly)], 3)
    # шея и лицо (на отдельном слое без штриховки)
    fd.rectangle([x - r * 0.3, hy + r * 0.6, x + r * 0.3, top + r * 0.1], fill=SKIN if kind != "jack" else (176, 168, 160))
    globals()["face"](fd, x, hy, r, f, kind_f, seed, look, T)

def figures(im, specs, hatch=0.32, alpha=1.0):
    lay, ld = layer(); lay2, fdd = layer()
    for i, s in enumerate(specs):
        vfig(ld, fd=fdd, **{"seed": i, **s})
    stamp(im, lay, hatch, 0.0, alpha)
    if alpha < 0.999:
        lay2.putalpha(Image.fromarray((np.asarray(lay2.getchannel("A")).astype(np.float32) * alpha).astype(np.uint8)))
    im.paste(lay2, (0, 0), lay2)

# ---------------------------------------------------------------- фоны
def glow(im, x, y, rad, k=1.0, c=LAMP):
    g = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(g)
    gd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=int(120 * k))
    g = g.filter(ImageFilter.GaussianBlur(rad * 0.45))
    im.paste(Image.new("RGB", (W, H), c), (0, 0), g)

def gas_lamp(im, d, x, base, k=1.0):
    LN(d, [(x, base), (x, base - 620)], 16, (30, 30, 32))
    LN(d, [(x - 40, base - 620), (x + 40, base - 620)], 10, (30, 30, 32))
    P(d, [(x - 40, base - 700), (x + 40, base - 700), (x + 28, base - 620), (x - 28, base - 620)], mix((60, 56, 50), LAMP, k), 4)
    P(d, [(x - 50, base - 700), (x + 50, base - 700), (x, base - 750)], (30, 30, 32), 4)
    if k > 0.05:
        glow(im, x, base - 660, 260, k)

def fog(im, T, k=0.5, y0=1100):
    f = Image.new("L", (W, H), 0); fd = ImageDraw.Draw(f)
    for j in range(7):
        y = y0 + j * 120 + math.sin(T * 0.4 + j) * 20
        x = ((T * (18 + j * 6) + j * 300) % (W + 900)) - 450
        fd.ellipse([x - 600, y - 70, x + 600, y + 70], fill=int(90 * k))
        fd.ellipse([x - 600 + 1100, y - 50, x + 600 + 1100, y + 50], fill=int(70 * k))
    f = f.filter(ImageFilter.GaussianBlur(40))
    im.paste(Image.new("RGB", (W, H), (176, 184, 182)), (0, 0), f)

def cobbles(d, y0=1450):
    d.rectangle([0, y0, W, H], fill=STONE)
    for row in range(12):
        y = y0 + 20 + row * 42
        for k in range(-1, 16):
            x = k * 76 + (38 if row % 2 else 0)
            d.ellipse([x, y, x + 66, y + 30], fill=STONE_L if (k + row) % 3 else (70, 72, 70), outline=(44, 46, 46), width=2)
    LN(d, [(0, y0), (W, y0)], 6)

def street(T, lamps=(1.0, 1.0), y0=1450, fogk=0.55):
    im, d = new(NIGHT)
    for k in range(5):                                                          # дома
        x = -60 + k * 240; top = 300 + (k * 131) % 260
        P(d, [(x, y0), (x, top), (x + 120, top - 90), (x + 230, top), (x + 230, y0)], BRICK if k % 2 else BRICK_D, 5)
        RR(d, [x + 160, top - 150, x + 200, top - 40], BRICK_D, 2, 4)            # труба
        for j in range(5):
            for c_ in range(2):
                wx = x + 35 + c_ * 100; wy = top + 80 + j * 190
                if wy > y0 - 150: continue
                lit = (k * 5 + j * 3 + c_) % 7 == 0
                RR(d, [wx, wy, wx + 60, wy + 110], (200, 150, 80) if lit else (28, 30, 34), 3, 3)
                LN(d, [(wx + 30, wy), (wx + 30, wy + 110)], 3)
    cobbles(d, y0)
    for x, k in zip((150, 930), lamps):
        gas_lamp(im, d, x, y0 + 40, k)
    d = ImageDraw.Draw(im, "RGBA")
    fog(im, T, fogk)
    return im, ImageDraw.Draw(im, "RGBA")

def skyline(T):
    im, d = new((44, 54, 58))
    d.ellipse([700, 260, 900, 460], fill=(226, 222, 200))
    glow(im, 800, 360, 260, 0.8, (210, 214, 200)); d = ImageDraw.Draw(im, "RGBA")
    P(d, [(80, 1200), (80, 560), (140, 480), (200, 560), (200, 1200)], (26, 30, 34), 0)     # башня с часами
    d.ellipse([105, 600, 175, 670], fill=(220, 210, 170))
    for k in range(12):
        x = 200 + k * 80; top = 860 + (k * 97) % 220
        d.rectangle([x, top, x + 82, 1300], fill=(26, 30, 34))
        d.rectangle([x + 20, top - 50, x + 34, top], fill=(26, 30, 34))
        if k % 3 == 0: d.rectangle([x + 30, top + 60, x + 50, top + 90], fill=(180, 140, 80))
    d.rectangle([0, 1300, W, H], fill=(20, 24, 28))
    fog(im, T, 0.6, 1050)
    return im, ImageDraw.Draw(im, "RGBA")

def desk(T, candle=True):
    im, d = new((40, 34, 30))
    if candle:
        glow(im, 820, 760, 420, 1.0, (250, 190, 110)); d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 1100, W, H], fill=(84, 58, 40)); LN(d, [(0, 1100), (W, 1100)], 6)
    for k in range(6):
        LN(d, [(0, 1180 + k * 130), (W, 1160 + k * 130)], 3, (66, 46, 32))
    if candle:
        RR(d, [790, 820, 850, 1100], (226, 216, 190), 6, 4)
        P(d, [(806, 820), (820, 750 - 10 * math.sin(R.NOW[0] * 13)), (834, 820)], LAMP, 3)
    return im, d

def letter(d, x, y, w, h, rot=0.0):
    RR(d, [x - w / 2, y - h / 2, x + w / 2, y + h / 2], PAPER, 4, 4)
    for j in range(int(h / 60) - 2):
        yy = y - h / 2 + 90 + j * 60
        pts = [(x - w / 2 + 50 + i * 20, yy + 6 * math.sin(i * 1.7 + j)) for i in range(int((w - 110) / 20))]
        LN(d, pts, 4, BLOOD_TXT)

# ---------------------------------------------------------------- типографика
def headline(d, l1, l2, c2=RED, k=1.0, y=230):
    if k <= 0: return
    a = int(255 * k)
    text_c(d, (540, y), l1, F(84, 9), WHITE + (a,), stroke=8, sfill=(12, 10, 10, a))
    if l2:
        text_c(d, (540, y + 100), l2, F(84, 9), c2 + (a,), stroke=8, sfill=(12, 10, 10, a))

def tag(d, s="ТАЙНЫ ИСТОРИИ · XVIII ВЕК"):
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

def dim(im, k=0.55, tint=(40, 8, 6)):
    return Image.blend(im, Image.new("RGB", (W, H), tint), k)
