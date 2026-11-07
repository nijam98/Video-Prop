# Y2K animated reel: clean AI-upscaled footage + Y2K motion graphics, 1080x1920 60fps.
# usage: python3 render.py [n_frames] [out.mp4]      (env SRC_VID = upscaled 60fps video)
import json, subprocess, sys, os, math, itertools
import numpy as np, cv2
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gfx, style

W, H, FPS, N = 1080, 1920, 60, 3600
SRC_VID = os.environ.get("SRC_VID", "work/cut60_sr.mp4")
AUDIO = os.environ.get("AUDIO", "work/audio_mix.wav")
E = json.load(open("work/edl.json")); T = E["tempo"]
SEC = {s["name"]: s for s in E["sections"]}


def at(sec, src_t):
    s = SEC[sec]; acc = s["start"]
    for a, b in s["audio"]:
        if a <= src_t <= b: return (acc + src_t - a) / T
        acc += b - a
    return acc / T


def start(sec): return SEC[sec]["start"] / T
def end(sec): return (SEC[sec]["start"] + SEC[sec]["dur"]) / T


# cut points on the final timeline
CUTS = []; acc = 0
for a, b in E["vpieces"][:-1]:
    acc += b - a; CUTS.append(acc / T)
SEC_STARTS = [start(n) for n in SEC if n != "hook"]
HOOK_CUTS = [c for c in CUTS if c < end("hook") + 0.01]

# ---------------------------------------------------------------- elements
# kind: chrome | gold | holo | pill | window | label ; anim decided by kind
EL = []
def chrome(t0, t1, text, y, size=170, gold=False, shine_every=1.6):
    EL.append(dict(t0=t0, t1=t1, kind="chrome", text=text, y=y, size=size, gold=gold, sh=shine_every))
def holo(t0, t1, text, y, size=96):
    EL.append(dict(t0=t0, t1=t1, kind="holo", text=text, y=y, size=size))
def pill(t0, t1, text, y, color, x="left"):
    EL.append(dict(t0=t0, t1=t1, kind="pill", text=text, y=y, color=color, x=x))
def window(t0, t1, title, lines, y, ok=False, cursor=None):
    # lines: [(type_start, type_end, text), ...]
    EL.append(dict(t0=t0, t1=t1, kind="window", title=title, lines=lines, y=y, ok=ok, cursor=cursor))

COLS = ["pink", "aqua", "lime", "purple"]
def items(sec, lst, y0=1090, step=128):
    for i, (st, txt) in enumerate(lst):
        pill(at(sec, st), end(sec), txt, y0 + i * step, COLS[i % 4])

# HOOK: "senang kata macam mana tengok, macam tu dapat, masuk cuci kaki"
window(0.0, end("hook"), "RUMAH_SIAP.EXE",
       [(0.12, 1.40, "MACAM MANA TENGOK,"), (at("hook", 95.10), at("hook", 95.55), "MACAM TU DAPAT!")], 450)
chrome(at("hook", 95.62), end("hook"), "MASUK", 900, 190)
chrome(at("hook", 96.02), end("hook"), "CUCI KAKI!", 1085, 112, gold=True)
pill(0.15, end("hook"), "SIAP RENO + PERABOT", 1470, "pink", x="center")
# INTRO
pill(at("intro", 0.15), at("intro", 2.45), "PELUANG INVESTMENT", 1250, "aqua", x="center")
chrome(at("intro", 2.50), end("intro"), "EVOKE", 560, 200)
holo(at("intro", 3.15), end("intro"), "KONDOMINIUM", 715, 92)
pill(at("intro", 3.90), end("intro"), "PERMATA PAUH", 840, "pink", x="center")
window(at("intro", 5.05), end("intro"), "OWNER.EXE",
       [(at("intro", 5.10), at("intro", 6.30), "OWNER NAK LEPAS"), (at("intro", 6.60), at("intro", 7.00), "FULLY FURNISHED!")],
       1330, ok=True, cursor=(at("intro", 6.4), at("intro", 7.15)))
