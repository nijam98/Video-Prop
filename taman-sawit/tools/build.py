#!/usr/bin/env python3
"""Generates index.html + compositions/*.html for the Taman Impian Mesra (Gurun) teres reel.

Look: "Berus Dakwat & Cop" (ink brush & chop seal) — dry-brush ink strokes with bristle streaks,
vermilion chop seals that slam in with ink speckle, ink splatter, hand-drawn enso circles and
arrows, rice-paper caption strips, ink-swipe transitions and a rice-paper grain over the frame.
Type: Knewave (brush lettering), Mansalva (hand notes), Barlow Condensed 800 (captions, seals).

Edit the tables below (EDL, captions, SFX) and re-run:
    python3 tools/build.py
"""
import json, math, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
TAIL = 3.5  # after the last word: 0.45 s to let the booking seals land, then the end card

# ---------------------------------------------------------------- palette
INK, RED, RICE, GOLD = "#17130F", "#D8321F", "#F4ECDD", "#E9A93A"

# ---------------------------------------------------------------- edit decision list
# a = source seconds of speech kept; v = [(offset inside segment, source in-point)] for the picture.
# One hand-held walk around the site, so the picture is taken from steady stretches of the clip;
# the half-second the camera passes the house columns is used as a freeze frame (assets/columns.jpg).
EDL = [
    dict(id="s1", a=(8.47, 11.25), v=[(0, 2.30)]),     # HOOK  teres paling murah, harga bermula RM228K
    dict(id="s2", a=(27.00, 28.22), v=[(0, 3.40)]),    # bulanan sangat murah                (moved up)
    dict(id="s3", a=(28.38, 30.52), v=[(0, 0.05)]),    # dekat dengan Taman Impian Mesra, Gurun (moved up)
    dict(id="s4", a=(5.665, 7.56), v=[(0, 9.20)]),      # sebelah sini kita ada semi-D        ("ok" cut)
    dict(id="s5", a=(11.53, 12.92), v=[(0, 11.30)]),   # unit sangat terhad
    dict(id="s6", a=(13.25, 16.00), v=[(0, 12.80)]),   # non-bumi lot available, bumi lot pun available lagi
    dict(id="s7", a=(16.36, 20.53), v=[(0, 15.60), (1.99, "columns")]),  # isi sahaja, siapa cepat dia dapat, sebab projek tengah berjalan
    dict(id="s8", a=(21.05, 23.55), v=[(0, 21.00)], extra=TAIL),          # and then unit pun sangat laju, orang dah booking
]
# removed: "ok nampak depan tu, depan ni ada satu lagi" (no picture to point at), "ok" + "and then depan ni",
# 2nd "harga RM228" (repeat), "macam biasa ... isi sahaja" (repeat of the CTA, unclear), "bye bye",
# and every pause (0.33 s before "non-bumi", 0.36 s before "yang penting", 0.52 s after "berjalan").
t = 0.0
for s in EDL:
    s["start"] = round(t, 3)
    s["dur"] = round(s["a"][1] - s["a"][0], 3)
    t += s["dur"]
VOICE_END = round(t, 3)
TOTAL = round(VOICE_END + TAIL, 3)
ST = {s["id"]: s["start"] for s in EDL}


def o(seg, src):
    """source second -> output second inside segment `seg`"""
    s = next(x for x in EDL if x["id"] == seg)
    return round(s["start"] + (src - s["a"][0]), 3)


# ---------------------------------------------------------------- captions (word level, source times)
# (segment, [(word, src_start, key?)...], src_end). The hook has no captions: its graphics carry every word.
CAPS = [
    ("s2", [("Bulanan", 27.02), ("sangat", 27.58), ("murah", 27.82, 1)], 28.16),
    ("s3", [("Dekat", 28.40), ("dengan", 28.72)], 28.84),
    ("s3", [("Taman", 28.84, 1), ("Impian", 29.38, 1), ("Mesra,", 29.70, 1)], 30.02),
    ("s3", [("Gurun", 30.02, 1)], 30.46),
    ("s4", [("Sebelah", 5.64), ("sini", 5.98)], 6.08),
    ("s4", [("kita", 6.08), ("ada", 6.40), ("semi-D", 6.70, 1)], 7.30),
    ("s5", [("Unit", 11.55), ("sangat", 11.85), ("terhad", 12.31, 1)], 12.71),
    ("s6", [("Non-bumi", 13.29, 1), ("lot", 13.69), ("available", 13.79)], 14.30),
    ("s6", [("Bumi", 14.35, 1), ("lot", 14.81), ("pun", 14.97)], 15.13),
    ("s6", [("available", 15.13), ("lagi", 15.31)], 15.75),
    ("s7", [("Yang", 16.36), ("penting", 16.46)], 16.88),
    ("s7", [("isi", 16.88, 1), ("sahaja", 17.16)], 17.44),
    ("s7", [("siapa", 17.44), ("cepat", 17.76, 1)], 18.08),
    ("s7", [("dia", 18.08), ("dapat", 18.16, 1)], 18.33),
    ("s7", [("Sebab", 18.35), ("projek", 18.55, 1)], 19.21),
    ("s7", [("tengah", 19.21), ("berjalan", 19.77, 1)], 20.33),
    ("s8", [("And", 21.05), ("then", 21.17), ("unit", 21.37), ("pun", 21.71)], 21.91),
    ("s8", [("sangat", 21.91), ("laju", 22.17, 1)], 22.71),
    ("s8", [("orang", 22.71), ("dah", 22.85), ("booking", 23.01, 1)], 23.30),
]

# ---------------------------------------------------------------- key beats (output seconds)
B = dict(
    paling=o("s1", 8.80), murah=o("s1", 8.98), harga=o("s1", 9.28), bermula=o("s1", 9.78), rm=o("s1", 10.12),
    bulanan=o("s2", 27.02), sangat=o("s2", 27.58), murah2=o("s2", 27.82),
    dekat=o("s3", 28.40), taman=o("s3", 28.84), mesra=o("s3", 29.70), gurun=o("s3", 30.02),
    sebelah=o("s4", 5.64), semid=o("s4", 6.70),
    unit=o("s5", 11.55), terhad=o("s5", 12.31),
    nonbumi=o("s6", 13.29), av1=o("s6", 13.79), bumi=o("s6", 14.35), av2=o("s6", 15.13),
    yang=o("s7", 16.36), isi=o("s7", 16.88), siapa=o("s7", 17.44), dapat=o("s7", 18.16),
    sebab=o("s7", 18.35), tengah=o("s7", 19.21), berjalan=o("s7", 19.77),
    unit2=o("s8", 21.37), laju=o("s8", 22.17), orang=o("s8", 22.71), booking=o("s8", 23.01),
)
COLS = round(ST["s7"] + 1.99, 3)  # columns freeze frame starts ("sebab projek...")
# scene windows: (cid, start, end)
SC = dict(hook=(0, ST["s2"]), bulanan=(ST["s2"], ST["s3"]), lokasi=(ST["s3"], ST["s4"]), semid=(ST["s4"], ST["s5"]),
          lot=(ST["s5"], ST["s7"]), isi=(ST["s7"], COLS), projek=(COLS, ST["s8"]), laju=(ST["s8"], VOICE_END + 0.45),
          cta=(VOICE_END + 0.45, TOTAL))
CTA = SC["cta"][0]
SWIPES = [ST["s3"], ST["s5"], CTA]  # ink-swipe transitions centred on these cuts


# ---------------------------------------------------------------- sound effects (output time, file, volume, media_start, dur)
# every file is pre-normalised to -20 LUFS (voice sits at -15), so 0.15-0.45 keeps them under the voice
def fx(at, name, vol=0.3, ms=0.0, dur=None):
    return dict(at=round(at, 3), name=name, vol=vol, ms=ms, dur=dur)


