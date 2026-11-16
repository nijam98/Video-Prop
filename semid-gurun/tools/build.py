#!/usr/bin/env python3
"""Generates index.html + compositions/*.html for the Semi-D Gurun reel.

Edit the tables below (EDL, captions, SFX, chapters) and re-run:
    python3 tools/build.py
"""
import json, math, os, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
TAIL = 1.7  # end-card hold after the last word

# ---------------------------------------------------------------- palette
PAPER, INK, MARKER, TERRA, MINT, RED = "#F6F0E4", "#1D2B4F", "#FFD43B", "#E8552D", "#2FA36B", "#D7263D"

# ---------------------------------------------------------------- edit decision list
# a = source seconds of the spoken part kept; v = source in-point for picture
# (defaults to a[0]; differs for J-cuts that keep the picture flowing)
EDL = [
    dict(id="s01", a=(0.00, 3.76), v=70.18, rate=2.0),      # hook: exterior at 2x under the hook line
    dict(id="s02", a=(5.12, 13.06)),
    dict(id="s03", a=(15.74, 17.22)),
    dict(id="s04", a=(18.04, 19.46)),
    dict(id="s05", a=(20.46, 23.86)),
    dict(id="s06", a=(24.76, 29.70)),
    dict(id="s07", a=(30.32, 30.94), v=29.70),              # picture keeps flowing
    dict(id="s08", a=(31.82, 32.24)),
    dict(id="s09", a=(33.52, 35.72), v=32.24),              # picture keeps flowing
    dict(id="s10", a=(36.26, 37.08)),
    dict(id="s11", a=(39.34, 43.94)),
    dict(id="s12", a=(44.96, 48.04)),
    dict(id="s13", a=(48.14, 51.72)),
    dict(id="s14", a=(57.48, 59.38)),
    dict(id="s15", a=(63.22, 67.64)),
    dict(id="s16", a=(69.42, 71.70)),
    dict(id="s17", a=(72.32, 73.44)),
    dict(id="s18", a=(75.60, 77.80), v=73.44, extra=TAIL),  # picture continues; holds under end card
]
t = 0.0
for s in EDL:
    s["start"] = round(t, 3)
    s["dur"] = round(s["a"][1] - s["a"][0], 3)
    t += s["dur"]
VOICE_END = round(t, 3)
TOTAL = round(VOICE_END + TAIL, 3)
ST = {s["id"]: s["start"] for s in EDL}

# ---------------------------------------------------------------- camera moves on the footage wrapper
# kind: zoom (zoom-through), whip, punch (hard punch-in), reset (hidden under an overlay)
CAM = [
    ("zoom", ST["s02"]), ("reset", ST["s03"]), ("whip", ST["s04"]), ("punch", ST["s05"]),
    ("reset", ST["s06"]), ("whip", ST["s08"]), ("punch", ST["s10"]), ("reset", ST["s11"]),
    ("zoom", ST["s12"]), ("punch", ST["s13"]), ("reset", ST["s14"]), ("whip", ST["s15"]),
    ("reset", ST["s16"]), ("zoom", ST["s17"]), ("punch", ST["s18"]),
]
PAPER_WIPES = [ST["s03"], ST["s11"], ST["s16"]]       # cut happens at wipe midpoint
SCRIBBLE_WIPES = [ST["s06"], ST["s14"]]

# ---------------------------------------------------------------- captions (output seconds)
# words wrapped in *stars* get the marker highlight
CAPTIONS = [
    (3.80, 4.32, "Pasal rumah ni"),
    (4.34, 5.62, "*4 bilik* *2 tandas*"),
    (5.66, 6.60, "*Cluster*"),
    (6.90, 7.86, "Ada *tanah tepi*"),
    (7.90, 8.62, "Tanah belakang tak ada"),
    (8.72, 9.86, "Tapi tanah belakang pun"),
    (9.88, 10.42, "dia ada lebih kurang"),
    (10.44, 11.66, "macam ruang *laundry*"),
    (11.74, 12.36, "Ruang tamu"),
    (12.38, 13.12, "dapat *sliding door*"),
    (13.20, 13.58, "Okay sebelah sini"),
    (13.60, 14.56, "*Master bedroom*"),
    (14.58, 15.80, "boleh muat *katil king*"),
    (16.00, 16.96, "and then..."),
    (16.98, 17.94, "*satu tandas*"),
    (17.98, 18.42, "Okay sebelah sini"),
    (18.44, 19.22, "*bilik nombor 2*"),
    (19.24, 19.88, "sama juga"),
    (20.04, 21.18, "boleh muat *katil king*"),
    (21.20, 21.94, "ataupun *queen*"),
    (22.10, 23.46, "dapat satu *tingkap*"),
    (23.54, 24.02, "Okay sebelah sini"),
    (24.04, 24.46, "ruang makan"),
    (24.48, 25.26, "sekali *ruang dapur*"),
    (25.30, 26.90, "ada satu *tandas* lagi"),
    (27.04, 27.76, "Bilik keempat"),
    (27.78, 28.26, "*tinggi*"),
    (28.28, 29.64, "boleh buat *loteng*"),
    (29.66, 30.46, "ada siap dengan"),
    (30.48, 31.50, "*pencahayaan*"),
    (31.58, 32.02, "Okay nampak ni"),
    (32.04, 32.80, "dapat *backsplash*"),
    (32.82, 34.60, "untuk kitchen"),
    (34.90, 36.00, "Jadi senang kata"),
    (36.02, 37.26, "buat terus"),
    (37.28, 38.14, "*kitchen cabinet*"),
    (38.30, 38.98, "Bilik ketiga"),
    (39.00, 40.12, "memang *sangat-sangat luas*"),
    (40.18, 40.90, "Ruang belakang ni"),
    (40.92, 42.00, "lebih pada ruang"),
    (42.02, 42.72, "kita dah buat"),
    (42.74, 44.44, "*washing machine*"),
    (44.68, 45.66, "Tanah tepi lebih kurang"),
    (45.68, 46.80, "*8 kaki* sahaja lagi"),
]

# ---------------------------------------------------------------- sound effects
# (output time the clip STARTS, file, volume, media_start)
def sfx(at, name, vol=0.6, ms=0.0):
    return dict(at=round(at, 3), name=name, vol=vol, ms=ms)

