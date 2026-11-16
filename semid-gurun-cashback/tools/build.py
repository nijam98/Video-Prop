#!/usr/bin/env python3
"""Generates index.html + compositions/*.html for the Semi-D Gurun "cashback" reel.

Look: "Krayon & Oil Pastel" — waxy crayon strokes with grain, hatched crayon fills,
Gochi Hand lettering + Rubik Doodle Shadow numbers, Remotion-style springs.

Edit the tables below (EDL, captions, SFX) and re-run:
    python3 tools/build.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
TAIL = 2.5  # hold after the last word

# ---------------------------------------------------------------- palette
SUN, CORAL, SKY, LEAF, LILAC, PLUM, CREAM = "#FFC83D", "#FF6A4D", "#4C9BFF", "#43C46B", "#A07CFF", "#2B1E3F", "#FFF6E6"

# ---------------------------------------------------------------- edit decision list
# a = source seconds of speech kept, v = source in-point for the picture (one continuous
# exterior shot, so the picture is taken from hand-free stretches of the clip).
EDL = [
    dict(id="s1", a=(3.62, 6.44), v=8.00),    # HOOK  harga bawah RM300 ribu, pusing satu Kedah tak jumpa dah
    dict(id="s2", a=(0.10, 3.42), v=17.20),   # rumah semi-D cluster, empat bilik dua tandas
    dict(id="s3", a=(6.66, 10.04), v=10.90),  # dekat mana rumah ni? dekat Gurun, Taman Impian Mesra
    dict(id="s4", a=(11.54, 13.20), v=20.50), # loan LPPSA boleh, loan bank boleh   ("macam biasa" cut)
    dict(id="s5", a=(13.68, 14.64), v=14.30), # SJKP pun boleh                       (0.5 s pause cut)
    dict(id="s6", a=(21.24, 23.24), v=15.30), # yang penting rumah ni cashback sangat tinggi (moved up)
    dict(id="s7", a=(19.24, 21.16), v=21.80),  # unit sangat-sangat terhad, jangan lepaskan peluang
    dict(id="s8", a=(16.96, 19.24), v=12.00, extra=TAIL),  # CTA: nak tahu detail, isi saja maklumat kat bawah ni
]
# removed: "macam biasa", "yang berniaga ok" (unclear), 2nd "nak tahu detail, isi saja" (repeat), all pauses
t = 0.0
for s in EDL:
    s["start"] = round(t, 3)
    s["dur"] = round(s["a"][1] - s["a"][0], 3)
    t += s["dur"]
VOICE_END = round(t, 3)
TOTAL = round(VOICE_END + TAIL, 3)
ST = {s["id"]: s["start"] for s in EDL}
SEG_END = {s["id"]: round(s["start"] + s["dur"], 3) for s in EDL}


def o(seg, src):
    """source second -> output second inside segment `seg`"""
    s = next(x for x in EDL if x["id"] == seg)
    return round(s["start"] + (src - s["a"][0]), 3)


# ---------------------------------------------------------------- captions (word level, source times)
# (segment, [(word, src_start, key?)...], src_end)
CAPS = [
    ("s1", [("Harga", 3.65), ("bawah", 3.90)], 4.30),
    ("s1", [("RM300", 4.30, 1), ("ribu", 4.85, 1)], 5.31),
    ("s1", [("pusing", 5.31), ("satu", 5.59), ("Kedah", 5.81, 1)], 6.12),
    ("s1", [("tak", 6.15), ("jumpa", 6.24), ("dah!", 6.34)], 6.44),
    ("s2", [("Rumah", 0.15), ("semi-D", 0.41, 1), ("cluster", 0.90, 1)], 1.69),
    ("s2", [("empat", 1.69, 1), ("bilik,", 2.16, 1)], 2.60),
    ("s2", [("dua", 2.64, 1), ("tandas", 2.94, 1)], 3.42),
    ("s3", [("Dekat", 6.70), ("mana", 6.97), ("rumah", 7.26), ("ni?", 7.62)], 7.90),
    ("s3", [("Dekat", 7.96), ("Gurun,", 8.26, 1)], 8.85),
    ("s3", [("Taman", 8.85), ("Impian", 9.28), ("Mesra", 9.80)], 10.04),
    ("s4", [("Loan", 11.64), ("LPPSA", 11.81, 1), ("boleh,", 12.12)], 12.66),
    ("s4", [("loan", 12.66), ("bank", 12.88, 1), ("boleh,", 13.02)], 13.20),
    ("s5", [("SJKP", 13.70, 1), ("pun", 13.95), ("boleh!", 14.29)], 14.64),
    ("s6", [("Yang", 21.37), ("penting", 21.43), ("rumah", 21.81), ("ni", 22.05)], 22.15),
    ("s6", [("cashback", 22.15, 1), ("sangat", 22.60), ("tinggi!", 22.88, 1)], 23.24),
    ("s7", [("Unit", 19.30), ("sangat-sangat", 19.39), ("terhad,", 19.94, 1)], 20.28),
    ("s7", [("jangan", 20.28), ("lepaskan", 20.60), ("peluang", 20.87, 1)], 21.16),
    ("s8", [("Nak", 17.05), ("tahu", 17.14), ("detail?", 17.38)], 17.72),
    ("s8", [("Isi", 17.72, 1), ("saja", 17.88), ("maklumat", 18.11)], 18.55),
    ("s8", [("kat", 18.55), ("bawah", 18.65, 1), ("ni", 19.01)], 19.24),
]

# ---------------------------------------------------------------- key beats (output seconds)
B = dict(
    kedah=o("s1", 5.31), takjumpa=o("s1", 6.15),
    cluster=o("s2", 0.90), empat=o("s2", 1.69), dua=o("s2", 2.64),
    mana=o("s3", 6.70), gurun=o("s3", 8.26), taman=o("s3", 8.85),
    lppsa=o("s4", 11.81), lppsa_ok=o("s4", 12.12), bank=o("s4", 12.66), bank_ok=o("s4", 13.00),
    sjkp=o("s5", 13.70), sjkp_ok=o("s5", 14.29),
    penting=o("s6", 21.37), cashback=o("s6", 22.15), tinggi=o("s6", 22.60), tinggi2=o("s6", 22.88),
    unit=o("s7", 19.30), terhad=o("s7", 19.94), peluang=o("s7", 20.28),
    nak=o("s8", 17.05), isi=o("s8", 17.72), bawah=o("s8", 18.55),
)

# ---------------------------------------------------------------- sound effects (output time, file, volume, media_start, dur)
# every file is pre-normalised to about -20 LUFS (voice sits at -15), so 0.2-0.4 keeps them well under the voice
def fx(at, name, vol=0.3, ms=0.0, dur=None):
    return dict(at=round(at, 3), name=name, vol=vol, ms=ms, dur=dur)

SFX = [
    # hook
    fx(0.00, "impact-soft", 0.30),
    fx(0.40, "crayon-underline", 0.30, 0.0, 0.9),
    fx(0.70, "sparkle", 0.16),
    fx(B["kedah"] - 0.05, "swoosh-soft", 0.20),
    fx(B["takjumpa"] - 0.02, "pop-soft", 0.42),
    # whip -> specs
    fx(ST["s2"] - 0.16, "whoosh-accent", 0.26),
    fx(ST["s2"] + 0.05, "crayon-write", 0.26, 0.0, 1.0),
    fx(B["cluster"] + 0.05, "crayon-scribble", 0.26),
    fx(B["empat"] - 0.02, "pop-bubble", 0.40),
    fx(B["dua"] - 0.02, "pop-bubble", 0.40),
    # punch -> lokasi
    fx(ST["s3"] - 0.08, "whoosh-sweep", 0.20),
    fx(B["mana"] + 0.05, "paper-flip", 0.40),
    fx(B["gurun"] - 0.30, "swoosh-soft", 0.16),
    fx(B["gurun"] - 0.02, "click-soft", 0.55),
    fx(B["taman"] + 0.02, "crayon-write", 0.22, 0.0, 0.9),
    # whip -> loan checklist
    fx(ST["s4"] - 0.16, "whoosh-accent", 0.24),
    fx(B["lppsa"] - 0.02, "paper-flip", 0.32),
    fx(B["lppsa_ok"] + 0.02, "crayon-underline", 0.30, 0.15, 0.35),
    fx(B["bank"] - 0.02, "paper-flip", 0.30),
    fx(B["bank_ok"] + 0.02, "crayon-underline", 0.30, 0.15, 0.35),
    fx(B["sjkp"] - 0.02, "paper-flip", 0.30),
    fx(B["sjkp_ok"] + 0.02, "crayon-underline", 0.30, 0.15, 0.35),
    fx(B["sjkp_ok"] + 0.10, "chime-positive", 0.18),
    # zoom-through + crayon swipe -> cashback
    fx(ST["s6"] - 0.22, "whoosh-sweep", 0.28),
    fx(B["cashback"] - 0.04, "coin-prize", 0.30),
    fx(B["tinggi"] - 0.05, "swoosh-soft", 0.18),
    fx(B["tinggi"] + 0.12, "kaching", 0.24),
    # whip -> unit terhad
    fx(ST["s7"] - 0.16, "whoosh-accent", 0.24),
    fx(B["unit"] + 0.02, "click-soft", 0.45),
    fx(B["terhad"] - 0.03, "impact-soft", 0.28),
    fx(B["peluang"] + 0.04, "crayon-write", 0.22, 0.0, 0.8),
    # crayon swipe -> CTA
    fx(ST["s8"] - 0.22, "whoosh-sweep", 0.26),
    fx(B["nak"] + 0.03, "crayon-write", 0.22, 0.0, 0.7),
    fx(B["isi"] - 0.02, "pop-bubble", 0.42),
    fx(B["isi"] + 0.15, "shimmer-success", 0.20),
    fx(B["bawah"], "swoosh-soft", 0.16),
    fx(VOICE_END + 0.0, "pop-soft", 0.30),
    fx(VOICE_END + 0.14, "pop-bubble", 0.32),
    fx(VOICE_END + 0.28, "pop-soft", 0.28),
    fx(VOICE_END + 0.45, "coin-shimmer", 0.20),
]

# ---------------------------------------------------------------- camera moves on #cam
CAM_JS = f"""
      tl.fromTo("#cam", {{ scale: 1.0, x: 0 }}, {{ scale: 1.07, duration: {ST['s2'] - 0.16:.3f}, ease: "none", immediateRender: false }}, 0);
      tl.to("#cam", {{ x: -150, scale: 1.3, duration: 0.16, ease: "power2.in" }}, {ST['s2'] - 0.16:.3f});
      tl.fromTo("#cam", {{ x: 150, scale: 1.3 }}, {{ x: 0, scale: 1.04, duration: 0.34, ease: "power3.out", immediateRender: false }}, {ST['s2']:.3f});
      tl.to("#cam", {{ scale: 1.09, duration: {ST['s3'] - ST['s2'] - 0.34:.3f}, ease: "none" }}, {ST['s2'] + 0.34:.3f});
      tl.fromTo("#cam", {{ scale: 1.18, x: 0 }}, {{ scale: 1.02, duration: 0.4, ease: "expo.out", immediateRender: false }}, {ST['s3']:.3f});
      tl.to("#cam", {{ scale: 1.06, x: 20, duration: {ST['s4'] - ST['s3'] - 0.56:.3f}, ease: "none" }}, {ST['s3'] + 0.4:.3f});
      tl.to("#cam", {{ x: 150, scale: 1.3, duration: 0.16, ease: "power2.in" }}, {ST['s4'] - 0.16:.3f});
      tl.fromTo("#cam", {{ x: -150, scale: 1.3 }}, {{ x: 0, scale: 1.05, duration: 0.34, ease: "power3.out", immediateRender: false }}, {ST['s4']:.3f});
      tl.fromTo("#cam", {{ scale: 1.2, x: 0 }}, {{ scale: 1.1, duration: 0.36, ease: "expo.out", immediateRender: false }}, {ST['s5']:.3f});
      tl.to("#cam", {{ scale: 1.42, duration: 0.14, ease: "power3.in" }}, {ST['s6'] - 0.14:.3f});
      tl.fromTo("#cam", {{ scale: 1.46, x: 0 }}, {{ scale: 1.03, duration: 0.5, ease: "expo.out", immediateRender: false }}, {ST['s6']:.3f});
      tl.to("#cam", {{ scale: 1.09, duration: {ST['s7'] - ST['s6'] - 0.66:.3f}, ease: "none" }}, {ST['s6'] + 0.5:.3f});
      tl.to("#cam", {{ x: -150, scale: 1.3, duration: 0.16, ease: "power2.in" }}, {ST['s7'] - 0.16:.3f});
      tl.fromTo("#cam", {{ x: 150, scale: 1.3 }}, {{ x: 0, scale: 1.05, duration: 0.34, ease: "power3.out", immediateRender: false }}, {ST['s7']:.3f});
      tl.fromTo("#cam", {{ scale: 1.2, x: 0 }}, {{ scale: 1.0, duration: 0.45, ease: "expo.out", immediateRender: false }}, {ST['s8']:.3f});
      tl.to("#cam", {{ scale: 1.08, duration: {TOTAL - ST['s8'] - 0.45:.3f}, ease: "none" }}, {ST['s8'] + 0.45:.3f});