SFX = [
    # hook: drum hit on frame 0, brush strokes paint the title, photo brushed in, price seal slams
    fx(0.00, "stamp-drum", 0.40),
    fx(0.02, "brush-swish", 0.30),
    fx(B["paling"] - 0.04, "stamp-wood", 0.42),
    fx(0.30, "brush-sweep", 0.20),
    fx(B["harga"] + 0.05, "brush-slice", 0.30),
    fx(B["rm"] - 0.06, "stamp-dry", 0.50),
    fx(B["rm"] - 0.04, "bass-hit", 0.30),
    fx(B["rm"] + 0.08, "ink-drop", 0.30),
    # bulanan
    fx(ST["s2"] - 0.10, "sweep-small", 0.26),
    fx(B["bulanan"] + 0.05, "scribble", 0.22, 0.0, 0.6),
    fx(B["murah2"] - 0.06, "stamp-wood", 0.42),
    fx(B["murah2"] + 0.04, "ink-drop", 0.26),
    # ink swipe -> lokasi
    fx(ST["s3"] - 0.24, "whoosh-fast", 0.26),
    fx(B["dekat"] + 0.10, "sign", 0.22, 0.0, 1.0),
    fx(B["taman"] + 0.05, "brush-slice", 0.24),
    fx(B["gurun"] - 0.16, "brush-swish", 0.18),
    fx(B["gurun"] - 0.04, "stamp-drum", 0.36),
    fx(B["gurun"] + 0.12, "chime", 0.14),
    # semi-D: photo slides in, enso painted round the semi-D units
    fx(ST["s4"] - 0.04, "paper-slide", 0.34),
    fx(B["sebelah"] + 0.10, "brush-sweep", 0.20),
    fx(B["semid"] - 0.20, "brush-swish", 0.30),
    fx(B["semid"] + 0.02, "pop-dry", 0.40),
    # ink swipe -> unit terhad + lots
    fx(ST["s5"] - 0.24, "whoosh-fast", 0.26),
    fx(B["terhad"] - 0.07, "stamp-drum", 0.45),
    fx(B["terhad"] - 0.05, "bass-hit", 0.30),
    fx(B["terhad"] + 0.06, "ink-splash", 0.16, 0.0, 0.8),
    fx(B["nonbumi"] - 0.04, "paper-move", 0.30),
    fx(B["av1"] + 0.05, "brush-slice", 0.32),
    fx(B["bumi"] - 0.04, "paper-move", 0.30),
    fx(B["av2"] + 0.05, "brush-slice", 0.32),
    fx(B["av2"] + 0.20, "chime", 0.14),
    # isi sahaja / siapa cepat
    fx(ST["s7"] - 0.08, "sweep-small", 0.26),
    fx(B["isi"] - 0.02, "scribble", 0.26, 0.0, 0.7),
    fx(B["siapa"] - 0.05, "whoosh-fast", 0.20),
    fx(B["dapat"] - 0.04, "stamp-wood", 0.42),
    # columns freeze: crane + progress bar painted
    fx(COLS - 0.12, "brush-sweep", 0.26),
    fx(COLS + 0.25, "sign", 0.20, 0.0, 0.9),
    fx(B["tengah"] + 0.05, "brush-swish", 0.24),
    fx(B["berjalan"] - 0.02, "pop-hard", 0.24),
    # laju + booking seals
    fx(ST["s8"] - 0.08, "sweep-small", 0.24),
    fx(B["laju"] - 0.12, "whoosh-fast", 0.24),
    fx(B["booking"] - 0.10, "stamp-dry", 0.40),
    fx(B["booking"] + 0.04, "stamp-dry", 0.36),
    fx(B["booking"] + 0.18, "stamp-dry", 0.36),
    fx(B["booking"] + 0.32, "stamp-wood", 0.40),
    # ink swipe -> end card
    fx(CTA - 0.24, "whoosh-fast", 0.26),
    fx(CTA + 0.12, "brush-sweep", 0.22),
    fx(CTA + 0.55, "stamp-drum", 0.36),
    fx(CTA + 0.95, "pop-dry", 0.34),
    fx(CTA + 1.10, "pop-dry", 0.30),
    fx(CTA + 1.25, "pop-dry", 0.30),
    fx(CTA + 1.45, "chime", 0.18),
]


# ---------------------------------------------------------------- camera moves on #cam
def cam_js():
    s = ST
    j = []
    a = j.append
    a(f'tl.fromTo("#cam", {{ scale: 1.0, x: 0 }}, {{ scale: 1.06, duration: {s["s2"] - 0.14:.3f}, ease: "none", immediateRender: false }}, 0);')
    # whip -> bulanan
    a(f'tl.to("#cam", {{ x: -160, scale: 1.24, duration: 0.14, ease: "power2.in" }}, {s["s2"] - 0.14:.3f});')
    a(f'tl.fromTo("#cam", {{ x: 160, scale: 1.24 }}, {{ x: 0, scale: 1.03, duration: 0.34, ease: "power3.out", immediateRender: false }}, {s["s2"]:.3f});')
    # lokasi (ink swipe covers the cut)
    a(f'tl.fromTo("#cam", {{ scale: 1.14, x: 0 }}, {{ scale: 1.02, duration: 2.0, ease: "power2.out", immediateRender: false }}, {s["s3"]:.3f});')
    # semi-D: punch
    a(f'tl.fromTo("#cam", {{ scale: 1.18, x: 0 }}, {{ scale: 1.04, duration: 0.45, ease: "expo.out", immediateRender: false }}, {s["s4"]:.3f});')
    a(f'tl.to("#cam", {{ scale: 1.08, duration: {s["s5"] - s["s4"] - 0.45:.3f}, ease: "none" }}, {s["s4"] + 0.45:.3f});')
    # lot (ink swipe)
    a(f'tl.fromTo("#cam", {{ scale: 1.1, x: 0 }}, {{ scale: 1.02, duration: 1.2, ease: "power2.out", immediateRender: false }}, {s["s5"]:.3f});')
    a(f'tl.fromTo("#cam", {{ scale: 1.16 }}, {{ scale: 1.04, duration: 0.4, ease: "expo.out", immediateRender: false }}, {s["s6"]:.3f});')
    a(f'tl.to("#cam", {{ scale: 1.1, duration: {s["s7"] - s["s6"] - 0.54:.3f}, ease: "none" }}, {s["s6"] + 0.4:.3f});')
    # isi: whip
    a(f'tl.to("#cam", {{ x: 160, scale: 1.24, duration: 0.14, ease: "power2.in" }}, {s["s7"] - 0.14:.3f});')
    a(f'tl.fromTo("#cam", {{ x: -160, scale: 1.24 }}, {{ x: 0, scale: 1.03, duration: 0.34, ease: "power3.out", immediateRender: false }}, {s["s7"]:.3f});')
    # columns freeze: zoom-through, then a slow push
    a(f'tl.to("#cam", {{ scale: 1.4, duration: 0.14, ease: "power3.in" }}, {COLS - 0.14:.3f});')
    a(f'tl.fromTo("#cam", {{ scale: 1.32, x: 0 }}, {{ scale: 1.0, duration: 0.5, ease: "expo.out", immediateRender: false }}, {COLS:.3f});')
    a(f'tl.fromTo("#colimg", {{ scale: 1.0 }}, {{ scale: 1.12, duration: {s["s8"] - COLS:.3f}, ease: "none", immediateRender: false }}, {COLS:.3f});')
    # laju: whip
    a(f'tl.fromTo("#cam", {{ x: -160, scale: 1.24 }}, {{ x: 0, scale: 1.03, duration: 0.34, ease: "power3.out", immediateRender: false }}, {s["s8"]:.3f});')
    a(f'tl.to("#cam", {{ scale: 1.09, duration: {CTA - s["s8"] - 0.34:.3f}, ease: "none" }}, {s["s8"] + 0.34:.3f});')
    # end card
    a(f'tl.fromTo("#cam", {{ scale: 1.16, x: 0 }}, {{ scale: 1.0, duration: {TOTAL - CTA:.3f}, ease: "power2.out", immediateRender: false }}, {CTA:.3f});')
    return "\n      ".join(j)


# ================================================================ shared building blocks
FONTS = """
@font-face { font-family: "Knewave"; src: url("assets/fonts/knewave.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Mansalva"; src: url("assets/fonts/mansalva.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Barlow Condensed"; font-weight: 800; src: url("assets/fonts/barlow-condensed.woff2") format("woff2"); font-display: block; }
"""

BASE_CSS = f"""
#root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
.abs {{ position: absolute; }}
.b {{ position: relative; }}
svg.dd {{ position: absolute; overflow: visible; }}
svg.dd .br {{ fill: none; stroke-linecap: round; stroke-linejoin: round; }}
.kb {{ font-family: "Knewave"; color: {RICE}; white-space: nowrap; line-height: 1; letter-spacing: 1px; }}
.mh {{ font-family: "Mansalva"; color: {INK}; white-space: nowrap; line-height: 1;
  text-shadow: 0 0 10px rgba(244,236,221,0.95), 0 0 22px rgba(244,236,221,0.7); }}
.bx {{ font-family: "Barlow Condensed"; font-weight: 800; text-transform: uppercase; white-space: nowrap; line-height: 0.92; letter-spacing: 1px; }}
.bntx {{ position: absolute; left: 0; right: 0; text-align: center; }}
.sealtx {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;
  font-family: "Barlow Condensed"; font-weight: 800; color: {RICE}; text-transform: uppercase; line-height: 0.9; letter-spacing: 2px; text-align: center; }}
"""


