"""Writes index.html + compositions/*.html for the Changlun house tour.

Style: "Scrapbook Stop-Motion" - torn kraft/cream paper, scissor-cut letter tiles,
washi tape, everything animated on 12 fps steps with a 2-frame boil.
All times below are OUTPUT seconds (after the transcript cut, see edit/timeline.json).

usage: python3 edit/build_comp.py   (from the project dir)
"""
import json, os, random, html

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(PROJ, "edit", "timeline.json")))
WORDS = TL["words"]
AROLL = 77.933
ROOT_DUR = 80.0
W, H = 1080, 1920

HOOK = (0.0, 6.53)
TOUR = (6.53, 68.83)
TOUR_PARTS = [(6.53, 32.82), (32.82, 52.75), (52.75, 68.83)]
CAP_PARTS = [(6.53, 39.0), (39.0, 77.933)]
CTA = (68.83, ROOT_DUR)
CAPS = (6.53, AROLL)
WIPE = (6.25, 0.75)

def wt(i):
    return WORDS[i]["start"]

# ---------------------------------------------------------------- paper shapes
def torn(seed, jag=6, step=(3, 7)):
    """Torn-edge clip-path: x in %, edge offsets in px, so it fits any box."""
    r = random.Random(seed)
    pts = []
    x = 0.0
    while x < 100:
        pts.append(f"{x:.1f}% {r.uniform(0, jag):.1f}px")
        x += r.uniform(*step)
    y = 0.0
    while y < 100:
        pts.append(f"calc(100% - {r.uniform(0, jag*0.6):.1f}px) {y:.1f}%")
        y += r.uniform(step[0] * 3, step[1] * 3)
    x = 100.0
    while x > 0:
        pts.append(f"{x:.1f}% calc(100% - {r.uniform(0, jag):.1f}px)")
        x -= r.uniform(*step)
    y = 100.0
    while y > 0:
        pts.append(f"{r.uniform(0, jag*0.6):.1f}px {y:.1f}%")
        y -= r.uniform(step[0] * 3, step[1] * 3)
    return "polygon(" + ",".join(pts) + ")"

def cut(seed, j=7):
    """Scissor-cut quad: four slightly skewed straight edges."""
    r = random.Random(seed)
    a = lambda: f"{r.uniform(0, j):.1f}px"
    b = lambda: f"calc(100% - {r.uniform(0, j):.1f}px)"
    return f"polygon({a()} {a()},{b()} {a()},{b()} {b()},{a()} {b()})"

def burst(seed, n=22, inner=40):
    r = random.Random(seed)
    import math
    pts = []
    for k in range(n * 2):
        ang = math.pi * k / n - math.pi / 2
        rad = 50 if k % 2 == 0 else inner
        rad += r.uniform(-2.5, 2.5)
        pts.append(f"{50 + rad*math.cos(ang):.1f}% {50 + rad*math.sin(ang):.1f}%")
    return "polygon(" + ",".join(pts) + ")"

NOISE = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' seed='7' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0.32  0 0 0 0 0.25  0 0 0 0 0.17  0 0 0 0.55 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")
FIBRE = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'>"
         "<filter id='f'><feTurbulence type='fractalNoise' baseFrequency='0.012 0.09' numOctaves='2' seed='3'/>"
         "<feColorMatrix values='0 0 0 0 0.35  0 0 0 0 0.24  0 0 0 0 0.13  0 0 0 0.35 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23f)'/></svg>\")")

PALETTE = {
    "kraft": ("#C99D6E", "#2A1D12"),
    "cream": ("#F7EEDB", "#211C17"),
    "tomato": ("#E4502F", "#FFF6E6"),
    "mustard": ("#F4B33A", "#211C17"),
    "teal": ("#18766B", "#FFF6E6"),
    "ink": ("#211C17", "#F7EEDB"),
    "sky": ("#9CCBEA", "#211C17"),
    "blush": ("#F3A9B7", "#211C17"),
}

SHARED_CSS = f"""
@font-face {{ font-family: 'Permanent Marker'; src: url('assets/fonts/permanent-marker.woff2') format('woff2'); }}
@font-face {{ font-family: 'Caveat Brush'; src: url('assets/fonts/caveat-brush.woff2') format('woff2'); }}
#root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
.abs {{ position: absolute; }}
.mv {{ position: relative; display: inline-block; opacity: 0; }}
.boil {{ position: relative; display: inline-block; }}
.shad {{ position: relative; display: inline-block; filter: drop-shadow(5px 7px 0 rgba(33,22,12,.34)); }}
.core {{ position: absolute; inset: -6px; background: #FFF9EE; }}
.face {{ position: relative; display: inline-block; white-space: nowrap; }}
.face::after {{ content: ''; position: absolute; inset: 0; background-image: {NOISE}; mix-blend-mode: multiply; opacity: .55; }}
.tape {{ position: absolute; width: 120px; height: 38px; background: rgba(244,179,58,.72);
        clip-path: polygon(0 8%,6% 0,12% 10%,18% 0,24% 8%,30% 0,70% 0,76% 9%,82% 0,88% 8%,94% 0,100% 9%,100% 92%,94% 100%,88% 91%,82% 100%,76% 92%,70% 100%,30% 100%,24% 92%,18% 100%,12% 91%,6% 100%,0 92%); }}
.tape.teal {{ background: rgba(24,118,107,.6); }}
.tape.pink {{ background: rgba(243,169,183,.75); }}
.f-arch {{ font-family: 'Archivo Black', sans-serif; }}
.f-goth {{ font-family: 'League Gothic', sans-serif; }}
.f-mono {{ font-family: 'Space Mono', monospace; font-weight: 700; }}
.f-play {{ font-family: 'Playfair Display', serif; font-weight: 900; font-style: italic; }}
.f-pop {{ font-family: 'Poppins', sans-serif; font-weight: 700; }}
.f-mark {{ font-family: 'Permanent Marker', cursive; }}
.f-brush {{ font-family: 'Caveat Brush', cursive; }}
""" + "".join(f".bg-{k} {{ background-color: {v[0]}; color: {v[1]}; }}\n" for k, v in PALETTE.items())

