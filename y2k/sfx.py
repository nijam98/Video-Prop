# Light Y2K sound effects synced to the graphics, mixed under the voice.
# writes work/audio_mix.wav from work/audio60.wav
import os, sys, wave, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render as R

SR = 48000
w = wave.open("work/audio60.wav"); ch = w.getnchannels()
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
v = v.reshape(-1, ch).mean(1)
fx = np.zeros(len(v) + SR, np.float32)
rng = np.random.default_rng(5)


def add(t, sig):
    i = int(t * SR)
    if i < 0 or i >= len(fx): return
    n = min(len(sig), len(fx) - i); fx[i:i + n] += sig[:n]


def tt(d): return np.arange(int(d * SR)) / SR


def shing():
    t = tt(0.45); s = np.zeros_like(t)
    for f in (2400, 3150, 4200, 5600, 7100):
        s += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t * rng.uniform(7, 12))
    s *= 0.5 + 0.5 * np.sin(2 * np.pi * 22 * t)          # shimmer
    th = np.sin(2 * np.pi * (90 - 40 * t[:len(t) // 3]) * t[:len(t) // 3]) * np.exp(-t[:len(t) // 3] * 22)
    s[:len(th)] += 2.2 * th                              # low thump for punch
    return s / np.abs(s).max()


def blip():
    t = tt(0.09); f = np.where(t < 0.045, 1046, 1568)
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + np.sin(2 * np.pi * f * t) * 0.6
    return s * np.exp(-t * 18)


def ding():
    t = tt(0.25)
    return (np.sin(2 * np.pi * 880 * t) * (t < 0.08) + np.sin(2 * np.pi * 1320 * t) * (t >= 0.08)) * np.exp(-t * 9)


def whoosh(d=0.26):
    n = int(d * SR); x = rng.normal(0, 1, n).astype(np.float32)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(fr + 1) - np.log(2500)) ** 2) / 1.2)
    y = np.fft.irfft(X, n); y /= np.abs(y).max() + 1e-9
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return y * env


def boot():
    t = tt(0.18); f = 300 + 9000 * t ** 1.4
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)


add(0.0, 0.16 * boot())
for c in R.SEC_STARTS: add(c - 0.08, 0.11 * whoosh())
for c in R.HOOK_CUTS: add(c - 0.05, 0.07 * whoosh(0.18))
for e in R.EL:
    k = e["kind"]
    if k == "chrome": add(e["t0"] + 0.1, 0.13 * shing())
    elif k == "pill": add(e["t0"] + 0.05, 0.06 * blip())
    elif k == "window": add(e["t0"], 0.07 * ding())
    if k == "window" and e["cursor"]: add(e["cursor"][1], 0.06 * blip())
mix = v + fx[:len(v)]
st = np.repeat(mix[:, None], 2, 1)
tmp = "work/_mix_raw.wav"
o = wave.open(tmp, "w"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
o.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "alimiter=limit=0.89:level=false", "-ar", "48000",
                "-c:a", "pcm_s16le", "work/audio_mix.wav"], check=True)
print("audio_mix ok", round(len(v) / SR, 2), "s")