def defs(p):
    """ink filters, prefixed per composition so every comp is self-contained"""
    return f"""<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<filter id="{p}-br" x="-20%" y="-30%" width="140%" height="160%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="3" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="16" xChannelSelector="R" yChannelSelector="G" result="rag"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.004 0.32" numOctaves="2" seed="11" result="streak"/>
  <feColorMatrix in="streak" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3.2 2.65" result="mask"/>
  <feComposite in="rag" in2="mask" operator="in"/>
</filter>
<filter id="{p}-st" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="5" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="5" xChannelSelector="R" yChannelSelector="G" result="rag"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="21" result="speck"/>
  <feColorMatrix in="speck" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -7 4.6" result="mask"/>
  <feComposite in="rag" in2="mask" operator="in"/>
</filter>
<filter id="{p}-mk" x="-20%" y="-30%" width="140%" height="160%">
  <feTurbulence type="fractalNoise" baseFrequency="0.025" numOctaves="2" seed="4" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="28" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="{p}-rf" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.06" numOctaves="2" seed="8" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="4" xChannelSelector="R" yChannelSelector="G"/>
</filter>
</defs></svg>"""


COMMON_JS = r"""
      var tl = gsap.timeline({ paused: true });
      // Remotion-style spring (mass 1): z = damping ratio, w = natural freq, T = seconds the tween spans
      function spring(z, w, T) {
        var wd = w * Math.sqrt(1 - z * z), a = z * w;
        return function (p) { if (p >= 1) return 1; var t = p * T;
          return 1 - Math.exp(-a * t) * (Math.cos(wd * t) + (a / wd) * Math.sin(wd * t)); };
      }
      var SPR = spring(0.45, 14, 0.9), SOFT = spring(0.75, 13, 0.7);
      function hh(n, s) { var x = Math.sin(n * 127.1 + (s || 1) * 311.7) * 43758.5453; return (x - Math.floor(x)) * 2 - 1; }
      var renders = [];
      // hand-painted "boil": the drawn layers re-jitter 6 times a second, like re-inked frames
      function boil(sel, amp, rot, seed) {
        var els = gsap.utils.toArray(sel);
        renders.push(function () {
          var st = Math.floor(tl.time() * 6);
          els.forEach(function (e, i) {
            gsap.set(e, { x: hh(st * 3 + i * 97, seed) * amp, y: hh(st * 3 + 1 + i * 97, seed) * amp,
                          rotation: hh(st * 3 + 2 + i * 97, seed) * rot });
          });
        });
      }
      function finish(id) {
        tl.eventCallback("onUpdate", function () { for (var i = 0; i < renders.length; i++) renders[i](); });
        for (var i = 0; i < renders.length; i++) renders[i]();
        window.__timelines[id] = tl;
      }
      // brush draw-on; strokes sharing data-i paint together, later data-i follow
      function draw(sel, at, dur, ease) {
        var ps = gsap.utils.toArray(sel + " .br");
        var n = 0; ps.forEach(function (p) { n = Math.max(n, +(p.getAttribute("data-i") || 0) + 1); });
        var seg = dur / Math.max(1, n * 0.75 + 0.25);
        ps.forEach(function (p) {
          var i = +(p.getAttribute("data-i") || 0), len = p.getTotalLength() + 6;
          gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len, opacity: 0 });
          tl.set(p, { opacity: 1 }, at + i * seg * 0.75);
          tl.to(p, { strokeDashoffset: 0, duration: seg, ease: ease || "power2.out" }, at + i * seg * 0.75);
        });
      }
      // text revealed left -> right, like a brush pass
      function write(sel, at, dur) {
        tl.fromTo(sel, { clipPath: "inset(-40% 104% -40% -6%)", opacity: 1 },
          { clipPath: "inset(-40% -6% -40% -6%)", duration: dur || 0.4, ease: "power2.out", immediateRender: true }, at);
        tl.set(sel, { clipPath: "none" }, at + (dur || 0.4) + 0.01);
      }
      // chop seal slam: drops from above the paper, lands hard, settles with a squash
      function slam(sel, at, r, s0) {
        tl.fromTo(sel, { scale: s0 || 2.3, opacity: 0, rotation: (r || 0) - 9 },
          { scale: 0.94, opacity: 1, rotation: r || 0, duration: 0.13, ease: "power3.in", immediateRender: true }, at);
        tl.to(sel, { scale: 1, duration: 0.3, ease: spring(0.4, 22, 0.3) }, at + 0.13);
      }
      function pop(sel, at, opt) {
        opt = opt || {};
        tl.fromTo(sel, { scale: opt.from == null ? 0.2 : opt.from, opacity: 0, rotation: opt.r0 || 0, y: opt.y0 || 0, x: opt.x0 || 0 },
          { scale: 1, opacity: 1, rotation: opt.r || 0, y: 0, x: 0, duration: opt.d || 0.8, ease: opt.ease || SPR, immediateRender: true }, at);
      }
      // ink splatter: drops burst out from the seal centre
      function splat(sel, at) {
        gsap.utils.toArray(sel + " .sp").forEach(function (d, i) {
          tl.fromTo(d, { scale: 0, opacity: 1, x: -(+d.getAttribute("data-dx")) * 0.6, y: -(+d.getAttribute("data-dy")) * 0.6 },
            { scale: 1, x: 0, y: 0, duration: 0.22 + (i % 3) * 0.05, ease: "expo.out", immediateRender: true, transformOrigin: "50% 50%" }, at + (i % 4) * 0.012);
        });
      }
      function out(sel, at, d) { tl.to(sel, { opacity: 0, scale: 0.9, duration: d || 0.16, ease: "power2.in" }, at); }
"""


def hsh(n, seed):
    x = math.sin(n * 127.1 + seed * 311.7) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def jit(pts, seed, amp=2.5):
    """jitter a polyline for a hand-painted wobble -> smooth path string"""
    q = [(x + hsh(i * 2, seed) * amp, y + hsh(i * 2 + 1, seed) * amp) for i, (x, y) in enumerate(pts)]
    d = f"M{q[0][0]:.1f} {q[0][1]:.1f}"
    for i in range(1, len(q) - 1):
        mx, my = (q[i][0] + q[i + 1][0]) / 2, (q[i][1] + q[i + 1][1]) / 2
        d += f" Q{q[i][0]:.1f} {q[i][1]:.1f} {mx:.1f} {my:.1f}"
    d += f" L{q[-1][0]:.1f} {q[-1][1]:.1f}"
    return d


def enso_d(cx, cy, rx, ry, seed, a0=-110, a1=232, amp=4):
    """open brush circle (enso): starts at a0, overshoots past the start, leaves a gap"""
    pts = []
    n = 22
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        wob = 1 + hsh(k, seed) * 0.025
        pts.append((cx + rx * wob * math.cos(a), cy + ry * wob * math.sin(a)))
    return jit(pts, seed, amp)


def wrap(id_, left, top, w, h, inner, extra_style=""):
    return (f'<div class="abs" id="{id_}" style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;{extra_style}">'
            f'<div class="b" style="width:{w}px;height:{h}px">{inner}</div></div>')


def strokes(p, vw, vh, paths, color=INK, sw=10, extra="", flt="br"):
    """brush svg: paths = [(d, data-i, color?, width?, opacity?)]"""
    body = ""
    for item in paths:
        d, i = item[0], item[1]
        c = item[2] if len(item) > 2 and item[2] else color
        ww = item[3] if len(item) > 3 else sw
        op = item[4] if len(item) > 4 else 1
        body += f'<path class="br" data-i="{i}" d="{d}" stroke="{c}" stroke-width="{ww}" opacity="{op}"/>'
    return (f'<svg class="dd" viewBox="0 0 {vw} {vh}" style="left:0;top:0;width:{vw}px;height:{vh}px;filter:url(#{p}-{flt})">'
            f'{extra}{body}</svg>')


def banner(p, id_, left, top, w, h, text, size, seed, color=INK, tcolor=RICE, rot=0, font="kb", ty=None):
    """ink brush banner: one fat dry-brush stroke + a thinner pass, lettering on top"""
    r = h / 2
    main = jit([(r * 0.7, r + 2), (w * 0.35, r - 4), (w * 0.7, r + 3), (w - r * 0.7, r - 2)], seed, 3)
    second = jit([(r * 0.9, r + h * 0.22), (w * 0.5, r + h * 0.18), (w - r * 0.5, r + h * 0.24)], seed + 1, 3)
    svg = strokes(p, w, h, [(main, 0, color, h * 0.84), (second, 0, color, h * 0.42, 0.85)])
    ty = (h - size) / 2 + size * 0.06 if ty is None else ty
    return wrap(id_, left, top, w, h, svg + f'<div class="bntx {font}" style="top:{ty:.0f}px;font-size:{size}px;color:{tcolor}">{text}</div>',
                f"rotate:{rot}deg")


