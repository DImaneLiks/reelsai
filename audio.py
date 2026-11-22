# -*- coding: utf-8 -*-
"""«История 05 — Сен-Жермен»: сборка звука из реплик F5-TTS (vo/NN.wav).
Выход: build/mix_loud.wav и build/timeline.json"""
import os, sys, json, wave, subprocess
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
REELS = "/Users/dmitrijpostnov/Documents/reels"
sys.path.insert(0, os.path.join(REELS, "ep1_build"))
import audio as A   # общие функции (тон, шум, шкатулка, огибающая)

SR, FF = A.SR, A.FF
TMP = os.path.join(ROOT, "clips"); os.makedirs(TMP, exist_ok=True)
LINES = json.load(open(os.path.join(ROOT, "lines.json")))
TEMPO = 1.18
FXN = "afftdn=nf=-28:nr=12," + A.BASE + ",aecho=0.8:0.45:40|75:0.10|0.06,volume=1.15,atempo=%.2f" % TEMPO

# пауза перед каждой репликой (1-based)
SKIP = set()
GAP = {i: 0.22 for i in range(1, 12)}
GAP.update({1: 0.05, 2: 0.08, 6: 0.35, 8: 0.4, 9: 0.35, 10: 0.35, 11: 0.45})
TAIL = 3.5

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return 0, len(x)
    return max(0, idx[0] - int(0.03 * SR)), min(len(x), idx[-1] + int(0.08 * SR))

