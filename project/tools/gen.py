"""Builds index.html (footage, audio, scene hosts, camera moves) and
compositions/captions.html from edl.json. Scenes are hand-written files."""
import json, sys, html

P = sys.argv[1]
D = json.load(open("edl.json"))
EDL, TOTAL, WORDS = D["edl"], round(D["total"], 3), D["words"]
_f = 0
for e in EDL:
    n = round(e["dur"] * 30)
    e["start"], e["dur"] = round(_f / 30, 4), None
    e["sf"], e["ef"] = _f, _f + n
    _f += n
TOTAL = round(_f / 30, 4)
fs = lambda f: f"{f/30:.4f}".rstrip("0").rstrip(".")
r3 = lambda x: f"{x:.3f}".rstrip("0").rstrip(".")
SEG = {e["i"]: e for e in EDL}
cut = [e["start"] for e in EDL]  # cut times

# ---------- scenes (id, file, start, dur) ----------
SCENES = [
    ("hook", 1), ("ccc", 2), ("movein", 3), ("peluang", 4), ("premium", 5), ("outro", 6)
]

# ---------- sfx: (id, file, start, volume) start = picture time + 1 frame - peak ----------
F = 1 / 30
SFX_PEAK = {
    "whoosh-short.mp3": 0.162, "mk-1993.mp3": 0.082, "mk-3115.mp3": 0.117, "mk-2903.mp3": 0.875,
    "mk-1936.mp3": 0.167, "mk-175.mp3": 0.462, "impact-bass-1.mp3": 0.073, "mk-2364.mp3": 0.044,
    "mk-1490.mp3": 0.721, "mk-1558.mp3": 0.594, "mk-3005.mp3": 0.022, "mk-772.mp3": 0.52,
    "mk-2358.mp3": 0.035, "mk-2350.mp3": 0.455, "mk-1492.mp3": 1.087, "mk-2356.mp3": 0.133,
    "mk-2000.mp3": 0.128,
}
SFX_DUR = {
    "whoosh-short.mp3": 0.57, "mk-1993.mp3": 1.07, "mk-3115.mp3": 0.6, "mk-2903.mp3": 3.0,
    "mk-1936.mp3": 2.0, "mk-175.mp3": 0.65, "impact-bass-1.mp3": 2.1, "mk-2364.mp3": 0.3,
    "mk-1490.mp3": 1.0, "mk-1558.mp3": 1.2, "mk-3005.mp3": 0.21, "mk-772.mp3": 0.9,
    "mk-2358.mp3": 0.5, "mk-2350.mp3": 2.0, "mk-1492.mp3": 1.35, "mk-2356.mp3": 0.34,
    "mk-2000.mp3": 1.5,
}
S2, S3, S4, S5, S6 = cut[1], cut[2], cut[3], cut[4], cut[5]
HITS = [  # (id, file, picture time, volume)
    ("sfx-cardA", "whoosh-short.mp3", 0.16, 0.30),
    ("sfx-15", "mk-1993.mp3", 1.40, 0.42),
    ("sfx-cardB", "mk-3115.mp3", 2.40, 0.32),
    ("sfx-impact", "mk-2903.mp3", 3.95, 0.30),
    ("sfx-coins", "mk-1936.mp3", 3.95, 0.34),
    ("sfx-cut1", "mk-175.mp3", S2, 0.30),
    ("sfx-stamp", "impact-bass-1.mp3", S2 + 1.20, 0.30),
    ("sfx-stamp2", "mk-2364.mp3", S2 + 1.20, 0.28),
    ("sfx-cut2", "mk-1490.mp3", S3, 0.30),
    ("sfx-keys", "mk-1558.mp3", S3 + 0.68, 0.65),
    ("sfx-cut3", "whoosh-short.mp3", S4, 0.26),
    ("sfx-peluang", "mk-3005.mp3", S4 + 0.68, 0.36),
    ("sfx-cut4", "mk-772.mp3", S5, 0.24),
    ("sfx-pin", "mk-2358.mp3", S5 + 1.00, 0.36),
    ("sfx-premium", "mk-2350.mp3", S5 + 1.88, 0.45),
    ("sfx-cut5", "mk-1492.mp3", S6, 0.26),
    ("sfx-next", "mk-2356.mp3", S6 + 0.80, 0.40),
    ("sfx-follow", "mk-2000.mp3", S6 + 1.25, 0.26),
]