def seal(p, id_, left, top, w, h, lines, size, rot=0, color=RED, tcolor=RICE, splats=True, seed=1, ls=2):
    """vermilion chop seal: rough rect, carved inner border, speckled ink; optional splatter around it"""
    sp = ""
    if splats:
        for k in range(9):
            a = math.radians(k * 40 + hsh(k, seed) * 18)
            dist = 0.62 + abs(hsh(k + 9, seed)) * 0.25
            sx = w / 2 + math.cos(a) * w * dist
            sy = h / 2 + math.sin(a) * h * dist * 1.1
            rr = 4 + abs(hsh(k + 3, seed)) * 9
            sp += (f'<svg class="dd sp" data-dx="{sx - w / 2:.0f}" data-dy="{sy - h / 2:.0f}" viewBox="0 0 40 40" '
                   f'style="left:{sx - 20:.0f}px;top:{sy - 20:.0f}px;width:40px;height:40px;filter:url(#{p}-rf)">'
                   f'<circle cx="20" cy="20" r="{rr:.1f}" fill="{color}"/></svg>')
    body = (f'<div class="b" style="width:{w}px;height:{h}px;filter:url(#{p}-st)">'
            f'<svg class="dd" viewBox="0 0 {w} {h}" style="left:0;top:0;width:{w}px;height:{h}px">'
            f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" rx="12" fill="{color}"/>'
            f'<rect x="13" y="13" width="{w - 26}" height="{h - 26}" rx="7" fill="none" stroke="{tcolor}" stroke-width="5"/></svg>'
            f'<div class="sealtx" style="font-size:{size}px;color:{tcolor};letter-spacing:{ls}px">{lines}</div></div>')
    return (f'<div class="abs" id="{id_}" style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;rotate:{rot}deg">'
            f'{sp}{body}</div>')


def photo_card(p, id_, left, top, w, h, seed, enso=None, img="assets/photo.jpg"):
    """the drone photo, painted in by a brush mask, with an ink frame drawn round it"""
    mx = [(-40, h * 0.18), (w * 0.5, h * 0.10), (w + 40, h * 0.2), (w + 40, h * 0.5), (-40, h * 0.52),
          (-40, h * 0.82), (w * 0.5, h * 0.9), (w + 40, h * 0.86)]
    mask = jit(mx, seed, 10)
    fr = jit([(6, 8), (w * 0.5, 4), (w - 6, 9), (w - 4, h * 0.5), (w - 8, h - 6), (w * 0.5, h - 3), (8, h - 8), (4, h * 0.5), (8, 10)], seed + 1, 3)
    out = (f'<svg class="dd" viewBox="0 0 {w} {h}" style="left:0;top:0;width:{w}px;height:{h}px">'
           f'<defs><mask id="{id_}-m" maskUnits="userSpaceOnUse" x="-60" y="-60" width="{w + 120}" height="{h + 120}">'
           f'<g style="filter:url(#{p}-mk)"><path class="br mk" data-i="0" d="{mask}" stroke="#fff" stroke-width="{h * 0.46:.0f}"/></g></mask></defs>'
           f'<g mask="url(#{id_}-m)"><image class="ph" href="{img}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/></g></svg>'
           + f'<div class="fr">{strokes(p, w, h, [(fr, 0, INK, 9)])}</div>')
    if enso:
        cx, cy, rx, ry, es = enso
        out += f'<div class="en">' + strokes(p, w, h, [(enso_d(cx, cy, rx, ry, es), 0, RED, 14), (enso_d(cx, cy, rx * 1.03, ry * 1.04, es + 1, -100, 210, 5), 0, RED, 6, 0.8)]) + '</div>'
    return wrap(id_, left, top, w, h, out)


def comp(cid, dur, css, body, js, p):
    return f"""<template>
  <style>
{FONTS}
{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-duration="{dur:.3f}">
{defs(p)}
{body}
  </div>
  <script>
    (function () {{
{COMMON_JS}
{js}
      finish("{cid}");
    }})();
  </script>
</template>
"""


SCENES = []  # (cid, start, dur, html)


def scene(cid):
    s, e = SC[cid]
    return s, round(e - s, 3), (lambda x: round(x - s, 3))


# ================================================================ scenes
def scene_hook():
    p = "hk"
    s, d, rel = scene("hook")
    css = f"""
#hk-note {{ font-size: 50px; rotate: -4deg; }}
#hk-pricelb {{ font-size: 38px; letter-spacing: 6px; }}
#hk-price {{ font-family: "Knewave"; font-size: 86px; letter-spacing: 0; line-height: 1; margin-top: 2px; }}
"""
    body = (
        banner(p, "hk-teres", 104, 292, 470, 150, "TERES", 112, 3, rot=-2)
        + seal(p, "hk-murah", 604, 290, 246, 192, "PALING<br>MURAH", 74, rot=5, seed=2)
        + photo_card(p, "hk-photo", 132, 500, 716, 360, 5, enso=(372, 172, 205, 150, 6))
        + '<div class="abs mh" id="hk-note" style="left:124px;top:904px">harga bermula</div>'
        + seal(p, "hk-rm", 446, 872, 334, 150, '<span id="hk-pricelb">dari</span><span id="hk-price">RM228K</span>', 40, rot=-4, seed=4, ls=0)
    )
    js = f"""
      // frame 0 already reads as the thumbnail: title + seal are on screen, the photo paints in
      tl.fromTo("#hk-teres", {{ scale: 1.12, transformOrigin: "20% 60%" }}, {{ scale: 1, duration: 0.6, ease: SOFT }}, 0);
      tl.fromTo("#hk-murah", {{ scale: 1.1, rotation: 2 }}, {{ scale: 1, rotation: 5, duration: 0.5, ease: SPR }}, 0);
      tl.to("#hk-murah", {{ scale: 1.08, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1 }}, {rel(B['murah']):.3f});
      draw("#hk-photo .fr", 0.0, 0.5);
      draw("#hk-photo .en", {rel(B['paling']) + 0.05:.3f}, 0.5);
      tl.fromTo("#hk-photo .ph", {{ scale: 1.12, transformOrigin: "50% 50%" }}, {{ scale: 1.0, duration: {d:.3f}, ease: "none" }}, 0);
      write("#hk-note", {rel(B['harga']):.3f}, 0.45);
      slam("#hk-rm", {rel(B['rm']) - 0.08:.3f}, -4);
      splat("#hk-rm", {rel(B['rm']) + 0.04:.3f});
      tl.to(["#hk-teres", "#hk-murah", "#hk-photo", "#hk-note", "#hk-rm"], {{ opacity: 0, y: -24, duration: 0.14, ease: "power2.in", stagger: 0.012 }}, {d - 0.16:.3f});
      boil("#hk-teres .b, #hk-photo .b", 1.0, 0.25, 3);
"""
    SCENES.append(("hook", s, d, comp("hook", d, css, body, js, p)))


def scene_bulanan():
    p = "bl"
    s, d, rel = scene("bulanan")
    cal = [
        (jit([(14, 30), (14, 150), (176, 150), (176, 30), (14, 30)], 1, 2), 0, INK, 10),
        (jit([(14, 62), (176, 62)], 2, 1.5), 1, INK, 9),
        (jit([(52, 14), (52, 44)], 3, 1), 1, INK, 10), (jit([(138, 14), (138, 44)], 4, 1), 1, INK, 10),
        (jit([(40, 90), (60, 90)], 5, 1), 2, INK, 9), (jit([(86, 90), (106, 90)], 6, 1), 2, INK, 9),
        (jit([(130, 90), (150, 90)], 7, 1), 2, INK, 9), (jit([(40, 122), (60, 122)], 8, 1), 2, INK, 9),
        (jit([(80, 108), (96, 132), (126, 98)], 9, 1.5), 3, RED, 12),
    ]
    body = (
        wrap("bl-cal", 120, 300, 190, 170, strokes(p, 190, 170, cal, extra=f'<rect x="16" y="32" width="158" height="116" fill="{RICE}" opacity="0.92"/>'))
        + banner(p, "bl-ban", 322, 318, 500, 128, "BULANAN", 92, 12, rot=-1.5)
        + seal(p, "bl-seal", 322, 466, 470, 118, "SANGAT MURAH", 62, rot=-3, seed=7)
    )
    js = f"""
      draw("#bl-cal", 0.0, 0.6);
      pop("#bl-cal", 0.0, {{ from: 0.6, r0: -10, r: -4, d: 0.6 }});
      draw("#bl-ban", 0.04, 0.22);
      write("#bl-ban .bntx", 0.12, 0.3);
      slam("#bl-seal", {rel(B['sangat']) - 0.08:.3f}, -3);
      splat("#bl-seal", {rel(B['murah2']):.3f});
      tl.to(["#bl-cal", "#bl-ban", "#bl-seal"], {{ opacity: 0, y: -24, duration: 0.12, ease: "power2.in" }}, {d - 0.14:.3f});
      boil("#bl-cal .b, #bl-ban .b", 1.0, 0.3, 4);
"""
    SCENES.append(("bulanan", s, d, comp("bulanan", d, "", body, js, p)))


