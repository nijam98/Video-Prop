#!/usr/bin/env python3
"""Build the audio for the Naz Property video.

- cleans the voiceover (assets/voiceover.m4a)
- writes a per-frame loudness envelope for lip sync (src/env.js)
- synthesises music + sound effects and mixes everything into build/mix.wav

Usage: python3 tools/audio.py
"""
import json
import os
import subprocess
import wave

import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
SR = 48000
DUR = 64.0
FPS = 30
N = int(SR * DUR)
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- helpers
def t_axis(d):
    return np.arange(int(SR * d)) / SR


def env_exp(d, decay):
    return np.exp(-t_axis(d) / decay)


def adsr(n, a=0.005, r=0.05):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def noise(d):
    return rng.standard_normal(int(SR * d))


def sweep_sine(f0, f1, d, curve="exp"):
    t = t_axis(d)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (t / d)
    else:
        f = f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def place(track, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(track):
        return
    j = min(len(track), i + len(clip))
    track[i:j] += clip[: j - i] * gain


def varlp(x, fc):
    """One-pole lowpass with a time-varying cutoff (array, Hz)."""
    y = np.zeros_like(x)
    a = np.exp(-2 * np.pi * np.clip(fc, 20, SR / 2.2) / SR)
    s = 0.0
    for i in range(len(x)):
        s = a[i] * s + (1 - a[i]) * x[i]
        y[i] = s
    return y


# ---------------------------------------------------------------- sfx
def sfx_whoosh(d=0.5, up=True):
    n = noise(d)
    t = t_axis(d) / d
    fc = (300 + 5000 * t ** 2) if up else (5300 - 5000 * t ** 0.5)
    y = varlp(n, fc) - varlp(n, fc * 0.25)
    e = np.sin(np.pi * np.clip(t, 0, 1)) ** 1.5
    return norm(y * e, 0.9)


def sfx_boom():
    d = 1.8
    body = sweep_sine(95, 32, d) * env_exp(d, 0.45)
    click = lp(noise(d), 900) * env_exp(d, 0.05)
    rumble = lp(noise(d), 160) * env_exp(d, 0.5)
    y = body * 1.0 + click * 0.8 + rumble * 2.2
    return norm(np.tanh(y * 2.2), 1.0)


def sfx_pop(f0=900, f1=260):
    d = 0.12
    y = sweep_sine(f0, f1, d) * env_exp(d, 0.03)
    y += hp(noise(d), 2000) * env_exp(d, 0.006) * 0.4
    return norm(y, 0.8)


def sfx_blip(f=1200, d=0.07):
    t = t_axis(d)
    y = np.sign(np.sin(2 * np.pi * f * t)) * 0.35 + np.sin(2 * np.pi * f * t)
    return norm(lp(y, 6000) * adsr(len(t), 0.002, 0.03), 0.6)


def bell(f, d=1.2, decay=0.35, partials=((1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12))):
    t = t_axis(d)
    y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (decay / (m ** 0.5))) for m, a in partials)
    return y * adsr(len(t), 0.001, 0.05)


def sfx_ding():
    return norm(bell(1318, 1.4, 0.5) + 0.5 * bell(1976, 1.4, 0.4), 0.8)


def sfx_chime():
    out = np.zeros(int(SR * 1.6))
    for k, f in enumerate([1047, 1319, 1568, 2093]):
        place(out, bell(f, 1.2, 0.4), k * 0.07, 0.6)
    return norm(out, 0.8)


def sfx_kaching():
    d = 1.3
    out = np.zeros(int(SR * d))
    ka = hp(noise(0.05), 1500) * env_exp(0.05, 0.008)
    place(out, ka, 0.0, 0.9)
    place(out, lp(noise(0.06), 400) * env_exp(0.06, 0.01), 0.0, 0.8)
    t = t_axis(1.1)
    trem = 1 + 0.25 * np.sin(2 * np.pi * 18 * t)
    ching = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(2093, 1), (3136, 0.7), (4186, 0.5), (5274, 0.35)])
    ching *= np.exp(-t / 0.35) * trem
    place(out, ching, 0.07, 0.5)
    for k in range(10):  # coins
        place(out, bell(2500 + 2500 * rng.random(), 0.25, 0.06), 0.1 + 0.6 * rng.random(), 0.25)
    return norm(out, 0.9)


def sfx_coins(d=0.9, count=18):
    out = np.zeros(int(SR * d))
    for _ in range(count):
        place(out, bell(2600 + 3000 * rng.random(), 0.2, 0.05), (d - 0.2) * rng.random(), 0.3)
    return norm(out, 0.7)