vids, auds, hosts = [], [], []
for e in EDL:
    vids.append(
        f'      <video id="v{e["i"]}" class="clip" src="assets/footage.mp4" muted playsinline '
        f'data-start="{fs(e["sf"])}" data-duration="{fs(e["ef"]-e["sf"])}" data-media-start="{r3(e["src"])}" '
        f'data-track-index="0"></video>')
    auds.append(
        f'    <audio id="vo{e["i"]}" class="clip" src="assets/voice.wav" data-start="{fs(e["sf"])}" '
        f'data-duration="{fs(e["ef"]-e["sf"])}" data-media-start="{r3(e["src"])}" data-volume="1" '
        f'data-fade-in="0.02" data-fade-out="0.03" data-audio-group="voice" data-track-index="{9 + e["i"] % 2}"></audio>')
for n, (sid, si) in enumerate(SCENES):
    e = SEG[si]
    hosts.append(
        f'    <div id="{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
        f'data-start="{fs(e["sf"])}" data-duration="{fs(e["ef"]-e["sf"])}" data-track-kind="graphics" '
        f'data-track-index="{2 + n % 2}" data-width="1080" data-height="1920" style="z-index:{20 + n}"></div>')
track_end = {}
for n, (hid, f, t, v) in enumerate(HITS):
    st = max(0.0, t + F - SFX_PEAK[f])
    dur = min(SFX_DUR[f], TOTAL - st)
    tr = next(k for k in range(12, 30) if track_end.get(k, -1) <= st)
    track_end[tr] = st + dur
    auds.append(
        f'    <audio id="{hid}" class="clip" src="assets/sfx/{f}" data-start="{r3(st)}" data-duration="{r3(dur)}" '
        f'data-volume="{v}" data-audio-group="sfx" data-track-index="{tr}"></audio>')

# music bed: ducked under the voice, a short hold before the RM30K payoff, lift after the last word
last_word = WORDS[-1]["e"]
pts = [(0, 0.11), (3.55, 0.11), (3.78, 0.03), (3.93, 0.03), (3.97, 0.13), (4.6, 0.11),
       (last_word + 0.05, 0.11), (last_word + 0.35, 0.30), (TOTAL - 0.45, 0.30), (TOTAL, 0.0)]
auto = {"version": 1, "lanes": [{"target": "volume", "points": [{"t": round(t, 3), "v": v} for t, v in pts]}]}
auto_attr = html.escape(json.dumps(auto, separators=(",", ":")), quote=True)
auds.append(
    f'    <audio id="bgm" class="clip" src="assets/music/tech-house-vibes.mp3" data-start="0" data-duration="{r3(TOTAL)}" '
    f'data-media-start="62.04" data-volume="1" data-automation="{auto_attr}" data-audio-group="music" '
    f'data-track-index="11"></audio>')