def scene_lokasi():
    p = "lk"
    s, d, rel = scene("lokasi")
    css = f"""
#lk-taman {{ font-size: 70px; }}
#lk-kedah {{ font-size: 44px; color: {RED}; rotate: -6deg; }}
"""
    road1 = jit([(-20, 250), (200, 205), (420, 182), (640, 158), (820, 96)], 21, 4)
    road2 = jit([(330, 190), (350, 300), (310, 440)], 22, 4)
    road3 = jit([(600, 162), (690, 260), (780, 330)], 23, 3)
    pal = []  # little palm-oil tufts along the road (the estate behind the site)
    for k, (x, y) in enumerate([(120, 120), (660, 330), (90, 360), (760, 230)]):
        for j in range(5):
            a = math.radians(-160 + j * 35)
            pal.append((jit([(x, y), (x + math.cos(a) * 34, y + math.sin(a) * 26)], 30 + k * 5 + j, 1.5), 3, "#2F5D3A", 7))
        pal.append((jit([(x, y), (x + 2, y + 40)], 60 + k, 1), 3, INK, 7))
    map_svg = strokes(p, 800, 440, [(road1, 0, INK, 30, 0.9), (road2, 1, INK, 22, 0.9), (road3, 2, INK, 14, 0.85)] + pal)
    ul = jit([(4, 14), (200, 6), (420, 16), (600, 8)], 26, 3)
    body = (
        wrap("lk-map", 100, 270, 800, 440, map_svg)
        + seal(p, "lk-pin", 330, 330, 200, 110, "GURUN", 66, rot=-4, seed=9)
        + '<div class="abs mh" id="lk-taman" style="left:150px;top:740px">Taman Impian Mesra</div>'
        + wrap("lk-ul", 150, 818, 600, 30, strokes(p, 600, 30, [(ul, 0, RED, 10)]))
        + '<div class="abs mh" id="lk-kedah" style="left:600px;top:236px">Kedah</div>'
    )
    js = f"""
      draw("#lk-map", 0.12, 1.1, "power1.inOut");
      write("#lk-taman", {rel(B['taman']) - 0.04:.3f}, 0.55);
      draw("#lk-ul", {rel(B['mesra']) - 0.05:.3f}, 0.3);
      // the seal is the map pin: it slams on the crossroads on "Gurun"
      slam("#lk-pin", {rel(B['gurun']) - 0.1:.3f}, -4);
      splat("#lk-pin", {rel(B['gurun']):.3f});
      pop("#lk-kedah", {rel(B['mesra']):.3f}, {{ r0: -20, r: 0, from: 0.4 }});
      tl.to(["#lk-map", "#lk-pin", "#lk-taman", "#lk-ul", "#lk-kedah"], {{ opacity: 0, y: -20, duration: 0.14, ease: "power2.in", stagger: 0.01 }}, {d - 0.16:.3f});
      boil("#lk-map .b, #lk-ul .b", 1.2, 0.3, 9);
"""
    SCENES.append(("lokasi", s, d, comp("lokasi", d, css, body, js, p)))


def scene_semid():
    p = "sd"
    s, d, rel = scene("semid")
    css = f"""
#sd-lb {{ font-size: 54px; rotate: -5deg; }}
"""
    # semi-D units sit bottom-left of the drone photo
    arr = [(jit([(220, 40), (150, 70), (92, 128)], 41, 2), 0, RED, 10), (jit([(88, 88), (90, 132), (132, 128)], 42, 2), 1, RED, 10)]
    body = (
        photo_card(p, "sd-photo", 132, 300, 716, 404, 31, enso=(82, 240, 112, 96, 32))
        + banner(p, "sd-ban", 120, 730, 430, 118, "+ SEMI-D", 82, 33, rot=-2)
        + wrap("sd-arr", 560, 712, 240, 150, strokes(p, 240, 150, arr))
        + '<div class="abs mh" id="sd-lb" style="left:610px;top:686px">sebelah sini!</div>'
    )
    js = f"""
      pop("#sd-photo", 0.0, {{ from: 0.85, y0: 60, r0: 3, r: -1.5, d: 0.6, ease: SOFT }});
      draw("#sd-photo defs", 0.02, 0.5, "power1.inOut");
      draw("#sd-photo .fr", 0.1, 0.5);
      // drift towards the semi-D units (zoom anchored on them), then the enso is painted round them
      tl.fromTo("#sd-photo .ph", {{ scale: 1.0, transformOrigin: "11% 59%" }}, {{ scale: 1.18, duration: {d:.3f}, ease: "power1.inOut" }}, 0);
      draw("#sd-photo .en", {rel(B['semid']) - 0.25:.3f}, 0.5);
      draw("#sd-ban", {rel(B['semid']) - 0.1:.3f}, 0.22);
      write("#sd-ban .bntx", {rel(B['semid']):.3f}, 0.3);
      draw("#sd-arr", {rel(B['semid']) + 0.12:.3f}, 0.3);
      write("#sd-lb", {rel(B['sebelah']) + 0.05:.3f}, 0.4);
      tl.to(["#sd-photo", "#sd-ban", "#sd-arr", "#sd-lb"], {{ opacity: 0, y: -20, duration: 0.14, ease: "power2.in" }}, {d - 0.16:.3f});
      boil("#sd-ban .b, #sd-arr .b", 1.0, 0.3, 5);
"""
    SCENES.append(("semid", s, d, comp("semid", d, css, body, js, p)))


def scene_lot():
    p = "lt"
    s, d, rel = scene("lot")
    css = f"""
.lttx {{ position: absolute; left: 120px; top: 0; font-family: "Barlow Condensed"; font-weight: 800; font-size: 64px; color: {INK};
  text-transform: uppercase; line-height: 1; white-space: nowrap; }}
.ltav {{ position: absolute; left: 498px; top: 18px; font-size: 52px; color: {RED}; text-shadow: none; }}
#lt-units {{ font-size: 50px; rotate: -3deg; }}
"""
    box = jit([(8, 10), (40, 6), (74, 10), (76, 44), (72, 76), (40, 78), (8, 74), (6, 40), (8, 12)], 51, 2)
    rows = ""
    for i, (lab, seed) in enumerate((("NON-BUMI LOT", 52), ("BUMI LOT", 54))):
        strip = jit([(30, 44), (300, 40), (600, 46), (640, 44)], seed, 3)
        tick = jit([(16, 42), (36, 66), (84, 4)], seed + 1, 2)
        rows += wrap(f"lt-r{i}", 120, 560 + i * 128, 660, 96,
                     strokes(p, 660, 96, [(strip, 0, RICE, 84, 0.95)])
                     + f'<svg class="dd" viewBox="0 0 90 90" style="left:12px;top:4px;width:86px;height:86px;filter:url(#lt-br)">'
                     f'<path d="{box}" fill="none" stroke="{INK}" stroke-width="7"/>'
                     f'<path class="br" data-i="1" d="{tick}" stroke="{RED}" stroke-width="14"/></svg>'
                     f'<div class="lttx" style="top:16px">{lab}</div>'
                     f'<div class="ltav mh">available</div>')
    hg = [(jit([(10, 8), (80, 8)], 55, 1), 0, INK, 9), (jit([(10, 132), (80, 132)], 56, 1), 0, INK, 9),
          (jit([(18, 10), (22, 46), (45, 70), (68, 46), (72, 10)], 57, 1.5), 1, INK, 7),
          (jit([(18, 130), (22, 94), (45, 70), (68, 94), (72, 130)], 58, 1.5), 1, INK, 7)]
    sand = f'<path d="M26 126 Q45 98 64 126 Z" fill="{RED}" opacity="0.9"/><path d="M28 26 Q45 50 62 26 Z" fill="{RED}" opacity="0.9"/>'
    body = (
        wrap("lt-hg", 120, 300, 90, 140, strokes(p, 90, 140, hg, extra=sand))
        + seal(p, "lt-seal", 236, 280, 560, 200, "UNIT SANGAT<br>TERHAD", 82, rot=-3, seed=13)
        + rows
    )
    js = f"""
      pop("#lt-hg", {rel(B['unit']) - 0.06:.3f}, {{ r0: -30, from: 0.4 }});
      draw("#lt-hg", {rel(B['unit']):.3f}, 0.4);
      tl.to("#lt-hg", {{ rotation: 180, duration: 0.7, ease: SPR }}, {rel(B['terhad']) + 0.35:.3f});
      slam("#lt-seal", {rel(B['terhad']) - 0.1:.3f}, -3);
      splat("#lt-seal", {rel(B['terhad']):.3f});
      // lot tags slide in, ticks are brushed on "available"
      pop("#lt-r0", {rel(B['nonbumi']) - 0.08:.3f}, {{ from: 0.9, x0: -120, d: 0.5, ease: SOFT }});
      draw("#lt-r0", {rel(B['nonbumi']) - 0.06:.3f}, 0.25);
      tl.set("#lt-r0 svg:nth-of-type(2) .br", {{ opacity: 0 }}, 0);
      draw("#lt-r0 svg:nth-of-type(2)", {rel(B['av1']):.3f}, 0.26);
      write("#lt-r0 .ltav", {rel(B['av1']) + 0.05:.3f}, 0.35);
      pop("#lt-r1", {rel(B['bumi']) - 0.08:.3f}, {{ from: 0.9, x0: -120, d: 0.5, ease: SOFT }});
      draw("#lt-r1", {rel(B['bumi']) - 0.06:.3f}, 0.25);
      tl.set("#lt-r1 svg:nth-of-type(2) .br", {{ opacity: 0 }}, 0);
      draw("#lt-r1 svg:nth-of-type(2)", {rel(B['av2']):.3f}, 0.26);
      write("#lt-r1 .ltav", {rel(B['av2']) + 0.05:.3f}, 0.35);
      tl.to("#lt-r1", {{ scale: 1.05, duration: 0.16, ease: "power2.out", yoyo: true, repeat: 1, transformOrigin: "10% 50%" }}, {rel(B['av2']) + 0.32:.3f});
      tl.to(["#lt-hg", "#lt-seal", "#lt-r0", "#lt-r1"], {{ opacity: 0, y: -20, duration: 0.14, ease: "power2.in", stagger: 0.01 }}, {d - 0.16:.3f});
      boil("#lt-hg .b, #lt-r0 .b, #lt-r1 .b", 1.0, 0.25, 11);
"""
    SCENES.append(("lot", s, d, comp("lot", d, css, body, js, p)))