SFX = [
    # hook
    sfx(0.00, "impact-zoom", 0.55, 0.40),
    sfx(0.70, "pop-hard", 0.45),
    sfx(1.30, "pencil-scribble", 0.9),
    sfx(2.04, "coin-prize", 0.38),
    sfx(2.55, "pencil-scribble", 0.9),
    # zoom-through into specs
    sfx(ST["s02"] - 0.30, "whoosh-sweep", 0.55),
    # specs card
    sfx(3.92, "paper-slide", 1.0),
    sfx(4.50, "pencil-write", 0.55, 0.9),
    sfx(5.02, "pencil-scribble", 0.85),
    sfx(5.66, "pop-hard", 0.45),
    sfx(6.92, "pop-long", 0.55),
    sfx(7.72, "pop-bubble", 0.6),
    sfx(10.46, "pencil-scribble", 0.8),
    # paper wipe -> ruang tamu
    sfx(ST["s03"] - 0.40, "paper-slide", 1.0),
    sfx(ST["s03"] - 0.30, "whoosh-sweep", 0.45),
    sfx(11.90, "pencil-write", 0.5, 0.9),
    # whip -> master
    sfx(ST["s04"] - 0.12, "whoosh-fast", 0.7),
    sfx(14.80, "pencil-scribble", 0.85),
    sfx(16.80, "pop-bubble", 0.6),
    # scribble wipe -> bilik 2
    sfx(ST["s06"] - 0.42, "pencil-scribble", 1.0),
    sfx(ST["s06"] - 0.10, "whoosh-accent", 0.5),
    sfx(20.40, "pencil-write", 0.5, 0.9),
    sfx(22.08, "pencil-scribble", 0.85),
    # whip -> ruang makan
    sfx(ST["s08"] - 0.12, "whoosh-fast", 0.7),
    sfx(25.52, "pop-bubble", 0.6),
    # paper wipe -> bilik 4
    sfx(ST["s11"] - 0.40, "paper-slide", 1.0),
    sfx(ST["s11"] - 0.30, "whoosh-sweep", 0.45),
    sfx(27.74, "pencil-scribble", 0.85),
    sfx(28.80, "pencil-write", 0.5, 0.9),
    sfx(30.05, "sparkle", 0.4),
    # zoom-through -> dapur
    sfx(ST["s12"] - 0.30, "whoosh-sweep", 0.55),
    sfx(32.10, "pencil-scribble", 0.85),
    sfx(37.10, "pencil-write", 0.5, 0.9),
    # scribble wipe -> bilik 3
    sfx(ST["s14"] - 0.42, "pencil-scribble", 1.0),
    sfx(ST["s14"] - 0.10, "whoosh-accent", 0.5),
    sfx(39.02, "whoosh-fast", 0.45),
    # whip -> ruang belakang
    sfx(ST["s15"] - 0.12, "whoosh-fast", 0.7),
    sfx(42.70, "pencil-scribble", 0.85),
    # paper wipe -> tanah tepi
    sfx(ST["s16"] - 0.40, "paper-slide", 1.0),
    sfx(ST["s16"] - 0.30, "whoosh-sweep", 0.45),
    sfx(45.60, "pencil-write", 0.5, 0.9),
    # end card
    sfx(ST["s17"] - 0.30, "whoosh-sweep", 0.55),
    sfx(46.80, "impact-zoom", 0.32, 0.40),
    sfx(47.30, "coins-clink", 0.28),
    sfx(47.55, "pencil-scribble", 0.9),
    sfx(47.86, "pencil-write", 0.5, 0.9),
    sfx(48.40, "paper-slide", 1.0),
    sfx(49.25, "pencil-scribble", 0.85),
    sfx(49.62, "notify-positive", 0.3),
]

# ================================================================ shared scene pieces
FONTS_CSS = """
@font-face { font-family: "Permanent Marker"; src: url("assets/fonts/permanent-marker-400.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Caveat"; font-weight: 700; src: url("assets/fonts/Caveat-700-latin.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Caveat Brush"; src: url("assets/fonts/CaveatBrush.woff2") format("woff2"); font-display: block; }
"""

BASE_CSS = f"""
#root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
.abs {{ position: absolute; }}
svg.dd {{ position: absolute; overflow: visible; }}
svg.dd path {{ fill: none; stroke-linecap: round; stroke-linejoin: round; }}
svg.dd path.halo {{ stroke: rgba(255,255,255,0.92); stroke-width: 20; }}
svg.dd path.ink {{ stroke: {INK}; stroke-width: 8; }}
svg.dd path.ink2 {{ stroke: {INK}; stroke-width: 3.5; opacity: 0.55; }}
svg.dd path.acc {{ stroke: {TERRA}; }}
svg.dd path.mint {{ stroke: {MINT}; }}
svg.dd path.red {{ stroke: {RED}; }}
.tag {{ position: absolute; left: 120px; top: 300px; padding: 20px 34px 22px 26px; background: {PAPER};
  box-shadow: 0 10px 28px rgba(20,25,45,0.28); white-space: nowrap; display: flex; align-items: baseline; gap: 18px;
  clip-path: polygon(0% 3%, 6% 0%, 14% 2%, 23% 0%, 35% 3%, 47% 0%, 58% 2%, 70% 0%, 82% 3%, 93% 0%, 100% 2%, 99% 30%, 100% 62%, 99% 100%, 88% 97%, 76% 100%, 63% 97%, 51% 100%, 38% 97%, 26% 100%, 13% 97%, 3% 100%, 0% 96%, 1% 60%, 0% 28%); }}
.tag .no {{ font-family: "Permanent Marker"; font-size: 44px; color: {TERRA}; }}
.tag .lb {{ font-family: "Permanent Marker"; font-size: 60px; color: {INK}; line-height: 1; }}
.tape {{ position: absolute; width: 150px; height: 46px; background: rgba(255,212,59,0.78); left: 92px; top: 280px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.12); }}
.note {{ position: absolute; white-space: nowrap; }}
.note .hl {{ position: absolute; left: -14px; right: -14px; top: 46%; bottom: 2%; background: {MARKER}; opacity: 0.92;
  border-radius: 10px 4px 12px 6px; transform-origin: 0 50%; }}
.note .tx {{ position: relative; font-family: "Caveat"; font-weight: 700; font-size: 86px; color: {INK}; line-height: 1;
  text-shadow: 0 0 10px rgba(255,255,255,0.9), 0 0 3px rgba(255,255,255,1); }}
.note.big .tx {{ font-size: 104px; }}
.note.sm .tx {{ font-size: 70px; }}
"""

HELPERS_JS = """
var NS = "http://www.w3.org/2000/svg";
function hh(n, s) { var x = Math.sin(n * 127.1 + (s || 1) * 311.7) * 43758.5453; return (x - Math.floor(x)) * 2 - 1; }
var renders = [];
function boil(els, amp, rot, seed) {
  els = gsap.utils.toArray(els);
  renders.push(function () {
    var st = Math.floor((tl.time() * 30) / 3);
    els.forEach(function (e, i) {
      gsap.set(e, { x: hh(st * 3 + i * 97, seed) * amp, y: hh(st * 3 + 1 + i * 97, seed) * amp,
                    rotation: hh(st * 3 + 2 + i * 97, seed) * rot });
    });
  });
}
function finish() {
  tl.eventCallback("onUpdate", function () { for (var i = 0; i < renders.length; i++) renders[i](); });
  for (var i = 0; i < renders.length; i++) renders[i]();
}
// draw every stroke of a doodle in sequence; halo/ink/ink2 copies of one stroke share data-i
function drawOn(sel, at, dur) {
  var paths = gsap.utils.toArray(sel + " path");
  var n = 0; paths.forEach(function (p) { n = Math.max(n, +p.getAttribute("data-i") + 1); });
  var seg = dur / Math.max(1, n * 0.85 + 0.15);
  paths.forEach(function (p) {
    var i = +p.getAttribute("data-i"), len = p.getTotalLength() + 2;
    var lag = p.classList.contains("ink2") ? seg * 0.35 : 0;
    gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len, opacity: 0 });
    tl.set(p, { opacity: p.classList.contains("ink2") ? 0.55 : 1 }, at + i * seg * 0.85 + lag);
    tl.to(p, { strokeDashoffset: 0, duration: seg, ease: "power1.inOut" }, at + i * seg * 0.85 + lag);
  });
}
// handwriting reveal: marker swipe, then the words write left to right
function note(sel, at, dur) {
  var hl = document.querySelector(sel + " .hl"), tx = document.querySelector(sel + " .tx");
  if (hl) tl.fromTo(hl, { scaleX: 0 }, { scaleX: 1, duration: 0.22, ease: "power2.out" }, at);
  tl.fromTo(tx, { clipPath: "inset(-20% 100% -20% -2%)" },
            { clipPath: "inset(-20% -4% -20% -2%)", duration: dur || 0.45, ease: "power1.inOut" }, at + 0.06);
}
function tagIn(sel, at) {
  tl.fromTo(sel, { y: -60, rotation: -9, opacity: 0 }, { y: 0, rotation: -2, opacity: 1, duration: 0.5, ease: "back.out(1.7)" }, at);
}
function out(sel, at, d) { tl.to(sel, { opacity: 0, y: -18, duration: d || 0.2, ease: "power2.in" }, at); }
"""