def main():
    voice = np.zeros(int(130 * SR), np.float32)
    tl, t = [], 0.0
    for i, text in enumerate(LINES, 1):
        if i in SKIP: continue
        src = os.path.join(ROOT, "vo", f"{i:02d}.wav")
        raw = os.path.join(TMP, f"{i:02d}_48k.wav")
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR), raw], check=True)
        x = A.load(raw)
        a0, a1 = trim(x)
        seg = x[a0:a1].copy()
        fi, fo = int(0.01 * SR), int(0.04 * SR)
        seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
        cut = os.path.join(TMP, f"{i:02d}_cut.wav"); out = os.path.join(TMP, f"{i:02d}.wav")
        with wave.open(cut, "w") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
            f.writeframes((np.clip(seg, -1, 1) * 32767).astype(np.int16).tobytes())
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", cut, "-af", FXN, "-ac", "1", "-ar", str(SR), out], check=True)
        y = A.load(out)
        dur = len(seg) / SR / TEMPO
        t += GAP[i]
        A.place(voice, y[: int(dur * SR + 0.5 * SR)], t)
        # слова: тайминги Whisper по исходнику -> со сдвигом обрезки и ускорением
        ws = [w for s in json.load(open(os.path.join(ROOT, "vo", f"{i:02d}.json"))) for w in s["words"]]
        toks = text.split()
        if len(ws) == len(toks):
            tm = [((w["s"] - a0 / SR) / TEMPO, (w["e"] - a0 / SR) / TEMPO) for w in ws]
        else:
            L = [len(x_) + 2 for x_ in toks]; tot = sum(L); acc = 0; tm = []
            for l in L:
                s_ = dur * acc / tot; acc += l; tm.append((s_, dur * acc / tot))
        words = [dict(w=w_, s=round(t + max(0, a), 3), e=round(t + min(dur, b), 3)) for w_, (a, b) in zip(toks, tm)]
        tl.append(dict(id=f"L{i:02d}", speaker="narr", start=round(t, 3), dur=round(dur, 3), text=text,
                       words=words, env=A.envelope(seg[::1])))
        print(f"L{i:02d} {t:6.2f}-{t + dur:6.2f}  {text}")
        t += dur
    TOTAL = round(t + TAIL, 2)
    AT = {c["id"]: c["start"] for c in tl}; END = {c["id"]: c["start"] + c["dur"] for c in tl}
    WS = lambda cid, i: next(c for c in tl if c["id"] == cid)["words"][min(i, len(next(c for c in tl if c["id"] == cid)["words"]) - 1)]["s"]
    # ---------- фон и звуки
    n = int(TOTAL * SR) + SR
    L = np.zeros(n, np.float32); tt = np.arange(n) / SR
    pad = 0.03 * np.sin(2 * np.pi * 55 * tt) + 0.02 * np.sin(2 * np.pi * 82.4 * tt + 1) + 0.012 * np.sin(2 * np.pi * 110 * tt)
    pad *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * tt)
    # гудящий фон убран — в паузах тишина
    tone, place, mbox = A.tone, A.place, A.music_box
    hit = tone(48, 1.6, 0.5, 0.003, 0.5)   # чистый низкий удар, без шумовой атаки
    # ================= ЗЛОВЕЩАЯ МУЗЫКА (чистые тоны, без шума)
    M = np.zeros(n, np.float32)
    def put(sig, t0, buf=M):
        place(buf, sig.astype(np.float32), t0)
    def bell(f, vol, dur=5.0):                       # колокол: негармоничные обертоны
        t_ = np.arange(int(dur * SR)) / SR
        x_ = sum(a_ * np.sin(2 * np.pi * f * m_ * t_) * np.exp(-t_ * dk) for m_, a_, dk in
                 ((0.5, 0.5, 0.6), (1, 1, 0.9), (2.0, 0.5, 1.4), (2.4, 0.35, 1.8), (3.0, 0.25, 2.2), (4.2, 0.15, 3)))
        return vol * x_ * np.minimum(1, t_ / 0.004)
    def mbox_note(f, vol, dur=1.6):                  # шкатулка
        t_ = np.arange(int(dur * SR)) / SR
        x_ = np.sin(2 * np.pi * f * t_) + 0.35 * np.sin(2 * np.pi * 2 * f * t_) * np.exp(-t_ * 6) + 0.12 * np.sin(2 * np.pi * 5.4 * f * t_) * np.exp(-t_ * 12)
        return vol * x_ * np.exp(-t_ * 2.4) * np.minimum(1, t_ / 0.003)
    def drone(t0, t1, freqs, vol, fade=2.0):
        n_ = int((t1 - t0) * SR); t_ = np.arange(n_) / SR
        x_ = sum(np.sin(2 * np.pi * f_ * t_ + i_) * (1 / (1 + i_ * 0.4)) for i_, f_ in enumerate(freqs))
        x_ *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t_)
        e_ = np.minimum(1, np.minimum(t_ / fade, (t1 - t0 - t_) / fade)).clip(0, 1)
        put(vol * x_ * e_, t0)
    def heart(t0, t1, vol=0.35, bpm=72):
        k_ = t0
        while k_ < t1:
            put(tone(52, 0.18, vol, 0.004, 0.12), k_); put(tone(48, 0.18, vol * 0.7, 0.004, 0.12), k_ + 0.24)
            k_ += 60 / bpm
    def tick(t0, t1, vol=0.05):
        k_ = t0; j_ = 0
        while k_ < t1:
            put(tone(2600 if j_ % 2 else 2200, 0.03, vol, 0.0005, 0.02) + tone(900, 0.03, vol * 0.6, 0.0005, 0.015), k_)
            k_ += 0.5; j_ += 1
    hz = lambda m_: 440 * 2 ** ((m_ - 69) / 12)
    def melody(t0, t1, vol, notes, step=0.62):
        k_ = t0; j_ = 0
        while k_ < t1 - 0.3:
            m_ = notes[j_ % len(notes)]
            if m_: put(mbox_note(hz(m_), vol), k_)
            k_ += step; j_ += 1
    def choir(t0, t1, freqs, vol, fade=1.5):          # «хор»: гармоники с формантой «о», медленное вибрато
        n_ = int((t1 - t0) * SR); t_ = np.arange(n_) / SR
        x_ = np.zeros(n_)
        for i_, f0 in enumerate(freqs):
            vib = 1 + 0.006 * np.sin(2 * np.pi * (4.8 + i_ * 0.3) * t_ + i_)
            ph = 2 * np.pi * np.cumsum(f0 * vib) / SR
            for h_ in range(1, 9):
                g_ = np.exp(-((f0 * h_ - 500) / 220) ** 2) + 0.6 * np.exp(-((f0 * h_ - 850) / 260) ** 2) + 0.15 / h_
                x_ += g_ * np.sin(ph * h_) / (1 + i_ * 0.3)
        x_ /= max(1e-6, np.abs(x_).max())
        e_ = np.minimum(1, np.minimum(t_ / fade, (t1 - t0 - t_) / fade)).clip(0, 1)
        put(vol * x_ * e_, t0)
    def swell(t_hit, dur=1.8, fs=(146.8, 155.6, 220), vol=0.05):
        n_sw = int(dur * SR); t_sw = np.arange(n_sw) / SR
        put(sum(np.sin(2 * np.pi * f_ * t_sw) for f_ in fs) * (t_sw / dur) ** 2 * vol, t_hit - dur)
    MOTIF = [69, 72, 76, 74, 72, 71, 69, None, 64, 69, 71, 72, 71, 69, 68, None]     # ля минор, клавесинно-менуэтный
    W_ = WS
    def harps(t0, t1, vol, notes, step=0.22):        # «клавесин»: быстрые арпеджио шкатулкой
        k_ = t0; j_ = 0
        while k_ < t1 - 0.2:
            put(mbox_note(hz(notes[j_ % len(notes)]), vol, 0.8), k_); k_ += step; j_ += 1
    # ---- хук
    put(hit, 0.0); put(bell(55, 0.35, 6.0), 0.0)
    put(hit, W_("L01", 2) - 0.03); put(bell(110, 0.3), W_("L01", 2) - 0.03)
    heart(W_("L01", 3), W_("L01", 12), 0.35, 100)
    for k_ in (5, 6, 9):
        put(tone(1568, 0.5, 0.06, 0.002, 0.4), W_("L01", k_)); put(hit * 0.6, W_("L01", k_) - 0.02)
    swell(W_("L01", 12), 1.0, (220, 233.1, 329.6), 0.05)
    put(hit, W_("L01", 12) - 0.03); put(bell(55, 0.35, 6.0), W_("L01", 12) - 0.03)
    # ---- графиня: то же лицо
    harps(AT["L02"], W_("L02", 9), 0.03, [57, 60, 64, 69, 64, 60])
    put(hit, W_("L02", 9) - 0.03); put(bell(110, 0.3), W_("L02", 9) - 0.03)
    # ---- имя, эликсир, Клеопатра
    choir(AT["L03"] - 0.2, END["L05"] + 0.4, [55, 82.4, 110, 130.8], 0.05, 1.2)
    melody(AT["L03"], END["L05"], 0.045, MOTIF, 0.45)
    put(bell(220, 0.2), W_("L03", 3) - 0.05)
    put(bell(329.6, 0.2), W_("L04", 12) - 0.03)
    # ---- смерть и возвращение
    drone(AT["L06"] - 0.3, END["L06"] + 0.3, [41.2, 55, 61.7], 0.06, 0.8)
    put(bell(55, 0.35, 6.0), W_("L06", 7) - 0.05)
    swell(W_("L07", 4), 1.2, (110, 116.5, 164.8), 0.06)
    put(hit, W_("L07", 4) - 0.03); put(bell(146.8, 0.25), W_("L07", 4) - 0.03)
    # ---- загадки
    choir(AT["L08"] - 0.3, END["L10"] + 0.4, [55, 82.4, 110, 130.8], 0.05, 1.2)
    melody(AT["L08"], END["L10"], 0.042, MOTIF, 0.5)
    for c_ in ("L08", "L09", "L10"):
        put(bell(110, 0.25), AT[c_] - 0.05)
    put(hit, W_("L08", 8) - 0.03)
    put(tone(1568, 0.7, 0.06, 0.002, 0.5), W_("L09", 10)); put(tone(2093, 0.7, 0.05, 0.002, 0.5), W_("L09", 10) + 0.1)
    put(hit, W_("L10", 15) - 0.03); put(bell(55, 0.3, 6.0), W_("L10", 15) - 0.03)
    # ---- финал
    choir(AT["L11"] - 0.3, END["L11"] + 3.0, [55, 82.4, 110], 0.05, 1.5)
    melody(AT["L11"], END["L11"] + 1.5, 0.045, MOTIF, 0.45)
    put(bell(220, 0.3), END["L11"] + 0.2); put(bell(110, 0.35, 6.0), END["L11"] + 0.2)
    S = np.zeros(n, np.float32)
    L += M
    # отдельная дорожка музыки для согласования
    mm = M[: int(TOTAL * SR)]; mm = mm / max(1e-6, np.abs(mm).max()) * 0.8
    with wave.open(os.path.join(ROOT, "music_only.wav"), "w") as f_:
        f_.setnchannels(1); f_.setsampwidth(2); f_.setframerate(SR)
        f_.writeframes((mm * 32767).astype(np.int16).tobytes())
    # ---------- микс
    nT = int(TOTAL * SR)
    v = voice[:nT]; b = L[:nT]
    env = A.lp_fast(np.abs(v), 2400)
    duck = 1 - 0.6 * np.clip(env * 12, 0, 1)
    vr = float(np.sqrt(np.mean(v[np.abs(v) > 0.005] ** 2)))          # уровень голоса
    s_ = S[:nT]
    mix = v + b * (vr * 0.3) * duck + s_ * vr * 0.25   # музыка и крики заметно тише голоса
    mix = mix / np.abs(mix).max() * 0.89
    raw = os.path.join(ROOT, "mix.wav")
    with wave.open(raw, "w") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    comp = "acompressor=threshold=-24dB:ratio=3:attack=5:release=120:makeup=4dB"
    meas = subprocess.run([FF, "-hide_banner", "-i", raw, "-af", comp + ",loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex("{"): meas.rindex("}") + 1])
    ln = ("loudnorm=I=-14:TP=-1:LRA=11:linear=true:measured_I={input_i}:measured_TP={input_tp}:"
          "measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}").format(**m)
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", raw, "-af", comp + "," + ln,
                    "-ar", str(SR), os.path.join(ROOT, "mix_loud.wav")], check=True)
    json.dump(dict(total=TOTAL, clips=tl), open(os.path.join(ROOT, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", TOTAL)

if __name__ == "__main__":
    main()