def scene_isi():
    p = "is"
    s, d, rel = scene("isi")
    css = f"""
#is-yp {{ font-size: 56px; rotate: -3deg; }}
"""
    form = [(jit([(10, 10), (150, 8), (152, 196), (8, 198), (10, 12)], 61, 2), 0, INK, 9),
            (jit([(30, 52), (126, 50)], 62, 1.5), 1, INK, 7), (jit([(30, 92), (110, 92)], 63, 1.5), 1, INK, 7),
            (jit([(30, 132), (120, 130)], 64, 1.5), 1, INK, 7),
            (jit([(36, 160), (50, 150), (64, 170), (80, 150), (96, 168), (112, 152)], 65, 1.5), 2, RED, 7)]
    pen = (f'<g id="is-pen"><path d="M0 0 L22 -10 L120 -112 L104 -128 L6 -26 Z" fill="{INK}"/>'
           f'<path d="M0 0 L22 -10 L6 -26 Z" fill="{RICE}" stroke="{INK}" stroke-width="3"/></g>')
    speed = [(jit([(0, 20), (180, 26)], 66, 2), 0, INK, 10), (jit([(30, 56), (230, 60)], 67, 2), 0, INK, 14),
             (jit([(10, 92), (160, 96)], 68, 2), 1, INK, 8)]
    body = (
        '<div class="abs mh" id="is-yp" style="left:126px;top:300px">yang penting...</div>'
        + wrap("is-form", 130, 360, 162, 210, strokes(p, 162, 210, form, extra=f'<rect x="12" y="12" width="138" height="184" fill="{RICE}" opacity="0.95"/>')
               + f'<svg class="dd" viewBox="-10 -140 140 150" style="left:96px;top:30px;width:140px;height:150px;overflow:visible">{pen}</svg>')
        + banner(p, "is-ban", 320, 400, 520, 138, "ISI SAHAJA", 96, 69, rot=-2)
        + wrap("is-speed", 120, 600, 240, 110, strokes(p, 240, 110, speed))
        + banner(p, "is-cep", 300, 590, 500, 112, "SIAPA CEPAT", 80, 70, color=RICE, tcolor=INK, rot=1.5)
        + seal(p, "is-dapat", 440, 704, 244, 96, "DIA DAPAT!", 52, rot=-5, seed=15)
    )
    js = f"""
      write("#is-yp", 0.02, 0.45);
      pop("#is-form", {rel(B['isi']) - 0.22:.3f}, {{ from: 0.5, r0: -12, r: -4 }});
      draw("#is-form", {rel(B['isi']) - 0.15:.3f}, 0.6);
      tl.fromTo("#is-pen", {{ x: 0, y: 0 }}, {{ x: -60, y: 26, duration: 0.14, ease: "sine.inOut", yoyo: true, repeat: 4 }}, {rel(B['isi']):.3f});
      draw("#is-ban", {rel(B['isi']) - 0.06:.3f}, 0.22);
      write("#is-ban .bntx", {rel(B['isi']) + 0.02:.3f}, 0.3);
      draw("#is-speed", {rel(B['siapa']) - 0.05:.3f}, 0.25, "power3.out");
      tl.fromTo("#is-cep", {{ x: 220, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "expo.out", immediateRender: true }}, {rel(B['siapa']) - 0.04:.3f});
      draw("#is-cep", {rel(B['siapa']) - 0.04:.3f}, 0.2);
      slam("#is-dapat", {rel(B['siapa']) + 0.3:.3f}, -5, 1.5);
      splat("#is-dapat", {rel(B['siapa']) + 0.4:.3f});
      tl.to(["#is-yp", "#is-form", "#is-ban", "#is-speed", "#is-cep", "#is-dapat"], {{ opacity: 0, y: -20, duration: 0.12, ease: "power2.in" }}, {d - 0.14:.3f});
      boil("#is-form .b, #is-ban .b, #is-speed .b", 1.0, 0.3, 13);
"""
    SCENES.append(("isi", s, d, comp("isi", d, css, body, js, p)))


def scene_projek():
    p = "pj"
    s, d, rel = scene("projek")
    css = f"""
#pj-lb {{ font-size: 46px; }}
#pj-pc {{ font-size: 64px; color: {RED}; }}
"""
    crane = [(jit([(60, 330), (60, 20)], 71, 1.5), 0, INK, 12), (jit([(84, 330), (84, 20)], 72, 1.5), 0, INK, 8),
             (jit([(10, 30), (300, 22)], 73, 1.5), 1, INK, 11), (jit([(60, 20), (110, -12), (170, 24)], 74, 1.5), 1, INK, 7),
             (jit([(64, 80), (82, 120), (62, 160), (82, 200), (62, 240), (82, 280)], 75, 1.5), 2, INK, 5),
             (jit([(250, 26), (250, 150)], 76, 1), 3, INK, 5), (jit([(232, 150), (268, 150), (268, 184), (232, 184), (232, 150)], 77, 1), 3, RED, 9)]
    bar_o = jit([(6, 8), (330, 4), (640, 10), (642, 62), (330, 66), (8, 62), (6, 10)], 78, 2.5)
    bar_f = jit([(30, 36), (200, 33), (420, 37)], 79, 2)
    body = (
        wrap("pj-crane", 110, 250, 320, 340, strokes(p, 320, 340, crane))
        + banner(p, "pj-ban", 300, 300, 560, 128, "PROJEK", 92, 81, rot=-2)
        + banner(p, "pj-ban2", 330, 430, 520, 106, "TENGAH BERJALAN", 64, 82, color=RICE, tcolor=INK, rot=1)
        + wrap("pj-bar", 130, 620, 660, 72, strokes(p, 660, 72, [(bar_o, 0, INK, 8), (bar_f, 1, RED, 44)],
                                                    extra=f'<path d="{bar_o}" fill="{RICE}" opacity="0.85"/>'))
        + '<div class="abs mh" id="pj-lb" style="left:134px;top:706px">sedang dibina</div>'
        + '<div class="abs mh" id="pj-pc" style="left:600px;top:700px">&#10140;</div>'
    )
    js = f"""
      draw("#pj-crane", 0.05, 0.8);
      tl.fromTo("#pj-crane svg path:nth-of-type(6), #pj-crane svg path:nth-of-type(7)", {{ x: -40 }}, {{ x: 30, duration: {d:.3f}, ease: "sine.inOut" }}, 0);
      draw("#pj-ban", 0.1, 0.22);
      write("#pj-ban .bntx", 0.16, 0.3);
      draw("#pj-ban2", {rel(B['tengah']) - 0.1:.3f}, 0.22);
      write("#pj-ban2 .bntx", {rel(B['tengah']) - 0.04:.3f}, 0.35);
      tl.set("#pj-bar .br[stroke='{RED}']", {{ opacity: 0 }}, 0);
      draw("#pj-bar", {rel(B['tengah']):.3f}, 1.0, "power1.inOut");
      write("#pj-lb", {rel(B['tengah']) + 0.3:.3f}, 0.4);
      tl.fromTo("#pj-pc", {{ x: -20, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "power2.out", immediateRender: true }}, {rel(B['berjalan']) + 0.25:.3f});
      tl.to("#pj-pc", {{ x: 14, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: 2 }}, {rel(B['berjalan']) + 0.55:.3f});
      tl.to(["#pj-crane", "#pj-ban", "#pj-ban2", "#pj-bar", "#pj-lb", "#pj-pc"], {{ opacity: 0, y: -20, duration: 0.12, ease: "power2.in" }}, {d - 0.14:.3f});
      boil("#pj-crane .b, #pj-bar .b", 1.0, 0.3, 15);
"""
    SCENES.append(("projek", s, d, comp("projek", d, css, body, js, p)))


