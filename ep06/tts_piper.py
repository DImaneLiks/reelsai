# -*- coding: utf-8 -*-
"""История 06 — «Амелия Эрхарт»: озвучка Piper (ru_RU-dmitri-medium) + тайминги слов.

python3 tts_piper.py [NN ...]   -> vo/NN.wav (48k mono int16) и vo/NN.json {words:[{w,s,e}]}

Тайминги: piper не отдаёт выравниваний для этой модели, поэтому границы слов
оцениваются по кумулятивному весу фонем (пауза-«пробел» короче) и «прилипают»
к ближайшему энергетическому провалу сигнала (RMS 20 мс).
"""
import os, sys, json, wave
import numpy as np
from piper import PiperVoice, SynthesisConfig

ROOT = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(ROOT, "vo"); os.makedirs(VO, exist_ok=True)
MODEL = "/workspace/voices/ru_RU-dmitri-medium.onnx"
LINES = json.load(open(os.path.join(ROOT, "lines.json")))
SR_OUT = 48000
voice = None

def get_voice():
    global voice
    if voice is None:
        voice = PiperVoice.load(MODEL)
    return voice

def run_one(i, text):
    v = get_voice(); sr = v.config.sample_rate
    toks = text.split()
    ps = [p for sent in v.phonemize(text) for p in sent]
    ids = v.phonemes_to_ids(ps)
    a = v.phoneme_ids_to_audio(ids, SynthesisConfig())
    a = (a / max(1e-8, np.max(np.abs(a)))).astype(np.float32)
    D = len(a) / sr; n = len(ps)
    wt = np.where(np.array([p == " " for p in ps]), 0.45, 1.0)
    cw = np.cumsum(wt) * D / wt.sum()
    sp = [k for k, p in enumerate(ps) if p == " "]           # индексы пауз между словами
    w = int(0.02 * sr)
    rms = np.array([np.sqrt(np.mean(a[j:j + w] ** 2)) for j in range(0, len(a) - w, w)])
    th = max(rms.max() * 0.10, 0.02); active = rms > th
    sil = []; run = None
    for j, val in enumerate(active):
        if not val and run is None: run = j
        elif val and run is not None:
            if (j - run) * 0.02 >= 0.05: sil.append((run * w / sr, j * w / sr))
            run = None
    def snap(t):
        for s, e in sil:
            if s - 0.06 <= t <= e + 0.06: return e if t > s else s
        return t
    b = sorted(set(round(snap(cw[k]), 3) for k in sp))
    starts = [0.0] + [x for x in b if x > 0.05]
    while len(starts) < len(toks): starts.append(min(D, starts[-1] + 0.1))
    starts = starts[:len(toks)]
    words = [dict(w=t_, s=round(st, 3), e=round(max(st + 0.05, min(starts[j + 1] if j + 1 < len(starts) else D, D)), 3))
             for j, (t_, st) in enumerate(zip(toks, starts))]
    # запись 48k mono int16
    out = os.path.join(VO, f"{i:02d}.wav")
    with wave.open(out, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR_OUT)
        f.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    json.dump(words, open(os.path.join(VO, f"{i:02d}.json"), "w"), ensure_ascii=False)
    print(f"L{i:02d} {D:5.2f}s words={len(words)}/{len(toks)}  {text[:55]}")

if __name__ == "__main__":
    idxs = [int(x) for x in sys.argv[1:]] or list(range(1, len(LINES) + 1))
    for i in idxs:
        run_one(i, LINES[i - 1])