# ---------------------------------------------------------------- doodle library (240x240 boxes)
ICONS = {
    "bed": ["M30 64 L30 196", "M30 152 L214 152 L214 196", "M30 122 L204 122 Q220 124 214 152",
            "M44 100 Q44 86 60 86 L94 86 Q108 86 108 100 Q108 114 94 114 L60 114 Q44 114 44 100 Z",
            "M38 196 L38 212 M206 196 L206 212"],
    "crown": ["M62 70 L70 22 L100 50 L120 12 L140 50 L170 22 L178 70 Z", "M64 84 L176 84"],
    "toilet": ["M62 26 L136 26 L136 92 L62 92 Z", "M40 96 L172 96 Q172 150 124 166 L124 204 L74 204 L74 166 Q40 150 40 96 Z",
               "M48 112 L164 112"],
    "door": ["M28 30 L132 30 L132 214 L28 214 Z", "M104 46 L212 46 L212 214 L104 214",
             "M56 124 L180 124 M158 104 L182 124 L158 144"],
    "window": ["M40 36 L204 36 L204 204 L40 204 Z", "M122 36 L122 204", "M40 120 L204 120",
               "M60 56 L92 56 M60 70 L80 70"],
    "bulb": ["M120 34 Q62 34 62 98 Q62 134 96 158 L96 186 L144 186 L144 158 Q178 134 178 98 Q178 34 120 34 Z",
             "M100 204 L140 204 M106 220 L134 220", "M104 158 L112 120 L120 140 L128 120 L136 158",
             "M120 -6 L120 12 M44 30 L58 44 M196 30 L182 44 M18 100 L36 100 M222 100 L204 100"],
    "cabinet": ["M18 40 L222 40", "M30 40 L210 40 L210 204 L30 204 Z", "M120 40 L120 204",
                "M104 108 L104 136 M136 108 L136 136", "M30 172 L210 172"],
    "washer": ["M46 24 L194 24 L194 216 L46 216 Z", "M46 66 L194 66",
               "M70 142 A50 50 0 1 0 170 142 A50 50 0 1 0 70 142", "M96 142 Q120 118 144 142",
               "M64 46 L82 46 M160 46 A6 6 0 1 0 172 46 A6 6 0 1 0 160 46"],
    "pin": ["M120 18 Q62 18 62 80 Q62 122 120 196 Q178 122 178 80 Q178 18 120 18 Z",
            "M120 58 A22 22 0 1 0 120.1 58"],
    "house": ["M24 116 L120 30 L216 116", "M48 98 L48 212 L192 212 L192 98", "M100 212 L100 152 L140 152 L140 212",
              "M62 128 L88 128 L88 152 L62 152 Z"],
    "check": ["M14 56 L44 88 L104 14"],
    "cross": ["M18 18 L92 92", "M92 18 L18 92"],
    "beds2": ["M14 70 L14 160 M14 130 L104 130 L104 160 M14 108 L98 108 Q108 110 104 130",
              "M126 50 L126 160 M126 130 L232 130 L232 160 M126 104 L224 104 Q236 106 232 130"],
}

def doodle(icon_id, icon, x, y, size, cls="", seed=1):
    """Emit an svg doodle: halo + ink + sketchy second pass for every stroke."""
    sc = size / 240.0
    paths = []
    for i, d in enumerate(ICONS[icon]):
        dx, dy = 2.5 + (seed % 3), 2.0 - (seed % 2) * 3.5
        paths.append(f'<path class="halo" data-i="{i}" d="{d}" style="stroke-width:{18/sc:.2f}"/>')
        paths.append(f'<path class="ink {cls}" data-i="{i}" d="{d}" style="stroke-width:{7/sc:.2f}"/>')
        paths.append(f'<path class="ink2 {cls}" data-i="{i}" d="{d}" style="stroke-width:{3/sc:.2f}" transform="translate({dx} {dy})"/>')
    return (f'<div class="abs" id="{icon_id}-w" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px">'
            f'<div class="abs" id="{icon_id}" style="inset:0">'
            f'<svg class="dd" viewBox="0 0 240 240" style="inset:0;width:{size}px;height:{size}px">'
            + "".join(paths) + '</svg></div></div>')

def raw_doodle(did, x, y, w, h, ds, cls=""):
    """Free-form doodle in scene pixel space (arrows, measure lines)."""
    paths = []
    for i, d in enumerate(ds):
        paths.append(f'<path class="halo" data-i="{i}" d="{d}"/>')
        paths.append(f'<path class="ink {cls}" data-i="{i}" d="{d}"/>')
        paths.append(f'<path class="ink2 {cls}" data-i="{i}" d="{d}" transform="translate(3 2)"/>')
    return (f'<div class="abs" id="{did}-w" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="abs" id="{did}" style="inset:0">'
            f'<svg class="dd" viewBox="0 0 {w} {h}" style="inset:0;width:{w}px;height:{h}px">' + "".join(paths) +
            '</svg></div></div>')

def note_html(nid, text, x, y, size="", rot=-2):
    return (f'<div class="note {size}" id="{nid}" style="left:{x}px;top:{y}px;rotate:{rot}deg">'
            f'<div class="hl"></div><span class="tx">{text}</span></div>')

def tag_html(prefix, no, label):
    return (f'<div class="tag" id="{prefix}-tag"><span class="no">{no}</span><span class="lb">{label}</span></div>')

