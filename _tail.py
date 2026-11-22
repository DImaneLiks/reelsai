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
