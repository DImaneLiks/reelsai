# -*- coding: utf-8 -*-
"""История 06 — «Амелия Эрхарт»: сборка звука из реплик Piper (vo/NN.wav + vo/NN.json).
Выход: mix_loud.wav и timeline.json  (формат как вHistory 05)"""
import os, sys, json, wave, subprocess
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/workspace")
from ep1_build import audio as A

SR, FF = A.SR, A.FF
TMP = os.path.join(ROOT, "clips"); os.makedirs(TMP, exist_ok=True)
LINES = json.load(open(os.path.join(ROOT, "lines.json")))
TEMPO = 1.06                                   # лёгкое ускорение речи
FXN = "afftdn=nf=-28:nr=10," + A.BASE + ",aecho=0.8:0.4:40|75:0.08|0.05,volume=1.1,atempo=%.2f" % TEMPO

GAP = {i: 0.3 for i in range(1, len(LINES) + 1)}
GAP.update({1: 0.05, 2: 0.25, 4: 0.4, 5: 0.35, 6: 0.35, 7: 0.35, 9: 0.4})
TAIL = 3.2

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx): return 0, len(x)
    return max(0, idx[0] - int(0.03 * SR)), min(len(x), idx[-1] + int(0.08 * SR))

def main():
    voice = np.zeros(int(120 * SR), np.float32); tl, t = [], 0.0
    for i, text in enumerate(LINES, 1):
        src = os.path.join(ROOT, "vo", f"{i:02d}.wav")
        raw = os.path.join(TMP, f"{i:02d}_24k.wav")
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
        # слова: тайминги piper по исходнику -> со сдвигом обрезки и ускорением
        ws = json.load(open(os.path.join(ROOT, "vo", f"{i:02d}.json")))
        toks = text.split()
        if len(ws) == len(toks):
            tm = [((w["s"] - a0 / SR) / TEMPO, (w["e"] - a0 / SR) / TEMPO) for w in ws]
        else:
            L_ = [len(x_) + 2 for x_ in toks]; tot = sum(L_); acc = 0; tm = []
            for l in L_:
                s_ = dur * acc / tot; acc += l; tm.append((s_, dur * acc / tot))
        words = [dict(w=w_, s=round(t + max(0, a), 3), e=round(t + min(dur, b), 3)) for w_, (a, b) in zip(toks, tm)]
        tl.append(dict(id=f"L{i:02d}", speaker="narr", start=round(t, 3), dur=round(dur, 3), text=text,
                       words=words, env=A.envelope(seg[::1])))
        print(f"L{i:02d} {t:6.2f}-{t + dur:6.2f}  {text}")
        t += dur
    TOTAL = round(t + TAIL, 2)
    AT = {c["id"]: c["start"] for c in tl}; END = {c["id"]: c["start"] + c["dur"] for c in tl}
    def WS(cid, k):
        c = next(c for c in tl if c["id"] == cid)
        return c["words"][min(k, len(c["words"]) - 1)]["s"]

    n = int(TOTAL * SR) + SR
    tt = np.arange(n) / SR
    M = np.zeros(n, np.float32)
    def put(sig, t0, buf=M): A.place(buf, sig.astype(np.float32), t0)
    tone, place = A.tone, A.place
    hit = tone(48, 1.6, 0.5, 0.003, 0.5)                      # низкий удар
    def bell(f, vol, dur=5.0):
        t_ = np.arange(int(dur * SR)) / SR
        x_ = sum(a_ * np.sin(2 * np.pi * f * m_ * t_) * np.exp(-t_ * dk) for m_, a_, dk in
                 ((0.5, 0.5, 0.6), (1, 1, 0.9), (2.0, 0.5, 1.4), (2.4, 0.35, 1.8), (3.0, 0.25, 2.2), (4.2, 0.15, 3)))
        return vol * x_ * np.minimum(1, t_ / 0.004)
    def drone(t0, t1, freqs, vol, fade=2.0):
        n_ = int((t1 - t0) * SR); t_ = np.arange(n_) / SR
        x_ = sum(np.sin(2 * np.pi * f_ * t_ + i_) * (1 / (1 + i_ * 0.4)) for i_, f_ in enumerate(freqs))
        x_ *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t_)
        e_ = np.minimum(1, np.minimum(t_ / fade, (t1 - t0 - t_) / fade)).clip(0, 1)
        put(vol * x_ * e_, t0)
    def swell(t_hit, dur=1.8, fs=(146.8, 155.6, 220), vol=0.05):
        n_sw = int(dur * SR); t_sw = np.arange(n_sw) / SR
        put(sum(np.sin(2 * np.pi * f_ * t_sw) for f_ in fs) * (t_sw / dur) ** 2 * vol, t_hit - dur)
    def choir(t0, t1, freqs, vol, fade=1.5):
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
    def prop(t0, t1, vol=0.05, step=0.32):                   # «пропеллер»: ритмичные тиканья
        k_ = t0
        while k_ < t1:
            put(tone(180 + 40 * (j_ % 2), 0.05, vol, 0.001, 0.04), k_); k_ += step
        # noop
    def motor(t0, t1, vol=0.06):                             # гул мотора: модулированный низкий тон
        n_ = int((t1 - t0) * SR); t_ = np.arange(n_) / SR
        x_ = np.sin(2 * np.pi * 62 * t_) * (0.7 + 0.3 * np.sin(2 * np.pi * 11 * t_))
        x_ += 0.35 * np.sin(2 * np.pi * 124 * t_)
        e_ = np.minimum(1, np.minimum(t_ / 1.2, (t1 - t0 - t_) / 1.2)).clip(0, 1)
        put(vol * x_ * e_, t0)
    def radio(t0, vol=0.2):                                  # радиопомеха + треск
        rng = np.random.default_rng(7)
        n_ = int(1.4 * SR); t_ = np.arange(n_) / SR
        x_ = (rng.standard_normal(n_) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t_))
              + np.sin(2 * np.pi * 640 * t_) * 0.3 * (np.abs(x_ := np.ones(n_))))
        x_ = rng.standard_normal(n_) * 0.3
        crack = np.zeros(n_); idx = rng.choice(n_, 12, replace=False)
        for q in idx: crack[q:q + 30] += rng.uniform(0.4, 1.0) * np.exp(-np.arange(30) / 8)
        x_ = (x_ * 0.5 + crack) * np.minimum(1, t_ / 0.05) * np.exp(-t_ * 1.4)
        put(vol * x_, t0)
    def splash(t0, vol=0.3):                                 # плеск воды/падение в океан
        rng = np.random.default_rng(11)
        n_ = int(2.2 * SR); t_ = np.arange(n_) / SR
        x_ = rng.standard_normal(n_) * np.exp(-t_ * 2.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t_))
        lp = np.convolve(x_, np.ones(200) / 200, "same")     # глушим — вода
        put(vol * lp, t0)
    def sonar(t0, vol=0.12):
        for q in range(3): put(tone(1000, 0.35, vol, 0.002, 0.5), t0 + q * 0.9)

    hz = lambda m_: 440 * 2 ** ((m_ - 69) / 12)
    def mbox_note(f, vol, dur=1.6):
        t_ = np.arange(int(dur * SR)) / SR
        x_ = np.sin(2 * np.pi * f * t_) + 0.35 * np.sin(2 * np.pi * 2 * f * t_) * np.exp(-t_ * 6) + 0.12 * np.sin(2 * np.pi * 5.4 * f * t_) * np.exp(-t_ * 12)
        return vol * x_ * np.exp(-t_ * 2.4) * np.minimum(1, t_ / 0.003)
    MOTIF = [69, 72, 76, 74, 72, 71, 69, None, 64, 69, 71, 72, 71, 69, 68, None]   # ля минор
    def melody(t0, t1, vol, notes=MOTIF, step=0.5):
        k_ = t0; j_ = 0
        while k_ < t1 - 0.3:
            m_ = notes[j_ % len(notes)]
            if m_: put(mbox_note(hz(m_), vol), k_)
            k_ += step; j_ += 1

    # ================= партитура по словам =================
    # L01 хук: исчезла над океаном... видели живой
    put(hit, 0.0); put(bell(55, 0.35, 6.0), 0.0)
    splash(WS("L01", 0), 0.35)                               # «Она исчезла»
    drone(AT["L01"], END["L01"] + 0.5, [41.2, 55, 61.7], 0.05, 1.5)
    put(hit, WS("L01", 3) - 0.03); put(tone(1568, 0.5, 0.06, 0.002, 0.4), WS("L01", 3))   # «Тихим океаном»
    swell(WS("L01", 7), 1.2, (110, 116.5, 164.8), 0.06)
    put(hit, WS("L01", 7) - 0.03); put(bell(110, 0.3), WS("L01", 7) - 0.03)               # «видели живым»
    # L02: первая женщина — героическая тема
    melody(AT["L02"], END["L02"], 0.045, step=0.45)
    motor(AT["L02"] + 0.5, END["L02"] + 0.3, 0.05)          # самолёт летит
    put(hit, WS("L02", 1) - 0.03); put(bell(220, 0.2), WS("L02", 1))
    # L03: облететь Землю по экватору, самый опасный рейс
    motor(AT["L03"], END["L03"] + 0.4, 0.06)
    choir(AT["L03"] - 0.2, END["L03"] + 0.4, [55, 82.4, 110, 130.8], 0.045, 1.2)
    put(tone(1568, 0.6, 0.05, 0.002, 0.4), WS("L03", 5)); put(hit * 0.6, WS("L03", 5) - 0.02)  # «экватору»
    swell(WS("L03", 10), 1.0, (98, 110, 146.8), 0.06); put(bell(146.8, 0.25), WS("L03", 10))   # «опасный»
    # L04: последний радиовызов
    radio(WS("L04", 1) - 0.4, 0.18)                          # эфир перед цитатой
    drone(AT["L04"] - 0.2, END["L04"] + 0.5, [55, 82.4], 0.05, 1.0)
    put(bell(110, 0.28), WS("L04", 5) - 0.05)                # «коротким»
    radio(END["L04"] - 0.6, 0.14)                            # эфир после цитаты
    # L05: загадка 1 — семнадцать дней, ни обломка
    put(bell(55, 0.32, 6.0), AT["L05"] - 0.05)
    splash(WS("L05", 10), 0.25)                              # «ни обломка»
    sonar(AT["L05"] + 1.0, 0.1)
    # L06: загадка 2 — фото в Японии
    put(bell(110, 0.25), AT["L06"] - 0.05)
    put(tone(2093, 0.4, 0.05, 0.002, 0.3), WS("L06", 8)); put(hit * 0.5, WS("L06", 8) - 0.02)  # «фотографировали»
    # L07: загадка 3 — череп, экспертиза опровергла
    put(bell(146.8, 0.25), AT["L07"] - 0.05)
    swell(WS("L07", 11), 1.0, (110, 123.5, 164.8), 0.06); put(hit, WS("L07", 11) - 0.03)       # «опровергла»
    # L08: моряк, субмарина
    drone(AT["L08"] - 0.2, END["L08"] + 0.4, [36.7, 55], 0.055, 1.0)
    sonar(AT["L08"] + 0.8, 0.12)
    put(tone(1568, 0.5, 0.05, 0.002, 0.4), WS("L08", 2))     # «субмарина»
    # L09: финальный вопрос
    choir(AT["L09"] - 0.3, END["L09"] + 2.6, [55, 82.4, 110], 0.05, 1.5)
    melody(AT["L09"], END["L09"] + 1.2, 0.045, step=0.45)
    splash(WS("L09", 0), 0.3)                                # «Погибла в море»
    put(hit, WS("L09", 4) - 0.03); put(bell(55, 0.35, 6.0), WS("L09", 4) - 0.03)              # «или пленницей»
    put(bell(220, 0.3), END["L09"] + 0.2); put(bell(110, 0.35, 6.0), END["L09"] + 0.2)

    # ---------- микс
    nT = int(TOTAL * SR)
    v = voice[:nT].copy(); s_ = M[:nT]
    env = A.lp_fast(np.abs(v), 2400)
    duck = 1 - 0.6 * np.clip(env * 12, 0, 1)
    vr = float(np.sqrt(np.mean(v[np.abs(v) > 0.005] ** 2)))
    mix = v + s_ * vr * 0.55 * duck
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