def scene_file(sid, dur, body, script, extra_css=""):
    return f"""<template>
  <style>
{FONTS_CSS}
{BASE_CSS.replace('#root', '#root')}
{extra_css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-duration="{dur:.3f}">
{body}
  </div>
  <script>
    (function () {{
      var tl = gsap.timeline({{ paused: true }});
{textwrap.indent(HELPERS_JS, '      ')}
{textwrap.indent(script, '      ')}
      finish();
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""

SCENES = []  # (sid, start, dur)

def write_scene(sid, start, dur, body, script, extra_css=""):
    with open(os.path.join(ROOT, "compositions", f"{sid}.html"), "w") as f:
        f.write(scene_file(sid, dur, body, script, extra_css))
    SCENES.append((sid, round(start, 3), round(dur, 3)))

# ================================================================ HOOK
hook_css = f"""
#hk-semid {{ left: 120px; top: 296px; font-family: "Archivo Black"; font-size: 150px; line-height: 1; color: {INK};
  text-shadow: 8px 8px 0 {MARKER}; letter-spacing: -2px; white-space: nowrap; }}
#hk-murah-w {{ left: 120px; top: 468px; }}
#hk-murah {{ background: {MARKER}; padding: 10px 28px 6px; font-family: "Permanent Marker"; font-size: 84px; color: {INK};
  line-height: 1.05; white-space: nowrap; box-shadow: 0 8px 20px rgba(0,0,0,0.25); }}
#hk-gurun {{ left: 214px; top: 598px; font-family: "Caveat"; font-weight: 700; font-size: 84px; color: {INK};
  text-shadow: 0 0 12px #fff, 0 0 4px #fff, 0 0 2px #fff; white-space: nowrap; }}
#hk-tag-w {{ left: 120px; top: 760px; width: 660px; height: 300px; }}
#hk-tagcard {{ position: absolute; inset: 0; background: {PAPER}; border-radius: 26px 26px 26px 26px;
  box-shadow: 0 16px 40px rgba(10,15,35,0.38);
  clip-path: polygon(9% 0, 100% 0, 100% 100%, 9% 100%, 0 50%); }}
#hk-hole {{ position: absolute; left: 34px; top: 132px; width: 36px; height: 36px; border-radius: 50%; background: rgba(29,43,79,0.85); }}
#hk-harga {{ position: absolute; left: 96px; top: 2px; font-family: "Permanent Marker"; font-size: 46px; color: {INK}; }}
#hk-price {{ position: absolute; left: 92px; top: 86px; font-family: "Archivo Black"; font-size: 124px; line-height: 1; color: {TERRA}; letter-spacing: -3px; }}
#hk-sahaja {{ position: absolute; left: 420px; top: 226px; font-family: "Caveat Brush"; font-size: 64px; color: {INK}; rotate: -6deg; white-space: nowrap; }}
"""
hook_body = "\n".join([
    '<div class="abs" id="hk-semid">SEMI-D</div>',
    '<div class="abs" id="hk-murah-w"><div id="hk-murah">PALING MURAH</div></div>',
    raw_doodle("hk-ul", 116, 568, 640, 50, ["M10 26 Q120 8 240 22 T470 18 Q560 14 620 30"], "acc"),
    doodle("hk-pin", "pin", 118, 604, 90, "acc", seed=2),
    '<div class="abs" id="hk-gurun">dekat Gurun, Kedah</div>',
    '<div class="abs" id="hk-tag-w"><div class="abs" id="hk-tag" style="inset:0"><div id="hk-tagcard"></div><div id="hk-hole"></div>'
    '<div id="hk-harga">HARGA</div><div id="hk-price">RM281K</div><div id="hk-sahaja">sahaja!</div></div></div>',
    raw_doodle("hk-circ", 130, 790, 680, 260,
               ["M60 120 Q40 22 320 20 Q610 16 625 105 Q640 196 340 198 Q70 204 50 130 Q46 90 120 58"], "acc"),
])
hook_js = """
// frame 0 already carries the hook line (thumbnail): SEMI-D lands from 1.18x
tl.fromTo("#hk-semid", { scale: 1.18, opacity: 1, transformOrigin: "0% 50%" }, { scale: 1, duration: 0.32, ease: "expo.out" }, 0);
tl.fromTo("#hk-murah", { scaleX: 0, opacity: 0, rotation: -3, transformOrigin: "0% 50%" }, { scaleX: 1, opacity: 1, rotation: -3, duration: 0.28, ease: "power3.out" }, 0.74);
drawOn("#hk-ul", 1.32, 0.42);
drawOn("#hk-pin", 1.30, 0.40);
tl.fromTo("#hk-gurun", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power2.out" }, 1.34);
// price tag swings in on its string
tl.fromTo("#hk-tag-w", { x: 900, rotation: 14, transformOrigin: "8% 50%" }, { x: 0, rotation: -3, duration: 0.55, ease: "back.out(1.5)" }, 1.86);
tl.fromTo("#hk-price", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2.2)" }, 2.14);
drawOn("#hk-circ", 2.58, 0.55);
tl.fromTo("#hk-sahaja", { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2.5)" }, 3.32);
boil(["#hk-ul", "#hk-circ", "#hk-pin"], 1.6, 0.5, 3);
boil(["#hk-tag"], 1.0, 0.25, 7);
"""
write_scene("hook", 0, ST["s02"], hook_body, hook_js, hook_css)

# ================================================================ SPECS CARD (s02)
sp_css = f"""
#sp-card-w {{ left: 120px; top: 300px; width: 640px; height: 760px; }}
#sp-card {{ position: absolute; inset: 0; background: {PAPER}; box-shadow: 0 18px 44px rgba(10,15,35,0.32);
  background-image: repeating-linear-gradient(0deg, transparent 0 77px, rgba(29,43,79,0.10) 77px 79px); }}
#sp-card .tape {{ left: 240px; top: -22px; rotate: 3deg; }}
#sp-title {{ position: absolute; left: 44px; top: 34px; font-family: "Permanent Marker"; font-size: 70px; color: {INK}; white-space: nowrap; }}
.sp-row {{ position: absolute; left: 150px; font-family: "Permanent Marker"; font-size: 60px; color: {INK}; white-space: nowrap; }}
.sp-row.c {{ font-family: "Caveat"; font-weight: 700; font-size: 68px; left: 120px; }}
#sp-stamp {{ position: absolute; left: 150px; top: 384px; padding: 6px 20px 2px; border: 6px solid {RED}; color: {RED};
  font-family: "Archivo Black"; font-size: 48px; letter-spacing: 3px; border-radius: 10px; }}
