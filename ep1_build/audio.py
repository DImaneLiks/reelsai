# -*- coding: utf-8 -*-
"""Общие аудио-хелперы (воссозданы по использованию в audio.py)."""
import wave
import numpy as np

SR = 24000
FF = "ffmpeg"
BASE = "highpass=f=90,lowpass=f=6800"


def load(path):
    with wave.open(path, "rb") as f:
        assert f.getnchannels() == 1, f"{path}: ожидается mono"
        x = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
    return x


def save(path, x, sr=SR):
    with wave.open(path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def place(buf, sig, t):
    """добавить sig в buf (numpy-массив, модифицируется in-place) начиная с момента t (сек)"""
    i = max(0, int(round(t * SR)))
    m = min(len(buf) - i, len(sig))
    if m > 0:
        buf[i:i + m] += sig[:m]


def tone(freq, dur, vol=1.0, atk=0.005, dec=0.3):
    t = np.arange(int(dur * SR)) / SR
    e = np.minimum(1, t / max(atk, 1e-5)) * np.exp(-t * (1.0 / max(dec, 1e-4)))
    x = np.sin(2 * np.pi * freq * t) * e
    return (vol * x / max(1e-9, np.abs(x).max())).astype(np.float32)


def envelope(x, n=512):
    """сжатая огибающая громкости для визуализации"""
    m = max(1, len(x) // n)
    e = np.sqrt(np.array([np.mean(x[i:i + m] ** 2) for i in range(0, len(x), m)]))
    mx = e.max() if e.max() > 0 else 1.0
    return [round(float(v / mx), 4) for v in e]


def lp_fast(x, cutoff_hz):
    """экспоненциальный сглаживатель (для дакинга)"""
    a = 1 - np.exp(-2 * np.pi * cutoff_hz / SR)
    out = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (abs(v) - acc)
        out[i] = acc
    return out


def music_box(freq, dur=1.2, vol=0.5):
    t = np.arange(int(dur * SR)) / SR
    x = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * 2.76 * freq * t) * np.exp(-t * 8)
         + 0.15 * np.sin(2 * np.pi * 5.4 * freq * t) * np.exp(-t * 14))
    x *= np.exp(-t * 3.0) * np.minimum(1, t / 0.003)
    return (vol * x / max(1e-9, np.abs(x).max())).astype(np.float32)