# SPEC / PARK / RENO / FURN / LOC
items("spec", [(10.40, "1140 KAKI PERSEGI"), (14.20, "FREEHOLD • NON BUMI LOT"), (16.50, "3 BILIK + 2 BILIK AIR"), (18.90, "LEVEL 10")])
items("park", [(24.60, "2 PARKING KERETA"), (26.05, "+ 1 PARKING MOTOR"), (29.30, "MAINTENANCE ±RM330")])
items("reno", [(43.90, "RENOVATION SIAP"), (48.90, "QUARTZ STONE TOP"), (52.40, "WET + DRY KITCHEN")])
items("furn", [(74.70, "4 UNIT AIRCON"), (77.15, "TV + KABINET TV"), (79.25, "MESIN BASUH"), (79.85, "MICROWAVE")])
items("loc", [(99.00, "DEKAT UiTM"), (99.60, "POLITEKNIK"), (101.80, "HIGHWAY")])
chrome(at("loc", 103.10), end("loc"), "SESUAI", 640, 170)
chrome(at("loc", 103.85), end("loc"), "INVESTMENT!", 800, 104, gold=True)
# CTA
chrome(at("cta", 107.40), N / FPS, "LINK DI BIO", 760, 128)
pill(at("cta", 109.15), N / FPS, "BOLEH LOAN LPPSA / BANK", 1000, "lime", x="center")
EL.append(dict(t0=at("cta", 107.0), t1=N / FPS, kind="cursor_cta", y=760))

LABELS = [("spec", "SPESIFIKASI"), ("park", "PARKING & YURAN"), ("reno", "RENOVATION"),
          ("furn", "PERABOT"), ("loc", "LOKASI")]
SLAMS = [e["t0"] for e in EL if e["kind"] == "chrome"]

# ---------------------------------------------------------------- helpers
CACHE = {}
def sprite(key, fn):
    if key not in CACHE: CACHE[key] = fn()
    return CACHE[key]


def comp(frame, ov, cx, cy, scale=1.0, alpha=1.0, left=None):
    if alpha <= 0.003: return
    if abs(scale - 1.0) > 1e-3:
        ov = cv2.resize(ov, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR if scale > 0.5 else cv2.INTER_AREA)
    h, w = ov.shape[:2]
    x0 = int(left) if left is not None else int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe <= xs or ye <= ys: return
    o = ov[ys - y0:ye - y0, xs - x0:xe - x0].astype(np.float32)
    a = o[..., 3:4] / 255 * alpha
    roi = frame[ys:ye, xs:xe].astype(np.float32)
    frame[ys:ye, xs:xe] = (roi * (1 - a) + o[..., 2::-1] * a).astype(np.uint8)


def ease_out(p): p = min(max(p, 0), 1); return 1 - (1 - p) ** 3
def back_out(p, s=1.9):
    p = min(max(p, 0), 1) - 1; return 1 + (s + 1) * p ** 3 + s * p ** 2


def exit_fade(t, t1, d=0.14):
    return max(0.0, min(1.0, (t1 - t) / d))


def burst(frame, t, t0, cx, cy, seed, n=8, spread=(360, 140)):
    dt = t - t0
    if dt < 0 or dt > 0.75: return
    r = np.random.default_rng(seed)
    p = dt / 0.75
    for k in range(n):
        ang = r.uniform(0, 2 * math.pi); dist = r.uniform(0.5, 1.0)
        x = cx + math.cos(ang) * spread[0] * (0.55 + 0.6 * ease_out(p)) * dist
        y = cy + math.sin(ang) * spread[1] * (0.55 + 0.9 * ease_out(p)) * dist
        sz = r.choice([26, 36, 48])
        sc = math.sin(math.pi * min(1, p * 1.15))
        col = [(140, 220, 255), (255, 140, 230), (255, 240, 160)][k % 3]
        comp(frame, sprite(("sp", sz, col), lambda: gfx.sparkle(sz, glow=col)), x, y, max(0.05, sc), sc)


def twinkle(frame, t, pts):
    for i, (x, y, sz) in enumerate(pts):
        s = math.sin(t * 3.1 + i * 2.3)
        if s <= 0: continue
        comp(frame, sprite(("sp", sz, "w"), lambda: gfx.sparkle(sz)), x, y, 0.3 + 0.7 * s, s)