#sp-laundry {{ position: absolute; left: 60px; top: 670px; font-family: "Caveat"; font-weight: 700; font-size: 58px; color: {TERRA}; white-space: nowrap; }}
"""
sp_body = "\n".join([
    '<div class="abs" id="sp-card-w"><div class="abs" id="sp-card-in" style="inset:0">',
    '<div id="sp-card"><div class="tape"></div></div>',
    '<div id="sp-title">SPEC RUMAH</div>',
    raw_doodle("sp-tul", 40, 108, 420, 40, ["M8 20 Q100 6 210 18 T410 16"], "acc"),
    doodle("sp-bed", "bed", 36, 158, 104, seed=1),
    '<div class="sp-row" id="sp-r1" style="top:182px">4 BILIK</div>',
    doodle("sp-wc", "toilet", 40, 270, 96, seed=2),
    '<div class="sp-row" id="sp-r2" style="top:290px">2 TANDAS</div>',
    '<div id="sp-stamp">CLUSTER</div>',
    doodle("sp-ok", "check", 46, 486, 82, "mint", seed=1),
    '<div class="sp-row c" id="sp-r3" style="top:478px">ada tanah tepi</div>',
    doodle("sp-no", "cross", 50, 588, 70, "red", seed=2),
    '<div class="sp-row c" id="sp-r4" style="top:572px">tanah belakang</div>',
    '<div id="sp-laundry">&#8627; tapi ada ruang laundry</div>',
    '</div></div>',
])
o = ST["s02"]
L = lambda t_: round(t_ - o, 3)
sp_js = f"""
tl.fromTo("#sp-card-w", {{ x: -760, rotation: -8 }}, {{ x: 0, rotation: -1.5, duration: 0.6, ease: "expo.out" }}, 0.10);
drawOn("#sp-tul", 0.55, 0.35);
drawOn("#sp-bed", {L(4.40)}, 0.55);
tl.fromTo("#sp-r1", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "power3.out" }}, {L(4.52)});
drawOn("#sp-wc", {L(4.94)}, 0.5);
tl.fromTo("#sp-r2", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.2, ease: "power3.out" }}, {L(5.02)});
tl.fromTo("#sp-stamp", {{ scale: 2.4, opacity: 0, rotation: -14 }}, {{ scale: 1, opacity: 1, rotation: -8, duration: 0.24, ease: "power4.in" }}, {L(5.46)});
drawOn("#sp-ok", {L(6.96)}, 0.3);
tl.fromTo("#sp-r3", {{ clipPath: "inset(-20% 100% -20% 0%)" }}, {{ clipPath: "inset(-20% -4% -20% 0%)", duration: 0.45, ease: "power1.inOut" }}, {L(7.00)});
tl.fromTo("#sp-r4", {{ clipPath: "inset(-20% 100% -20% 0%)" }}, {{ clipPath: "inset(-20% -4% -20% 0%)", duration: 0.45, ease: "power1.inOut" }}, {L(7.80)});
drawOn("#sp-no", {L(8.30)}, 0.28);
tl.fromTo("#sp-laundry", {{ clipPath: "inset(-20% 100% -20% 0%)" }}, {{ clipPath: "inset(-20% -4% -20% 0%)", duration: 0.6, ease: "power1.inOut" }}, {L(10.50)});
tl.to("#sp-card-w", {{ x: -820, rotation: -10, duration: 0.32, ease: "power3.in" }}, {L(ST['s03'] - 0.40)});
boil(["#sp-card-in"], 0.8, 0.2, 5);
"""
write_scene("specs", o, ST["s03"] - o, sp_body, sp_js, sp_css)

# ================================================================ chapters
def chapter(sid, start, end, no, label, items, js_extra=""):
    body = ['<div class="tape" id="%s-tape"></div>' % sid, tag_html(sid, no, label)]
    js = [f'tagIn("#{sid}-tag", 0.12);',
          f'tl.fromTo("#{sid}-tape", {{ opacity: 0, scaleX: 0.3, rotation: -14 }}, {{ opacity: 1, scaleX: 1, rotation: -14, duration: 0.18, ease: "power2.out" }}, 0.42);']
    boils = []
    for it in items:
        body.append(it["html"])
        js.append(it["js"])
        boils += it.get("boil", [])
    if boils:
        js.append(f'boil({json.dumps(boils)}, 1.5, 0.5, {len(sid)});')
    js.append(js_extra)
    d = round(end - start, 3)
    js.append(f'out(["#{sid}-tag", "#{sid}-tape"], {d - 0.24:.3f}, 0.18);')
    write_scene(sid, start, d, "\n".join(body), "\n".join(js))

def D(sid, name, icon, x, y, size, at, dur=0.55, cls="", seed=1):
    did = f"{sid}-{name}"
    return dict(html=doodle(did, icon, x, y, size, cls, seed), js=f'drawOn("#{did}", {at:.3f}, {dur});', boil=[f"#{did}"])

def RD(sid, name, x, y, w, h, ds, at, dur=0.5, cls=""):
    did = f"{sid}-{name}"
    return dict(html=raw_doodle(did, x, y, w, h, ds, cls), js=f'drawOn("#{did}", {at:.3f}, {dur});', boil=[f"#{did}"])

def N(sid, name, text, x, y, at, size="", rot=-2, dur=0.45):
    nid = f"{sid}-{name}"
    return dict(html=note_html(nid, text, x, y, size, rot), js=f'note("#{nid}", {at:.3f}, {dur});')

def ch(sid, seg_from, seg_to_next, no, label, spec):
    s0 = ST[seg_from]
    s1 = ST[seg_to_next] if seg_to_next else VOICE_END
    rel = lambda t_: round(t_ - s0, 3)
    chapter(sid, s0, s1, no, label, spec(sid, rel))

ch("c01", "s03", "s04", "01", "RUANG TAMU", lambda c, r: [
    D(c, "door", "door", 120, 450, 210, r(11.92), 0.5),
    N(c, "n1", "sliding door &#10003;", 130, 690, r(12.40), "", -2, 0.4),
])
ch("c02", "s04", "s06", "02", "MASTER BEDROOM", lambda c, r: [
    D(c, "crown", "crown", 180, 420, 130, r(14.70), 0.4, "acc", 2),
    D(c, "bed", "bed", 120, 480, 250, r(14.82), 0.7),
    N(c, "n1", "muat katil KING", 130, 740, r(15.05)),
    D(c, "wc", "toilet", 120, 880, 140, r(16.86), 0.5, seed=3),
    N(c, "n2", "+ 1 tandas", 290, 940, r(17.05), "sm", 3),
])
ch("c03", "s06", "s08", "03", "BILIK 2", lambda c, r: [
    D(c, "beds", "beds2", 120, 430, 290, r(20.40), 0.7),
    N(c, "n1", "king / queen &#10003;", 130, 730, r(20.70)),
    D(c, "win", "window", 120, 880, 140, r(22.10), 0.5, seed=2),
    N(c, "n2", "+ tingkap", 290, 940, r(22.50), "sm", 3),
])
ch("c04", "s08", "s11", "04", "MAKAN + DAPUR", lambda c, r: [
    N(c, "n1", "ruang makan + dapur", 130, 450, r(24.30), "sm", -3, 0.6),
    D(c, "wc", "toilet", 120, 590, 180, r(25.40), 0.55, seed=1),
    N(c, "n2", "+ 1 tandas lagi", 130, 790, r(25.75)),
])
ch("c05", "s11", "s12", "05", "BILIK 4", lambda c, r: [
    RD(c, "tall", 770, 410, 110, 640, ["M55 20 L55 620", "M25 58 L55 20 L85 58", "M25 582 L55 620 L85 582"], r(27.70), 0.5),
    N(c, "n1", "siling TINGGI", 130, 450, r(27.85), "", -2),
    RD(c, "loft", 120, 590, 620, 120, ["M10 30 L600 30", "M50 30 L50 110 L190 110", "M80 56 L170 56 M80 84 L170 84"], r(28.80), 0.6, "acc"),
    N(c, "n2", "boleh buat loteng", 130, 720, r(29.10), "sm", -2),
    D(c, "bulb", "bulb", 120, 840, 170, r(30.10), 0.6, seed=2),
    N(c, "n3", "siap lampu &#10003;", 310, 920, r(30.55), "sm", 3),
])
ch("c06", "s12", "s14", "06", "DAPUR", lambda c, r: [
    RD(c, "brk", 120, 430, 120, 400, ["M100 10 Q30 10 30 50 L30 180 Q30 200 6 200 Q30 200 30 220 L30 350 Q30 390 100 390"], r(32.10), 0.5, "acc"),
    N(c, "n1", "BACKSPLASH &#10003;", 250, 570, r(32.30), "big"),
    D(c, "cab", "cabinet", 120, 870, 170, r(37.00), 0.6, seed=3),
    N(c, "n2", "pasang kabinet", 310, 940, r(37.30), "sm", 3, 0.5),
])
ch("c07", "s14", "s15", "07", "BILIK 3", lambda c, r: [
    N(c, "n1", "SANGAT LUAS!", 130, 470, r(39.05), "big", -3),
    RD(c, "wide", 120, 640, 660, 130, ["M20 65 L640 65", "M70 25 L20 65 L70 105", "M590 25 L640 65 L590 105"], r(38.96), 0.45, "acc"),
])
ch("c08", "s15", "s16", "08", "RUANG BELAKANG", lambda c, r: [
    D(c, "wm", "washer", 120, 450, 220, r(42.70), 0.7),
    N(c, "n1", "ruang mesin basuh", 130, 700, r(42.95)),
])
ch("c09", "s16", "s17", "09", "TANAH TEPI", lambda c, r: [
    N(c, "n1", "&#177; 8 KAKI", 130, 460, r(45.75), "big", -2),
    RD(c, "dim", 120, 640, 680, 140, ["M20 70 L660 70", "M20 28 L20 112", "M660 28 L660 112", "M66 42 L20 70 L66 98", "M614 42 L660 70 L614 98"], r(45.60), 0.55, "acc"),
])

# ================================================================ END CARD (s17 .. end)
e0 = ST["s17"]
R = lambda t_: round(t_ - e0, 3)
end_css = f"""
#en-harga-w {{ left: 120px; top: 300px; }}
#en-harga {{ background: {MARKER}; padding: 10px 30px 6px; font-family: "Permanent Marker"; font-size: 78px; color: {INK}; white-space: nowrap; box-shadow: 0 8px 20px rgba(0,0,0,0.25); }}
#en-300 {{ left: 120px; top: 420px; font-family: "Archivo Black"; font-size: 150px; line-height: 1; color: {INK}; text-shadow: 8px 8px 0 {MARKER}; white-space: nowrap; letter-spacing: -3px; }}
#en-281 {{ left: 300px; top: 600px; font-family: "Caveat Brush"; font-size: 116px; line-height: 1; color: {TERRA}; white-space: nowrap;
  text-shadow: 0 0 14px rgba(255,255,255,0.95), 0 0 4px #fff; }}