# Runtime helpers shared by every scene: stepped ease + 2-frame boil, all pure functions of tl.time().
JS_HELPERS = """
  const tl = gsap.timeline({ paused: true });
  const STEP = (n, base) => { const f = gsap.parseEase(base || "power2.out"); return (p) => (p >= 1 ? 1 : f(Math.floor(p * n + 1e-6) / n)); };
  const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const IN = (sel, t, o) => { o = o || {}; const d = o.d || 0.34;
    tl.fromTo(sel, { opacity: 0, scale: o.s0 ?? 0.35, rotation: o.r0 ?? -14, x: o.x0 || 0, y: o.y0 ?? -50 },
      { opacity: 1, scale: 1, rotation: o.r1 ?? 0, x: 0, y: 0, duration: d, ease: STEP(Math.max(2, Math.round(d * 12)), o.ease || "back.out(2.2)") }, t); };
  const OUT = (sel, t, o) => { o = o || {}; const d = o.d || 0.25;
    tl.fromTo(sel, { opacity: 1, scale: 1, rotation: o.r1 ?? 0, x: 0, y: 0 },
      { opacity: 0, scale: o.s1 ?? 0.6, rotation: o.r2 ?? 18, x: o.x2 || 0, y: o.y2 ?? -70, duration: d, ease: STEP(3, "power2.in"), immediateRender: false }, t - d);
    tl.set(sel, { opacity: 0 }, t); };
  const BOIL = (dur) => { const els = Array.from(document.querySelectorAll("#root .boil"));
    const drv = { v: 0 };
    tl.to(drv, { v: 1, duration: dur, ease: "none", onUpdate: () => { const s = Math.floor(tl.time() * 6 + 1e-6);
      for (let i = 0; i < els.length; i++) { gsap.set(els[i], { rotation: (hash(s * 31 + i * 7) - 0.5) * 1.6, x: (hash(s * 13 + i * 3) - 0.5) * 2.6, y: (hash(s * 17 + i * 5) - 0.5) * 2.6 }); } } }, 0); };
"""

def esc(s):
    return html.escape(s, quote=True)

def piece(inner, color="cream", seed=1, pad="14px 26px", fs=44, font="f-arch", extra_face="", core=True, shape=None, tape=None):
    shape = shape or torn(seed)
    core_html = f'<div class="core" style="clip-path:{torn(seed+500, jag=9)}"></div>' if core else ""
    tape_html = ""
    if tape:
        tx, ty, tr, tc = tape
        tape_html = f'<div class="tape {tc}" style="left:{tx}px;top:{ty}px;transform:rotate({tr}deg)"></div>'
    return (f'<div class="boil"><div class="shad">{core_html}'
            f'<div class="face bg-{color} {font}" style="clip-path:{shape};padding:{pad};font-size:{fs}px;{extra_face}">{inner}</div>'
            f'</div>{tape_html}</div>')

def scene_file(cid, dur, body, script, extra_css=""):
    return f"""<template>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-duration="{dur:.3f}">
    <style>
{SHARED_CSS}
{extra_css}
    </style>
{body}
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
(function () {{
{JS_HELPERS}
{script}
  window.__timelines["{cid}"] = tl;
}})();
    </script>
  </div>
</template>
"""

SFX = []  # (abs_time_of_hit, file, peak_offset, duration, volume)
SFXMETA = {
    "flip-1": (0.246, 0.47), "flip-2": (0.291, 0.549), "flip-3": (0.082, 0.549),
    "impact-bass-1": (0.073, 2.116), "kaching": (0.375, 1.123), "marker": (0.324, 2.038),
    "pop": (0.12, 0.72), "rustle": (0.639, 3.997), "slide-1": (0.59, 1.416), "slide-2": (0.456, 1.228),
    "slide-3": (0.491, 1.176), "snip": (0.025, 0.288), "sparkle": (0.027, 1.802),
    "tear-long": (0.545, 1.411), "tear-short": (0.317, 0.408), "whoosh-short": (0.162, 0.575),
}
import subprocess
REAL_DUR = {n: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(PROJ, "assets", "sfx", n + ".mp3")], capture_output=True, text=True).stdout) - 0.06 for n in SFXMETA}
def sfx(t, name, vol=0.42, dur=None):
    SFX.append((t, name, vol, dur))

