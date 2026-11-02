"""Builds index.html (cuts, music, SFX, scene hosts) and compositions/captions.html
from one edit plan, so every time below is in one place.

Run: python3 -I tools/build.py   (from /home/user/Video-Prop/edit)
"""
import json, html, os

ROOT = os.path.join(os.path.dirname(__file__), "..", "semid")
FPS = 30

# ---- Cut list: (source in, source out). Pauses, the opening "Ok" and the
# repeated "Saya ulang, dua empat bilik dua tandas" are left out.
SEGMENTS = [
    (0.67, 4.02),    # A  Orang-orang Alor Setar ... semi-D empat bilik dua tandas
    (4.66, 10.84),   # B  Taman Seri Pagi Fasa 2 ... Kedai Bohor
    (11.17, 13.25),  # C  Masuk ikut Taman Dahlia Lama
    (13.50, 14.70),  # D  Terus ke taman ni
    (15.01, 16.72),  # E  Jadi kawasan yang sangat strategik
    (17.39, 20.99),  # F  Dekat dengan semua kemudahan ... tol Alor Setar Selatan
    (21.62, 22.32),  # G  Yang mana berminat
    (22.77, 26.16),  # H  Macam biasa tekan link dekat bio ... terus contact
    (26.71, 29.36),  # I  Jangan lepaskan peluang. Unit terhad semi-D ...
]
TAIL = 1.80          # footage keeps rolling (muted) under the end card
# Punch-in per segment so each jump cut reads as intended.
ZOOM = [1.0, 1.12, 1.0, 1.14, 1.0, 1.08, 1.0, 1.1, 1.16, 1.16]

def r(x):
    return round(x + 1e-9, 3)

starts, t = [], 0.0
for a, b in SEGMENTS:
    starts.append(r(t))
    t += b - a
SPEECH_END = r(t)
TOTAL = r(t + TAIL)

def out_time(src):
    for (a, b), s in zip(SEGMENTS, starts):
        if a - 0.2 <= src <= b + 0.05:
            return r(s + max(0.0, src - a))
    raise ValueError(src)

# ---- Words: (text, src start, src end, emphasis). Times from the Whisper pass,
# spelling corrected by ear-context (Alor Setar, Fasa 2, tandas, terus...).
W = lambda t, s, e, em=False: (t, s, e, em)
GROUPS = [
    [W("Orang-orang", .70, 1.06), W("Alor", 1.06, 1.21), W("Setar", 1.21, 1.36)],
    [W("yang", 1.36, 1.48), W("mana", 1.48, 1.60), W("nak", 1.60, 1.72), W("cari", 1.72, 1.90)],
    [W("semi-D", 1.90, 2.28, True)],
    [W("empat", 2.28, 2.72, True), W("bilik", 2.72, 3.04, True)],
    [W("dua", 3.04, 3.26, True), W("tandas", 3.26, 3.96, True)],
    [W("Taman", 4.74, 5.22), W("Seri", 5.22, 5.42), W("Pagi", 5.42, 5.66)],
    [W("Fasa", 5.66, 5.90), W("2,", 5.90, 6.16), W("masuk.", 6.16, 6.60)],
    [W("Jangan", 6.78, 7.16, True), W("masuk", 7.16, 7.36)],
    [W("ke", 7.36, 7.44), W("Kuala", 7.44, 7.60), W("Tim.", 7.60, 7.76)],
    [W("Kita", 7.80, 8.10), W("masuk", 8.10, 8.34), W("ke", 8.34, 8.52)],
    [W("Jalan", 8.52, 9.30), W("Lencong", 9.30, 9.60), W("Barat,", 9.60, 9.86)],
    [W("Kedai", 9.86, 10.24), W("Bohor.", 10.24, 10.60)],
    [W("Masuk", 11.17, 11.54), W("ikut", 11.54, 11.98)],
    [W("Taman", 11.98, 12.30), W("Dahlia", 12.30, 12.64), W("Lama.", 12.64, 12.92)],
    [W("Terus", 13.52, 13.90), W("ke", 13.90, 14.04), W("taman", 14.04, 14.40, True), W("ni.", 14.40, 14.64)],
    [W("Jadi", 15.04, 15.12), W("kawasan", 15.12, 15.46)],
    [W("yang", 15.46, 15.68), W("sangat", 15.68, 15.98), W("strategik.", 15.98, 16.64, True)],
    [W("Dekat", 17.42, 17.72), W("dengan", 17.72, 17.80)],
    [W("semua", 17.80, 17.96), W("kemudahan.", 17.96, 18.40, True)],
    [W("Dekat", 18.44, 18.70), W("dengan", 18.70, 18.94)],
    [W("tol", 19.22, 19.50, True), W("Alor", 19.50, 19.78), W("Setar", 19.78, 20.06), W("Selatan.", 20.06, 20.70)],
    [W("Yang", 21.64, 21.72), W("mana", 21.72, 21.82), W("berminat?", 21.82, 22.22, True)],
    [W("Macam", 22.78, 22.94), W("biasa", 22.94, 23.16)],
    [W("tekan", 23.16, 23.60), W("link", 23.60, 23.84, True)],
    [W("dekat", 23.84, 24.14), W("bio.", 24.14, 24.58, True)],
    [W("Sekejap", 24.70, 25.06), W("lagi", 25.06, 25.18)],
    [W("saya", 25.18, 25.36), W("terus", 25.36, 25.76), W("contact.", 25.76, 26.10, True)],
    [W("Jangan", 26.72, 26.82), W("lepaskan", 26.82, 27.14), W("peluang!", 27.14, 27.40, True)],
    [W("Unit", 27.44, 27.58, True), W("terhad", 27.58, 27.94, True)],
    [W("semi-D", 27.94, 28.36), W("empat", 28.36, 28.58), W("bilik", 28.58, 28.80)],
    [W("dua", 28.80, 28.94), W("tandas.", 28.94, 29.32)],
]