def scene_laju():
    p = "lj"
    s, d, rel = scene("laju")
    css = f"""
#lj-or {{ font-size: 56px; rotate: -3deg; }}
"""
    speed = [(jit([(0, 18), (150, 22)], 91, 2), 0, INK, 9), (jit([(20, 52), (200, 56)], 92, 2), 0, INK, 13), (jit([(6, 86), (130, 90)], 93, 2), 0, INK, 7)]
    houses, seals = "", ""
    for k in range(6):
        hx = 128 + k * 112
        hp = [(jit([(8, 50), (48, 12), (88, 50)], 100 + k, 1.5), 0, INK, 7), (jit([(16, 46), (16, 98), (80, 98), (80, 46)], 110 + k, 1.5), 0, INK, 7),
              (jit([(40, 98), (40, 72), (56, 72), (56, 98)], 120 + k, 1), 1, INK, 5)]
        houses += wrap(f"lj-h{k}", hx, 600, 96, 104, strokes(p, 96, 104, hp, extra='<rect x="18" y="48" width="60" height="48" fill="#F4ECDD" opacity="0.9"/>'))
    for n, k in enumerate((0, 2, 3, 5)):
        seals += seal(p, f"lj-s{n}", 128 + k * 112 - 14, 636, 124, 62, "BOOKED", 34, rot=(-12 if n % 2 else 9), splats=False, seed=30 + n, ls=0)
    body = (
        wrap("lj-speed", 112, 300, 200, 100, strokes(p, 200, 100, speed))
        + banner(p, "lj-ban", 300, 288, 520, 142, "UNIT LAJU!", 98, 95, rot=-2)
        + '<div class="abs mh" id="lj-or" style="left:150px;top:470px">orang dah booking...</div>'
        + houses + seals
    )
    js = f"""
      draw("#lj-speed", {rel(B['unit2']) - 0.1:.3f}, 0.3, "power3.out");
      tl.fromTo("#lj-ban", {{ x: 260, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.4, ease: "expo.out", immediateRender: true }}, {rel(B['laju']) - 0.12:.3f});
      draw("#lj-ban", {rel(B['laju']) - 0.12:.3f}, 0.2);
      tl.to("#lj-speed", {{ x: -30, duration: 0.2, ease: "sine.inOut", yoyo: true, repeat: 5 }}, {rel(B['laju']):.3f});
      [0, 1, 2, 3, 4, 5].forEach(function (k) {{
        pop("#lj-h" + k, 0.1 + k * 0.08, {{ from: 0.5, y0: 30, d: 0.6 }});
        draw("#lj-h" + k, 0.1 + k * 0.08, 0.4);
      }});
      write("#lj-or", {rel(B['laju']) + 0.25:.3f}, 0.5);
      [0, 1, 2, 3].forEach(function (n) {{ slam("#lj-s" + n, {rel(B['booking']) - 0.12:.3f} + n * 0.14, n % 2 ? -12 : 9); }});
      boil("#lj-speed .b, #lj-ban .b, [id^='lj-h'] .b", 1.0, 0.35, 17);
"""
    SCENES.append(("laju", s, d, comp("laju", d, css, body, js, p)))


def scene_cta():
    p = "ct"
    s, d, rel = scene("cta")
    css = f"""
.chip {{ position: absolute; height: 76px; }}
.chip .t {{ position: absolute; left: 0; right: 0; top: 14px; text-align: center; font-family: "Barlow Condensed"; font-weight: 800;
  font-size: 50px; color: {INK}; text-transform: uppercase; white-space: nowrap; line-height: 1; }}
"""
    arr = lambda sd: [(jit([(40, 6), (38, 62), (40, 110)], sd, 2), 0, RED, 12), (jit([(14, 82), (40, 114), (66, 82)], sd + 1, 2), 1, RED, 12)]

    def chip(id_, l, t, w, txt, seed, col=RICE, tcol=INK):
        st = jit([(30, 38), (w * 0.5, 34), (w - 30, 40)], seed, 3)
        return (f'<div class="chip" id="{id_}" style="left:{l}px;top:{t}px;width:{w}px"><div class="b" style="width:{w}px;height:76px">'
                + strokes(p, w, 76, [(st, 0, col, 70, 0.96)]) + f'<div class="t" style="color:{tcol}">{txt}</div></div></div>')
    body = (
        photo_card(p, "ct-photo", 132, 258, 716, 380, 121)
        + banner(p, "ct-ban", 140, 652, 520, 126, "BERMINAT?", 88, 122, rot=-2)
        + seal(p, "ct-btn", 120, 784, 660, 130, "ISI MAKLUMAT DI BAWAH", 66, rot=-1.5, seed=19)
        + wrap("ct-a1", 230, 930, 80, 124, strokes(p, 80, 124, arr(131)))
        + wrap("ct-a2", 410, 936, 80, 124, strokes(p, 80, 124, arr(133)))
        + wrap("ct-a3", 590, 930, 80, 124, strokes(p, 80, 124, arr(135)))
        + chip("ct-c1", 120, 1080, 300, "Teres &middot; Semi-D", 141, INK, RICE)
        + chip("ct-c2", 436, 1080, 300, "dari RM228K", 142, RED, RICE)
        + chip("ct-c3", 120, 1166, 560, "Tmn Impian Mesra, Gurun", 143)
    )
    pulse_n = max(1, int((d - 1.2) / 0.5))
    bob_n = max(1, int((d - 1.0) / 0.36))
    js = f"""
      pop("#ct-photo", 0.08, {{ from: 0.85, y0: 40, r0: -3, r: 1.5, d: 0.6, ease: SOFT }});
      draw("#ct-photo defs", 0.1, 0.55, "power1.inOut");
      draw("#ct-photo .fr", 0.2, 0.5);
      tl.fromTo("#ct-photo .ph", {{ scale: 1.15, transformOrigin: "50% 50%" }}, {{ scale: 1.0, duration: {d:.3f}, ease: "none" }}, 0);
      draw("#ct-ban", 0.3, 0.22);
      write("#ct-ban .bntx", 0.36, 0.3);
      slam("#ct-btn", 0.55, -1.5);
      splat("#ct-btn", 0.65);
      tl.to("#ct-btn", {{ scale: 1.04, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: {pulse_n * 2 - 1} }}, 1.2);
      ["#ct-a1", "#ct-a2", "#ct-a3"].forEach(function (a, i) {{
        draw(a, 0.85 + i * 0.12, 0.25);
        tl.to(a, {{ y: 14, duration: 0.18, ease: "sine.inOut", yoyo: true, repeat: {bob_n * 2 - 1} }}, 1.15 + i * 0.06);
      }});
      pop("#ct-c1", 0.8, {{ y0: 30, r0: -6, r: -1.5, d: 0.6 }});
      pop("#ct-c2", 0.9, {{ y0: 30, r0: 6, r: 1.5, d: 0.6 }});
      pop("#ct-c3", 1.0, {{ y0: 30, r0: -6, r: -1, d: 0.6 }});
      boil("#ct-ban .b, #ct-a1 .b, #ct-a2 .b, #ct-a3 .b, .chip .b", 1.0, 0.3, 19);
"""
    SCENES.append(("cta", s, d, comp("cta", d, css, body, js, p)))


