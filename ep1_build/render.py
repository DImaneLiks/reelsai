# -*- coding: utf-8 -*-
"""Локальная замена внешнего модуля reels/ep1_build/render.py.

Содержит только то, что использует build05/render.py: константы кадра,
хелперы (ramp/lerp/ease/mix/clamp/camera/F/text_c) и субтитры по timeline.json.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 1080, 1920
FPS = 30
FF = "ffmpeg"

YEL = (242, 200, 92)

NOW = [0.0]          # текущее время кадра (используется для анимаций)
TL = {"total": 0.0, "clips": []}
CHUNKS = []
SPEECH = {}

STOP = set("""и в во со не он она они мы вы я ты к от до над под за на по о об же бы ли
как но а ну да их его её ей ему нас вас вам тебя меня мне этого этом этой этот эта это
тоже даже уже ещё еще через между про при для без после перед было была были быть есть
был будет будут""".split())

# ---------------------------------------------------------------- шрифты
_FDIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
          os.path.expanduser("~/Library/Fonts"), "C:/Windows/Fonts"]

def _find(name):
    for d in _FDIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None

_BOLD = _find("DejaVuSans-Bold.ttf") or _find("LiberationSans-Bold.ttf")
_REG = _find("DejaVuSans.ttf") or _find("LiberationSans-Regular.ttf") or _BOLD
_cache = {}

def F(size, w=9):
    """w>=9 — жирный."""
    path = _BOLD if w >= 9 else _REG
    key = (path, size)
    f = _cache.get(key)
    if f is None:
        f = ImageFont.truetype(path, size)
        _cache[key] = f
    return f

# ---------------------------------------------------------------- хелперы
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ramp(T, a, b):
    if b <= a:
        return 1.0
    return clamp((T - a) / (b - a))

def lerp(a, b, k):
    return a + (b - a) * k

def ease(k):
    k = clamp(k)
    return k * k * (3 - 2 * k)

def mix(c1, c2, k):
    k = clamp(k)
    return tuple(int(round(a + (b - a) * k)) for a, b in zip(c1[:3], c2[:3])) + \
           (c1[3:] if len(c1) > 3 else ())

def camera(im, z, cx=None, cy=None):
    """Зум с центром (cx, cy) в координатах кадра; z=1 — без изменений."""
    if abs(z - 1.0) < 1e-4:
        return im
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    nw, nh = int(W * z), int(H * z)
    big = im.resize((nw, nh), Image.BILINEAR)
    x = int(clamp(cx * z - W / 2, 0, nw - W))
    y = int(clamp(cy * z - H / 2, 0, nh - H))
    return big.crop((x, y, x + W, y + H))

def text_c(d, xy, s, font, fill, stroke=0, sfill=None, anchor="mm"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=sfill)

# ---------------------------------------------------------------- чанки и субтитры
def build_chunks():
    """Разбивает реплики спикеров на короткие чанки 2–4 слова по таймингам слов."""
    CHUNKS.clear()
    for spk, clips in SPEECH.items():
        for c in clips:
            words = c["words"]
            i = 0
            while i < len(words):
                n = 3 if i + 3 <= len(words) else len(words) - i
                # не рвём посреди коротких слов-связок
                while n > 2 and i + n < len(words) and words[i + n - 1]["w"].strip(
                        ".,!?«»—–: ").lower() in ("и", "в", "не", "во", "со", "на", "но"):
                    n -= 1
                ch = words[i:i + n]
                CHUNKS.append(dict(spk=spk, s=ch[0]["s"], e=ch[-1]["e"],
                                   words=[w["w"] for w in ch]))
                i += n
    CHUNKS.sort(key=lambda c: c["s"])