# ---- Sound effects: (id, file, out time the hit should land, volume, media start)
# Each clip is placed so its measured peak lands one frame after the picture.
SFX_PEAK = {"1104": .145, "1133": .194, "1143": .63, "1464": .106, "1492": 1.087,
            "1530": .358, "166": .295, "2150": .186, "2182": .057, "2357": .241,
            "2364": .044, "2369": .171, "2585": 0.0, "2997": 0.0, "3005": .022,
            "3115": .117, "3194": 1.574, "772": .52}
SFX_DUR = {"1104": .496, "1133": .392, "1143": 4.101, "1464": 1.149, "1492": 1.384, "1530": 1.123,
           "166": .81, "2150": .627, "2182": .444, "2357": .418, "2364": 1.202, "2369": 1.228,
           "2585": 1.149, "2997": 1.097, "3005": .209, "3115": .601, "3194": 1.907, "772": 1.254}
SFX = [
    # hook
    ("sfx-hook-hit", "2150", 0.20, 0.55, 0),     # title settles
    ("sfx-pin", "2369", 0.42, 0.45, 0),          # pin + 'Alor Setar' scribble
    ("sfx-underline", "3194", 1.26, 0.35, 1.30), # marker underline under SEMI-D
    ("sfx-chip1", "2364", 1.64, 0.55, 0),        # 4 BILIK
    ("sfx-chip2", "2357", 2.40, 0.55, 0),        # 2 TANDAS
    ("sfx-cut1", "1492", 3.38, 0.42, 0),         # into the route map
    # route map
    ("sfx-map-pin", "2369", 3.50, 0.35, 0),
    ("sfx-map-x", "3005", 5.52, 0.50, 0),        # cross out Kuala Tim
    ("sfx-map-road", "3194", 7.30, 0.30, 0.90),
    ("sfx-map-shop", "2364", 8.60, 0.35, 0),
    ("sfx-map-dahlia", "2369", 10.38, 0.35, 0),
    ("sfx-map-home", "2357", 11.70, 0.60, 0),
    ("sfx-cut2", "3115", 12.82, 0.45, 0),
    # strategik
    ("sfx-strat-hit", "2150", 13.82, 0.60, 0),
    ("sfx-strat-ring", "2369", 14.02, 0.35, 0),
    ("sfx-cut3", "1464", 14.54, 0.40, 0),
    # kemudahan + tol
    ("sfx-icons", "3005", 14.98, 0.45, 0),
    ("sfx-icons2", "2364", 15.20, 0.35, 0),
    ("sfx-sign", "166", 16.40, 0.40, 0),
    ("sfx-cut4", "3115", 18.14, 0.40, 0),
    # cta
    ("sfx-ask", "2369", 18.24, 0.35, 0),
    ("sfx-tap", "2997", 19.26, 0.70, 0),
    ("sfx-chat", "2357", 20.86, 0.50, 0),
    ("sfx-chat2", "3005", 21.18, 0.40, 0),
    ("sfx-cut5", "1492", 22.24, 0.40, 0),
    # unit terhad
    ("sfx-write", "3194", 22.36, 0.30, 1.20),
    ("sfx-stamp-body", "2150", 22.98, 0.55, 0),
    ("sfx-stamp", "2182", 22.98, 0.95, 0),
    ("sfx-c1", "3005", 23.48, 0.40, 0),
    ("sfx-c2", "2364", 23.90, 0.40, 0),
    ("sfx-c3", "2357", 24.48, 0.45, 0),
    ("sfx-end", "1464", 24.66, 0.35, 0),
]

