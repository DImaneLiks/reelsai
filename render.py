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
# ---------------------------------------------------------------- субтитры: белые КАПСОМ, ключевое слово красным
CAP_RED = (236, 40, 36)
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
    sc = 0.82 + 0.18 * k + 0.08 * math.sin(math.pi * k)          # лёгкий «прыжок»
    f = F(max(10, int(96 * sc)), 9)
    parts = [w.replace("—", "–").replace("«", "").replace("»", "").upper() for w in words]
    sp = f.getlength(" ")
    widths = [f.getlength(p) for p in parts]
    tw = sum(widths) + sp * (len(parts) - 1)
    if tw > 980:                                                     # слишком длинно — уменьшаем
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

# ---------------------------------------------------------------- обработка «старой бумаги»
rng = np.random.default_rng(21)
GR = [np.array(Image.fromarray((rng.standard_normal((H // 2, W // 2)) * 12).astype(np.float32)).resize((W, H), Image.BILINEAR))
      for _ in range(4)]
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.62 * np.clip(((xx - W / 2) / (W * 0.68)) ** 2 + ((yy - H / 2) / (H * 0.64)) ** 2, 0, 1) ** 1.1).astype(np.float32)
PAPERT = np.array(Image.fromarray((rng.random((H // 6, W // 6)) * 16).astype(np.float32)).resize((W, H), Image.BICUBIC))
PAPERT += np.array(Image.fromarray((rng.random((H // 40, W // 40)) * 14).astype(np.float32)).resize((W, H), Image.BICUBIC))
LUM = np.array([0.3, 0.59, 0.11], np.float32)
TINT = np.array([1.04, 0.98, 0.9], np.float32)

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
    if T < END["L11"]:
        tag(d)
    R.caption(im, T)
    return im

def main():
    args = sys.argv[1:]
    if args and args[0] == "--frames":
        os.makedirs(os.path.join(ROOT, "frames"), exist_ok=True)
        for x in args[1].split(","):
            T = float(x)
            frame(T, int(T * FPS)).save(os.path.join(ROOT, "frames", f"f_{T:05.1f}.png"))
        return
    cmd = [R.FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
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