#en-card-w {{ left: 120px; top: 790px; width: 640px; height: 330px; }}
#en-card {{ position: absolute; inset: 0; background: {PAPER}; box-shadow: 0 18px 44px rgba(10,15,35,0.35); }}
#en-card .tape {{ left: 250px; top: -20px; rotate: -4deg; }}
#en-q {{ position: absolute; left: 40px; top: 30px; font-family: "Permanent Marker"; font-size: 74px; color: {INK}; white-space: nowrap; }}
#en-l {{ position: absolute; left: 42px; top: 138px; font-family: "Caveat"; font-weight: 700; font-size: 66px; color: {INK}; white-space: nowrap; }}
#en-chips {{ position: absolute; left: 44px; top: 238px; font-family: "Archivo Black"; font-size: 32px; color: {TERRA}; letter-spacing: 1px; white-space: nowrap; }}
"""
end_body = "\n".join([
    '<div class="abs" id="en-harga-w"><div id="en-harga">HARGA BAWAH</div></div>',
    '<div class="abs" id="en-300">RM300K</div>',
    raw_doodle("en-strike", 110, 430, 660, 120, ["M10 80 Q200 40 360 62 T710 30", "M20 100 Q260 70 420 84 T700 56"], "red"),
    '<div class="abs" id="en-281">RM281K je!</div>',
    raw_doodle("en-circ", 250, 560, 600, 210, ["M70 110 Q40 18 300 16 Q570 12 580 100 Q590 196 310 198 Q60 204 50 120 Q46 84 110 56"], "acc"),
    '<div class="abs" id="en-card-w"><div class="abs" id="en-card-in" style="inset:0"><div id="en-card"><div class="tape"></div></div>'
    '<div id="en-q">BERMINAT?</div><div id="en-l">isi link kat bawah ni</div>'
    '<div id="en-chips">4 BILIK &#183; 2 TANDAS</div></div></div>',
    raw_doodle("en-arrow", 330, 1100, 260, 230, ["M120 10 Q40 70 110 130 Q150 160 130 214", "M86 176 L130 216 L170 172"], "acc"),
])
end_js = f"""
tl.fromTo("#en-harga", {{ scaleX: 0, rotation: -3, transformOrigin: "0% 50%" }}, {{ scaleX: 1, rotation: -3, duration: 0.26, ease: "power3.out" }}, {R(46.92)});
tl.fromTo("#en-300", {{ scale: 1.6, opacity: 0, transformOrigin: "0% 50%" }}, {{ scale: 1, opacity: 1, duration: 0.24, ease: "power4.in" }}, {R(46.96)});
drawOn("#en-strike", {R(47.60)}, 0.35);
tl.fromTo("#en-281", {{ clipPath: "inset(-30% 100% -30% -2%)" }}, {{ clipPath: "inset(-30% -4% -30% -2%)", duration: 0.5, ease: "power1.inOut" }}, {R(47.92)});
drawOn("#en-circ", {R(48.20)}, 0.5);
tl.fromTo("#en-card-w", {{ y: 1300, rotation: 9 }}, {{ y: 0, rotation: -1.5, duration: 0.7, ease: "expo.out" }}, {R(48.42)});
tl.fromTo("#en-l", {{ clipPath: "inset(-30% 100% -30% -2%)" }}, {{ clipPath: "inset(-30% -4% -30% -2%)", duration: 0.7, ease: "power1.inOut" }}, {R(48.75)});
tl.fromTo("#en-chips", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, {R(49.20)});
drawOn("#en-arrow", {R(49.30)}, 0.45);
// two deterministic nudges on the arrow after it lands (no loop)
tl.to("#en-arrow-w", {{ y: 22, duration: 0.22, ease: "power2.out" }}, {R(50.00)});
tl.to("#en-arrow-w", {{ y: 0, duration: 0.3, ease: "power2.inOut" }}, {R(50.22)});
tl.to("#en-arrow-w", {{ y: 22, duration: 0.22, ease: "power2.out" }}, {R(50.70)});
tl.to("#en-arrow-w", {{ y: 0, duration: 0.3, ease: "power2.inOut" }}, {R(50.92)});
boil(["#en-strike", "#en-circ", "#en-arrow"], 1.6, 0.5, 11);
boil(["#en-card-in"], 0.8, 0.2, 4);
"""
write_scene("endcard", e0, TOTAL - e0, end_body, end_js, end_css)

# ================================================================ CAPTIONS
cap_css = f"""
.cap {{ position: absolute; left: 120px; width: 660px; bottom: 684px; text-align: center; opacity: 0; visibility: hidden;
  font-family: "Archivo Black"; font-size: 58px; line-height: 1.14; text-transform: uppercase; color: #fff;
  -webkit-text-stroke: 11px {INK}; paint-order: stroke fill; text-shadow: 0 7px 0 {INK}; letter-spacing: 0.5px; }}