# ---------------------------------------------------------------- per element drawing
def draw_el(frame, e, t, idx):
    dt = t - e["t0"]; fa = exit_fade(t, e["t1"])
    k = e["kind"]
    if k == "chrome":
        key = ("ch", e["text"], e["size"], e["gold"])
        spr, m = sprite(key, lambda: gfx.chrome_text(e["text"], e["size"], stops=gfx.GOLD if e["gold"] else gfx.CHROME,
                                                      glow=(80, 220, 255) if e["gold"] else (255, 80, 220)))
        if spr.shape[1] > W - 20:
            s0 = (W - 20) / spr.shape[1]
            spr, m = sprite(key + ("fit",), lambda: (cv2.resize(spr, None, fx=s0, fy=s0, interpolation=cv2.INTER_AREA),
                                                     cv2.resize(m, None, fx=s0, fy=s0, interpolation=cv2.INTER_AREA)))
        # slam: big -> land with overshoot, then gentle float + periodic shine
        if dt < 0.13: s = 2.3 - 1.36 * ease_out(dt / 0.13); a = min(1, dt / 0.06)
        elif dt < 0.26: p = (dt - 0.13) / 0.13; s = 0.94 + 0.06 * ease_out(p); a = 1
        else: s = 1 + 0.012 * math.sin(dt * 5); a = 1
        sp = ((dt - 0.22) % e["sh"]) / 0.55 if dt > 0.22 else -1
        img = gfx.shine(spr, m, sp) if 0 < sp < 1 else spr
        sx = sy = 0
        if 0.13 < dt < 0.4:
            amp = 14 * (1 - (dt - 0.13) / 0.27); sx = amp * math.sin(dt * 90); sy = amp * math.cos(dt * 77)
        comp(frame, img, W / 2 + sx, e["y"] + sy, s * (0.9 + 0.1 * fa), a * fa)
        burst(frame, t, e["t0"] + 0.12, W / 2, e["y"], idx, n=9, spread=(min(480, img.shape[1] * 0.55), 150))
    elif k == "holo":
        spr = sprite(("ho", e["text"], e["size"]), lambda: gfx.holo_text(e["text"], e["size"]))
        p = ease_out(dt / 0.3)
        comp(frame, spr, W / 2, e["y"] + 40 * (1 - p), 0.85 + 0.15 * back_out(dt / 0.35), p * fa)
    elif k == "pill":
        spr = sprite(("pi", e["text"], e["color"]), lambda: gfx.pill(e["text"], e["color"]))
        bob = 4 * math.sin(t * 4 + idx)
        if e["x"] == "left":
            tx = 40; x = tx - (1 - back_out(dt / 0.32, 1.4)) * (spr.shape[1] + 80)
            comp(frame, spr, 0, e["y"] + bob, 1.0, min(1, dt / 0.08) * fa, left=x)
            if 0 <= dt < 0.5:
                twinkle_x = x + spr.shape[1] - 40
                burst(frame, t, e["t0"] + 0.18, twinkle_x, e["y"], idx, n=4, spread=(90, 70))
        else:
            s = back_out(dt / 0.3, 2.2)
            comp(frame, spr, W / 2, e["y"] + bob, max(0.05, s), min(1, dt / 0.08) * fa)
    elif k == "window":
        shown = []
        for (a0, a1, txt) in e["lines"]:
            if t < a0: break
            n = len(txt) if t >= a1 else int(len(txt) * (t - a0) / max(1e-3, a1 - a0))
            shown.append(txt[:n])
        blink = "_" if (int(t * 4) % 2 == 0) else " "
        if shown and len(shown[-1]) < len(e["lines"][len(shown) - 1][2]): shown[-1] += blink
        elif not shown: shown = [blink]
        full = [l[2] for l in e["lines"]]
        # fixed size window: pad with blank lines
        lines = shown + [""] * (len(full) - len(shown))
        key = ("wi", e["title"], tuple(lines), e["ok"])
        spr = sprite(key, lambda: gfx.window(e["title"], lines, ok=e["ok"]))
        s = back_out(dt / 0.22, 2.0) if dt < 0.3 else 1
        comp(frame, spr, W / 2, e["y"], max(0.05, s), min(1, dt / 0.06) * fa)
        if e["cursor"]:
            c0, c1 = e["cursor"]
            if t >= c0:
                p = ease_out((t - c0) / max(1e-3, c1 - c0))
                okx, oky = W / 2 + 30, e["y"] + spr.shape[0] / 2 - 70
                cx = 950 + (okx - 950) * p; cy = 1820 + (oky - 1820) * p
                click = 0.85 if 0 < t - c1 < 0.12 else 1.0
                cur = sprite(("cur",), gfx.cursor)
                comp(frame, cur, cx + cur.shape[1] / 2, cy + cur.shape[0] / 2, click, fa)
                burst(frame, t, c1, okx, oky, idx + 99, n=5, spread=(120, 70))
    elif k == "cursor_cta":
        cur = sprite(("cur",), gfx.cursor)
        p = ease_out(dt / 0.6)
        cx = 1000 + (720 - 1000) * p; cy = 1750 + (e["y"] + 40 - 1750) * p
        click = 0.85 if 0.65 < dt < 0.8 or 1.6 < dt < 1.75 else 1.0
        comp(frame, cur, cx + cur.shape[1] / 2, cy + cur.shape[0] / 2, click, 1.0)