def sfx_popper():
    d = 0.5
    y = hp(noise(d), 800) * env_exp(d, 0.03) + sweep_sine(500, 120, d) * env_exp(d, 0.03)
    return norm(y, 0.9)


def sfx_sparkle(d=0.8, count=14):
    out = np.zeros(int(SR * (d + 0.4)))
    for k in range(count):
        place(out, bell(3000 + 4000 * rng.random(), 0.35, 0.08), d * k / count + 0.03 * rng.random(), 0.3)
    return norm(out, 0.6)


def sfx_shimmer(d=0.8):
    t = t_axis(d)
    y = sum(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.5 * t / d)) / SR) for f0 in (520, 780, 1040))
    y *= (0.6 + 0.4 * np.sin(2 * np.pi * 22 * t)) * np.sin(np.pi * t / d)
    y += hp(noise(d), 6000) * 0.15 * np.sin(np.pi * t / d)
    return norm(y, 0.6)


def sfx_glitch(d=0.25):
    n = noise(d)
    gate = (rng.random(int(d * 40) + 2) > 0.4).repeat(int(SR / 40) + 1)[: len(n)].astype(float)
    crushed = np.round(n * 3) / 3
    t = t_axis(d)
    y = crushed * gate * 0.5 + np.sign(np.sin(2 * np.pi * 180 * t)) * gate * 0.3
    return norm(bp(y, 300, 7000) * adsr(len(n), 0.002, 0.04), 0.7)


def sfx_rise(d=1.8):
    t = t_axis(d)
    tone = sweep_sine(60, 240, d) * 0.6
    n = noise(d)
    air = varlp(n, 200 + 4000 * (t / d) ** 2) * 1.2
    e = (t / d) ** 1.5 * np.exp(-np.maximum(0, t - d + 0.25) / 0.08)
    return norm((tone + air) * e, 0.85)


def sfx_scribble(d=0.45):
    t = t_axis(d)
    n = bp(noise(d), 1800, 5000)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * (9 + 4 * np.sin(2 * np.pi * 2 * t)) * t)
    return norm(n * am * adsr(len(t), 0.01, 0.05), 0.5)


def sfx_thud():
    d = 0.4
    y = sweep_sine(160, 55, d) * env_exp(d, 0.08) + lp(noise(d), 1200) * env_exp(d, 0.015) * 0.6
    return norm(y, 0.9)


def sfx_alarm():
    out = np.zeros(int(SR * 0.8))
    for k, f in enumerate([880, 660, 880, 660]):
        t = t_axis(0.18)
        y = np.sign(np.sin(2 * np.pi * f * t)) * adsr(len(t), 0.005, 0.03)
        place(out, lp(y, 3500), k * 0.19, 0.5)
    return out


def sfx_tick():
    d = 0.03
    return norm(bp(noise(d), 2500, 6000) * env_exp(d, 0.004), 0.4)


def sfx_scratch(music):
    """Record scratch: play a bit of the music with a wobbling playback rate."""
    d = 0.45
    i0 = int(34.5 * SR)
    src = music[i0 : i0 + int(SR * 0.7)]
    t = t_axis(d)
    rate = 2.2 * np.sin(2 * np.pi * 3.2 * t) - 0.5
    pos = np.clip(int(0.3 * SR) + np.cumsum(rate), 0, len(src) - 2)
    y = np.interp(pos, np.arange(len(src)), src)
    y = norm(y, 0.8) + bp(noise(d), 800, 4000) * 0.35 * np.abs(rate) / 2.5
    return norm(y * adsr(len(t), 0.003, 0.08), 0.95)


# ---------------------------------------------------------------- music
BPM = 100
BEAT = 60 / BPM
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name, octave):
    return 440 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


CHORDS = [("C", [0, 4, 7]), ("G", [7, 11, 14]), ("A", [9, 12, 16]), ("F", [5, 9, 12])]


def saw(f, d, harmonics=10):
    t = t_axis(d)
    return sum(((-1) ** (k + 1)) * np.sin(2 * np.pi * f * k * t) / k for k in range(1, harmonics + 1))


def drum_kick():
    d = 0.35
    return sweep_sine(130, 45, d) * env_exp(d, 0.12)


def drum_snare():
    d = 0.2
    return bp(noise(d), 1200, 7000) * env_exp(d, 0.05) * 0.6 + np.sin(2 * np.pi * 190 * t_axis(d)) * env_exp(d, 0.04) * 0.4


def drum_hat():
    d = 0.05
    return hp(noise(d), 7000) * env_exp(d, 0.012)