"""
SWIPES = []   # crayon swipe overlay (compositions/swipe.html) — off: camera moves carry the cuts

# ================================================================ shared building blocks
FONTS = """
@font-face { font-family: "Gochi Hand"; src: url("assets/fonts/gochi-hand.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Rubik Doodle Shadow"; src: url("assets/fonts/rubik-doodle-shadow.woff2") format("woff2"); font-display: block; }
"""

BASE_CSS = f"""
#root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
.abs {{ position: absolute; }}
.b {{ position: relative; }}
svg.dd {{ position: absolute; overflow: visible; }}
svg.dd .cr {{ fill: none; stroke-linecap: round; stroke-linejoin: round; }}
.hand {{ font-family: "Gochi Hand"; color: #fff; -webkit-text-stroke: 12px {PLUM}; paint-order: stroke fill;
  text-shadow: 0 6px 0 {PLUM}; white-space: nowrap; line-height: 1; letter-spacing: 0.5px; }}
.doodle {{ font-family: "Rubik Doodle Shadow"; white-space: nowrap; line-height: 0.95; text-shadow: 4px 6px 0 {PLUM}; }}
"""


def defs(p):
    """crayon filters + hatch fills, prefixed per composition so every comp is self-contained"""
    hatch = ""
    for name, col in (("sun", SUN), ("coral", CORAL), ("sky", SKY), ("leaf", LEAF), ("cream", CREAM), ("lilac", LILAC)):
        hatch += (f'<pattern id="{p}-h-{name}" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(-32)">'
                  f'<rect width="16" height="16" fill="{col}" opacity="0.82"/>'
                  f'<line x1="0" y1="5" x2="16" y2="5" stroke="{col}" stroke-width="7"/>'
                  f'<line x1="0" y1="13" x2="16" y2="13" stroke="#fff" stroke-opacity="0.18" stroke-width="2"/></pattern>')
    return f"""<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<filter id="{p}-cr" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="4" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="5" xChannelSelector="R" yChannelSelector="G" result="wob"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="9" result="grain"/>
  <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.75" result="mask"/>
  <feComposite in="wob" in2="mask" operator="in"/>
</filter>
<filter id="{p}-tx" x="-10%" y="-20%" width="120%" height="140%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="2" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="3" xChannelSelector="R" yChannelSelector="G" result="wob"/>
  <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="1" seed="5" result="grain"/>
  <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.9 1.45" result="mask"/>
  <feComposite in="wob" in2="mask" operator="in"/>
</filter>
{hatch}</defs></svg>"""


COMMON_JS = r"""
      var tl = gsap.timeline({ paused: true });
      // Remotion-style spring (mass 1): z = damping ratio, w = natural freq, T = seconds the tween spans
      function spring(z, w, T) {
        var wd = w * Math.sqrt(1 - z * z), a = z * w;
        return function (p) { if (p >= 1) return 1; var t = p * T;
          return 1 - Math.exp(-a * t) * (Math.cos(wd * t) + (a / wd) * Math.sin(wd * t)); };
      }
      var SPR = spring(0.42, 13, 0.9), SOFT = spring(0.72, 13, 0.7);
      function hh(n, s) { var x = Math.sin(n * 127.1 + (s || 1) * 311.7) * 43758.5453; return (x - Math.floor(x)) * 2 - 1; }
      var renders = [];
      // crayon "boil": inner wrappers re-jitter 8 times a second, like a re-drawn frame
      function boil(sel, amp, rot, seed) {
        var els = gsap.utils.toArray(sel);
        renders.push(function () {
          var st = Math.floor(tl.time() * 8);
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
      function pop(sel, at, opt) {
        opt = opt || {};
        tl.fromTo(sel, { scale: opt.from == null ? 0.2 : opt.from, opacity: 0, rotation: opt.r0 || 0, y: opt.y0 || 0 },
          { scale: 1, opacity: 1, rotation: opt.r || 0, y: 0, duration: opt.d || 0.9, ease: opt.ease || SPR, immediateRender: true }, at);
      }
      // crayon stroke draw-on; strokes sharing data-i draw together
      function draw(sel, at, dur) {
        var ps = gsap.utils.toArray(sel + " .cr");
        var n = 0; ps.forEach(function (p) { n = Math.max(n, +(p.getAttribute("data-i") || 0) + 1); });
        var seg = dur / Math.max(1, n * 0.8 + 0.2);
        ps.forEach(function (p) {
          var i = +(p.getAttribute("data-i") || 0), len = p.getTotalLength() + 4;
          gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len, opacity: 0 });
          tl.set(p, { opacity: 1 }, at + i * seg * 0.8);
          tl.to(p, { strokeDashoffset: 0, duration: seg, ease: "power1.inOut" }, at + i * seg * 0.8);
        });
      }
      // handwriting reveal, left to right
      function write(sel, at, dur) {
        tl.fromTo(sel, { clipPath: "inset(-30% 105% -30% -4%)", opacity: 1 },
          { clipPath: "inset(-30% -4% -30% -4%)", duration: dur || 0.5, ease: "power1.inOut", immediateRender: true }, at);
        tl.set(sel, { clipPath: "none" }, at + (dur || 0.5) + 0.01);
      }
      function out(sel, at, d) { tl.to(sel, { opacity: 0, scale: 0.86, duration: d || 0.22, ease: "power2.in" }, at); }
"""


def jit(pts, seed, amp=2.5):
    """jitter a polyline for a hand-drawn wobble -> smooth path string"""
    import math
    def h(n):
        x = math.sin(n * 127.1 + seed * 311.7) * 43758.5453
        return (x - math.floor(x)) * 2 - 1
    q = [(x + h(i * 2) * amp, y + h(i * 2 + 1) * amp) for i, (x, y) in enumerate(pts)]
    d = f"M{q[0][0]:.1f} {q[0][1]:.1f}"
    for i in range(1, len(q) - 1):
        mx, my = (q[i][0] + q[i + 1][0]) / 2, (q[i][1] + q[i + 1][1]) / 2
        d += f" Q{q[i][0]:.1f} {q[i][1]:.1f} {mx:.1f} {my:.1f}"
    d += f" L{q[-1][0]:.1f} {q[-1][1]:.1f}"
    return d


def blob(w, h, seed, r=0.22, amp=5):
    """wobbly rounded rectangle path (crayon card)"""
    import math
    rr = min(w, h) * r
    pts = []
    corners = [(w - rr, rr, -90), (w - rr, h - rr, 0), (rr, h - rr, 90), (rr, rr, 180)]
    for cx, cy, a0 in corners:
        for k in range(4):
            a = math.radians(a0 + k * 30)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    def hh(n):
        x = math.sin(n * 127.1 + seed * 311.7) * 43758.5453
        return (x - math.floor(x)) * 2 - 1
    pts = [(x + hh(i * 2) * amp, y + hh(i * 2 + 1) * amp) for i, (x, y) in enumerate(pts)]
    d = ""
    n = len(pts)
    for i in range(n):
        p0, p1 = pts[i], pts[(i + 1) % n]
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        d += (f"M{mx:.1f} {my:.1f}" if i == 0 else f" Q{p0[0]:.1f} {p0[1]:.1f} {mx:.1f} {my:.1f}")
    p0 = pts[0]; p1 = pts[1]
    d += f" Q{p0[0]:.1f} {p0[1]:.1f} {(p0[0] + p1[0]) / 2:.1f} {(p0[1] + p1[1]) / 2:.1f} Z"
    return d


def card(p, w, h, fill, seed, stroke=PLUM, sw=7, op=1.0):
    """crayon-filled card: hatch fill + wobbly plum outline, both through the crayon filter"""
    d = blob(w, h, seed)
    return (f'<svg class="dd" viewBox="0 0 {w} {h}" style="left:0;top:0;width:{w}px;height:{h}px;filter:url(#{p}-cr);opacity:{op}">'
            f'<path d="{d}" fill="url(#{p}-h-{fill})"/>'
            f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/></svg>')


def strokes(p, vw, vh, w, h, paths, color=PLUM, sw=8, extra=""):
    """doodle svg: paths = [(d, data-i, color?, width?)] drawn as crayon strokes"""
    body = ""
    for item in paths:
        d, i = item[0], item[1]
        c = item[2] if len(item) > 2 and item[2] else color
        ww = item[3] if len(item) > 3 else sw
        body += f'<path class="cr" data-i="{i}" d="{d}" stroke="{c}" stroke-width="{ww}"/>'
    return (f'<svg class="dd" viewBox="0 0 {vw} {vh}" style="left:0;top:0;width:{w}px;height:{h}px;filter:url(#{p}-cr)">'
            f'{extra}{body}</svg>')


def sparkle(p, size, col=SUN):
    d = "M50 4 Q56 44 96 50 Q56 56 50 96 Q44 56 4 50 Q44 44 50 4 Z"
    return (f'<svg class="dd" viewBox="0 0 100 100" style="left:0;top:0;width:{size}px;height:{size}px;filter:url(#{p}-cr)">'
            f'<path d="{d}" fill="{col}" stroke="{PLUM}" stroke-width="6" stroke-linejoin="round"/></svg>')


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


def wrap(id_, left, top, w, h, inner, extra_style=""):
    return (f'<div class="abs" id="{id_}" style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;{extra_style}">'
            f'<div class="b" style="width:{w}px;height:{h}px">{inner}</div></div>')


# ================================================================ scenes
SCENES = []  # (cid, start, dur, html)


def scene_hook():
    p, s, d = "hk", 0.0, ST["s2"]
    rel = lambda x: round(x - s, 3)
    css = f"""
#hk-tagtx {{ position:absolute; left:26px; top:12px; font-family:"Gochi Hand"; font-size:50px; color:{PLUM}; white-space:nowrap; filter:url(#hk-tx); }}
#hk-bawah {{ font-size:76px; rotate:-4deg; }}
#hk-price {{ font-size:176px; color:{CORAL}; filter:url(#hk-tx); }}
#hk-stamptx {{ position:absolute; left:0; right:0; top:16px; text-align:center; font-family:"Rubik Doodle Shadow"; font-size:50px; color:{CORAL}; filter:url(#hk-tx); white-space:nowrap; text-shadow:3px 4px 0 {PLUM}; }}
"""
    ul = jit([(8, 34), (120, 20), (260, 30), (400, 18), (540, 26), (660, 16)], 3, 3)
    ul2 = jit([(40, 46), (200, 36), (360, 44), (520, 34), (640, 40)], 5, 3)
    mag = ("M52 52 m-34 0 a34 34 0 1 0 68 0 a34 34 0 1 0 -68 0", "M78 78 L112 112")
    stamp_box = jit([(8, 10), (150, 4), (300, 10), (322, 50), (316, 92), (160, 98), (12, 92), (4, 50), (10, 12)], 8, 3)
    body = (
        wrap("hk-tag", 120, 262, 430, 84, card(p, 430, 84, "cream", 2) + '<div id="hk-tagtx">Semi-D &middot; Gurun</div>')
        + f'<div class="abs hand" id="hk-bawah" style="left:132px;top:362px">harga bawah</div>'
        + f'<div class="abs doodle" id="hk-price" style="left:124px;top:432px">RM300K</div>'
        + wrap("hk-ul", 116, 596, 680, 60, strokes(p, 680, 60, 680, 60, [(ul, 0, SUN, 13), (ul2, 1, SUN, 9)]))
        + wrap("hk-mag", 700, 250, 130, 130, strokes(p, 130, 130, 130, 130, [(mag[0], 0, PLUM, 9), (mag[1], 1, PLUM, 12)],
               extra='<circle cx="52" cy="52" r="30" fill="#ffffff" opacity="0.55"/>'))
        + wrap("hk-stamp", 572, 264, 330, 104, strokes(p, 330, 104, 330, 104, [(stamp_box, 0, CORAL, 9)],
               extra=f'<path d="{stamp_box}" fill="{CREAM}" opacity="0.92"/>') + '<div id="hk-stamptx">tak jumpa!</div>')
        + wrap("hk-sp1", 150, 640, 74, 74, sparkle(p, 74))
        + wrap("hk-sp2", 840, 628, 60, 60, sparkle(p, 60, CREAM))
        + wrap("hk-sp3", 470, 600, 46, 46, sparkle(p, 46))
    )
    js = f"""
      // frame 0 already reads as the thumbnail: price lands from 1.14x
      tl.fromTo("#hk-price", {{ scale: 1.14, transformOrigin: "0% 60%" }}, {{ scale: 1, duration: 0.7, ease: SOFT }}, 0);
      tl.fromTo("#hk-bawah", {{ x: -30 }}, {{ x: 0, duration: 0.6, ease: SOFT }}, 0);
      tl.fromTo("#hk-tag", {{ y: -14, rotation: -3 }}, {{ y: 0, rotation: -2, duration: 0.7, ease: SPR }}, 0);
      draw("#hk-ul", 0.40, 0.55);
      pop("#hk-sp1", 0.62, {{ r0: -90, r: 0 }}); pop("#hk-sp3", 0.80, {{ r0: 90 }}); pop("#hk-sp2", 0.95, {{ r0: -60 }});
      tl.to(["#hk-sp1 .dd", "#hk-sp2 .dd", "#hk-sp3 .dd"], {{ scale: 0.72, duration: 0.35, ease: "sine.inOut", yoyo: true, repeat: 4, transformOrigin: "50% 50%" }}, 1.1);
      // "pusing satu Kedah" — magnifier searches the sky
      pop("#hk-mag", {rel(B['kedah']) - 0.05:.3f}, {{ from: 0.3 }});
      tl.to("#hk-mag", {{ x: -60, y: 20, duration: 0.28, ease: "sine.inOut", yoyo: true, repeat: 2 }}, {rel(B['kedah']) + 0.2:.3f});
      out("#hk-mag", {rel(B['takjumpa']) - 0.12:.3f}, 0.14);
      // "tak jumpa dah!" stamp slams
      pop("#hk-stamp", {rel(B['takjumpa']) - 0.04:.3f}, {{ from: 1.7, r0: 4, r: 7, d: 0.6 }});
      boil("#hk-ul .b, #hk-tag .b, #hk-stamp .b, #hk-mag .b", 1.4, 0.5, 3);
"""
    SCENES.append(("hook", s, d, comp("hook", d, css, body, js, p)))


def scene_specs():
    p, s = "sp", ST["s2"]
    d = ST["s3"] - s
    rel = lambda x: round(x - s, 3)
    css = f"""
#sp-title {{ font-size:96px; }}
.chipnum {{ position:absolute; font-family:"Rubik Doodle Shadow"; font-size:104px; color:{PLUM}; filter:url(#sp-tx); line-height:1; }}
.chiplb {{ position:absolute; font-family:"Gochi Hand"; font-size:54px; color:{PLUM}; filter:url(#sp-tx); white-space:nowrap; line-height:1; }}
"""
    house = jit([(10, 62), (60, 14), (112, 62)], 1, 2)
    house2 = jit([(24, 52), (24, 110), (98, 110), (98, 52)], 2, 2)
    door = jit([(50, 110), (50, 80), (72, 80), (72, 110)], 3, 1.5)
    loop = jit([(40, 70), (60, 18), (200, 6), (340, 18), (372, 62), (330, 110), (190, 118), (40, 104), (14, 64), (60, 26), (110, 18)], 4, 4)
    bed = [(jit([(8, 92), (8, 30)], 5, 1), 0), (jit([(8, 70), (120, 70), (120, 92)], 6, 1.5), 1),
           (jit([(16, 58), (16, 46), (44, 44), (48, 58)], 7, 1), 2), (jit([(54, 58), (56, 48), (116, 50), (118, 66)], 8, 1.5), 2)]
    bath = [(jit([(6, 54), (120, 54)], 9, 1), 0), (jit([(12, 56), (22, 88), (60, 96), (104, 88), (114, 56)], 10, 1.5), 1),
            (jit([(26, 54), (26, 18), (40, 8), (54, 18)], 11, 1), 2), (jit([(36, 96), (28, 108)], 12, 1), 3), (jit([(90, 96), (98, 108)], 13, 1), 3)]
    body = (
        wrap("sp-house", 120, 280, 112, 112, strokes(p, 124, 124, 112, 112, [(house, 0, CORAL, 10), (house2, 1, PLUM, 9), (door, 2, PLUM, 8)]))
        + '<div class="abs hand" id="sp-title" style="left:250px;top:290px">Semi-D <span id="sp-clw" style="position:relative;display:inline-block">Cluster'
        + wrap("sp-loop", -46, -26, 0, 0, strokes(p, 380, 124, 0, 0, [(loop, 0, SUN, 9)]).replace('<svg ', '<svg preserveAspectRatio="none" '), "right:-40px;bottom:-34px;width:auto;height:auto")
        .replace('<div class="b" style="width:0px;height:0px">', '<div class="b" style="position:absolute;inset:0">')
        .replace('width:0px;height:0px;filter', 'width:100%;height:100%;filter')
        + '</span></div>'
        + wrap("sp-c1", 110, 430, 360, 160, card(p, 360, 160, "sun", 21)
               + '<div class="abs" style="left:24px;top:34px;width:110px;height:100px">' + strokes(p, 128, 110, 110, 95, bed, PLUM, 8) + '</div>'
               + '<div class="chipnum" style="left:156px;top:22px">4</div><div class="chiplb" style="left:232px;top:58px">bilik</div>')
        + wrap("sp-c2", 490, 430, 400, 160, card(p, 400, 160, "sky", 22)
               + '<div class="abs" style="left:24px;top:30px;width:110px;height:100px">' + strokes(p, 128, 116, 110, 100, bath, PLUM, 8) + '</div>'
               + '<div class="chipnum" style="left:156px;top:22px">2</div><div class="chiplb" style="left:234px;top:58px">tandas</div>')
    )
    js = f"""
      draw("#sp-house", 0.02, 0.5);
      write("#sp-title", 0.08, 0.7);
      draw("#sp-loop", {rel(B['cluster']) + 0.02:.3f}, 0.5);
      pop("#sp-c1", {rel(B['empat']) - 0.04:.3f}, {{ r0: -10, r: -2, y0: 40 }});
      draw("#sp-c1 .abs", {rel(B['empat']) + 0.12:.3f}, 0.45);
      pop("#sp-c2", {rel(B['dua']) - 0.04:.3f}, {{ r0: 10, r: 2, y0: 40, d: 0.7 }});
      draw("#sp-c2 .abs", {rel(B['dua']) + 0.12:.3f}, 0.45);
      tl.to(["#sp-title", "#sp-house", "#sp-loop", "#sp-c1", "#sp-c2"], {{ opacity: 0, y: -20, duration: 0.16, ease: "power2.in", stagger: 0.02 }}, {d - 0.2:.3f});
      boil("#sp-house .b, #sp-loop .b, #sp-c1 .b, #sp-c2 .b", 1.3, 0.4, 5);
"""
    SCENES.append(("specs", s, d, comp("specs", d, css, body, js, p)))


def scene_lokasi():
    p, s = "lk", ST["s3"]
    d = ST["s4"] - s
    rel = lambda x: round(x - s, 3)
    css = f"""
#lk-q {{ font-size:90px; }}
#lk-qm {{ font-size:190px; color:{LILAC}; filter:url(#lk-tx); }}
#lk-gurun {{ font-size:100px; color:#2A6FD6; }}
#lk-kedah {{ font-size:58px; color:{PLUM}; }}
#lk-taman {{ font-size:70px; }}
"""
    pin = "M60 8 Q18 8 18 50 Q18 80 60 132 Q102 80 102 50 Q102 8 60 8 Z"
    dash = jit([(20, 10), (60, 60), (130, 110), (210, 150)], 14, 3)
    arrow_hd = jit([(176, 150), (212, 152), (200, 118)], 15, 2)
    ul = jit([(6, 20), (160, 10), (330, 22), (500, 12), (560, 18)], 16, 3)
    body = (
        '<div class="abs hand" id="lk-q" style="left:120px;top:300px">dekat mana?</div>'
        + '<div class="abs doodle" id="lk-qm" style="left:640px;top:240px">?</div>'
        + wrap("lk-pin", 120, 390, 120, 140,
               f'<svg class="dd" viewBox="0 0 120 140" style="left:0;top:0;width:120px;height:140px;filter:url(#lk-cr)">'
               f'<path d="{pin}" fill="url(#lk-h-coral)" stroke="{PLUM}" stroke-width="7" stroke-linejoin="round"/>'
               f'<circle cx="60" cy="50" r="16" fill="{CREAM}" stroke="{PLUM}" stroke-width="6"/></svg>')
        + wrap("lk-shadow", 140, 528, 80, 18, f'<div style="width:80px;height:18px;border-radius:50%;background:rgba(43,30,63,0.35)"></div>')
        + '<div class="abs doodle" id="lk-gurun" style="left:262px;top:388px">GURUN</div>'
        + '<div class="abs hand" id="lk-kedah" style="left:680px;top:420px;-webkit-text-stroke:0;text-shadow:none;color:#2B1E3F;rotate:-6deg">'
          f'<span style="background:{SUN};padding:2px 14px;border-radius:10px 4px 12px 6px">Kedah</span></div>'
        + '<div class="abs hand" id="lk-taman" style="left:266px;top:500px">Taman Impian Mesra</div>'
        + wrap("lk-ul", 262, 578, 570, 36, strokes(p, 570, 36, 570, 36, [(ul, 0, CORAL, 9)]))
        + wrap("lk-arrow", 200, 540, 230, 170, strokes(p, 230, 170, 230, 170, [(dash, 0, "#ffffff", 9), (arrow_hd, 1, "#ffffff", 9)]))
    )
    js = f"""
      write("#lk-q", 0.04, 0.55);
      pop("#lk-qm", 0.12, {{ r0: -30, r: 10 }});
      tl.to("#lk-qm", {{ rotation: -8, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 3 }}, 0.9);
      out(["#lk-q", "#lk-qm"], {rel(B['gurun']) - 0.42:.3f}, 0.18);
      // pin drops on "Gurun" with a spring + squash shadow
      tl.fromTo("#lk-pin", {{ y: -520, opacity: 1 }}, {{ y: 0, duration: 0.8, ease: spring(0.38, 15, 0.8), immediateRender: true }}, {rel(B['gurun']) - 0.32:.3f});
      tl.fromTo("#lk-shadow", {{ scaleX: 0.2, opacity: 0 }}, {{ scaleX: 1, opacity: 1, duration: 0.5, ease: SOFT, immediateRender: true }}, {rel(B['gurun']) - 0.12:.3f});
      pop("#lk-gurun", {rel(B['gurun']) - 0.02:.3f}, {{ from: 0.4, y0: 30 }});
      pop("#lk-kedah", {rel(B['gurun']) + 0.28:.3f}, {{ r0: -20, r: -6 }});
      write("#lk-taman", {rel(B['taman']) - 0.05:.3f}, 0.4);
      draw("#lk-ul", {rel(B['taman']) + 0.35:.3f}, 0.3);
      draw("#lk-arrow", {rel(B['taman']) + 0.2:.3f}, 0.55);
      tl.to(["#lk-pin", "#lk-shadow", "#lk-gurun", "#lk-kedah", "#lk-taman", "#lk-ul", "#lk-arrow"], {{ opacity: 0, y: -20, duration: 0.16, ease: "power2.in", stagger: 0.015 }}, {d - 0.2:.3f});
      boil("#lk-pin .b, #lk-ul .b, #lk-arrow .b", 1.3, 0.5, 9);
"""
    SCENES.append(("lokasi", s, d, comp("lokasi", d, css, body, js, p)))


def scene_loan():
    p, s = "ln", ST["s4"]
    d = ST["s6"] - s
    rel = lambda x: round(x - s, 3)
    css = f"""
#ln-head {{ font-size:66px; }}
.lnlb {{ position:absolute; left:104px; top:2px; font-family:"Rubik Doodle Shadow"; font-size:78px; line-height:1; text-shadow:3px 4px 0 {PLUM}; }}
"""
    box = blob(74, 74, 31, 0.18, 3)
    tick = jit([(14, 40), (32, 62), (70, 6)], 32, 2)
    rows = ""
    for i, (lab, col) in enumerate((("LPPSA", "#E8452A"), ("BANK", "#2A6FD6"), ("SJKP", "#1F9A4A"))):
        rows += wrap(f"ln-r{i}", 130, 380 + i * 92, 520, 84,
                     f'<svg class="dd" viewBox="0 0 80 80" style="left:0;top:4px;width:78px;height:78px;filter:url(#ln-cr)">'
                     f'<path d="{box}" fill="{CREAM}" stroke="{PLUM}" stroke-width="6"/>'
                     f'<path class="cr" d="{tick}" stroke="{LEAF}" stroke-width="12" transform="translate(4 2)"/></svg>'
                     f'<div class="lnlb" style="color:{col}">{lab}</div>')
    body = (
        wrap("ln-card", 100, 270, 600, 380, card(p, 600, 380, "cream", 41, PLUM, 7, 0.9))
        + '<div class="abs hand" id="ln-head" style="left:134px;top:290px">loan boleh:</div>'
        + rows
    )
    js = f"""
      pop("#ln-card", 0.02, {{ from: 0.6, r0: -4, r: -1.5, y0: 30 }});
      write("#ln-head", 0.12, 0.45);
      pop("#ln-r0", {rel(B['lppsa']) - 0.04:.3f}, {{ from: 0.4, y0: 20 }});
      draw("#ln-r0", {rel(B['lppsa_ok']):.3f}, 0.28);
      pop("#ln-r1", {rel(B['bank']) - 0.04:.3f}, {{ from: 0.4, y0: 20 }});
      draw("#ln-r1", {rel(B['bank_ok']):.3f}, 0.28);
      pop("#ln-r2", {rel(B['sjkp']) - 0.04:.3f}, {{ from: 0.4, y0: 20 }});
      draw("#ln-r2", {rel(B['sjkp_ok']):.3f}, 0.28);
      tl.to("#ln-r2", {{ scale: 1.08, duration: 0.18, ease: "power2.out", yoyo: true, repeat: 1, transformOrigin: "10% 50%" }}, {rel(B['sjkp_ok']) + 0.28:.3f});
      tl.to(["#ln-card", "#ln-head", "#ln-r0", "#ln-r1", "#ln-r2"], {{ opacity: 0, scale: 0.9, duration: 0.14, ease: "power2.in" }}, {d - 0.16:.3f});
      boil("#ln-card .b, #ln-r0 .b, #ln-r1 .b, #ln-r2 .b", 1.1, 0.35, 11);
"""
    SCENES.append(("loan", s, d, comp("loan", d, css, body, js, p)))


def scene_cashback():
    p, s = "cb", ST["s6"]
    d = ST["s7"] - s
    rel = lambda x: round(x - s, 3)
    css = f"""
#cb-yp {{ font-size:66px; }}
#cb-word {{ font-size:132px; color:{SUN}; filter:url(#cb-tx); }}
#cb-tinggi {{ font-size:64px; color:{CORAL}; -webkit-text-stroke:11px #fff; text-shadow:0 5px 0 {PLUM}; }}
.coin {{ position:absolute; font-family:"Rubik Doodle Shadow"; font-size:34px; color:{PLUM}; left:0; right:0; top:22px; text-align:center; }}
"""
    import math
    cx, cy, r = 150, 150, 118
    def arc(a0, a1):
        x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}"
    gauge = strokes(p, 300, 170, 300, 170, [(arc(184, 236), 0, LEAF, 24), (arc(240, 296), 1, SUN, 24), (arc(300, 356), 2, CORAL, 24)])
    needle = (f'<svg class="dd" viewBox="0 0 300 170" style="left:0;top:0;width:300px;height:170px;filter:url(#cb-cr)">'
              f'<g id="cb-needle"><path d="M150 150 L150 52" stroke="{PLUM}" stroke-width="11" stroke-linecap="round"/></g>'
              f'<circle cx="150" cy="150" r="17" fill="{PLUM}"/></svg>')
    def coin(id_, l, t, sz):
        return wrap(id_, l, t, sz, sz,
                    f'<svg class="dd" viewBox="0 0 100 100" style="left:0;top:0;width:{sz}px;height:{sz}px;filter:url(#cb-cr)">'
                    f'<circle cx="50" cy="50" r="44" fill="url(#cb-h-sun)" stroke="{PLUM}" stroke-width="6"/>'
                    f'<circle cx="50" cy="50" r="31" fill="none" stroke="{PLUM}" stroke-width="4" opacity="0.6"/></svg>'
                    f'<div class="coin" data-layout-ignore style="font-size:{int(sz * 0.32)}px;top:{int(sz * 0.3)}px">RM</div>')
    body = (
        '<div class="abs hand" id="cb-yp" style="left:120px;top:282px">yang penting...</div>'
        + '<div class="abs doodle" id="cb-word" style="left:112px;top:352px">CASHBACK</div>'
        + coin("cb-co1", 790, 262, 96) + coin("cb-co2", 96, 486, 78) + coin("cb-co3", 812, 486, 70)
        + wrap("cb-gauge", 300, 480, 300, 170, gauge + needle)
        + '<div class="abs hand" id="cb-tinggi" style="left:600px;top:560px">TINGGI!</div>'
    )
    js = f"""
      write("#cb-yp", 0.06, 0.5);
      pop("#cb-word", {rel(B['cashback']) - 0.06:.3f}, {{ from: 0.3, r0: -6, r: -3, d: 1.0 }});
      pop("#cb-co1", {rel(B['cashback']) + 0.08:.3f}, {{ y0: -60, r0: -90 }});
      pop("#cb-co2", {rel(B['cashback']) + 0.18:.3f}, {{ y0: -60, r0: 90 }});
      pop("#cb-co3", {rel(B['cashback']) + 0.26:.3f}, {{ y0: -60, r0: -60, d: 0.7 }});
      tl.to(["#cb-co1 .dd", "#cb-co2 .dd", "#cb-co3 .dd"], {{ scaleX: 0.15, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: 3, transformOrigin: "50% 50%" }}, {rel(B['cashback']) + 0.7:.3f});
      pop("#cb-gauge", 0.3, {{ from: 0.5, y0: 30 }});
      draw("#cb-gauge", 0.35, 0.6);
      gsap.set("#cb-needle", {{ rotation: -78, svgOrigin: "150 150" }});
      tl.to("#cb-needle", {{ rotation: -30, duration: 0.4, ease: SOFT }}, 0.8);
      tl.to("#cb-needle", {{ rotation: 66, duration: 1.0, ease: spring(0.3, 14, 1.0) }}, {rel(B['tinggi']) - 0.04:.3f});
      pop("#cb-tinggi", {rel(B['tinggi']) + 0.1:.3f}, {{ from: 1.8, r0: 0, r: -7, d: 0.45 }});
      tl.to(["#cb-yp", "#cb-word", "#cb-co1", "#cb-co2", "#cb-co3", "#cb-gauge", "#cb-tinggi"], {{ opacity: 0, y: -24, duration: 0.15, ease: "power2.in", stagger: 0.01 }}, {d - 0.2:.3f});
      boil("#cb-gauge .b, #cb-co1 .b, #cb-co2 .b, #cb-co3 .b", 1.3, 0.6, 13);
"""
    SCENES.append(("cashback", s, d, comp("cashback", d, css, body, js, p)))


def scene_terhad():
    p, s = "th", ST["s7"]
    d = ST["s8"] - s
    rel = lambda x: round(x - s, 3)
    css = f"""
#th-stamptx {{ position:absolute; left:0; right:0; top:14px; text-align:center; font-family:"Rubik Doodle Shadow"; font-size:74px; color:{CORAL}; filter:url(#th-tx); white-space:nowrap; line-height:1; text-shadow:4px 5px 0 {PLUM}; top:24px; }}
#th-pel {{ font-size:70px; }}
#th-hl {{ position:absolute; left:-14px; right:-14px; top:38%; bottom:-4%; }}
"""
    hg = [(jit([(16, 8), (96, 8)], 41, 1), 0, PLUM, 10), (jit([(16, 136), (96, 136)], 42, 1), 0, PLUM, 10),
          (jit([(24, 10), (28, 46), (56, 72), (84, 46), (88, 10)], 43, 1.5), 1, PLUM, 8),
          (jit([(24, 134), (28, 98), (56, 72), (84, 98), (88, 134)], 44, 1.5), 1, PLUM, 8)]
    sand = (f'<path d="M34 128 Q56 98 78 128 Z" fill="url(#th-h-sun)"/>'
            f'<path d="M38 26 Q56 52 74 26 Z" fill="url(#th-h-sun)"/>')
    box = jit([(8, 12), (300, 4), (600, 12), (612, 64), (604, 118), (300, 126), (10, 118), (4, 64), (10, 14)], 45, 3)
    hl = blob(420, 50, 46, 0.4, 4)
    body = (
        wrap("th-hg", 118, 296, 112, 144, strokes(p, 112, 144, 112, 144, hg, extra=sand))
        + wrap("th-stamp", 250, 300, 620, 132, strokes(p, 620, 132, 620, 132, [(box, 0, CORAL, 10)],
               extra=f'<path d="{box}" fill="{CREAM}" opacity="0.93"/>') + '<div id="th-stamptx">UNIT TERHAD!</div>')
        + '<div class="abs hand" id="th-pel" style="left:128px;top:478px">jangan lepaskan '
          '<span style="position:relative;display:inline-block"><span id="th-hl">'
          f'<svg class="dd" viewBox="0 0 420 50" style="left:0;top:0;width:100%;height:100%;filter:url(#th-cr)" preserveAspectRatio="none">'
          f'<path d="{hl}" fill="url(#th-h-sun)"/></svg></span><span style="position:relative">peluang</span></span></div>'
    )
    js = f"""
      pop("#th-hg", {rel(B['unit']) - 0.04:.3f}, {{ r0: -40 }});
      draw("#th-hg", {rel(B['unit']):.3f}, 0.4);
      tl.to("#th-hg", {{ rotation: 180, duration: 0.6, ease: SPR }}, {rel(B['terhad']) + 0.3:.3f});
      pop("#th-stamp", {rel(B['terhad']) - 0.06:.3f}, {{ from: 1.9, r0: 0, r: -4, d: 0.6 }});
      write("#th-pel", {rel(B['peluang']):.3f}, 0.75);
      tl.fromTo("#th-hl", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.3, ease: "power2.out", immediateRender: true }}, {rel(B['peluang']) + 0.55:.3f});
      tl.to(["#th-hg", "#th-stamp", "#th-pel"], {{ opacity: 0, y: -20, duration: 0.15, ease: "power2.in" }}, {d - 0.18:.3f});
      boil("#th-hg .b, #th-stamp .b", 1.2, 0.45, 17);
"""
    SCENES.append(("terhad", s, d, comp("terhad", d, css, body, js, p)))


def scene_cta():
    p, s = "ct", ST["s8"]
    d = TOTAL - s
    rel = lambda x: round(x - s, 3)
    css = f"""
#ct-q {{ font-size:90px; }}
#ct-btntx {{ position:absolute; left:0; right:0; top:22px; text-align:center; font-family:"Gochi Hand"; font-size:64px; color:#fff;
  -webkit-text-stroke:10px {PLUM}; paint-order:stroke fill; white-space:nowrap; line-height:1; }}
.sum {{ position:absolute; font-family:"Gochi Hand"; font-size:50px; color:{PLUM}; white-space:nowrap; line-height:1; padding:12px 24px 14px; }}
.sum .bg {{ position:absolute; inset:0; }}
.sum .t {{ position:relative; filter:url(#ct-tx); }}
"""
    arr = lambda sd: [(jit([(40, 6), (36, 60), (40, 112)], sd, 2), 0, "#fff", 10), (jit([(14, 86), (40, 118), (68, 84)], sd + 1, 2), 1, "#fff", 10)]
    def chip(id_, l, t, w, txt, col, seed):
        return (f'<div class="sum" id="{id_}" style="left:{l}px;top:{t}px;width:{w}px">'
                f'<div class="bg"><div class="b" style="width:{w}px;height:76px">{card(p, w, 76, col, seed, PLUM, 5)}</div></div>'
                f'<div class="t">{txt}</div></div>')
    body = (
        '<div class="abs hand" id="ct-q" style="left:120px;top:286px">nak tahu detail?</div>'
        + wrap("ct-btn", 120, 398, 680, 112, card(p, 680, 112, "coral", 51, PLUM, 7) + '<div id="ct-btntx">isi maklumat di bawah</div>')
        + wrap("ct-a1", 170, 528, 80, 124, strokes(p, 80, 124, 80, 124, arr(61)))
        + wrap("ct-a2", 420, 534, 80, 124, strokes(p, 80, 124, 80, 124, arr(63)))
        + wrap("ct-a3", 670, 528, 80, 124, strokes(p, 80, 124, 80, 124, arr(65)))
        + chip("ct-s1", 120, 1000, 220, "Semi-D", "cream", 71)
        + chip("ct-s2", 356, 1000, 410, "4 bilik &middot; 2 tandas", "sun", 72)
        + chip("ct-s3", 120, 1084, 372, "bawah RM300K", "sky", 73)
        + chip("ct-s4", 120, 1168, 390, "cashback tinggi", "leaf", 74)
        + wrap("ct-sp1", 160, 636, 66, 66, sparkle(p, 66)) + wrap("ct-sp2", 820, 622, 54, 54, sparkle(p, 54, CREAM))
    )
    end = round(d, 3)
    pulse_n = max(1, int((end - rel(B['isi']) - 0.9) / 0.5))
    bob_n = max(1, int((end - rel(B['bawah']) - 0.5) / 0.36))
    js = f"""
      write("#ct-q", 0.04, 0.6);
      pop("#ct-btn", {rel(B['isi']) - 0.06:.3f}, {{ from: 0.3, r0: -5, r: -1.5 }});
      tl.to("#ct-btn", {{ scale: 1.05, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: {pulse_n * 2 - 1} }}, {rel(B['isi']) + 0.9:.3f});
      ["#ct-a1", "#ct-a2", "#ct-a3"].forEach(function (a, i) {{
        draw(a, {rel(B['bawah']) - 0.1:.3f} + i * 0.08, 0.3);
        tl.to(a, {{ y: 16, duration: 0.18, ease: "sine.inOut", yoyo: true, repeat: {bob_n * 2 - 1} }}, {rel(B['bawah']) + 0.35:.3f} + i * 0.06);
      }});
      pop("#ct-sp1", 0.5, {{ r0: -90 }}); pop("#ct-sp2", 0.7, {{ r0: 90 }});
      tl.to(["#ct-sp1 .dd", "#ct-sp2 .dd"], {{ scale: 0.7, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: 7, transformOrigin: "50% 50%" }}, 1.1);
      // summary chips take over the caption band once the voice ends
      pop("#ct-s1", {VOICE_END - s - 0.02:.3f}, {{ y0: 40, r0: -8, r: -2 }});
      pop("#ct-s2", {VOICE_END - s + 0.12:.3f}, {{ y0: 40, r0: 8, r: 1.5 }});
      pop("#ct-s3", {VOICE_END - s + 0.26:.3f}, {{ y0: 40, r0: -8, r: 1 }});
      pop("#ct-s4", {VOICE_END - s + 0.40:.3f}, {{ y0: 40, r0: 8, r: -2 }});
      boil("#ct-btn .b, #ct-a1 .b, #ct-a2 .b, #ct-a3 .b, .sum .b", 1.2, 0.4, 19);
"""
    SCENES.append(("cta", s, d, comp("cta", d, css, body, js, p)))


def scene_captions():
    p, s = "cp", 0.0
    d = VOICE_END
    css = f"""
.cap {{ position:absolute; left:116px; width:664px; bottom:{H - 1240}px; text-align:center; visibility:hidden;
  font-family:"Gochi Hand"; font-size:68px; line-height:1.1; }}
.w {{ display:inline-block; color:#fff; -webkit-text-stroke:12px {PLUM}; paint-order:stroke fill; text-shadow:0 6px 0 {PLUM};
  margin:0 2px; opacity:0; }}
.w.k {{ color:{SUN}; }}
"""
    body, js = "", ""
    for ci, (seg, words, end_src) in enumerate(CAPS):
        t0 = o(seg, words[0][1])
        t1 = o(seg, end_src)
        nxt = CAPS[ci + 1] if ci + 1 < len(CAPS) else None
        if nxt:
            t1 = min(t1, o(nxt[0], nxt[1][0][1]))
        spans = ""
        for wi, w in enumerate(words):
            k = len(w) > 2 and w[2]
            spans += (" " if wi else "") + f'<span class="w{" k" if k else ""}" id="cp{ci}w{wi}">{w[0]}</span>'
        body += f'<div class="cap" id="cp{ci}">{spans}</div>\n'
        js += f'      tl.set("#cp{ci}", {{ visibility: "visible" }}, {max(0, t0 - 0.02):.3f}); tl.set("#cp{ci}", {{ visibility: "hidden" }}, {t1:.3f});\n'
        for wi, w in enumerate(words):
            wt = max(t0, o(seg, w[1]))
            js += (f'      tl.fromTo("#cp{ci}w{wi}", {{ opacity: 0, scale: 0.55, y: 18 }}, '
                   f'{{ opacity: 1, scale: 1, y: 0, duration: 0.45, ease: SPR, immediateRender: false }}, {max(0, wt - 0.03):.3f});\n')
    SCENES.append(("captions", s, d, comp("captions", d, css, body, js, p)))


def swipe_comp():
    p = "sw"
    d = 0.56
    paths = [(jit([(-120, 1500), (300, 1100), (700, 700), (1200, 300)], 81, 20), 0, SUN, 260),
             (jit([(-120, 1900), (400, 1300), (800, 900), (1200, 600)], 82, 20), 0, CORAL, 280),
             (jit([(-120, 1100), (300, 700), (700, 300), (1200, -100)], 83, 20), 0, SKY, 260),
             (jit([(-120, 2200), (500, 1700), (900, 1300), (1200, 1100)], 84, 20), 0, LEAF, 280)]
    body = wrap("sw-s", 0, 0, W, H, strokes(p, W, H, W, H, paths))
    js = """
      var ps = gsap.utils.toArray("#sw-s .cr");
      ps.forEach(function (p, i) {
        var len = p.getTotalLength() + 4;
        gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len });
        tl.to(p, { strokeDashoffset: 0, duration: 0.24, ease: "power2.in" }, i * 0.025);
        tl.to(p, { strokeDashoffset: -len, duration: 0.24, ease: "power2.out" }, 0.3 + i * 0.025);
      });
"""
    return d, comp("swipe", d, "", body, js, p)


# ================================================================ index.html
def build():
    scene_hook(); scene_specs(); scene_lokasi(); scene_loan(); scene_cashback(); scene_terhad(); scene_cta(); scene_captions()
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    for cid, s, d, html in SCENES:
        with open(os.path.join(ROOT, "compositions", f"{cid}.html"), "w") as f:
            f.write(html)
    sw_d, sw_html = swipe_comp()
    if SWIPES:
        with open(os.path.join(ROOT, "compositions", "swipe.html"), "w") as f:
            f.write(sw_html)

    vids, auds, comps = [], [], []
    for i, sg in enumerate(EDL):
        vd = round(sg["dur"] + sg.get("extra", 0), 3)
        vids.append(f'        <video id="v{i + 1}" class="clip" src="assets/footage.mp4" muted playsinline data-start="{sg["start"]}" '
                    f'data-duration="{vd}" data-media-start="{sg["v"]}" data-track-index="0"></video>')
        chain = json.dumps({"version": 1, "nodes": [
            {"type": "highpass", "id": "vo1", "label": "Remove rumble", "params": {"frequency": 85}},
            {"type": "peaking", "id": "vo2", "label": "Presence", "params": {"frequency": 3200, "gain": 2, "q": 1}},
            {"type": "limiter", "id": "vo3", "params": {"limit": -1}}]}).replace('"', "&quot;")
        auds.append(f'      <audio id="vo{i + 1}" src="assets/voice.wav" data-start="{sg["start"]}" data-duration="{sg["dur"]}" '
                    f'data-media-start="{sg["a"][0]}" data-volume="1.0" data-fade-in="0.012" data-fade-out="0.02" '
                    f'data-fx-chain="{chain}" data-track-index="10"></audio>')
    lanes = {"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0.3}, {"t": 0.35, "v": 0.21}, {"t": VOICE_END, "v": 0.21},
        {"t": VOICE_END + 0.35, "v": 0.5}, {"t": TOTAL - 0.7, "v": 0.5}, {"t": TOTAL, "v": 0.0}]}]}
    mfx = {"version": 1, "nodes": [
        {"type": "peaking", "id": "mu1", "label": "Make room for the voice", "params": {"frequency": 2500, "gain": -5, "q": 0.8}},
        {"type": "peaking", "id": "mu2", "label": "Clear low mids", "params": {"frequency": 300, "gain": -3, "q": 1}}]}
    auds.append(f'      <audio id="music" src="assets/music/bed-lucky-acoustic.mp3" data-start="0" data-duration="{TOTAL}" '
                f'data-media-start="0" data-volume="1" data-automation="{json.dumps(lanes).replace(chr(34), "&quot;")}" '
                f'data-fx-chain="{json.dumps(mfx).replace(chr(34), "&quot;")}" data-track-index="11"></audio>')
    import subprocess
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
                     f'data-start="{at - 0.28:.3f}" data-duration="{sw_d}" data-width="{W}" data-height="{H}" data-track-index="4" '
                     f'data-track-kind="graphics" style="z-index:8"></div>')

    html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #1a1424; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 45.8%; z-index: 1; }}
      #cam video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #vign {{ position: absolute; inset: 0; z-index: 2; pointer-events: none;
        background: linear-gradient(180deg, rgba(20,14,36,0.20) 0%, rgba(20,14,36,0) 22%, rgba(20,14,36,0) 58%, rgba(20,14,36,0.22) 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}" data-fps="{FPS}" data-motion-blur="on">
      <div id="cam">
{chr(10).join(vids)}
      </div>
      <div id="vign"></div>
{chr(10).join(comps)}
{chr(10).join(auds)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      gsap.set("#cam", {{ scale: 1, x: 0 }});
{CAM_JS}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(html)
    print(f"voice {VOICE_END}s, total {TOTAL}s, segments:", {k: v for k, v in ST.items()})
    print("beats:", B)


if __name__ == "__main__":
    build()