# ================================================================== HOOK
def build_hook():
    s0, s1 = HOOK
    dur = s1 - s0
    body, js = [], []
    # Ransom "FULL RENO" - each letter its own scissor-cut tile
    letters = "FULL RENO"
    fonts = ["f-arch", "f-play", "f-goth", "f-mono", "f-arch", "f-play", "f-goth", "f-arch"]
    colors = ["tomato", "cream", "mustard", "ink", "teal", "cream", "tomato", "mustard"]
    r = random.Random(11)
    x = 84
    k = 0
    for ch in letters:
        if ch == " ":
            x += 34
            continue
        size = r.choice([112, 120, 128])
        fs = {"f-goth": 140, "f-mono": 96, "f-play": 104, "f-arch": 96}[fonts[k % 8]]
        rot = r.uniform(-9, 9)
        y = 250 + r.uniform(-14, 14)
        w = size * (0.74 if fonts[k % 8] == "f-goth" else 0.86)
        body.append(f'<div class="abs" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{size}px">'
                    f'<div class="mv" id="hk-t{k}" style="width:100%;height:100%">'
                    f'<div class="boil" style="width:100%;height:100%"><div class="shad" style="width:100%;height:100%">'
                    f'<div class="face bg-{colors[k % 8]} {fonts[k % 8]}" style="clip-path:{cut(100+k)};width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:{fs}px;line-height:1;transform:rotate({rot:.1f}deg)">{ch}</div>'
                    f'</div></div></div></div>')
        x += w + 6
        k += 1
    # FULL visible on frame 0 (thumbnail); RENO lands on the word "reno"
    js.append('for (let i = 0; i < 4; i++) tl.fromTo("#hk-t" + i, {opacity:1, scale:1, rotation:0, y:0}, {opacity:1, scale:1.12, rotation:(i%2?4:-4), y:-6, duration:0.17, ease:STEP(2,"power1.out"), yoyo:true, repeat:1}, 0.18 + i*0.03);')
    t_reno = wt(2) - s0
    for i in range(4, 8):
        js.append(f'IN("#hk-t{i}", {t_reno + (i-4)*0.083:.3f}, {{d:0.25, r0:{-30 if i%2 else 30}, y0:-120, s0:1.6, ease:"power3.out"}});')
    sfx(wt(2), "pop", 0.38)
    sfx(wt(2) + 0.25, "snip", 0.35)
    # strip "dari depan -> sampai belakang"
    body.append(f'<div class="abs" style="left:64px;top:430px"><div class="mv" id="hk-strip">'
                + piece('DARI DEPAN <span id="hk-arrow" style="display:inline-block;color:#E4502F">&#10140;</span> SAMPAI BELAKANG', "cream", 21, pad="16px 30px", fs=40, font="f-arch",
                        tape=(-30, -14, -24, "")) + '</div></div>')
    js.append(f'IN("#hk-strip", {wt(5)-s0-0.05:.3f}, {{r0:-6, y0:0, x0:-420, s0:1, ease:"power3.out", d:0.33}});')
    js.append(f'tl.fromTo("#hk-arrow", {{x:-14}}, {{x:14, duration:{wt(8)-wt(6):.2f}, ease:STEP(5,"sine.inOut")}}, {wt(6)-s0:.3f});')
    sfx(wt(5) + 0.1, "slide-2", 0.4)
    # tear it all away on "Pasal"
    t_tear = wt(9) - s0 - 0.05
    for i in range(8):
        js.append(f'OUT("#hk-t{i}", {t_tear + 0.25 + i*0.025:.3f}, {{r2:{(-1)**i * 40}, y2:-260, s1:0.8, d:0.3}});')
    js.append(f'OUT("#hk-strip", {t_tear + 0.3:.3f}, {{x2:700, y2:-30, r2:12, s1:1, d:0.3}});')
    sfx(wt(9) + 0.2, "tear-long", 0.45)
    # hanging price tag: RUMAH DIJUAL / habis murah
    tag_poly = "polygon(14% 0,100% 0,100% 100%,14% 100%,0 50%)"
    body.append('<div class="abs" style="left:300px;top:250px"><div class="mv" id="hk-tag" style="transform-origin:12% 50%">'
                '<div class="boil"><div class="shad">'
                f'<div class="face bg-kraft f-arch" style="clip-path:{tag_poly};padding:26px 54px 26px 112px;font-size:58px;line-height:1.02;text-align:left">'
                '<div style="position:absolute;left:46px;top:50%;width:30px;height:30px;margin-top:-15px;border-radius:50%;background:#3B2A1C"></div>'
                'RUMAH<br>DIJUAL'
                '<div id="hk-murah" class="f-mark" style="font-size:50px;color:#E4502F;margin-top:6px;clip-path:inset(0 100% 0 0)">habis murah!</div>'
                '</div></div></div></div></div>')
    t_tag = wt(10) - s0 - 0.1
    js.append(f'IN("#hk-tag", {t_tag:.3f}, {{r0:-70, y0:-420, s0:1, d:0.42, ease:"back.out(1.6)"}});')
    js.append(f'tl.fromTo("#hk-tag", {{rotation:0}}, {{rotation:-7, duration:0.5, ease:STEP(6,"sine.inOut"), yoyo:true, repeat:3, immediateRender:false}}, {t_tag+0.42:.3f});')
    sfx(wt(10) - 0.1 + 0.3, "slide-3", 0.42)
    js.append(f'tl.fromTo("#hk-murah", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.6, ease:STEP(7,"none")}}, {wt(15)-s0:.3f});')
    sfx(wt(15) - 0.0, "marker", 0.32, dur=1.0)
    # the payoff: starburst "BAWAH MARKET VALUE"
    body.append(f'<div class="abs" style="left:150px;top:600px;width:780px;height:780px"><div class="mv" id="hk-burst" style="width:100%;height:100%">'
                f'<div class="boil" style="width:100%;height:100%"><div class="shad" style="width:100%;height:100%">'
                f'<div class="core" style="inset:-10px;clip-path:{burst(77, 24, 41)}"></div>'
                f'<div class="face bg-tomato f-arch" style="clip-path:{burst(78, 24, 42)};width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:74px;line-height:1.0;text-align:center">'
                f'<div class="f-mark" style="font-size:44px;color:#F4B33A;transform:rotate(-4deg)">harga</div>BAWAH<br>MARKET<br>VALUE</div>'
                f'</div></div></div></div>')
    t_b = wt(17) - s0 - 0.03
    js.append(f'IN("#hk-burst", {t_b:.3f}, {{s0:2.4, r0:-30, r1:-6, y0:0, d:0.25, ease:"power4.out"}});')
    js.append(f'tl.fromTo("#hk-burst", {{scale:1}}, {{scale:1.06, duration:0.17, ease:STEP(2,"power1.out"), yoyo:true, repeat:1, immediateRender:false}}, {wt(19)-s0:.3f});')
    sfx(wt(17), "impact-bass-1", 0.5)
    sfx(wt(17) + 0.02, "tear-short", 0.35)
    sfx(wt(19), "kaching", 0.4)
    js.append(f"BOIL({dur:.3f});")
    return scene_file("hook", dur, "\n".join(body), "\n".join(js))

# ================================================================== WIPE (hook -> tour)
def build_wipe():
    t0, dur = WIPE
    body, js = [], []
    cols = ["kraft", "cream", "mustard", "teal", "tomato", "kraft", "cream"]
    for i, c in enumerate(cols):
        top = -260 + i * 330
        body.append(f'<div class="abs" style="left:-60px;top:{top}px;width:1200px;height:420px"><div class="mv" id="wp-{i}" style="width:100%;height:100%">'
                    f'<div class="shad" style="width:100%;height:100%"><div class="face bg-{c}" style="width:100%;height:100%;clip-path:{torn(300+i, jag=26, step=(1.5,3.5))}"></div></div></div></div>')
        cover = 6.53 - t0  # fully covered at the cut
        js.append(f'tl.fromTo("#wp-{i}", {{opacity:1, x:-1300, rotation:-7}}, {{x:0, rotation:-7, duration:{cover-0.02 - i*0.03:.3f}, ease:STEP(4,"power3.out")}}, {i*0.03:.3f});')
        js.append(f'tl.fromTo("#wp-{i}", {{x:0}}, {{x:1350, rotation:-4, duration:0.33, ease:STEP(4,"power3.in"), immediateRender:false}}, {cover + 0.03 + i*0.025:.3f});')
    sfx(6.53, "tear-long", 0.4)
    sfx(6.36, "whoosh-short", 0.3)
    return scene_file("wipe", dur, "\n".join(body), "\n".join(js), extra_css="#root{overflow:hidden}")