def hud(frame, t):
    if t < end("hook"): return
    # segmented "loading" progress bar (Win9x style), top
    x0, y0, w, h, nseg = 300, 238, 480, 30, 16
    p = min(1, t / (N / FPS))
    key = ("bar", int(p * nseg))
    def mk():
        a = np.zeros((h + 8, w + 8, 4), np.uint8)
        cv2.rectangle(a, (0, 0), (w + 7, h + 7), (255, 255, 255, 230), 2)
        cv2.rectangle(a, (2, 2), (w + 5, h + 5), (60, 10, 30, 140), -1)
        sw = (w - 4) / nseg
        for i in range(int(p * nseg)):
            c = (255, 120, 230) if i % 2 else (120, 230, 255)
            cv2.rectangle(a, (int(6 + i * sw), 6), (int(6 + (i + 1) * sw) - 4, h + 1), c[::-1] + (255,), -1)
        return a[..., [2, 1, 0, 3]]
    comp(frame, sprite(key, mk), W / 2, y0, 1, 0.92)
    for sec, txt in LABELS:
        if start(sec) <= t < end(sec):
            dt = t - start(sec)
            spr = sprite(("lab", txt), lambda: gfx.pixel_label("* " + txt + " *"))
            x = 40 - (1 - ease_out(dt / 0.25)) * 500
            comp(frame, spr, 0, 310, 1, exit_fade(t, end(sec)), left=x)


def transitions(frame, t):
    out = frame
    # CRT power-on at the very start
    if t < 0.16:
        p = ease_out(t / 0.16); hh = max(4, int(H * p))
        m = np.zeros_like(out); y0 = (H - hh) // 2
        m[y0:y0 + hh] = out[y0:y0 + hh]
        m[max(0, y0 - 3):y0 + 3] = 255; m[y0 + hh - 3:min(H, y0 + hh + 3)] = 255
        out = m
    flash = 0.0; split = 0
    for c in HOOK_CUTS + [0.0]:
        d = t - c
        if 0 <= d < 0.12: flash = max(flash, 0.55 * (1 - d / 0.12)); split = max(split, int(18 * (1 - d / 0.12)))
    for c in SEC_STARTS:
        d = t - c
        if 0 <= d < 0.16: flash = max(flash, 0.7 * (1 - d / 0.16)); split = max(split, int(26 * (1 - d / 0.16)))
        if -0.06 <= d < 0: split = max(split, 10)
    for c in SLAMS:
        d = t - c - 0.12
        if 0 <= d < 0.08: flash = max(flash, 0.35 * (1 - d / 0.08))
    if split:
        o = out.copy()
        o[:, split:, 2] = out[:, :-split, 2]; o[:, :-split, 0] = out[:, split:, 0]
        # glitch slices
        r = np.random.default_rng(int(t * 1000))
        for _ in range(5):
            y = int(r.integers(0, H - 60)); hh = int(r.integers(12, 60)); sh = int(r.integers(-split * 2, split * 2 + 1))
            o[y:y + hh] = np.roll(o[y:y + hh], sh, axis=1)
        out = o
    if flash > 0:
        tint = np.array([255, 235, 250], np.float32)  # BGR soft pink-white
        out = (out.astype(np.float32) * (1 - flash) + tint * flash).astype(np.uint8)
    return out


def zoom(frame, t):
    z = 1.0
    for c in HOOK_CUTS + [0.0]:
        d = t - c
        if 0 <= d < 0.3: z = max(z, 1.10 - 0.10 * ease_out(d / 0.3))
    for c in SEC_STARTS:
        d = t - c
        if 0 <= d < 0.3: z = max(z, 1.07 - 0.07 * ease_out(d / 0.3))
    if t < end("hook"): z *= 1.0 + 0.03 * ((t % 0.9) / 0.9)   # slow push inside each hook shot
    if z <= 1.0005: return frame
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


AMBIENT = [(120, 560, 30), (960, 980, 24), (110, 1560, 22), (980, 420, 26)]


def work(args):
    fi, buf = args
    t = fi / FPS
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    f = style.grade(f)
    f = zoom(f, t)
    f = np.ascontiguousarray(f)
    twinkle(f, t, AMBIENT)
    hud(f, t)
    for i, e in enumerate(EL):
        if e["t0"] <= t < e["t1"]:
            draw_el(f, e, t, i)
    f = transitions(f, t)
    return f.tobytes()


def reader(lim):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC_VID, "-vf", f"scale={W}:{H}:flags=lanczos,tpad=stop_mode=clone:stop=30",
                          "-frames:v", str(lim), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    fi = 0
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield fi, b; fi += 1


if __name__ == "__main__":
    lim = int(sys.argv[1]) if len(sys.argv) > 1 else N
    out = sys.argv[2] if len(sys.argv) > 2 else "work/final.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
                            "-profile:v", "high", "-level", "4.2", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-shortest",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for k, b in enumerate(pool.imap(work, reader(lim), chunksize=4)):
            enc.stdin.write(b)
            if k % 300 == 0: print("frame", k, flush=True)
    enc.stdin.close(); enc.wait(); print("done", out)