SCENES = [  # id, start, end
    ("hook", 0.0, starts[1]),
    ("route", starts[1], starts[4]),
    ("strategik", starts[4], starts[5]),
    ("kemudahan", starts[5], starts[6]),
    ("cta", starts[6], starts[8]),
    ("terhad", starts[8], TOTAL),
]

VOICE_FX = {"version": 1, "nodes": [
    {"type": "highpass", "id": "hp", "label": "Remove rumble", "params": {"frequency": 90}},
    {"type": "peaking", "id": "mud", "label": "Less boom", "params": {"frequency": 220, "gain": -2.5, "q": 1}},
    {"type": "peaking", "id": "pres", "label": "Clarity", "params": {"frequency": 3200, "gain": 2.5, "q": 1}},
    {"type": "compressor", "id": "comp", "label": "Even level", "params": {"threshold": -22, "ratio": 3, "attack": 0.005, "release": 0.12}},
    {"type": "limiter", "id": "lim", "label": "No clipping", "params": {"limit": -1.5}},
]}
MUSIC_FX = {"version": 1, "nodes": [
    {"type": "highpass", "id": "mhp", "label": "Keep low end off the voice", "params": {"frequency": 70}},
    {"type": "peaking", "id": "carve", "label": "Room for the voice", "params": {"frequency": 2500, "gain": -5, "q": 0.8}},
    {"type": "limiter", "id": "mlim", "params": {"limit": -2}},
]}

def attr_json(o):
    return html.escape(json.dumps(o, separators=(",", ":")), quote=True)