# ================================================================== TOUR
def build_tour(part):
    s0, s1 = TOUR_PARTS[part]
    T0 = s0
    offu, offb, offm, offd = wt(116) - 0.12, wt(129) - 0.12, wt(151) - 0.12, wt(190) - 0.12
    dur = s1 - s0
    body, js = [], []
    flips = ["flip-1", "flip-2", "flip-3"]
    chapters = [
        ("01", "RUANG TAMU", 6.60, 19.15, "tomato"),
        ("02", "MASTER BEDROOM", wt(60) - 0.05, wt(100) - 0.12, "teal"),
        ("03", "UTILITY + LOTENG", wt(100) - 0.05, wt(116) - 0.1, "mustard"),
        ("04", "BILIK KEDUA", wt(116) - 0.05, wt(129) - 0.1, "teal"),
        ("05", "RUANG MAKAN", wt(129) - 0.05, wt(151) - 0.1, "tomato"),
        ("06", "BILIK KETIGA", wt(151) - 0.05, wt(173) - 0.1, "mustard"),
        ("07", "DAPUR", wt(173) - 0.05, wt(190) - 0.1, "teal"),
        ("08", "LAUNDRY", wt(190) - 0.05, s1 + 0.0, "tomato"),
    ]
    for i, (num, name, a, b, col) in enumerate(chapters):
        if not (s0 - 0.01 <= a < s1):
            continue
        cid = f"ch-{i}"
        body.append(f'<div class="abs" style="left:52px;top:226px"><div class="mv" id="{cid}" style="transform-origin:0% 0%">'
                    f'<div class="boil" style="display:flex;align-items:center;gap:0">'
                    f'<div class="shad"><div class="core" style="clip-path:{torn(450+i, 9)}"></div><div class="face bg-cream f-arch" style="clip-path:{torn(460+i)};padding:18px 30px 18px 34px;font-size:50px;letter-spacing:.5px">{name}</div></div>'
                    f'</div><div class="tape" style="left:40px;top:-16px;transform:rotate(-5deg)"></div></div></div>')
        js.append(f'IN("#{cid}", {a - s0:.3f}, {{r0:-24, y0:-180, s0:1, d:0.42, ease:"back.out(1.8)"}});')
        if b <= s1 + 1e-6:
            js.append(f'OUT("#{cid}", {b - s0:.3f}, {{r2:-28, y2:-240, s1:1, d:0.25}});')
        sfx(a + 0.17, flips[i % 3], 0.5)

    # generic chip helper
    def chip(cid, text, col, x, y, t_in, t_out, seed, fs=46, font="f-arch", sound="pop", vol=0.4, icon="", r0=-16, tape=None):
        if not (s0 <= t_in < s1):
            return
        body.append(f'<div class="abs" style="left:{x}px;top:{y}px"><div class="mv" id="{cid}">'
                    + piece(icon + text, col, seed, pad="14px 26px", fs=fs, font=font, tape=tape) + '</div></div>')
        js.append(f'IN("#{cid}", {t_in - s0:.3f}, {{r0:{r0}, y0:-40, s0:0.3}});')
        js.append(f'OUT("#{cid}", {t_out - s0:.3f}, {{r2:20, y2:-60}});')
        if sound:
            sfx(t_in + 0.08, sound, vol)

    CHECK = '<span style="color:#E4502F;font-family:\'Permanent Marker\';margin-right:12px">&#10003;</span>'
    if part == 0:
        # --- living room checklist card (notebook paper)
        rows = [("Siling plaster", 33), ("Skirting", 36), ("Lampu + kipas", 38)]
        card_in, card_out = wt(28) - 0.05, wt(41) - 0.1
        rows_html = "".join(f'<div id="lv-r{j}" style="opacity:0;font-family:\'Poppins\';font-weight:700;font-size:44px;line-height:72px">{CHECK}{t}</div>' for j, (t, _) in enumerate(rows))
        body.append('<div class="abs" style="left:56px;top:400px"><div class="mv" id="lv-card">'
                    '<div class="boil"><div class="shad">'
                    f'<div class="core" style="clip-path:{torn(601, 10)}"></div>'
                    f'<div class="face bg-cream" style="clip-path:{torn(602)};padding:22px 40px 26px 64px;width:560px;'
                    'background-image:repeating-linear-gradient(transparent 0 71px, rgba(30,90,160,.25) 71px 73px);background-position:0 22px;color:#211C17">'
                    '<div style="position:absolute;left:42px;top:0;bottom:0;width:3px;background:rgba(228,80,47,.55)"></div>'
                    '<div class="f-mark" style="font-size:46px;color:#18766B;line-height:66px">Siap dengan:</div>'
                    f'{rows_html}</div></div>'
                    '<div class="tape pink" style="left:220px;top:-18px;transform:rotate(3deg)"></div></div></div></div>')
        js.append(f'IN("#lv-card", {card_in - s0:.3f}, {{r0:8, y0:-80, s0:0.8, d:0.4}});')
        sfx(card_in + 0.1, "slide-1", 0.4)
        snd = ["snip", "pop", "snip"]
        for j, (t, wi) in enumerate(rows):
            js.append(f'tl.fromTo("#lv-r{j}", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:0.17, ease:STEP(2,"power2.out")}}, {wt(wi) - s0 - 0.04:.3f});')
            sfx(wt(wi), snd[j], 0.42)
        js.append(f'OUT("#lv-card", {card_out - s0:.3f}, {{r2:-14, y2:-120, s1:0.9}});')

        # --- plates joke
        plate = ('<div style="position:relative;width:250px;height:250px">'
                 f'<div class="shad" style="position:absolute;left:0;top:0"><div class="face bg-cream" style="width:250px;height:250px;border-radius:50%;clip-path:circle(49% at 50% 50%)">'
                 '<div style="position:absolute;inset:30px;border-radius:50%;border:10px solid #18766B"></div><div style="position:absolute;inset:62px;border-radius:50%;background:#EFE2C8"></div></div></div>'
                 f'<div class="shad" style="position:absolute;left:70px;top:-58px"><div class="face bg-sky" style="width:170px;height:96px;clip-path:polygon(0 0,100% 0,88% 70%,70% 100%,30% 100%,12% 70%)">'
                 '<div style="position:absolute;left:0;right:0;top:14px;height:10px;background:#18766B"></div></div></div></div>')
        body.append(f'<div class="abs" style="left:720px;top:400px"><div class="mv" id="pl"><div class="boil">{plate}</div></div></div>')
        js.append(f'IN("#pl", {wt(46) - s0 - 0.05:.3f}, {{r0:30, y0:-160, s0:0.4, d:0.34}});')
        sfx(wt(46) + 0.05, "pop", 0.4)
        body.append('<div class="abs" style="left:610px;top:640px"><div class="mv" id="pl-tag">'
                    + piece('LAGI MAHAL!', "tomato", 611, pad="12px 24px", fs=46, font="f-arch") + '</div></div>')
        js.append(f'IN("#pl-tag", {wt(56) - s0 - 0.05:.3f}, {{r0:-40, r1:-8, s0:2, y0:0, d:0.25, ease:"power4.out"}});')
        sfx(wt(56) + 0.05, "kaching", 0.36)
        body.append('<div class="abs" style="left:650px;top:740px"><div class="mv" id="pl-note">'
                    '<div class="boil f-mark" style="font-size:46px;color:#FFF6E6;text-shadow:3px 3px 0 #211C17">dari almari &#8599;</div></div></div>')
        js.append(f'IN("#pl-note", {wt(57) - s0:.3f}, {{r0:0, r1:-6, y0:20, s0:1, d:0.25}});')
        for sel in ("#pl", "#pl-tag", "#pl-note"):
            js.append(f'OUT("{sel}", {wt(60) - 0.12 - s0:.3f}, {{r2:25, x2:300, y2:-30, s1:1}});')

    # --- master bedroom: bed sizes, built-in toilet, almari
    CROWN = '<span style="display:inline-block;width:46px;height:34px;margin-right:12px;vertical-align:-2px;background:#F4B33A;clip-path:polygon(0 100%,0 20%,25% 55%,50% 0,75% 55%,100% 20%,100% 100%)"></span>'
    off = wt(85) - 0.15
    chip("ms-king", "KATIL KING", "ink", 56, 400, wt(73), off, 701, icon=CROWN, sound="pop")
    chip("ms-super", "SUPER KING &#10003;", "mustard", 56, 500, wt(76), off, 702, sound="snip")
    chip("ms-queen", "QUEEN &#10003;", "sky", 56, 600, wt(80), off, 703, sound="pop")
    off2 = wt(95) - 0.1
    chip("ms-wc", "BUILT-IN TANDAS", "teal", 56, 400, wt(82), off2, 704, sound="slide-3", vol=0.35)
    chip("ms-almari", "ALMARI DITINGGAL &#10003;", "cream", 56, 500, wt(90), off2, 705, sound="pop")
    if part == 0:
        body.append('<div class="abs" style="left:96px;top:620px"><div class="mv" id="ms-ask"><div class="boil">'
                    + piece('Nak katil? <span style="color:#E4502F">Beritahu!</span>', "cream", 706, pad="10px 26px", fs=50, font="f-brush", core=False)
                    + '</div></div></div>')
        js.append(f'IN("#ms-ask", {wt(95) - s0:.3f}, {{r0:-10, r1:-3, y0:10, s0:0.6, d:0.25}});')
        js.append(f'OUT("#ms-ask", {wt(100) - 0.12 - s0:.3f}, {{r2:-10, y2:-40}});')
        sfx(wt(98), "snip", 0.3)

    # --- utility + loft
    LADDER = ('<span style="display:inline-block;width:34px;height:46px;margin-right:12px;vertical-align:-6px;'
              'background:repeating-linear-gradient(#211C17 0 6px, transparent 6px 14px) 6px 4px/22px 40px no-repeat,'
              'linear-gradient(#211C17,#211C17) 0 0/6px 100% no-repeat, linear-gradient(#211C17,#211C17) 28px 0/6px 100% no-repeat"></span>')
    offu = wt(116) - 0.12
    chip("ut-store", "BOLEH BUAT STORE", "kraft", 56, 400, wt(109), offu, 801, sound="pop")
    chip("ut-loft", "LOTENG SIAP &#10003;", "mustard", 56, 500, wt(112), offu, 802, icon=LADDER, sound="snip")
    if part == 1:
        body.append('<div class="abs" style="left:640px;top:410px"><div class="mv" id="ut-nice"><div class="boil f-mark" style="font-size:60px;color:#F4B33A;text-shadow:3px 3px 0 #211C17;transform:rotate(-8deg)">just nice!</div></div></div>')
        js.append(f'IN("#ut-nice", {wt(107) - s0:.3f}, {{r0:-30, r1:0, y0:0, s0:0.3, d:0.25}});')
        js.append(f'OUT("#ut-nice", {offu - s0:.3f}, {{}});')

    # --- bilik 2: sun + wind
    if part == 1:
        SUN = ('<div style="position:relative;width:210px;height:210px">'
               f'<div class="shad" style="position:absolute;inset:0"><div class="face bg-mustard" style="width:210px;height:210px;clip-path:{burst(901, 14, 36)}"></div></div>'
               '<div class="shad" style="position:absolute;left:52px;top:52px"><div class="face bg-tomato" style="width:106px;height:106px;clip-path:circle(48% at 50% 50%)"></div></div></div>')
        body.append(f'<div class="abs" style="left:790px;top:390px"><div class="mv" id="b2-sun"><div class="boil" id="b2-sunspin">{SUN}</div></div></div>')
        offb = wt(129) - 0.12
        js.append(f'IN("#b2-sun", {wt(124) - s0:.3f}, {{r0:-90, y0:-100, s0:0.3, d:0.4}});')
        js.append(f'tl.fromTo("#b2-sun", {{rotation:0}}, {{rotation:60, duration:{offb - wt(124) - 0.7:.2f}, ease:STEP({int((offb - wt(124))*6)},"none"), immediateRender:false}}, {wt(124) - s0 + 0.4:.3f});')
        js.append(f'OUT("#b2-sun", {offb - s0:.3f}, {{r1:60, r2:120}});')
        sfx(wt(124) + 0.1, "pop", 0.35)
    WIND = '<span class="f-mark" style="color:#9CCBEA;margin-right:10px">&#8776;</span>'
    chip("b2-udara", "PENGUDARAAN", "teal", 56, 400, wt(126), offb, 902, icon=WIND, sound="snip")
    chip("b2-cahaya", "PENCAHAYAAN", "mustard", 56, 500, wt(128), offb, 903, icon='<span style="color:#E4502F;margin-right:10px">&#9728;</span>', sound="pop")

    # --- ruang makan
    if part == 1:
        body.append(f'<div class="abs" style="left:700px;top:380px;width:320px;height:320px"><div class="mv" id="mk-star" style="width:100%;height:100%">'
                    f'<div class="boil" style="width:100%;height:100%"><div class="shad" style="width:100%;height:100%"><div class="face bg-mustard f-arch" style="clip-path:{burst(1001, 18, 40)};width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:40px;line-height:1.05;text-align:center">PALING<br>SPESIAL</div></div></div></div></div>')
        offm = wt(151) - 0.12
        js.append(f'IN("#mk-star", {wt(139) - s0:.3f}, {{r0:-120, r1:8, y0:0, s0:0.2, d:0.34}});')
        js.append(f'OUT("#mk-star", {wt(146) - 0.1 - s0:.3f}, {{r1:8, r2:60}});')
        sfx(wt(139) + 0.05, "sparkle", 0.3)
    chip("mk-part", "SIAP PARTITION &#10003;", "cream", 56, 400, wt(143), offm, 1002, sound="pop")
    chip("mk-meja", "MEJA MAKAN: OWNER TINGGAL", "tomato", 56, 500, wt(147), offm, 1003, sound="snip", fs=42)

    # --- bilik 3 + toilet 2
    off3 = wt(173) - 0.12
    chip("b3-bujang", "BILIK BUJANG", "sky", 56, 400, wt(166), off3, 1101, sound="pop")
    chip("b3-single", "KATIL SINGLE &#10003;", "cream", 56, 500, wt(168), off3, 1102, sound="snip")
    chip("b3-wc", "+ TOILET KEDUA", "teal", 56, 600, wt(170), off3, 1103, sound="slide-3", vol=0.35)

    # --- dapur: extend + full-height cabinet arrow
    offd = wt(190) - 0.12
    chip("dp-ext", "EXTEND &#10140; BELAKANG", "mustard", 56, 400, wt(176), offd, 1201, sound="slide-2", vol=0.38)
    chip("dp-cab", "KABINET FULL", "tomato", 56, 500, wt(181), offd, 1202, sound="pop")
    if part == 2:
        body.append('<div class="abs" style="left:930px;top:470px;width:110px;height:640px"><div class="mv" id="dp-arrow" style="width:100%;height:100%">'
                    '<div class="shad" style="width:100%;height:100%"><div id="dp-arrow-face" class="face bg-tomato" style="width:100%;height:100%;'
                    'clip-path:polygon(50% 0,100% 16%,68% 16%,68% 100%,32% 100%,32% 16%,0 16%)"></div></div></div></div>')
        js.append(f'tl.fromTo("#dp-arrow", {{opacity:1, scaleY:0, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:{wt(189) - wt(185):.2f}, ease:STEP(8,"power1.inOut")}}, {wt(185) - s0:.3f});')
        js.append(f'OUT("#dp-arrow", {offd - s0:.3f}, {{y2:-200, r2:0, s1:1}});')
        sfx(wt(185) + 0.4, "slide-1", 0.36)

    # --- laundry
    chip("ld-room", "RUANG LAUNDRY", "sky", 56, 400, wt(194), s1 + 0.0, 1301, sound="pop")
    chip("ld-ext", "SIAP EXTEND &#10003;", "kraft", 56, 500, wt(198), s1 + 0.0, 1302, sound="snip")

    js.append(f"BOIL({dur:.3f});")
    return scene_file(f"tour-{part+1}", dur, "\n".join(body), "\n".join(js))