def music_bed():
    mus = np.zeros(N)
    kick, snare, hat = drum_kick(), drum_snare(), drum_hat()
    bar = 4 * BEAT

    def upbeat(t0, t1, bright=False):
        nb = int((t1 - t0) / bar) + 1
        for b in range(nb):
            tb = t0 + b * bar
            root_i, tones = CHORDS[b % 4][0], CHORDS[b % 4][1]
            base = midi("C", 3)
            for beat in range(4):
                tt = tb + beat * BEAT
                if tt >= t1:
                    break
                place(mus, kick, tt, 0.9 if beat in (0, 2) else 0.0)
                if beat in (1, 3):
                    place(mus, snare, tt, 0.35)
                for h in range(2):
                    place(mus, hat, tt + h * BEAT / 2, 0.18 if h else 0.1)
                # bass 8ths
                for h in range(2):
                    f = base * 2 ** (tones[0] / 12) / 2
                    nd = BEAT / 2 * 0.9
                    bl = lp(saw(f, nd, 6), 700) * adsr(int(nd * SR), 0.005, 0.05)
                    place(mus, bl, tt + h * BEAT / 2, 0.22)
            # pad
            pd = min(bar, t1 - tb)
            if pd > 0.1:
                pad = sum(saw(base * 2 ** (n / 12) * dt, pd, 6) for n in tones for dt in (0.997, 1.003))
                pad = lp(pad, 1800) * adsr(int(pd * SR), 0.25, 0.3)
                place(mus, pad, tb, 0.035)
            if bright:  # pluck arpeggio 16ths
                for s in range(16):
                    tt = tb + s * BEAT / 4
                    if tt >= t1:
                        break
                    n = tones[s % 3] + (12 if s % 6 >= 3 else 0)
                    f = base * 2 * 2 ** (n / 12)
                    pl = bell(f, 0.3, 0.12, ((1, 1), (2, 0.3), (3, 0.1)))
                    place(mus, pl, tt, 0.06)

    upbeat(0.36, 35.12)
    # tense section after the record scratch
    t0, t1 = 35.6, 45.95
    tt = t0
    k = 0
    while tt < t1:
        f = midi("A", 1)
        nd = BEAT / 2 * 0.8
        bl = lp(saw(f, nd, 8), 500) * adsr(int(nd * SR), 0.005, 0.06)
        place(mus, bl, tt, 0.3 if k % 2 == 0 else 0.18)
        place(mus, hat, tt, 0.08)
        if k % 8 == 0:
            place(mus, kick, tt, 0.6)
        tt += BEAT / 2
        k += 1
    dr = t1 - t0
    drone = lp(saw(midi("A", 2), dr, 6) + saw(midi("D", 3) * 1.0595, dr, 6) * 0.5, 600) * adsr(int(dr * SR), 1.0, 0.4)
    place(mus, drone, t0, 0.04)
    upbeat(46.0, 64.0, bright=True)
    # fade out tail
    fo = int(1.2 * SR)
    mus[-fo:] *= np.linspace(1, 0, fo)
    return mus


# ---------------------------------------------------------------- main
def run(cmd):
    subprocess.run(cmd, check=True)