def build_index():
    vids = []
    z = 1
    for i, ((a, b), s) in enumerate(zip(SEGMENTS, starts)):
        d = r(b - a)
        vids.append(
            f'        <video id="v{i+1}" class="clip footage" src="assets/video/walk.mp4" '
            f'data-start="{s}" data-duration="{d}" data-media-start="{a}" data-track-index="0" '
            f'data-has-audio="true" data-volume="1" data-fade-in="0.02" data-fade-out="0.03" '
            f'data-fx-chain="{attr_json(VOICE_FX)}" playsinline></video>')
    vids.append(
        f'        <video id="vtail" class="clip footage" src="assets/video/walk.mp4" '
        f'data-start="{SPEECH_END}" data-duration="{r(TAIL)}" data-media-start="{SEGMENTS[-1][1]}" '
        f'data-track-index="0" muted playsinline></video>')

    hosts = []
    for i, (sid, a, b) in enumerate(SCENES):
        hosts.append(
            f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
            f'data-start="{r(a)}" data-duration="{r(b - a)}" data-track-index="2" data-track-kind="graphics" '
            f'data-width="1080" data-height="1920" style="z-index:20"></div>')

    music_lane = {"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0.12}, {"t": SPEECH_END - 0.05, "v": 0.12}, {"t": SPEECH_END + 0.35, "v": 0.32}]}]}
    audio = [
        f'      <audio id="music" class="clip" src="assets/music/m33.mp3" data-start="0" '
        f'data-duration="{TOTAL}" data-media-start="12.12" data-track-index="4" data-volume="1" '
        f'data-fade-out="0.9" data-automation="{attr_json(music_lane)}" '
        f'data-fx-chain="{attr_json(MUSIC_FX)}"></audio>']
    lane_end = {}
    for sid, f, hit, vol, ms in SFX:
        start = r(max(0.0, hit + 1 / FPS - (SFX_PEAK[f] - ms)))
        dur = r(min(SFX_DUR[f] - ms, TOTAL - start))
        lane = next(k for k in range(5, 20) if lane_end.get(k, -1) <= start)
        lane_end[lane] = start + dur
        ms_attr = f' data-media-start="{ms}"' if ms else ""
        audio.append(
            f'      <audio id="{sid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{start}" data-duration="{dur}"{ms_attr} '
            f'data-track-index="{lane}" data-volume="{vol}"></audio>')

    zoom_sets = "\n".join(
        f'        tl.set("#cam", {{ scale: {z} }}, {s});'
        for z, s in zip(ZOOM, starts + [SPEECH_END]))

    return f'''<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0d1626; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 42%; }}
      .footage {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}"
      data-width="1080" data-height="1920" data-fps="30">
      <div id="cam" data-layout-ignore>
{chr(10).join(vids)}
      </div>
{chr(10).join(hosts)}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{SPEECH_END}" data-track-index="3" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index:15"></div>
{chr(10).join(audio)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{zoom_sets}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''

def build_captions():
    groups_html, groups_js = [], []
    for gi, g in enumerate(GROUPS):
        words = []
        for wi, (text, s, e, em) in enumerate(g):
            cls = "w em" if em else "w"
            words.append(f'<span id="c{gi}w{wi}" class="{cls}"><i class="hl"></i><b>{html.escape(text)}</b></span>')
        groups_html.append(f'    <div id="cg{gi}" class="cg">{" ".join(words)}</div>')
        ws = [(out_time(s), out_time(e)) for _, s, e, _ in g]
        g_in = r(max(0.08, ws[0][0] - 0.06))
        nxt = out_time(GROUPS[gi + 1][0][1]) - 0.06 if gi + 1 < len(GROUPS) else SPEECH_END
        g_out = r(min(ws[-1][1] + 0.35, nxt))
        if gi + 1 < len(GROUPS):
            g_out = r(min(g_out, out_time(GROUPS[gi + 1][0][1]) - 0.06))
        groups_js.append({"id": f"cg{gi}", "in": g_in, "out": g_out,
                          "words": [{"id": f"c{gi}w{wi}", "s": a, "e": b} for wi, (a, b) in enumerate(ws)]})
    data = json.dumps(groups_js, separators=(",", ":"))
    return f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cg {{
      position: absolute; left: 110px; width: 860px; bottom: 600px;
      text-align: center; opacity: 0; visibility: hidden;
      font-family: "Archivo Black", sans-serif; font-size: 70px; line-height: 1.12;
      color: #ffffff; letter-spacing: -0.5px; overflow: visible;
    }}
    .w {{ position: relative; display: inline-block; margin: 0 6px; }}
    .w b {{
      position: relative; font-weight: 400; z-index: 1;
      text-shadow: 0 0 2px #13213c, 3px 3px 0 #13213c, -2px -2px 0 #13213c, 2px -2px 0 #13213c,
        -2px 2px 0 #13213c, 0 6px 14px rgba(0,0,0,.45);
    }}
    .hl {{
      position: absolute; left: -10px; right: -10px; top: 14%; bottom: 4%;
      background: #ffd93d; border-radius: 10px 4px 12px 5px; transform-origin: 0 50%;
      z-index: 0;
    }}
    .em .hl {{ background: #e63b2e; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(groups_html)}
  </div>
  <script>
    const G = {data};
    const tl = gsap.timeline({{ paused: true }});
    for (const g of G) {{
      const el = "#" + g.id;
      tl.set(el, {{ visibility: "visible" }}, g.in);
      tl.fromTo(el, {{ opacity: 0, y: 18, filter: "blur(6px)" }},
        {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.14, ease: "power3.out" }}, g.in);
      g.words.forEach((w, i) => {{
        const hl = "#" + w.id + " .hl", txt = "#" + w.id + " b";
        const em = document.querySelector("#" + w.id).classList.contains("em");
        tl.fromTo(hl, {{ scaleX: 0, rotation: -1.5, opacity: 1 }}, {{ scaleX: 1, rotation: -1.5, opacity: 1, duration: 0.12, ease: "power2.out", immediateRender: true }}, w.s);
        tl.fromTo(txt, {{ color: "#ffffff" }}, {{ color: em ? "#ffffff" : "#13213c", duration: 0.06 }}, w.s + 0.03);
        const next = i + 1 < g.words.length ? g.words[i + 1].s : g.out - 0.1;
        if (i + 1 < g.words.length) {{
          tl.to(hl, {{ opacity: 0, duration: 0.08 }}, next);
          tl.to(txt, {{ color: "#ffffff", duration: 0.06 }}, next);
        }}
      }});
      tl.to(el, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, g.out - 0.1);
      tl.set(el, {{ opacity: 0, visibility: "hidden" }}, g.out);
    }}
    window.__timelines["captions"] = tl;
  </script>
</template>
'''

if __name__ == "__main__":
    open(os.path.join(ROOT, "index.html"), "w").write(build_index())
    open(os.path.join(ROOT, "compositions", "captions.html"), "w").write(build_captions())
    print("segments start", starts, "speech end", SPEECH_END, "total", TOTAL)
    print("scenes", [(s, r(a), r(b)) for s, a, b in SCENES])
    for g in GROUPS:
        print(round(out_time(g[0][1]), 2), " ".join(w[0] for w in g))