# ================================================================== CTA
def build_cta():
    s0, s1 = CTA
    dur = s1 - s0
    body, js = [], []
    CHECK = '<span style="color:#E4502F;font-family:\'Permanent Marker\';margin-right:14px">&#10003;</span>'
    # finance card
    body.append('<div class="abs" style="left:52px;top:240px"><div class="mv" id="ct-card">'
                '<div class="boil"><div class="shad">'
                f'<div class="core" style="clip-path:{torn(1401, 10)}"></div>'
                f'<div class="face bg-cream" style="clip-path:{torn(1402)};padding:30px 44px 34px 44px;width:820px;color:#211C17;white-space:normal">'
                '<div class="f-arch" style="display:inline-block;background:#18766B;color:#FFF6E6;padding:6px 18px;font-size:40px;transform:rotate(-2deg)">PEMBIAYAAN</div>'
                f'<div id="ct-r0" class="f-arch" style="opacity:0;font-size:58px;line-height:84px;margin-top:10px">{CHECK}LOAN LPPSA</div>'
                f'<div id="ct-r1" class="f-arch" style="opacity:0;font-size:58px;line-height:84px">{CHECK}LOAN BANK</div>'
                '<div id="ct-r2" style="opacity:0;font-family:\'Poppins\';font-weight:700;font-size:36px;line-height:1.3;margin-top:8px;color:#5A4632">'
                'Peniaga: <span style="background:#F4B33A;color:#211C17;padding:0 8px">SSM</span> + penyata bank 6 bulan</div>'
                '</div></div><div class="tape teal" style="left:330px;top:-18px;transform:rotate(-3deg)"></div></div></div></div>')
    js.append(f'IN("#ct-card", 0.0, {{r0:-6, y0:-200, s0:1, d:0.36, ease:"back.out(1.5)"}});')
    sfx(s0 + 0.12, "slide-1", 0.42)
    for j, wi in enumerate([201, 204, 207]):
        js.append(f'tl.fromTo("#ct-r{j}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:0.17, ease:STEP(2,"power2.out")}}, {wt(wi) - s0 - 0.03:.3f});')
        if j < 2:
            sfx(wt(wi + 1), ["snip", "pop"][j], 0.42)
    js.append(f'OUT("#ct-card", {wt(219) - 0.05 - s0:.3f}, {{r2:-20, y2:-300, s1:0.9, d:0.3}});')
    # "CEPAT!" ransom tiles
    word = "CEPAT!"
    cols = ["tomato", "mustard", "ink", "cream", "teal", "tomato"]
    fonts = ["f-arch", "f-play", "f-goth", "f-arch", "f-mono", "f-arch"]
    r = random.Random(5)
    x = 150
    for k, ch in enumerate(word):
        size = 150
        w = 118 if fonts[k] != "f-goth" else 100
        body.append(f'<div class="abs" style="left:{x}px;top:{300 + r.uniform(-16, 16):.0f}px;width:{w}px;height:{size}px"><div class="mv" id="ct-c{k}" style="width:100%;height:100%">'
                    f'<div class="boil" style="width:100%;height:100%"><div class="shad" style="width:100%;height:100%">'
                    f'<div class="face bg-{cols[k]} {fonts[k]}" style="clip-path:{cut(1500+k)};width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:{150 if fonts[k]=="f-goth" else 108}px;line-height:1;transform:rotate({r.uniform(-10, 10):.1f}deg)">{ch}</div>'
                    f'</div></div></div></div>')
        x += w + 8
        js.append(f'IN("#ct-c{k}", {wt(219) - s0 + k*0.06:.3f}, {{r0:{(-1)**k * 35}, y0:-150, s0:1.7, d:0.25, ease:"power3.out"}});')
        js.append(f'OUT("#ct-c{k}", {wt(223) - 0.05 - s0 + k*0.02:.3f}, {{r2:{(-1)**k * 40}, y2:-260, s1:0.8, d:0.25}});')
    sfx(wt(219) + 0.05, "pop", 0.4)
    sfx(wt(221), "snip", 0.35)
    # location pin + address strips
    PIN = ('<div class="shad"><div class="face bg-tomato" style="width:150px;height:200px;clip-path:path(\'M75 0 C 120 0 150 34 150 76 C 150 128 96 160 75 200 C 54 160 0 128 0 76 C 0 34 30 0 75 0 Z\')">'
           '<div style="position:absolute;left:43px;top:43px;width:64px;height:64px;border-radius:50%;background:#F7EEDB"></div></div></div>')
    body.append(f'<div class="abs" style="left:465px;top:250px"><div class="mv" id="ct-pin"><div class="boil">{PIN}</div></div></div>')
    body.append('<div class="abs" style="left:0;width:1080px;top:478px;text-align:center"><div class="mv" id="ct-addr">'
                + piece("TAMAN JELUTONG FASA 1", "cream", 1601, pad="16px 30px", fs=54, font="f-arch", tape=(-26, -12, -20, "pink")) + '</div></div>')
    body.append('<div class="abs" style="left:0;width:1080px;top:600px;text-align:center"><div class="mv" id="ct-town">'
                + piece("CHANGLUN, KEDAH", "ink", 1602, pad="12px 30px", fs=46, font="f-arch") + '</div></div>')
    body.append('<div class="abs" style="left:0;width:1080px;top:720px;text-align:center"><div class="mv" id="ct-roger">'
                + piece('Berminat? <span style="color:#E4502F">Roger je!</span>', "mustard", 1603, pad="12px 34px", fs=64, font="f-brush") + '</div></div>')
    t_pin = wt(223) - s0
    js.append(f'IN("#ct-pin", {t_pin - 0.05:.3f}, {{r0:0, y0:-420, s0:1, d:0.34, ease:"bounce.out"}});')
    js.append(f'IN("#ct-addr", {t_pin + 0.1:.3f}, {{r0:-10, r1:-2, y0:0, x0:-500, s0:1, d:0.3}});')
    js.append(f'IN("#ct-town", {wt(226) - s0:.3f}, {{r0:10, r1:2, y0:0, x0:500, s0:1, d:0.3}});')
    js.append(f'IN("#ct-roger", {wt(227) - s0:.3f}, {{r0:-20, r1:-3, y0:40, s0:0.3, d:0.3}});')
    sfx(wt(223), "slide-2", 0.42)
    sfx(wt(223) + 0.29, "pop", 0.36)
    sfx(wt(226), "flip-2", 0.42)
    sfx(wt(227) + 0.05, "sparkle", 0.32)
    # end card: once the footage ends, the stack slides to the middle of the kraft board
    t_end = AROLL - s0
    for sel in ("#ct-pin", "#ct-addr", "#ct-town", "#ct-roger"):
        js.append(f'tl.to("{sel}", {{y:300, duration:0.34, ease:STEP(4,"back.out(1.6)")}}, {t_end - 0.05:.3f});')
    sfx(AROLL, "flip-3", 0.38)
    js.append(f"BOIL({dur:.3f});")
    return scene_file("cta", dur, "\n".join(body), "\n".join(js))