# camera (footage wrapper) moves, all on the root timeline
cam = f"""
      const tl = gsap.timeline({{ paused: true }});
      gsap.set("#cam", {{ transformOrigin: "50% 45%", scale: 1, x: 0, y: 0 }});
      // hook: punch on 15% and harder on RM30,000
      tl.to("#cam", {{ scale: 1.06, duration: 0.3, ease: "expo.out" }}, 1.36);
      tl.to("#cam", {{ scale: 1.13, duration: 0.22, ease: "expo.out" }}, 3.93);
      tl.to("#cam", {{ y: -8, duration: 0.05, yoyo: true, repeat: 3, ease: "sine.inOut" }}, 3.95);
      // cut 1 ({r3(S2)}): zoom-out settle + flash
      tl.fromTo("#cam", {{ scale: 1.2, y: 0 }}, {{ scale: 1.0, duration: 0.5, ease: "expo.out", immediateRender: false }}, {r3(S2)});
      tl.fromTo("#flash", {{ opacity: 0.6 }}, {{ opacity: 0, duration: 0.22, ease: "power2.out", immediateRender: false }}, {r3(S2)});
      // CCC stamp shake
      tl.to("#cam", {{ scale: 1.035, duration: 0.04 }}, {r3(S2 + 1.18)});
      tl.to("#cam", {{ keyframes: {{ y: [0, -14, 10, -6, 3, 0] }}, duration: 0.28, ease: "none" }}, {r3(S2 + 1.2)});
      tl.to("#cam", {{ scale: 1.0, duration: 0.3, ease: "power2.out" }}, {r3(S2 + 1.5)});
      // cut 2 ({r3(S3)}): horizontal whip
      tl.to("#cam", {{ x: -110, scale: 1.22, duration: 0.12, ease: "power3.in" }}, {r3(S3 - 0.12)});
      tl.set("#cam", {{ x: 110 }}, {r3(S3)});
      tl.to("#cam", {{ x: 0, scale: 1.0, duration: 0.38, ease: "expo.out" }}, {r3(S3)});
      tl.fromTo("#streak", {{ xPercent: -120, opacity: 0.9 }}, {{ xPercent: 120, opacity: 0.9, duration: 0.24, ease: "power2.inOut", immediateRender: false }}, {r3(S3 - 0.12)});
      tl.set("#streak", {{ opacity: 0 }}, {r3(S3 + 0.13)});
      // cut 3 ({r3(S4)}): hard punch-in for "Jangan lepaskan peluang"
      tl.set("#cam", {{ scale: 1.14 }}, {r3(S4)});
      // cut 4 ({r3(S5)}): ease back out + flash
      tl.to("#cam", {{ scale: 1.0, duration: 0.55, ease: "expo.out" }}, {r3(S5)});
      tl.fromTo("#flash", {{ opacity: 0.45 }}, {{ opacity: 0, duration: 0.2, ease: "power2.out", immediateRender: false }}, {r3(S5)});
      // "premium": slow push while the word lands
      tl.to("#cam", {{ scale: 1.05, duration: 0.7, ease: "power2.out" }}, {r3(S5 + 1.86)});
      // cut 5 ({r3(S6)}): dip cut
      tl.to("#dip", {{ opacity: 0.45, duration: 0.1, ease: "power1.in" }}, {r3(S6 - 0.1)});
      tl.set("#cam", {{ scale: 1.0 }}, {r3(S6)});
      tl.to("#dip", {{ opacity: 0, duration: 0.2, ease: "power2.out" }}, {r3(S6)});
      window.__timelines["main"] = tl;
"""

index = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #08140f; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #cam {{ position: absolute; inset: 0; overflow: hidden; }}
      #cam video {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #flash {{ position: absolute; inset: 0; background: #fff8ec; opacity: 0; z-index: 60; pointer-events: none; }}
      #dip {{ position: absolute; inset: 0; background: #000; opacity: 0; z-index: 61; pointer-events: none; }}
      #streak {{ position: absolute; top: 0; left: 0; width: 1080px; height: 1920px; opacity: 0; z-index: 59; pointer-events: none;
        background: linear-gradient(100deg, transparent 30%, rgba(233,201,139,0.0) 38%, rgba(255,241,201,0.85) 50%, rgba(233,201,139,0.0) 62%, transparent 70%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{r3(TOTAL)}" data-width="1080" data-height="1920">
      <div id="cam">
{chr(10).join(vids)}
      </div>
      <div id="streak" data-layout-ignore></div>
      <div id="flash" data-layout-ignore></div>
      <div id="dip" data-layout-ignore></div>
{chr(10).join(hosts)}
    <div id="captions" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{r3(TOTAL)}" data-track-kind="captions" data-track-index="4" data-width="1080" data-height="1920" style="z-index:40"></div>
{chr(10).join(auds)}
    </div>
    <script>{cam}    </script>
  </body>
</html>
"""
open(f"{P}/index.html", "w").write(index)

# ---------- captions ----------
GROUPS = [
    ([26, 27], []), ([28, 29, 30], [30]), ([31, 32, 33], []), ([34, 35, 36], [36]),
    ([1, 2, 3], []), ([4, 5], []), ([6, 7, 8, 9], [6]),
    ([13, 14, 15], []), ([16, 17], [16, 17]),
    ([41, 42, 43], []), ([44, 45], []), ([46, 47], []), ([48], [48]), ([49, 50, 51], []),
    ([52, 53], []), ([54, 55], [55]),
]
DISPLAY = {"15%.": "15%", "lot,": "lot", "RM30,000.": "RM30,000", "ni,": "ni", "dah.": "dah", "masuk,": "masuk,",
           "in.": "in", "ni.": "ni", "tune.": "tuned", "video.": "video!", "yang": "yang"}
WK = {w["k"]: w for w in WORDS}
groups_html, js = [], []
for gi, (ks, emph) in enumerate(GROUPS):
    ws = [WK[k] for k in ks]
    nxt = WK[GROUPS[gi + 1][0][0]]["s"] if gi + 1 < len(GROUPS) else TOTAL
    gs = max(0.0, ws[0]["s"] - 0.06)
    seg_end = SEG[ws[-1]["seg"]]["ef"] / 30
    ge = min(nxt - 0.06, ws[-1]["e"] + 0.45, TOTAL - 0.05, seg_end - 0.02)
    spans = []
    for k, w in zip(ks, ws):
        txt = DISPLAY.get(w["w"], w["w"])
        if k == 52: txt = "Stay"
        if k == 1: txt = "Yang"
        if k == 13: txt = "Boleh"
        if k == 16: txt = "Move"
        if k == 41: txt = "Nak"
        if k == 44: txt = "di"
        cls = "w em" if k in emph else "w"
        spans.append(f'<span id="cw{k}" class="{cls}">{html.escape(txt)}</span>')
    groups_html.append(f'      <div id="cg{gi}" class="cg"><div class="pill">{" ".join(spans)}</div></div>')
    js.append(f'  tl.fromTo("#cg{gi} .pill", {{opacity:0, y:22, scale:0.96}}, {{opacity:1, y:0, scale:1, duration:0.16, ease:"power3.out", immediateRender:false}}, {r3(gs)});')
    js.append(f'  tl.set("#cg{gi}", {{visibility:"visible"}}, {r3(gs)});')
    for i, (k, w) in enumerate(zip(ks, ws)):
        if k in emph:
            js.append(f'  tl.fromTo("#cw{k}", {{scale:1.45, opacity:0}}, {{scale:1, opacity:1, duration:0.22, ease:"expo.out", immediateRender:false}}, {r3(max(gs, w["s"] - 0.03))});')
        else:
            js.append(f'  tl.fromTo("#cw{k}", {{color:"#fff8ec"}}, {{color:"#f2cf8d", duration:0.06, immediateRender:false}}, {r3(max(gs, w["s"] - 0.02))});')
            if i + 1 < len(ws):
                js.append(f'  tl.to("#cw{k}", {{color:"#fff8ec", duration:0.08}}, {r3(ws[i + 1]["s"] - 0.02)});')
    js.append(f'  tl.to("#cg{gi} .pill", {{opacity:0, y:-10, duration:0.1, ease:"power2.in"}}, {r3(ge - 0.1)});')
    js.append(f'  tl.set("#cg{gi}", {{visibility:"hidden"}}, {r3(ge)});')

cap = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cg {{ position: absolute; left: 0; top: 1150px; width: 1080px; height: 170px; display: flex; align-items: center;
      justify-content: center; visibility: hidden; overflow: visible; }}
    .pill {{ max-width: 860px; text-align: center; padding: 12px 30px 16px; border-radius: 26px;
      background: rgba(6, 26, 19, 0.58); box-shadow: 0 10px 40px rgba(0,0,0,0.25);
      font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 62px; line-height: 1.12; color: #fff8ec;
      letter-spacing: -0.01em; text-shadow: 0 3px 14px rgba(0,0,0,0.45); opacity: 0; }}
    .w {{ display: inline-block; }}
    .w.em {{ font-family: "Playfair Display", serif; font-style: italic; font-weight: 900; font-size: 84px;
      color: #f2cf8d; letter-spacing: 0; line-height: 1; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(groups_html)}
  </div>
  <script>
  const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
  window.__timelines["captions"] = tl;
  </script>
</template>
"""
open(f"{P}/compositions/captions.html", "w").write(cap)
print("ok total", TOTAL, "cuts", [r3(c) for c in cut])