.cap .em {{ display: inline-block; color: {INK}; -webkit-text-stroke: 0; text-shadow: none; background: {MARKER};
  padding: 2px 14px 0; border-radius: 8px 3px 10px 4px; rotate: -2deg; margin: 0 2px; }}
"""
c0 = ST["s02"]
cap_body, cap_js = [], []
for i, (a, b, txt) in enumerate(CAPTIONS):
    cid = f"cap{i:02d}"
    segs = txt.split("*")
    html = "".join((f'<span class="em">{s}</span>' if k % 2 else s) for k, s in enumerate(segs))
    cap_body.append(f'<div class="cap" id="{cid}">{html}</div>')
    la, lb = round(a - c0, 3), round(b - c0, 3)
    cap_js.append(f'tl.set("#{cid}", {{ visibility: "visible" }}, {la});')
    cap_js.append(f'tl.fromTo("#{cid}", {{ opacity: 0, scale: 0.86, y: 16 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.14, ease: "back.out(2)" }}, {la});')
    cap_js.append(f'tl.to("#{cid}", {{ opacity: 0, duration: 0.08, ease: "power2.in" }}, {round(lb - 0.08, 3)});')
    cap_js.append(f'tl.set("#{cid}", {{ opacity: 0, visibility: "hidden" }}, {lb});')
cap_end = CAPTIONS[-1][1] + 0.1
with open(os.path.join(ROOT, "compositions", "captions.html"), "w") as f:
    f.write(f"""<template>
  <style>
#root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
{cap_css}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}" data-duration="{cap_end - c0:.3f}">
{chr(10).join(cap_body)}
  </div>
  <script>
    (function () {{
      var tl = gsap.timeline({{ paused: true }});
{textwrap.indent(chr(10).join(cap_js), '      ')}
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
""")

# ================================================================ TRANSITION OVERLAYS
def torn(n, seed, amp):
    pts = []
    for i in range(n + 1):
        y = i / n * 100
        x = amp * (0.5 + 0.5 * math.sin(i * 12.9898 + seed * 78.233) * math.cos(i * 4.1 + seed))
        pts.append((x, y))
    return pts

left_edge = torn(28, 3, 4.0)
right_edge = torn(28, 9, 4.0)
poly = ", ".join([f"{x:.2f}% {y:.2f}%" for x, y in left_edge] +
                 [f"{100 - x:.2f}% {y:.2f}%" for x, y in reversed(right_edge)])
PAPER_DUR = 0.9
with open(os.path.join(ROOT, "compositions", "wipe-paper.html"), "w") as f:
    f.write(f"""<template>
  <style>
#root {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
#wp-sheet {{ position: absolute; top: -60px; left: 0; width: 1500px; height: 2040px; background: {PAPER};
  clip-path: polygon({poly});
  background-image: repeating-linear-gradient(0deg, transparent 0 78px, rgba(29,43,79,0.10) 78px 80px); }}
#wp-shadow {{ position: absolute; top: -60px; left: 40px; width: 1500px; height: 2040px; background: rgba(10,15,35,0.28);
  clip-path: polygon({poly}); filter: blur(14px); }}
#wp-scrawl {{ position: absolute; left: 470px; top: 820px; width: 560px; height: 260px; overflow: visible; }}
#wp-scrawl path {{ fill: none; stroke: {TERRA}; stroke-width: 16; stroke-linecap: round; stroke-linejoin: round; }}
  </style>
  <div id="root" data-composition-id="wipe-paper" data-width="{W}" data-height="{H}" data-duration="{PAPER_DUR}">
    <div id="wp-shadow"></div>
    <div id="wp-sheet"><svg id="wp-scrawl" viewBox="0 0 560 260"><path d="M20 140 Q160 60 300 130 T540 120 M470 70 L540 120 L470 176"/></svg></div>
  </div>
  <script>
    (function () {{
      var tl = gsap.timeline({{ paused: true }});
      // the sheet fully covers the frame at {PAPER_DUR / 2:.2f}s, where the host cuts beneath it
      tl.fromTo(["#wp-sheet", "#wp-shadow"], {{ x: 1140, rotation: 4 }}, {{ x: -1600, rotation: -3, duration: {PAPER_DUR}, ease: "power2.inOut" }}, 0);
      window.__timelines["wipe-paper"] = tl;
    }})();
  </script>
</template>
""")

SCRIB_DUR = 1.0
bands = 9
band_paths = []
for b in range(bands):
    bh = H / bands
    y0 = b * bh + bh / 2
    d = f"M -100 {y0 + 18 * math.sin(b * 3.1):.1f}"
    for i in range(1, 6):
        x = (W + 200) * i / 5 - 100
        y = y0 + (1 if i % 2 else -1) * bh * 0.30 + 12 * math.sin(b * 7 + i)
        d += f" L {x:.1f} {y:.1f}"
    band_paths.append(f'<path id="ws-b{b}" d="{d}" stroke-width="{bh * 0.95:.0f}"/>')
with open(os.path.join(ROOT, "compositions", "wipe-scribble.html"), "w") as f:
    f.write(f"""<template>
  <style>
#root {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
#ws-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
#ws-svg path {{ fill: none; stroke: {MARKER}; stroke-linecap: round; stroke-linejoin: round; }}
#ws-solid {{ position: absolute; inset: 0; background: {MARKER}; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="wipe-scribble" data-width="{W}" data-height="{H}" data-duration="{SCRIB_DUR}">
    <svg id="ws-svg" viewBox="0 0 {W} {H}">{''.join(band_paths)}</svg>
    <div id="ws-solid"></div>
  </div>
  <script>
    (function () {{
      var tl = gsap.timeline({{ paused: true }});
      var ps = gsap.utils.toArray("#ws-svg path");
      ps.forEach(function (p, i) {{
        var len = p.getTotalLength();
        gsap.set(p, {{ strokeDasharray: len, strokeDashoffset: i % 2 ? -len : len }});
        tl.to(p, {{ strokeDashoffset: 0, duration: 0.3, ease: "power2.in" }}, 0.02 * i);
      }});
      // full cover 0.42-0.56; the host cuts at 0.5
      tl.to("#ws-solid", {{ opacity: 1, duration: 0.06, ease: "none" }}, 0.40);
      tl.to("#ws-solid", {{ opacity: 0, duration: 0.06, ease: "none" }}, 0.56);
      ps.forEach(function (p, i) {{
        var len = p.getTotalLength();
        tl.to(p, {{ strokeDashoffset: i % 2 ? len : -len, duration: 0.32, ease: "power2.out" }}, 0.58 + 0.015 * i);
      }});
      window.__timelines["wipe-scribble"] = tl;
    }})();
  </script>