# ================================================================== CAPTIONS
GROUPS = [
    (20, 24, "Sekarang ni kita duduk-duduk", None), (25, 27, "kat ruang tamu", "tamu"),
    (28, 30, "Nampak ruang tamu", None), (31, 34, "siap dengan siling plaster", "plaster"),
    (35, 36, "ada skirting", "skirting"), (37, 40, "ada lampu, siap kipas", "kipas"),
    (41, 44, "Barang ni akan tinggal", "tinggal"),
    (45, 47, "Cuma pinggan mangkuk", "pinggan"), (48, 50, "ni ambil lah", None),
    (51, 54, "Sebab pinggan mangkuk ni", None), (55, 56, "lagi mahal", "mahal"), (57, 59, "daripada almari ni", "almari"),
    (60, 62, "Okey, kita tengok", None), (63, 65, "di bilik ni,", None), (66, 67, "master bedroom", "master"),
    (68, 70, "Master bedroom ni", None), (71, 72, "boleh memakai", None), (73, 74, "katil king", "king"),
    (75, 78, "ataupun super king pun lepas", "super"), (79, 81, "ataupun queen pun lepas", "queen"),
    (82, 84, "Built-in satu", "Built-in"), (85, 88, "Satu tandas yang cantik", "cantik"),
    (89, 94, "Okey, almari pun akan tinggal", "almari"), (95, 99, "Kalau anda nak katil, beritahu", "beritahu"),
    (100, 104, "Sebelah sini kita ada utility", "utility"), (105, 108, "Utility pun just nice", "nice"),
    (109, 111, "Boleh buat store", "store"), (112, 115, "Ada satu loteng siap", "loteng"),
    (116, 120, "Okey, ni bilik yang kedua", "kedua"), (121, 122, "pun cantik", "cantik"),
    (123, 125, "Ada ruang untuk", None), (126, 128, "pengudaraan dan pencahayaan", "pencahayaan"),
    (129, 131, "Okey, kita tengok", None), (132, 136, "di ruang makan, ruang dapur", "makan"),
    (137, 140, "Yang ni paling spesial", "spesial"), (141, 142, "paling cantik", "cantik"),
    (143, 145, "Siap dengan partition", "partition"), (146, 148, "Okey, meja makan", "meja"), (149, 150, "Owner tinggal", "Owner"),
    (151, 155, "Haa, ni kita tengok ni", None), (156, 159, "ruang bilik nombor tiga", "tiga"),
    (160, 163, "Haa, bilik nombor tiga", None), (164, 167, "boleh memakai bilik bujang", "bujang"), (168, 169, "Katil single", "single"),
    (170, 172, "Toilet yang kedua", "Toilet"),
    (173, 175, "Haa, ruang dapur", "dapur"), (176, 180, "Siap extend sampai ke belakang", "extend"),
    (181, 184, "Dapat kitchen cabinet full", "full"), (185, 189, "daripada bawah sampai ke atas", "atas"),
    (190, 193, "Lepas tu, yang ni", None), (194, 195, "ruang laundry", "laundry"), (196, 197, "Okey, belakang", None),
    (198, 200, "Siap dengan extend", "extend"),
    (201, 203, "Loan LPPSA boleh,", "LPPSA"), (204, 206, "loan bank boleh", "bank"), (207, 209, "Yang mana berniaga,", None),
    (210, 213, "perlu SSM", "SSM"), (214, 218, "dan statement bank 6 bulan", "6 bulan"),
    (219, 222, "Cepat, jangan lepaskan peluang", "peluang"),
    (223, 226, "Taman Jelutong, Changlun", "Changlun"), (227, 228, "Roger sahaja", "Roger"), (229, 230, "Bye bye!", None),
]