def scene_captions():
    p = "cp"
    s, d = 0.0, VOICE_END
    css = f"""
.cap {{ position: absolute; left: 116px; width: 664px; bottom: {H - 1170}px; text-align: center; visibility: hidden; }}
.ln {{ position: relative; display: inline-block; padding: 10px 26px 12px; }}
.ln .bg {{ position: absolute; left: 0; top: 0; right: 0; bottom: 0; }}
.w {{ position: relative; display: inline-block; font-family: "Barlow Condensed"; font-weight: 800; font-size: 66px; line-height: 1;
  color: {INK}; text-transform: uppercase; margin: 0 4px; opacity: 0; }}
.w.k {{ color: {RED}; }}
"""
    body, js = "", ""
    for ci, (seg, words, end_src) in enumerate(CAPS):
        t0 = o(seg, words[0][1])
        t1 = o(seg, end_src)
        nxt = CAPS[ci + 1] if ci + 1 < len(CAPS) else None
        if nxt:
            t1 = min(t1, o(nxt[0], nxt[1][0][1]))
        if seg != (nxt[0] if nxt else None):
            t1 = min(t1, next(x for x in EDL if x["id"] == seg)["start"] + next(x for x in EDL if x["id"] == seg)["dur"])
        spans = ""
        for wi, w in enumerate(words):
            k = len(w) > 2 and w[2]
            spans += f'<span class="w{" k" if k else ""}" id="cp{ci}w{wi}">{w[0]}</span>'
        st = jit([(16, 46), (200, 42), (420, 48), (640, 44)], 200 + ci, 4)
        bg = (f'<svg class="dd" viewBox="0 0 656 92" preserveAspectRatio="none" style="left:0;top:0;width:100%;height:100%;filter:url(#cp-br)">'
              f'<path class="br" d="{st}" stroke="{RICE}" stroke-width="86" opacity="0.96"/></svg>')
        body += f'<div class="cap" id="cp{ci}"><div class="ln"><div class="bg" id="cp{ci}bg">{bg}</div>{spans}</div></div>\n'
        js += f'      tl.set("#cp{ci}", {{ visibility: "visible" }}, {max(0, t0 - 0.03):.3f}); tl.set("#cp{ci}", {{ visibility: "hidden" }}, {t1:.3f});\n'
        js += (f'      tl.fromTo("#cp{ci}bg", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.16, '
               f'ease: "power2.out", immediateRender: true }}, {max(0, t0 - 0.03):.3f});\n')
        for wi, w in enumerate(words):
            wt = max(t0, o(seg, w[1]))
            js += (f'      tl.fromTo("#cp{ci}w{wi}", {{ opacity: 0, y: 14, scale: 0.8 }}, '
                   f'{{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: SPR, immediateRender: false }}, {max(0, wt - 0.03):.3f});\n')
    SCENES.append(("captions", s, d, comp("captions", d, css, body, js, p)))


def swipe_comp():
    """ink swipe: three dry-brush strokes cross the frame, cover the cut, then lift off"""
    p = "sw"
    d = 0.6
    paths = [(jit([(-200, 1500), (300, 1050), (700, 700), (1300, 250)], 81, 20), 0, INK, 560),
             (jit([(-200, 2150), (400, 1550), (800, 1150), (1300, 820)], 82, 20), 0, INK, 600),
             (jit([(-200, 900), (300, 480), (700, 120), (1300, -300)], 83, 20), 0, INK, 560),
             (jit([(-200, 1700), (400, 1250), (900, 820), (1300, 520)], 84, 14), 1, RED, 120)]
    body = wrap("sw-s", 0, 0, W, H, strokes(p, W, H, paths))
    js = """
      gsap.utils.toArray("#sw-s .br").forEach(function (p, i) {
        var len = p.getTotalLength() + 6;
        gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len });
        tl.to(p, { strokeDashoffset: 0, duration: 0.26, ease: "power2.in" }, i * 0.03);
        tl.to(p, { strokeDashoffset: -len, duration: 0.26, ease: "power2.out" }, 0.32 + i * 0.02);
      });
"""
    return d, comp("swipe", d, "", body, js, p)


# ================================================================ index.html
def build():
    for f in (scene_hook, scene_bulanan, scene_lokasi, scene_semid, scene_lot, scene_isi, scene_projek, scene_laju, scene_cta, scene_captions):
        f()
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    for cid, s, d, html in SCENES:
        with open(os.path.join(ROOT, "compositions", f"{cid}.html"), "w") as fh:
            fh.write(html)
    sw_d, sw_html = swipe_comp()
    with open(os.path.join(ROOT, "compositions", "swipe.html"), "w") as fh:
        fh.write(sw_html)

    vids, auds, comps = [], [], []
    n = 0
    for sg in EDL:
        seg_len = round(sg["dur"] + sg.get("extra", 0), 3)
        cuts = sg["v"] + [(seg_len, None)]
        for (off, src), (nxt, _) in zip(cuts, cuts[1:]):
            n += 1
            st, du = round(sg["start"] + off, 3), round(nxt - off, 3)
            if src == "columns":
                vids.append(f'        <img id="colimg" class="clip" src="assets/columns.jpg" alt="" data-start="{st}" data-duration="{du}" data-track-index="1" '
                            f'style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;object-fit:cover;transform-origin:50% 40%">')
            else:
                vids.append(f'        <video id="v{n}" class="clip" src="assets/footage.mp4" muted playsinline data-start="{st}" '
                            f'data-duration="{du}" data-media-start="{src}" data-track-index="0"></video>')
    chain = json.dumps({"version": 1, "nodes": [
        {"type": "highpass", "id": "vo1", "label": "Remove rumble", "params": {"frequency": 90}},
        {"type": "peaking", "id": "vo2", "label": "Presence", "params": {"frequency": 3200, "gain": 2, "q": 1}},
        {"type": "limiter", "id": "vo3", "params": {"limit": -1}}]}).replace('"', "&quot;")
    for i, sg in enumerate(EDL):
        auds.append(f'      <audio id="vo{i + 1}" src="assets/voice.wav" data-start="{sg["start"]}" data-duration="{sg["dur"]}" '
                    f'data-media-start="{sg["a"][0]}" data-volume="1.0" data-fade-in="0.012" data-fade-out="0.025" '
                    f'data-fx-chain="{chain}" data-track-index="10"></audio>')
    lanes = {"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0.32}, {"t": 0.3, "v": 0.17}, {"t": VOICE_END, "v": 0.17},
        {"t": CTA + 0.2, "v": 0.42}, {"t": TOTAL - 0.6, "v": 0.42}, {"t": TOTAL, "v": 0.0}]}]}
    mfx = {"version": 1, "nodes": [
        {"type": "peaking", "id": "mu1", "label": "Make room for the voice", "params": {"frequency": 2500, "gain": -5, "q": 0.8}},
        {"type": "peaking", "id": "mu2", "label": "Clear low mids", "params": {"frequency": 300, "gain": -3, "q": 1}}]}
    auds.append(f'      <audio id="music" src="assets/music/bed-hiphop-02.mp3" data-start="0" data-duration="{TOTAL}" '
                f'data-media-start="0" data-volume="1" data-automation="{json.dumps(lanes).replace(chr(34), "&quot;")}" '
                f'data-fx-chain="{json.dumps(mfx).replace(chr(34), "&quot;")}" data-track-index="11"></audio>')

    def dur_of(name):
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              os.path.join(ROOT, "assets", "sfx", name + ".mp3")], capture_output=True, text=True).stdout
        return float(out.strip())
    lane_end = {}
    for i, e in enumerate(sorted(SFX, key=lambda x: x["at"])):
        fd = dur_of(e["name"]) - e["ms"]
        dd = min(fd, e["dur"]) if e["dur"] else fd
        dd = min(dd, TOTAL - e["at"])
        ms = f' data-media-start="{e["ms"]}"' if e["ms"] else ""
        fo = ' data-fade-out="0.08"' if e["dur"] else ""
        lane = next(l for l in range(20, 40) if lane_end.get(l, -1) <= e["at"])
        lane_end[lane] = e["at"] + dd
        auds.append(f'      <audio id="fx{i:02d}" src="assets/sfx/{e["name"]}.mp3" data-start="{e["at"]}" data-duration="{dd:.3f}"{ms} '
                    f'data-volume="{e["vol"]}"{fo} data-track-index="{lane}"></audio>')
    for cid, s, d, _ in SCENES:
        z, tr, kind = (6, 3, "captions") if cid == "captions" else (5, 2, "graphics")
        comps.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s:.3f}" '
                     f'data-duration="{d:.3f}" data-width="{W}" data-height="{H}" data-track-index="{tr}" data-track-kind="{kind}" style="z-index:{z}"></div>')
    for i, at in enumerate(SWIPES):
        comps.append(f'      <div id="swipe-{i + 1}" data-composition-id="swipe" data-composition-src="compositions/swipe.html" '
                     f'data-start="{at - 0.29:.3f}" data-duration="{sw_d}" data-width="{W}" data-height="{H}" data-track-index="4" '
                     f'data-track-kind="graphics" style="z-index:8"></div>')

    html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: {INK}; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 55%; z-index: 1; }}
      #cam video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #vign {{ position: absolute; inset: 0; z-index: 2; pointer-events: none;
        background: radial-gradient(ellipse 85% 70% at 50% 45%, rgba(23,19,15,0) 55%, rgba(23,19,15,0.28) 100%); }}
      #grain {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 9; pointer-events: none;
        mix-blend-mode: overlay; opacity: 0.55; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}" data-fps="{FPS}" data-motion-blur="on">
      <div id="cam">
{chr(10).join(vids)}
      </div>
      <div id="vign"></div>
{chr(10).join(comps)}
      <img id="grain" src="assets/paper-grain.png" alt="" />
{chr(10).join(auds)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      gsap.set("#cam", {{ scale: 1, x: 0 }});
      {cam_js()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w") as fh:
        fh.write(html)
    print(f"voice {VOICE_END}s, total {TOTAL}s, segments:", ST)
    print("beats:", B)


if __name__ == "__main__":
    build()