</template>
""")

# ================================================================ ROOT index.html
lines = []
z = 1
vid = []
for i, s in enumerate(EDL):
    v_in = s.get("v", s["a"][0])
    rate = s.get("rate", 1.0)
    dur = round(s["dur"] + s.get("extra", 0), 3)
    rate_attr = f' data-playback-rate="{rate}"' if rate != 1.0 else ""
    vid.append(f'        <video id="v{i+1:02d}" class="clip" src="assets/footage.mp4" muted playsinline data-start="{s["start"]}" '
               f'data-duration="{dur}" data-media-start="{v_in}"{rate_attr} data-track-index="0"></video>')
VO_FX = {"version": 1, "nodes": [
    {"type": "highpass", "id": "vo1", "label": "Remove rumble", "params": {"frequency": 90}},
    {"type": "peaking", "id": "vo2", "label": "Presence", "params": {"frequency": 3000, "gain": 3, "q": 1}},
    {"type": "limiter", "id": "vo3", "params": {"limit": -1}}]}
MUS_FX = {"version": 1, "nodes": [
    {"type": "peaking", "id": "mu1", "label": "Make room for the voice", "params": {"frequency": 2500, "gain": -5, "q": 0.8}},
    {"type": "peaking", "id": "mu2", "label": "Clear low mids", "params": {"frequency": 300, "gain": -3, "q": 1}}]}
aud = []
for i, s in enumerate(EDL):
    aud.append(f'      <audio id="vo{i+1:02d}" src="assets/voice.wav" data-start="{s["start"]}" data-duration="{s["dur"]}" '
               f'data-media-start="{s["a"][0]}" data-volume="1.45" data-fade-in="0.015" data-fade-out="0.02" '
               f'data-fx-chain="{json.dumps(VO_FX).replace(chr(34), "&quot;")}" data-track-index="10"></audio>')

# music bed: low under the voice, opens up for the tail, fades out
mus_auto = {"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.08}, {"t": VOICE_END - 0.1, "v": 0.08}, {"t": VOICE_END + 0.35, "v": 0.36},
    {"t": TOTAL - 1.0, "v": 0.36}, {"t": TOTAL, "v": 0.0}]}]}
music = (f'      <audio id="music" src="assets/music/bed-hiphop97.mp3" data-start="0" data-duration="{TOTAL}" data-media-start="0.055" '
         f'data-volume="1" data-automation="{json.dumps(mus_auto).replace(chr(34), "&quot;")}" '
         f'data-fx-chain="{json.dumps(MUS_FX).replace(chr(34), "&quot;")}" data-track-index="11"></audio>')

# sfx lanes: greedy, one lane until clips overlap
sfx_lines = []
lanes_end = []
durs = {}
import subprocess
for s_ in SFX:
    n = s_["name"]
    if n not in durs:
        out_ = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                               os.path.join(ROOT, "assets", "sfx", n + ".mp3")], capture_output=True, text=True).stdout
        durs[n] = float(out_.strip())
for s_ in SFX:
    s_["vol"] = round(s_["vol"] * 0.45, 3)
for k, s_ in enumerate(sorted(SFX, key=lambda d: d["at"])):
    d = round(min(durs[s_["name"]] - s_["ms"], TOTAL - s_["at"]), 3)
    lane = next((li for li, e in enumerate(lanes_end) if e <= s_["at"]), None)
    if lane is None:
        lanes_end.append(0)
        lane = len(lanes_end) - 1
    lanes_end[lane] = s_["at"] + d
    ms = f' data-media-start="{s_["ms"]}"' if s_["ms"] else ""
    sfx_lines.append(f'      <audio id="fx{k:02d}" src="assets/sfx/{s_["name"]}.mp3" data-start="{s_["at"]}" data-duration="{d}"{ms} '
                     f'data-volume="{s_["vol"]}" data-track-index="{20 + lane}"></audio>')

hosts = []
for sid, st, du in SCENES:
    hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st}" '
                 f'data-duration="{du}" data-width="{W}" data-height="{H}" data-track-index="2" data-track-kind="graphics" style="z-index:5"></div>')
hosts.append(f'      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="{c0}" '
             f'data-duration="{round(cap_end - c0, 3)}" data-width="{W}" data-height="{H}" data-track-index="3" data-track-kind="captions" style="z-index:6"></div>')
for k, t_ in enumerate(PAPER_WIPES):
    hosts.append(f'      <div id="wipe-paper-{k+1}" data-composition-id="wipe-paper" data-composition-src="compositions/wipe-paper.html" '
                 f'data-start="{round(t_ - PAPER_DUR / 2, 3)}" data-duration="{PAPER_DUR}" data-width="{W}" data-height="{H}" data-track-index="4" data-track-kind="graphics" style="z-index:8"></div>')
for k, t_ in enumerate(SCRIBBLE_WIPES):
    hosts.append(f'      <div id="wipe-scribble-{k+1}" data-composition-id="wipe-scribble" data-composition-src="compositions/wipe-scribble.html" '
                 f'data-start="{round(t_ - 0.5, 3)}" data-duration="{SCRIB_DUR}" data-width="{W}" data-height="{H}" data-track-index="4" data-track-kind="graphics" style="z-index:8"></div>')

cam_js = []
for kind, t_ in CAM:
    if kind == "zoom":
        cam_js.append(f'tl.fromTo("#cam", {{ scale: 1, x: 0 }}, {{ scale: 1.32, duration: 0.26, ease: "power3.in", immediateRender: false }}, {t_ - 0.26:.3f});')
        cam_js.append(f'tl.fromTo("#cam", {{ scale: 1.4, x: 0 }}, {{ scale: 1, duration: 0.42, ease: "expo.out", immediateRender: false }}, {t_:.3f});')
    elif kind == "whip":
        cam_js.append(f'tl.fromTo("#cam", {{ x: 0, scale: 1 }}, {{ x: -220, scale: 1.45, duration: 0.16, ease: "power2.in", immediateRender: false }}, {t_ - 0.16:.3f});')
        cam_js.append(f'tl.fromTo("#cam", {{ x: 220, scale: 1.45 }}, {{ x: 0, scale: 1, duration: 0.3, ease: "power3.out", immediateRender: false }}, {t_:.3f});')
    elif kind == "punch":
        cam_js.append(f'tl.set("#cam", {{ scale: 1.12, x: 0 }}, {t_:.3f});')
    elif kind == "reset":
        cam_js.append(f'tl.set("#cam", {{ scale: 1, x: 0 }}, {t_:.3f});')

index = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0e1222; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 45%; z-index: 1; }}
      #cam video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}" data-fps="30" data-motion-blur="on">
      <div id="cam">
{chr(10).join(vid)}
      </div>
{chr(10).join(hosts)}
{chr(10).join(aud)}
{music}
{chr(10).join(sfx_lines)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      gsap.set("#cam", {{ scale: 1, x: 0 }});
{textwrap.indent(chr(10).join(cam_js), '      ')}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
with open(os.path.join(ROOT, "index.html"), "w") as f:
    f.write(index)
print("voice end", VOICE_END, "total", TOTAL, "scenes", len(SCENES), "sfx", len(SFX))