def build_captions(part):
    s0, s1 = CAP_PARTS[part]
    dur = s1 - s0
    body, js = [], []
    for g, (a, b, text, key) in enumerate(GROUPS):
        t_in = wt(a) - 0.06
        if not (s0 <= t_in + 0.06 < s1):
            continue
        t_out = WORDS[b]["end"] + 0.12
        if g + 1 < len(GROUPS):
            t_out = min(t_out + 0.25, wt(GROUPS[g + 1][0]) - 0.07)
        t_out = min(t_out, s1 - 0.01)
        t_in = max(t_in, s0 + 0.0)
        chars = len(text)
        fs = max(44, min(64, int(780 / (chars * 0.6))))
        t_html = esc(text)
        if key:
            t_html = t_html.replace(esc(key), f'<span class="hl">{esc(key)}</span>', 1)
        rot = (-1.4, 1.1, -0.6, 1.6)[g % 4]
        col = "cream"
        body.append(f'<div class="abs cap" style="left:100px;width:820px;bottom:640px;text-align:center"><div class="mv" id="cp-{g}">'
                    f'<div class="shad">'
                    f'<div class="face bg-{col} f-pop" style="clip-path:{torn(2100+g, 5)};padding:10px 26px 12px;font-size:{fs}px;line-height:1.15;transform:rotate({rot}deg)">{t_html}</div></div>'
                    f'</div></div>')
        js.append(f'tl.fromTo("#cp-{g}", {{opacity:0, scale:0.7, y:14}}, {{opacity:1, scale:1, y:0, duration:0.12, ease:STEP(2,"back.out(2)")}}, {t_in - s0:.3f});')
        js.append(f'tl.set("#cp-{g}", {{opacity:0}}, {t_out - s0:.3f});')
    css = ".hl { background: #F4B33A; padding: 0 8px; margin: 0 -2px; box-shadow: 2px 3px 0 rgba(33,22,12,.35); display:inline-block; transform: rotate(-2deg); }"
    return scene_file(f"captions-{part+1}", dur, "\n".join(body), "\n".join(js), extra_css=css)

