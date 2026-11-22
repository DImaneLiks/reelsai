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