def read_wav(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
    return a


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def main():
    os.makedirs(BUILD, exist_ok=True)
    vo_path = os.path.join(BUILD, "vo.wav")
    run([
        "ffmpeg", "-v", "error", "-y", "-i", os.path.join(ROOT, "assets", "voiceover.m4a"),
        "-af", "highpass=f=85,afftdn=nf=-28,acompressor=threshold=-22dB:ratio=3:attack=5:release=90:makeup=2,"
               "loudnorm=I=-15:TP=-2:LRA=7",
        "-ac", "1", "-ar", str(SR), vo_path,
    ])
    vo = read_wav(vo_path)
    vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]

    # lip-sync envelope, one value per video frame
    hop = SR // FPS
    frames = int(DUR * FPS)
    rms = np.array([np.sqrt(np.mean(vo[i * hop:(i + 1) * hop] ** 2)) for i in range(frames)])
    ref = np.percentile(rms, 95) + 1e-9
    envv = np.clip((rms / ref - 0.12) / 0.88, 0, 1)
    envv = np.convolve(envv, [0.25, 0.5, 0.25], mode="same")
    with open(os.path.join(ROOT, "src", "env.js"), "w") as f:
        f.write("window.ENV=" + json.dumps([round(float(v), 2) for v in envv]) + ";\n")

    # ducking curve from the voice
    vabs = lp(np.abs(vo), 6)
    vabs = vabs / (np.percentile(vabs, 95) + 1e-9)
    duck = 1 - 0.55 * np.clip(vabs * 1.5, 0, 1)

    music = music_bed()

    sfx = np.zeros(N)
    cues = [
        (0.00, sfx_whoosh(0.4, True), 0.7),
        (0.36, sfx_boom(), 1.0),
        (0.40, sfx_pop(1400, 500), 0.4),
        (1.45, sfx_glitch(0.18), 0.3),
        (3.15, sfx_pop(), 0.6), (3.50, sfx_pop(1000, 300), 0.6), (3.85, sfx_pop(1100, 350), 0.6),
        (5.10, sfx_thud(), 0.7),
        (7.76, sfx_shimmer(0.6), 0.6),
        (10.55, sfx_glitch(), 0.6), (10.60, sfx_shimmer(0.8), 0.7),
        (16.74, sfx_ding(), 0.8),
        (17.10, sfx_sparkle(0.6), 0.4),
        (20.05, sfx_glitch(), 0.55),
        (20.80, sfx_shimmer(0.5), 0.4),
        (23.20, sfx_whoosh(0.35), 0.5),
        (23.96, sfx_kaching(), 0.85), (24.05, sfx_coins(), 0.5),
        (25.25, sfx_whoosh(0.35), 0.5),
        (26.40, sfx_boom(), 1.0), (26.42, sfx_popper(), 0.7), (26.48, sfx_kaching(), 0.85),
        (26.55, sfx_coins(1.2, 26), 0.5),
        (26.70, sfx_rise(1.7), 0.7),
        (28.50, sfx_sparkle(), 0.5),
        (31.70, sfx_scribble(0.5), 0.6),
        (32.90, sfx_scribble(0.4), 0.5),
        (35.45, sfx_alarm(), 0.45),
        (35.60, sfx_whoosh(0.45, False), 0.5),
        (36.40, sfx_pop(700, 200), 0.6),
        (38.86, sfx_thud(), 0.8),
        (40.00, sfx_whoosh(0.4, False), 0.35),
        (41.86, sfx_pop(), 0.6), (42.34, sfx_pop(1000, 300), 0.6), (42.92, sfx_pop(1100, 350), 0.6),
        (43.70, sfx_pop(1200, 400), 0.6), (43.15, sfx_alarm()[: int(SR * 0.38)], 0.25),
        (45.95, sfx_whoosh(0.5), 0.55),
        (46.10, sfx_chime(), 0.55),
        (48.60, sfx_pop(), 0.5), (49.40, sfx_pop(800, 250), 0.5),
        (50.00, sfx_scribble(0.35), 0.7),
        (50.50, sfx_chime(), 0.6), (50.55, sfx_sparkle(), 0.4),
        (51.20, sfx_whoosh(0.45), 0.7), (51.28, sfx_glitch(0.18), 0.35),
        (51.65, sfx_whoosh(0.5), 0.6), (52.05, sfx_shimmer(0.7), 0.5),
        (54.50, sfx_pop(900, 400), 0.7),
        (55.30, sfx_pop(), 0.45), (57.90, sfx_pop(), 0.45),
        (60.98, sfx_blip(1300, 0.09), 0.5), (61.94, sfx_blip(1500, 0.09), 0.5), (62.72, sfx_blip(1750, 0.09), 0.5),
        (63.45, sfx_sparkle(0.6), 0.5),
    ]
    # typing GAJI + keypad presses
    for k, tt in enumerate([12.96, 13.06, 13.16, 13.26]):
        cues.append((tt, sfx_blip(1500 + 120 * k, 0.05), 0.35))
    for tt in [14.28, 14.62, 14.76, 15.54, 15.85, 16.00]:
        cues.append((tt, sfx_blip(1000 + 600 * rng.random(), 0.07), 0.45))
    # data chirps while numbers fly
    tt = 12.8
    while tt < 19.6:
        cues.append((tt, sfx_blip(2000 + 1500 * rng.random(), 0.035), 0.12))
        tt += 0.22 + 0.25 * rng.random()
    # countdown ticks
    for s in range(10):
        cues.append((10.6 + s * 0.95, sfx_tick(), 0.35))
    # count-up blips
    for k in range(6):
        cues.append((20.8 + k * 0.08, sfx_blip(1800 + 200 * k, 0.04), 0.2))
    # CTA pulse ticks
    tt = 54.6
    while tt < 63.3:
        cues.append((tt, sfx_tick(), 0.12))
        tt += 0.9

    for at, clip, g in cues:
        place(sfx, clip, at, g)
    place(sfx, sfx_scratch(music), 35.10, 0.9)

    mix = vo * 1.0 + music * duck * 0.16 + sfx * 0.38
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    raw = os.path.join(BUILD, "mix_raw.wav")
    write_wav(raw, mix * 0.9)
    run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", str(SR),
         os.path.join(BUILD, "mix.wav")])
    print("audio ok")


if __name__ == "__main__":
    main()