# ================================================================== INDEX
def build_index():
    tape_corners = "".join(
        f'<div class="tape{c}" style="left:{x}px;top:{y}px;transform:rotate({r}deg);width:170px;height:46px"></div>'
        for x, y, r, c in [(-30, 30, -38, ""), (940, 30, 38, " teal"), (-30, 1850, 38, " pink"), (940, 1850, -38, "")])
    sfx_html = []
    lane_end = []
    for i, (t, name, vol, dur) in enumerate(sorted(SFX)):
        peak, _ = SFXMETA[name]
        fdur = REAL_DUR[name]
        start = round(t - peak + 1 / 30, 3)
        d = min(dur or fdur, fdur)
        if start < 0:
            start = 0.0
        d = round(min(d, ROOT_DUR - start), 3)
        lane = next((k for k, e in enumerate(lane_end) if e <= start), None)
        if lane is None:
            lane_end.append(0); lane = len(lane_end) - 1
        lane_end[lane] = start + d
        sfx_html.append(f'      <audio id="sfx-{i:02d}" class="clip" src="assets/sfx/{name}.mp3" data-start="{start}" data-duration="{d:.3f}" data-volume="{vol}" data-track-index="{10 + lane}" data-audio-group="sfx"></audio>')
    music_auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0.19}, {"t": 6.35, "v": 0.19}, {"t": 6.55, "v": 0.32}, {"t": 6.9, "v": 0.17},
        {"t": 77.6, "v": 0.17}, {"t": 78.1, "v": 0.5}, {"t": ROOT_DUR, "v": 0.5}]}]}).replace('"', "&quot;")
    music_fx = json.dumps({"version": 1, "nodes": [
        {"type": "highpass", "id": "m1", "label": "Clear the low end", "params": {"frequency": 55}},
        {"type": "peaking", "id": "m2", "label": "Room for the voice", "params": {"frequency": 2500, "gain": -4, "q": 0.9}},
        {"type": "limiter", "id": "m3", "params": {"limit": -1}}]}).replace('"', "&quot;")
    hosts = [("hook", HOOK[0], HOOK[1] - HOOK[0], 3, 10, "graphics"), ("wipe", WIPE[0], WIPE[1], 7, 40, "graphics")]
    hosts += [(f"tour-{k+1}", a, b - a, 4, 10, "graphics") for k, (a, b) in enumerate(TOUR_PARTS)]
    hosts += [("cta", CTA[0], CTA[1] - CTA[0], 5, 10, "graphics")]
    hosts += [(f"captions-{k+1}", a, b - a, 6, 20, "captions") for k, (a, b) in enumerate(CAP_PARTS)]
    host_html = "\n".join(
        f'      <div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" data-start="{a:.3f}" data-duration="{d:.3f}" '
        f'data-track-index="{ti}" data-track-kind="{kind}" data-width="{W}" data-height="{H}" style="z-index:{z}"></div>'
        for h, a, d, ti, z, kind in hosts)
    return f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #C99D6E; }}
      #root {{ width: 100%; height: 100%; position: relative; }}
      #board {{ position: absolute; inset: 0; background-color: #C99D6E; background-image: {FIBRE}, {NOISE}; }}
      #frame {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 1;
               background-color: #EFE0C4; background-image: repeating-linear-gradient(transparent 0 78px, rgba(30,90,160,.16) 78px 80px), {NOISE}; }}
      #aroll {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
      #tapes {{ position: absolute; inset: 0; z-index: 2; }}
      .tape {{ position: absolute; background: rgba(244,179,58,.72);
        clip-path: polygon(0 8%,6% 0,12% 10%,18% 0,24% 8%,30% 0,70% 0,76% 9%,82% 0,88% 8%,94% 0,100% 9%,100% 92%,94% 100%,88% 91%,82% 100%,76% 92%,70% 100%,30% 100%,24% 92%,18% 100%,12% 91%,6% 100%,0 92%); }}
      .tape.teal {{ background: rgba(24,118,107,.62); }}
      .tape.pink {{ background: rgba(243,169,183,.78); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{ROOT_DUR}" data-width="{W}" data-height="{H}">
      <div id="board"></div>
      <div id="frame">
        <video id="aroll" class="clip" src="assets/aroll.mp4" data-start="0" data-duration="{AROLL}" data-track-index="0" muted playsinline></video>
      </div>
{host_html}
      <audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{AROLL}" data-volume="1" data-track-index="1" data-audio-group="voiceover"></audio>
      <audio id="music" class="clip" src="assets/music/airplane-mode.mp3" data-start="0" data-duration="{ROOT_DUR}" data-media-start="50.07" data-fx-chain="{music_fx}" data-volume="1" data-fade-out="1.1" data-track-index="2" data-timeline-role="music" data-audio-group="music" data-automation="{music_auto}"></audio>
{chr(10).join(sfx_html)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    os.makedirs(os.path.join(PROJ, "compositions"), exist_ok=True)
    files = {"compositions/hook.html": build_hook(), "compositions/wipe.html": build_wipe(), "compositions/cta.html": build_cta()}
    for k in range(len(TOUR_PARTS)):
        files[f"compositions/tour-{k+1}.html"] = build_tour(k)
    for k in range(len(CAP_PARTS)):
        files[f"compositions/captions-{k+1}.html"] = build_captions(k)
    files["index.html"] = build_index()
    for p, s in files.items():
        open(os.path.join(PROJ, p), "w").write(s)
    print("wrote", ", ".join(files), "| sfx:", len(SFX))
