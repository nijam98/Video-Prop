"""Build the Kulim "Pop-Art Komik" edit: index.html + compositions/*.html.

Edit copy and timings in the SCENES / SFX lists, then run:  python3 build.py
All times are seconds on the cut timeline (assets/footage.mp4 + assets/voice.wav, 60.0 s).

Look: Silver-age pop-art comic. Ben-Day halftone dots, CMYK inks (cyan / magenta / yellow / black)
on cream paper, jagged starbursts, yellow narration boxes, misregistered print shadows,
panel-slice wipes. Info graphics move on Remotion-style springs (odometer counters,
checklists, progress bars).

Safe zone (TikTok + IG Reels): every word sits inside x 72-900, y 240-1300.
No face is in the footage (POV walk-through), so graphics may use the middle band.
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
TOTAL = 60.0

C, M, Y, K, P, WHT = "#00B4EF", "#FF2D8A", "#FFE500", "#111111", "#FFF6DE", "#FFFFFF"
RED = "#FF3B2F"

FONT = """
    @font-face { font-family: 'Bangers'; src: url('assets/fonts/Bangers.woff2') format('woff2'); }
    @font-face { font-family: 'ComicNeue'; src: url('assets/fonts/ComicNeue-700.woff2') format('woff2'); font-weight: 700; }
"""

CSS = f"""
    #root {{ position: absolute; inset: 0; pointer-events: none; color: {K}; font-family: 'ComicNeue', sans-serif; }}
    .a {{ position: absolute; }}
    .bang {{ position: absolute; font-family: 'Bangers', sans-serif; color: {WHT}; white-space: nowrap; line-height: 0.92;
             letter-spacing: 0.02em; -webkit-text-stroke: 12px {K}; paint-order: stroke fill;
             text-shadow: -6px -4px 0 {C}, 10px 10px 0 {K}; }}
    .bang.y {{ color: {Y}; }}
    .bang.m {{ color: {M}; }}
    .box {{ position: absolute; background: {Y}; border: 7px solid {K}; box-shadow: 10px 10px 0 {K};
            font-weight: 700; text-transform: uppercase; white-space: nowrap; padding: 10px 26px 8px; line-height: 1.05; }}
    .card {{ position: absolute; background: {P}; border: 8px solid {K}; box-shadow: 14px 14px 0 {K}; }}
    .dots {{ background-image: radial-gradient(circle, rgba(17,17,17,0.22) 30%, transparent 33%); background-size: 18px 18px; }}
    .dotsw {{ background-image: radial-gradient(circle, rgba(255,255,255,0.35) 30%, transparent 33%); background-size: 18px 18px; }}
    .lbl {{ position: absolute; font-family: 'Bangers', sans-serif; white-space: nowrap; line-height: 1; letter-spacing: 0.03em; }}
    .odo {{ position: absolute; overflow: hidden; }}
    .odo .col {{ position: absolute; left: 0; top: 0; display: flex; flex-direction: column; }}
    .odo .col span {{ display: block; text-align: center; }}
"""

# Remotion-style spring as a GSAP ease. The tween's duration must equal `dur` so the
# physics plays in real seconds. Defaults match Remotion's spring() (damping 10, stiffness 100).
SPRING_JS = """
    const spr = (damping = 10, stiffness = 100, mass = 1, dur = 1) => {
      const w = Math.sqrt(stiffness / mass), z = damping / (2 * Math.sqrt(stiffness * mass));
      const wd = w * Math.sqrt(Math.max(1e-6, 1 - z * z));
      return (p) => {
        const t = p * dur;
        if (p >= 1) return 1;
        if (z < 1) return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
        return 1 - Math.exp(-w * t) * (1 + w * t);
      };
    };
    const SP = (sel, from, to, at, cfg = {}) => {
      const d = cfg.dur || 1.0;
      tl.fromTo(sel, from, Object.assign({}, to, { duration: d, ease: spr(cfg.damping || 10, cfg.stiffness || 100, 1, d) }), at);
    };
"""


def burst(sid, w, h, fill, points=14, inner=0.62, jitter=0.10, stroke=10, dots=True, seed=1):
    """Jagged comic starburst as inline SVG (deterministic)."""
    cx, cy = w / 2, h / 2
    rx, ry = w / 2 - stroke, h / 2 - stroke
    pts = []
    n = points * 2
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        j = 1 + jitter * math.sin(seed * 12.9898 + i * 78.233)
        r = (1.0 if i % 2 == 0 else inner) * j
        pts.append(f"{cx + rx * r * math.cos(a):.1f},{cy + ry * r * math.sin(a):.1f}")
    pat = ""
    over = ""
    if dots:
        pat = (f'<defs><pattern id="ht-{sid}" width="18" height="18" patternUnits="userSpaceOnUse">'
               f'<circle cx="9" cy="9" r="3.4" fill="rgba(17,17,17,0.22)"/></pattern></defs>')
        over = f'<polygon points="{" ".join(pts)}" fill="url(#ht-{sid})"/>'
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0;overflow:visible">{pat}'
            f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{K}" stroke-width="{stroke}" stroke-linejoin="miter"/>{over}</svg>')


def speedlines(w, h, n=28, color=K, inner=0.42, seed=3):
    cx, cy = w / 2, h / 2
    out = []
    for i in range(n):
        a = i * 2 * math.pi / n + 0.07 * math.sin(i * seed)
        r0 = inner * (0.9 + 0.2 * abs(math.sin(i * 1.7 + seed)))
        x0, y0 = cx + cx * r0 * math.cos(a), cy + cy * r0 * math.sin(a)
        x1, y1 = cx + cx * 1.05 * math.cos(a), cy + cy * 1.05 * math.sin(a)
        wdt = 6 + 6 * abs(math.sin(i * 2.3))
        out.append(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="{color}" stroke-width="{wdt:.0f}" stroke-linecap="round"/>')
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0;overflow:visible">{"".join(out)}</svg>'


def check(size, fill=M):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" style="position:absolute;left:0;top:0">'
            f'<circle cx="50" cy="50" r="44" fill="{fill}" stroke="{K}" stroke-width="8"/>'
            f'<path d="M28 52 L44 68 L74 34" fill="none" stroke="{WHT}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def pin(size):
    return (f'<svg width="{size}" height="{size * 1.3:.0f}" viewBox="0 0 100 130" style="position:absolute;left:0;top:0;overflow:visible">'
            f'<path d="M50 125 C50 125 8 72 8 46 A42 42 0 1 1 92 46 C92 72 50 125 50 125 Z" fill="{RED}" stroke="{K}" stroke-width="8" stroke-linejoin="round"/>'
            f'<circle cx="50" cy="46" r="17" fill="{P}" stroke="{K}" stroke-width="7"/></svg>')


def odometer(oid, text, x, y, fs, color, stroke_px=8, digit_w=None):
    """Slot-machine digits. Each digit column holds 0-9 twice; the column is animated to its target."""
    dw = digit_w or int(fs * 0.56)
    lh = int(fs * 1.0)
    cols, xs = [], 0
    for i, ch in enumerate(text):
        style = (f"font-family:'Bangers',sans-serif;font-size:{fs}px;line-height:{lh}px;color:{color};"
                 f"-webkit-text-stroke:{stroke_px}px {K};paint-order:stroke fill;")
        if ch.isdigit():
            nums = "".join(f"<span style='height:{lh}px;width:{dw}px'>{n % 10}</span>" for n in range(20))
            cols.append(f'<div class="odo" style="left:{xs}px;top:0;width:{dw}px;height:{lh}px;">'
                        f'<div id="{oid}-d{i}" class="col" style="{style}">{nums}</div></div>')
            xs += dw
        else:
            cw = int(fs * 0.3) if ch in ",." else dw
            cols.append(f'<div class="a" style="left:{xs}px;top:0;width:{cw}px;height:{lh}px;text-align:center;{style}">{ch}</div>')
            xs += cw
    html = f'<div id="{oid}" class="a" style="left:{x}px;top:{y}px;width:{xs}px;height:{lh}px;">{"".join(cols)}</div>'
    return html, lh, xs


def odo_js(oid, text, lh, at, stagger=0.07, dur=1.3):
    """Spin each digit column from 0 up to (10 + digit) so every column rolls a full turn."""
    js, k = [], 0
    for i, ch in enumerate(text):
        if ch.isdigit():
            target = 10 + int(ch)
            js.append(f'    tl.fromTo("#{oid}-d{i}", {{ y: 0 }}, {{ y: -{target * lh}, duration: {dur}, ease: spr(26, 120, 1, {dur}) }}, {at + k * stagger:.3f});')
            k += 1
    return "\n".join(js) + "\n"


def scene(sid, dur, body, js):
    return f"""<template>
  <style>{FONT}{CSS}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-layout-allow-overlap data-layout-allow-overflow>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{SPRING_JS}
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


def out(sel, t, d=0.22):
    return f'    tl.to("{sel}", {{ scale: 0.6, opacity: 0, duration: {d}, ease: "back.in(2)", stagger: 0.03 }}, {t:.3f});\n'


SCENES = []  # (id, start, dur, body, js) ; js times are relative to the scene start


# ---------------------------------------------------------------- 1. HOOK 0.00 - 4.37
# "Nak cari rumah fully renovated dekat kawasan Kulim? Ini masanya, ini rumahnya."
s0 = 0.0
SCENES.append(("hook", s0, 4.40, f"""
    <div id="hk-frame" class="a" style="left:0;top:0;width:{W}px;height:{H}px;border:22px solid {P};box-shadow: inset 0 0 0 10px {K};"></div>
    <div id="hk-tag" class="box" style="left:84px;top:252px;font-size:40px;transform-origin:0 50%;">misi hari ini:</div>
    <div id="hk-t1" class="bang" style="left:84px;top:342px;font-size:118px;transform-origin:0 50%;">NAK CARI RUMAH</div>
    <div id="hk-t2" class="bang y" style="left:84px;top:464px;font-size:150px;transform-origin:0 50%;">FULLY RENOVATED?</div>
    <div id="hk-b1" class="a" style="left:330px;top:640px;width:560px;height:330px;transform-origin:50% 50%;">
      {burst("hk1", 560, 330, M, points=13, inner=0.7, seed=2)}
      <div class="bang" style="left:0;top:96px;width:560px;text-align:center;font-size:132px;">KULIM?!</div>
    </div>
    <div id="hk-masa" class="box" style="left:96px;top:300px;font-size:84px;background:{C};transform-origin:0 50%;">INI MASANYA!</div>
    <div id="hk-sl" class="a" style="left:40px;top:430px;width:1000px;height:760px;opacity:0;">{speedlines(1000, 760, n=34)}</div>
    <div id="hk-b2" class="a" style="left:110px;top:470px;width:860px;height:640px;transform-origin:50% 50%;">
      {burst("hk2", 860, 640, Y, points=16, inner=0.68, seed=5)}
      <div class="bang" style="left:0;top:200px;width:860px;text-align:center;font-size:96px;">INI</div>
      <div class="bang m" style="left:0;top:290px;width:860px;text-align:center;font-size:150px;">RUMAHNYA!</div>
    </div>
""", f"""
    SP("#hk-t1", {{ scale: 0.9, rotation: -2 }}, {{ scale: 1, rotation: -2 }}, 0, {{ dur: 0.9 }});
    SP("#hk-t2", {{ scale: 0.86, rotation: -2 }}, {{ scale: 1, rotation: -2 }}, 0.05, {{ dur: 0.9 }});
    SP("#hk-tag", {{ x: -40 }}, {{ x: 0 }}, 0, {{ dur: 0.8 }});
    SP("#hk-b1", {{ scale: 0, rotation: -25 }}, {{ scale: 1, rotation: 6 }}, 1.62, {{ dur: 0.9, damping: 9, stiffness: 180 }});
{out("#hk-tag, #hk-t1, #hk-t2", 2.06)}{out("#hk-b1", 2.62)}
    SP("#hk-masa", {{ x: -820, rotation: -8 }}, {{ x: 0, rotation: -4 }}, 2.18, {{ dur: 0.8, damping: 11, stiffness: 190 }});
    tl.fromTo("#hk-sl", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 0.9, scale: 1.08, duration: 0.9, ease: "power2.out" }}, 3.12);
    SP("#hk-b2", {{ scale: 0, rotation: 18 }}, {{ scale: 1, rotation: -3 }}, 3.12, {{ dur: 1.0, damping: 8, stiffness: 160 }});
    tl.to("#hk-b2", {{ scale: 1.06, duration: 0.5, ease: "sine.inOut" }}, 3.75);
"""))


# ---------------------------------------------------------------- 2. LOKASI 4.37 - 7.62
s0 = 4.37
SCENES.append(("lokasi", s0, 3.20, f"""
    <div id="lk-card" class="card dots" style="left:96px;top:300px;width:700px;height:250px;background-color:{P};"></div>
    <div id="lk-pin" class="a" style="left:130px;top:250px;width:150px;height:195px;transform-origin:50% 100%;">{pin(150)}</div>
    <div id="lk-t1" class="lbl" style="left:310px;top:330px;font-size:44px;color:{K};">KAWASAN</div>
    <div id="lk-t2" class="bang y" style="left:306px;top:380px;font-size:132px;">KULIM</div>
    <div id="lk-row" class="a" style="left:120px;top:610px;width:760px;height:120px;">
      <div class="a" style="left:0;top:0;width:110px;height:110px;">{check(110)}</div>
      <div class="box" style="left:130px;top:10px;font-size:56px;background:{WHT};">dekat semua kemudahan</div>
    </div>
""", f"""
    SP("#lk-card", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1 }}, 0.0, {{ dur: 0.9, damping: 14, stiffness: 140 }});
    tl.set("#lk-pin", {{ y: -500, scaleY: 1 }}, 0);
    SP("#lk-pin", {{ y: -500 }}, {{ y: 0 }}, 0.05, {{ dur: 1.1, damping: 8, stiffness: 140 }});
    tl.fromTo("#lk-pin", {{ scaleY: 0.82 }}, {{ scaleY: 1, duration: 0.3, ease: "back.out(3)", immediateRender: false }}, 0.42);
    SP("#lk-t1", {{ x: 60, opacity: 0 }}, {{ x: 0, opacity: 1 }}, 0.15, {{ dur: 0.8 }});
    SP("#lk-t2", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1 }}, 0.25, {{ dur: 0.9, damping: 9, stiffness: 170 }});
    SP("#lk-row", {{ x: -1300 }}, {{ x: 0 }}, {6.25 - s0:.2f}, {{ dur: 0.9, damping: 13, stiffness: 160 }});
{out("#lk-row, #lk-t2, #lk-t1, #lk-pin, #lk-card", 2.92)}"""))


# ---------------------------------------------------------------- 3. RENO 7.62 - 11.45
s0 = 7.62
SCENES.append(("reno", s0, 3.85, f"""
    <div id="rn-b" class="a" style="left:80px;top:280px;width:900px;height:430px;transform-origin:50% 50%;">
      {burst("rn1", 900, 430, M, points=15, inner=0.74, seed=7)}
      <div class="bang y" style="left:0;top:92px;width:900px;text-align:center;font-size:128px;">FULLY</div>
      <div class="bang" style="left:0;top:206px;width:900px;text-align:center;font-size:128px;">RENOVATED!</div>
    </div>
    <div id="rn-bar" class="a" style="left:110px;top:760px;width:780px;height:150px;">
      <div class="lbl" style="left:0;top:0;font-size:44px;color:{WHT};-webkit-text-stroke:8px {K};paint-order:stroke fill;">DEPAN</div>
      <div class="lbl" style="left:780px;top:0;font-size:44px;color:{WHT};-webkit-text-stroke:8px {K};paint-order:stroke fill;transform:translateX(-100%);">BELAKANG</div>
      <div class="a" style="left:0;top:62px;width:780px;height:62px;background:{P};border:7px solid {K};box-shadow:8px 8px 0 {K};"></div>
      <div id="rn-fill" class="a dots" style="left:7px;top:69px;width:766px;height:48px;background-color:{Y};transform-origin:0 50%;"></div>
    </div>
    <div id="rn-q" class="a" style="left:470px;top:300px;width:430px;height:250px;">
      <svg width="430" height="250" viewBox="0 0 430 250" style="position:absolute;left:0;top:0;overflow:visible">
        <ellipse cx="215" cy="110" rx="205" ry="100" fill="{WHT}" stroke="{K}" stroke-width="8"/>
        <circle cx="90" cy="222" r="18" fill="{WHT}" stroke="{K}" stroke-width="7"/>
        <circle cx="55" cy="246" r="10" fill="{WHT}" stroke="{K}" stroke-width="6"/>
      </svg>
      <div class="lbl" style="left:0;top:66px;width:430px;text-align:center;font-size:84px;color:{K};">CANTIK TAK?</div>
    </div>
    <div id="rn-yes" class="a" style="left:150px;top:420px;width:560px;height:330px;transform-origin:50% 50%;">
      {burst("rn2", 560, 330, Y, points=12, inner=0.7, seed=9)}
      <div class="bang m" style="left:0;top:96px;width:560px;text-align:center;font-size:140px;">CANTIK!</div>
    </div>
""", f"""
    SP("#rn-b", {{ scale: 0, rotation: -14 }}, {{ scale: 1, rotation: -3 }}, 0.0, {{ dur: 1.0, damping: 8, stiffness: 170 }});
    tl.fromTo("#rn-bar", {{ y: 80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, {8.70 - s0:.2f});
    SP("#rn-fill", {{ scaleX: 0 }}, {{ scaleX: 1 }}, {9.00 - s0:.2f}, {{ dur: 1.0, damping: 18, stiffness: 90 }});
{out("#rn-b, #rn-bar", 10.0 - s0)}
    SP("#rn-q", {{ scale: 0, transformOrigin: "20% 100%" }}, {{ scale: 1 }}, {10.38 - s0:.2f}, {{ dur: 0.6, damping: 10, stiffness: 200 }});
    tl.to("#rn-q", {{ scale: 0.7, opacity: 0, duration: 0.15, ease: "power2.in" }}, {10.98 - s0:.2f});
    SP("#rn-yes", {{ scale: 0, rotation: 20 }}, {{ scale: 1, rotation: -5 }}, {11.04 - s0:.2f}, {{ dur: 0.58, damping: 9, stiffness: 260 }});
    tl.to("#rn-yes", {{ scale: 0, rotation: 30, duration: 0.2, ease: "back.in(2)" }}, {11.62 - s0:.2f});
"""))


# ---------------------------------------------------------------- 4. CHECKLIST 11.50 - 17.10
s0 = 11.75
ITEMS = [("PLASTER CEILING", 12.34), ("SAMPAI KE BELAKANG", 13.92), ("LAMPU", 15.30), ("GRILL", 15.90)]
rows, rjs = [], []
for i, (txt, t) in enumerate(ITEMS):
    y = 410 + i * 128
    rows.append(f"""    <div id="ck-r{i}" class="a" style="left:118px;top:{y}px;width:760px;height:110px;">
      <div id="ck-c{i}" class="a" style="left:0;top:4px;width:96px;height:96px;transform-origin:50% 50%;">{check(96, M if i % 2 == 0 else C)}</div>
      <div class="lbl" style="left:120px;top:18px;font-size:76px;color:{K};">{txt}</div>
    </div>""")
    rjs.append(f'    SP("#ck-r{i}", {{ x: -60, opacity: 0 }}, {{ x: 0, opacity: 1 }}, {t - s0:.2f}, {{ dur: 0.8, damping: 14, stiffness: 170 }});')
    rjs.append(f'    SP("#ck-c{i}", {{ scale: 0, rotation: -90 }}, {{ scale: 1, rotation: 0 }}, {t - s0 + 0.05:.2f}, {{ dur: 0.9, damping: 8, stiffness: 200 }});')
SCENES.append(("checklist", s0, 5.37, f"""
    <div id="ck-card" class="card" style="left:84px;top:300px;width:830px;height:640px;"></div>
    <div id="ck-head" class="box" style="left:66px;top:256px;font-size:46px;background:{C};">siap dengan:</div>
{chr(10).join(rows)}
""", f"""
    SP("#ck-card", {{ scaleY: 0, transformOrigin: "50% 0%" }}, {{ scaleY: 1 }}, 0.05, {{ dur: 0.9, damping: 15, stiffness: 150 }});
    SP("#ck-head", {{ x: -500, rotation: -6 }}, {{ x: 0, rotation: -3 }}, 0.0, {{ dur: 0.9, damping: 12, stiffness: 170 }});
{chr(10).join(rjs)}
{out("#ck-r3, #ck-r2, #ck-r1, #ck-r0, #ck-head, #ck-card", 5.07)}"""))


def label_scene(sid, s0, dur, small, big, color, t_in, extra="", extra_js="", top=270):
    """Comic narration box ("room caption") pinned top-left."""
    body = f"""
    <div id="{sid}-s" class="box" style="left:84px;top:{top}px;font-size:40px;background:{WHT};">{small}</div>
    <div id="{sid}-b" class="bang {color}" style="left:84px;top:{top + 74}px;font-size:136px;transform-origin:0 50%;">{big}</div>
{extra}"""
    js = f"""    SP("#{sid}-s", {{ x: -420, rotation: -6 }}, {{ x: 0, rotation: -2 }}, {t_in - s0:.2f}, {{ dur: 0.85, damping: 12, stiffness: 170 }});
    SP("#{sid}-b", {{ scale: 0.3, rotation: -8, opacity: 0 }}, {{ scale: 1, rotation: -2, opacity: 1 }}, {t_in - s0 + 0.08:.2f}, {{ dur: 0.9, damping: 9, stiffness: 180 }});
{extra_js}{out(f"#{sid}-b, #{sid}-s", dur - 0.3)}"""
    return (sid, s0, dur, body, js)


# ---------------------------------------------------------------- 5. BILIK UTAMA 17.30 - 20.00
s0 = 17.30
SCENES.append(label_scene("utama", s0, 2.72, "panel #1", "BILIK UTAMA", "y", 17.68, extra=f"""
    <div id="ut-r" class="a" style="left:96px;top:520px;width:700px;height:110px;">
      <div class="a" style="left:0;top:0;width:100px;height:100px;">{check(100, C)}</div>
      <div class="box" style="left:120px;top:8px;font-size:58px;">built-in 1 tandas</div>
    </div>""", extra_js=f"""    SP("#ut-r", {{ x: -1200 }}, {{ x: 0 }}, {18.42 - s0:.2f}, {{ dur: 0.9, damping: 13, stiffness: 170 }});
    tl.to("#ut-r", {{ scale: 0.6, opacity: 0, duration: 0.2, ease: "back.in(2)" }}, {2.72 - 0.34:.2f});
"""))


# ---------------------------------------------------------------- 6. STATS 20.10 - 26.20
s0 = 20.10
SCENES.append(("stats", s0, 6.12, f"""
    <div id="st-a" class="card dots" style="left:84px;top:290px;width:390px;height:330px;background-color:{Y};transform-origin:50% 100%;">
      <div class="bang" style="left:0;top:20px;width:374px;text-align:center;font-size:210px;">3</div>
      <div class="lbl" style="left:0;top:236px;width:374px;text-align:center;font-size:64px;color:{K};">BILIK TIDUR</div>
    </div>
    <div id="st-b" class="card dots" style="left:510px;top:290px;width:390px;height:330px;background-color:{C};transform-origin:50% 100%;">
      <div class="bang y" style="left:0;top:20px;width:374px;text-align:center;font-size:210px;">2</div>
      <div class="lbl" style="left:0;top:236px;width:374px;text-align:center;font-size:64px;color:{K};">TANDAS</div>
    </div>
    <div id="st-f" class="a" style="left:96px;top:690px;width:440px;height:130px;transform-origin:50% 50%;">
      <div class="a" style="left:0;top:0;width:420px;height:120px;border:9px solid {RED};background:rgba(255,246,222,0.92);box-shadow:8px 8px 0 {K};"></div>
      <div class="lbl" style="left:0;top:22px;width:420px;text-align:center;font-size:86px;color:{RED};">FREEHOLD</div>
    </div>
    <div id="st-n" class="a" style="left:470px;top:820px;width:440px;height:130px;transform-origin:50% 50%;">
      <div class="a" style="left:0;top:0;width:420px;height:120px;border:9px solid {RED};background:rgba(255,246,222,0.92);box-shadow:8px 8px 0 {K};"></div>
      <div class="lbl" style="left:0;top:22px;width:420px;text-align:center;font-size:80px;color:{RED};">NON-BUMI LOT</div>
    </div>
""", f"""
    SP("#st-a", {{ scale: 0, y: 60 }}, {{ scale: 1, y: 0 }}, {21.70 - s0:.2f}, {{ dur: 1.0, damping: 9, stiffness: 160 }});
    SP("#st-b", {{ scale: 0, y: 60 }}, {{ scale: 1, y: 0 }}, {22.70 - s0:.2f}, {{ dur: 1.0, damping: 9, stiffness: 160 }});
    tl.fromTo("#st-f", {{ scale: 2.6, rotation: -24, opacity: 0 }}, {{ scale: 1, rotation: -7, opacity: 1, duration: 0.22, ease: "power4.in" }}, {23.62 - s0 - 0.2:.2f});
    tl.fromTo("#st-n", {{ scale: 2.6, rotation: 20, opacity: 0 }}, {{ scale: 1, rotation: 5, opacity: 1, duration: 0.22, ease: "power4.in" }}, {24.50 - s0 - 0.2:.2f});
{out("#st-n, #st-f, #st-b, #st-a", 25.25 - s0)}"""))


# ---------------------------------------------------------------- 7. SEMUA BOLEH BELI 25.45 - 28.05
s0 = 25.45
SCENES.append(("semua", s0, 2.62, f"""
    <div id="sm-sl" class="a" style="left:40px;top:300px;width:1000px;height:760px;opacity:0;">{speedlines(1000, 760, n=30, color=M)}</div>
    <div id="sm-b" class="a" style="left:100px;top:380px;width:860px;height:560px;transform-origin:50% 50%;">
      {burst("sm1", 860, 560, C, points=16, inner=0.7, seed=11)}
      <div class="bang y" style="left:0;top:150px;width:860px;text-align:center;font-size:120px;">SEMUA</div>
      <div class="bang" style="left:0;top:270px;width:860px;text-align:center;font-size:120px;">BOLEH BELI!</div>
    </div>
    <div id="sm-s" class="box" style="left:150px;top:980px;font-size:46px;">tak ada yang terkecuali</div>
""", f"""
    tl.fromTo("#sm-sl", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 0.85, scale: 1.1, duration: 1.2, ease: "power2.out" }}, {25.82 - s0:.2f});
    SP("#sm-b", {{ scale: 0, rotation: -20 }}, {{ scale: 1, rotation: 3 }}, {25.82 - s0:.2f}, {{ dur: 1.0, damping: 8, stiffness: 170 }});
    SP("#sm-s", {{ y: 300, opacity: 0 }}, {{ y: 0, opacity: 1 }}, {26.55 - s0:.2f}, {{ dur: 0.8, damping: 13, stiffness: 160 }});
{out("#sm-s, #sm-b, #sm-sl", 2.30)}"""))


# ---------------------------------------------------------------- 8. BILIK KEDUA 28.55 - 30.30
s0 = 28.55
SCENES.append(label_scene("kedua", s0, 1.78, "panel #2", "BILIK KEDUA", "m", 28.90))


# ---------------------------------------------------------------- 9. KELUASAN 31.70 - 34.70 (odometer)
s0 = 31.70
odo_html, odo_lh, odo_w = odometer("ls-o", "1,194", 0, 0, 230, Y, stroke_px=12, digit_w=128)
SCENES.append(("luas", s0, 3.00, f"""
    <div id="ls-card" class="card dots" style="left:84px;top:300px;width:830px;height:470px;background-color:{M};"></div>
    <div id="ls-h" class="box" style="left:64px;top:262px;font-size:44px;background:{WHT};">keluasan</div>
    <div id="ls-ow" class="a" style="left:{(1000 - odo_w) // 2}px;top:350px;width:{odo_w}px;height:{odo_lh}px;">
      {odo_html}
    </div>
    <div id="ls-u" class="bang" style="left:84px;top:600px;width:830px;text-align:center;font-size:110px;">KAKI PERSEGI</div>
    <div id="ls-ruler" class="a" style="left:130px;top:800px;width:740px;height:70px;transform-origin:0 50%;">
      <svg width="740" height="70" viewBox="0 0 740 70" style="position:absolute;left:0;top:0">
        <rect x="4" y="4" width="732" height="62" fill="{Y}" stroke="{K}" stroke-width="7"/>
        {''.join(f'<line x1="{20 + i * 35}" y1="4" x2="{20 + i * 35}" y2="{34 if i % 2 == 0 else 22}" stroke="{K}" stroke-width="5"/>' for i in range(21))}
      </svg>
    </div>
""", f"""
    SP("#ls-card", {{ scale: 0.2, rotation: -10 }}, {{ scale: 1, rotation: -1 }}, 0.0, {{ dur: 1.0, damping: 12, stiffness: 160 }});
    SP("#ls-h", {{ x: -400 }}, {{ x: 0 }}, 0.05, {{ dur: 0.8 }});
    tl.fromTo("#ls-ow", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, 0.15);
{odo_js("ls-o", "1,194", odo_lh, 0.2, stagger=0.12, dur=1.2)}
    SP("#ls-u", {{ y: 90, opacity: 0 }}, {{ y: 0, opacity: 1 }}, {33.82 - s0:.2f}, {{ dur: 0.8, damping: 11, stiffness: 180 }});
    SP("#ls-ruler", {{ scaleX: 0 }}, {{ scaleX: 1 }}, 0.35, {{ dur: 1.3, damping: 20, stiffness: 80 }});
{out("#ls-ruler, #ls-u, #ls-ow, #ls-h, #ls-card", 2.72)}"""))


# ---------------------------------------------------------------- 10. RUANG MAKAN 35.20 - 38.15
s0 = 35.20
SCENES.append(label_scene("makan", s0, 2.95, "panel #3", "RUANG MAKAN", "y", 35.28, extra=f"""
    <div id="mk-r" class="a" style="left:96px;top:520px;width:700px;height:110px;">
      <div class="a" style="left:0;top:0;width:100px;height:100px;">{check(100, M)}</div>
      <div class="box" style="left:120px;top:8px;font-size:58px;background:{C};">siap partition</div>
    </div>""", extra_js=f"""    SP("#mk-r", {{ x: -1200 }}, {{ x: 0 }}, {37.38 - s0:.2f}, {{ dur: 0.9, damping: 13, stiffness: 170 }});
    tl.to("#mk-r", {{ scale: 0.6, opacity: 0, duration: 0.2, ease: "back.in(2)" }}, {2.95 - 0.34:.2f});
"""))


# ---------------------------------------------------------------- 11. DAPUR 39.40 - 44.05
s0 = 39.40
SCENES.append(label_scene("dapur", s0, 4.70, "panel #4", "RUANG DAPUR", "m", 39.58, extra=f"""
    <div id="dp-r0" class="a" style="left:96px;top:520px;width:700px;height:110px;">
      <div class="a" style="left:0;top:0;width:100px;height:100px;">{check(100, C)}</div>
      <div class="box" style="left:120px;top:8px;font-size:58px;">fully tiled</div>
    </div>
    <div id="dp-r1" class="a" style="left:96px;top:650px;width:700px;height:110px;">
      <div class="a" style="left:0;top:0;width:100px;height:100px;">{check(100, M)}</div>
      <div class="box" style="left:120px;top:8px;font-size:58px;background:{WHT};">siap table top</div>
    </div>""", extra_js=f"""    SP("#dp-r0", {{ x: -1200 }}, {{ x: 0 }}, {40.66 - s0:.2f}, {{ dur: 0.9, damping: 13, stiffness: 170 }});
    SP("#dp-r1", {{ x: -1200 }}, {{ x: 0 }}, {42.62 - s0:.2f}, {{ dur: 0.9, damping: 13, stiffness: 170 }});
    tl.to("#dp-r1, #dp-r0", {{ scale: 0.6, opacity: 0, duration: 0.2, ease: "back.in(2)", stagger: 0.03 }}, {4.70 - 0.36:.2f});
"""))


# ---------------------------------------------------------------- 12. TANDAS KEDUA 44.10 - 45.50
s0 = 44.10
SCENES.append(label_scene("tandas", s0, 1.40, "panel #5", "TANDAS KEDUA", "", 44.14))


# ---------------------------------------------------------------- 13. BILIK KETIGA 45.85 - 48.20
s0 = 45.85
SCENES.append(label_scene("ketiga", s0, 2.30, "panel #6", "BILIK KETIGA", "y", 45.90))


# ---------------------------------------------------------------- 14. HARGA 48.80 - 51.45 (odometer + ka-ching)
s0 = 48.80
pr_html, pr_lh, pr_w = odometer("pr-o", "370,000", 0, 0, 176, M, stroke_px=12, digit_w=94)
SCENES.append(("harga", s0, 2.95, f"""
    <div id="pr-sl" class="a" style="left:40px;top:250px;width:1000px;height:900px;opacity:0;">{speedlines(1000, 900, n=36, color=K)}</div>
    <div id="pr-b" class="a" style="left:60px;top:300px;width:960px;height:720px;transform-origin:50% 50%;">
      {burst("pr1", 960, 720, Y, points=18, inner=0.74, seed=13)}
    </div>
    <div id="pr-h" class="box" style="left:330px;top:430px;font-size:46px;background:{WHT};">berharga</div>
    <div id="pr-rm" class="bang" style="left:{(1080 - pr_w) // 2 + 50 - 118}px;top:610px;font-size:104px;">RM</div>
    <div id="pr-ow" class="a" style="left:{(1080 - pr_w) // 2 + 50}px;top:580px;width:{pr_w}px;height:{pr_lh}px;">
      {pr_html}
    </div>
    <div id="pr-k" class="a" style="left:560px;top:820px;width:400px;height:200px;transform-origin:50% 50%;">
      {burst("pr2", 400, 200, M, points=11, inner=0.72, seed=17, dots=False)}
      <div class="bang y" style="left:0;top:58px;width:400px;text-align:center;font-size:84px;">KA-CHING!</div>
    </div>
""", f"""
    SP("#pr-b", {{ scale: 0, rotation: -30 }}, {{ scale: 1, rotation: -2 }}, 0.05, {{ dur: 1.0, damping: 10, stiffness: 150 }});
    tl.fromTo("#pr-sl", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 0.8, scale: 1.1, duration: 2.4, ease: "power1.out" }}, 0.05);
    SP("#pr-h", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1 }}, 0.18, {{ dur: 0.8 }});
    SP("#pr-rm", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1 }}, {49.55 - s0:.2f}, {{ dur: 0.8, damping: 10, stiffness: 200 }});
    tl.fromTo("#pr-ow", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {49.58 - s0:.2f});
{odo_js("pr-o", "370,000", pr_lh, 49.60 - s0, stagger=0.09, dur=1.15)}
    SP("#pr-k", {{ scale: 0, rotation: 25 }}, {{ scale: 1, rotation: -6 }}, {50.90 - s0:.2f}, {{ dur: 0.6, damping: 9, stiffness: 260 }});
{out("#pr-k, #pr-ow, #pr-rm, #pr-h, #pr-b, #pr-sl", 2.72)}"""))


# ---------------------------------------------------------------- 15. CTA LINK + LOAN 51.50 - 56.40
s0 = 51.50
SCENES.append(("link", s0, 4.92, f"""
    <div id="ln-q" class="a" style="left:96px;top:280px;width:560px;height:250px;">
      <svg width="560" height="250" viewBox="0 0 560 250" style="position:absolute;left:0;top:0;overflow:visible">
        <path d="M30 20 H530 V180 H170 L110 240 L120 180 H30 Z" fill="{WHT}" stroke="{K}" stroke-width="8" stroke-linejoin="round"/>
      </svg>
      <div class="lbl" style="left:30px;top:52px;width:500px;text-align:center;font-size:100px;color:{K};">BERMINAT?</div>
    </div>
    <div id="ln-btn" class="a" style="left:96px;top:580px;width:820px;height:190px;transform-origin:50% 50%;">
      <div class="a dotsw" style="left:0;top:0;width:800px;height:170px;background-color:{M};border:9px solid {K};box-shadow:14px 14px 0 {K};border-radius:26px;"></div>
      <div class="bang" style="left:0;top:28px;width:800px;text-align:center;font-size:106px;">TEKAN LINK &darr;</div>
    </div>
    <div id="ln-loan" class="a" style="left:96px;top:830px;width:820px;height:250px;">
      <div class="box" style="left:0;top:0;font-size:50px;background:{C};">urusan loan</div>
      <div class="a" style="left:0;top:96px;width:800px;height:120px;background:{P};border:8px solid {K};box-shadow:10px 10px 0 {K};"></div>
      <div id="ln-fill" class="a dots" style="left:8px;top:104px;width:784px;height:104px;background-color:{Y};transform-origin:0 50%;"></div>
      <div class="bang" style="left:30px;top:106px;font-size:100px;">A</div>
      <div id="ln-z" class="bang m" style="left:700px;top:106px;font-size:100px;">Z</div>
      <div class="lbl" style="left:0;top:122px;width:800px;text-align:center;font-size:60px;color:{K};">SAMPAI</div>
    </div>
""", f"""
    SP("#ln-q", {{ scale: 0, transformOrigin: "20% 100%" }}, {{ scale: 1 }}, {51.78 - s0:.2f}, {{ dur: 0.8, damping: 10, stiffness: 200 }});
    SP("#ln-btn", {{ scale: 0, rotation: -8 }}, {{ scale: 1, rotation: -2 }}, {52.55 - s0:.2f}, {{ dur: 1.0, damping: 8, stiffness: 180 }});
    tl.to("#ln-btn", {{ scale: 1.05, duration: 0.35, ease: "sine.inOut", yoyo: true, repeat: 3 }}, {53.4 - s0:.2f});
    SP("#ln-loan", {{ x: -1300 }}, {{ x: 0 }}, {54.30 - s0:.2f}, {{ dur: 0.9, damping: 13, stiffness: 160 }});
    SP("#ln-fill", {{ scaleX: 0 }}, {{ scaleX: 1 }}, {55.25 - s0:.2f}, {{ dur: 1.1, damping: 20, stiffness: 100 }});
    tl.fromTo("#ln-z", {{ scale: 1 }}, {{ scale: 1.5, duration: 0.15, ease: "power2.out", yoyo: true, repeat: 1 }}, {56.30 - s0:.2f});
{out("#ln-loan, #ln-btn, #ln-q", 4.62)}"""))


# ---------------------------------------------------------------- 16. END CARD 56.42 - 60.00
s0 = 56.42
SCENES.append(("endcard", s0, TOTAL - s0, f"""
    <div id="ec-frame" class="a" style="left:0;top:0;width:{W}px;height:{H}px;border:22px solid {P};box-shadow: inset 0 0 0 10px {K};"></div>
    <div id="ec-top" class="box" style="left:84px;top:262px;font-size:44px;">jangan lepaskan!</div>
    <div id="ec-b" class="a" style="left:70px;top:330px;width:940px;height:520px;transform-origin:50% 50%;">
      {burst("ec1", 940, 520, Y, points=17, inner=0.72, seed=19)}
      <div class="bang" style="left:0;top:110px;width:940px;text-align:center;font-size:100px;">RUMAH FULLY RENO</div>
      <div class="bang m" style="left:0;top:220px;width:940px;text-align:center;font-size:150px;">KULIM</div>
    </div>
    <div id="ec-chips" class="a" style="left:84px;top:880px;width:830px;height:110px;">
      <div class="box" style="left:0;top:0;font-size:52px;background:{WHT};">3 bilik</div>
      <div class="box" style="left:248px;top:0;font-size:52px;background:{C};">2 tandas</div>
      <div class="box" style="left:534px;top:0;font-size:52px;background:{WHT};">1,194 sqft</div>
    </div>
    <div id="ec-price" class="a" style="left:84px;top:1030px;width:830px;height:200px;transform-origin:50% 50%;">
      <div class="a dotsw" style="left:0;top:0;width:810px;height:180px;background-color:{M};border:9px solid {K};box-shadow:14px 14px 0 {K};border-radius:26px;"></div>
      <div class="bang y" style="left:0;top:22px;width:810px;text-align:center;font-size:96px;">RM370K</div>
      <div class="lbl" style="left:0;top:118px;width:810px;text-align:center;font-size:44px;color:{WHT};-webkit-text-stroke:7px {K};paint-order:stroke fill;">TEKAN LINK &bull; LOAN A-Z</div>
    </div>
""", f"""
    tl.fromTo("#ec-frame", {{ scale: 1.15, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.45, ease: "power3.out" }}, 0.0);
    SP("#ec-top", {{ x: -500, rotation: -6 }}, {{ x: 0, rotation: -3 }}, 0.15, {{ dur: 0.9, damping: 12, stiffness: 170 }});
    SP("#ec-b", {{ scale: 0, rotation: -18 }}, {{ scale: 1, rotation: -2 }}, 0.1, {{ dur: 1.0, damping: 8, stiffness: 160 }});
    SP("#ec-chips", {{ y: 160, opacity: 0 }}, {{ y: 0, opacity: 1 }}, 0.55, {{ dur: 0.9, damping: 12, stiffness: 160 }});
    SP("#ec-price", {{ scale: 0 }}, {{ scale: 1 }}, 0.85, {{ dur: 1.0, damping: 9, stiffness: 170 }});
    tl.to("#ec-price", {{ scale: 1.05, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: 3 }}, 1.9);
"""))


# ---------------------------------------------------------------- WIPES (comic panel slices)
WIPES = [4.37, 17.22, 34.72, 56.42]
wipe_body, wipe_js = [], []
cols = [(Y, "dots"), (M, "dotsw"), (C, "dots")]
for wi, t in enumerate(WIPES):
    for pi, (col, cls) in enumerate(cols):
        wid = f"wp{wi}{pi}"
        wipe_body.append(f'    <div id="{wid}" class="a" style="left:0;top:-240px;width:620px;height:2400px;">'
                         f'<div class="a {cls}" style="left:0;top:0;width:620px;height:2400px;background-color:{col};'
                         f'border-left:12px solid {K};border-right:12px solid {K};transform:skewX(-12deg);"></div></div>')
        st = t - 0.30 + pi * 0.05
        wipe_js.append(f'    tl.fromTo("#{wid}", {{ x: 1500 }}, {{ x: {-180 + pi * 360}, duration: 0.26, ease: "power3.out" }}, {st:.3f});')
        wipe_js.append(f'    tl.to("#{wid}", {{ x: -1500, duration: 0.30, ease: "power3.in" }}, {t + 0.02 + pi * 0.04:.3f});')
SCENES.append(("wipes", 0.0, TOTAL, "\n".join(wipe_body), "\n".join(wipe_js) + "\n" + "".join(
    f'    tl.set("#wp{wi}{pi}", {{ x: 1500 }}, 0);\n' for wi in range(len(WIPES)) for pi in range(3))))


# ---------------------------------------------------------------- SFX  (file, hit time, volume)
# hit time = when the picture lands; the clip is placed so its measured peak lands 1 frame later.
PEAK = {"punch": 0.33, "whoosh-cartoon": 1.99, "swish": 0.05, "whoosh-deep": 0.63, "kaching": 0.37, "shutter": 1.17,
        "pop": 0.03, "boing": 0.03, "gleam": 2.24, "impact": 0.03, "pageflip": 0.35, "scratch": 0.75, "ding": 0.07,
        "riser": 1.45, "keys": 1.64}
DUR = {"punch": 0.59, "whoosh-cartoon": 2.35, "swish": 0.33, "whoosh-deep": 1.94, "kaching": 0.83, "shutter": 1.4,
       "pop": 0.14, "boing": 0.74, "gleam": 3.79, "impact": 1.54, "pageflip": 0.56, "scratch": 1.24, "ding": 1.26,
       "riser": 2.96, "keys": 2.4}
SFX = [
    ("swish", 0.02, 0.30),            # title settles on frame 0
    ("punch", 1.66, 0.42),            # KULIM?!
    ("pop", 2.20, 0.40),              # INI MASANYA!
    ("impact", 3.14, 0.36),           # INI RUMAHNYA!
    ("whoosh-deep", 4.37, 0.40),      # panel wipe 1
    ("boing", 4.75, 0.22),            # map pin lands
    ("pop", 6.30, 0.38),              # dekat semua kemudahan
    ("punch", 7.66, 0.40),            # FULLY RENOVATED!
    ("swish", 9.02, 0.30),            # depan -> belakang bar
    ("pop", 10.42, 0.35),             # cantik tak?
    ("ding", 11.07, 0.26),            # CANTIK!
    ("pageflip", 11.78, 0.40),        # checklist card
    ("pop", 12.36, 0.36),
    ("pop", 13.94, 0.32),
    ("pop", 15.32, 0.36),
    ("pop", 15.92, 0.32),
    ("whoosh-cartoon", 17.22, 0.30),  # panel wipe 2
    ("pageflip", 17.70, 0.38),        # BILIK UTAMA
    ("pop", 18.46, 0.34),
    ("pop", 21.72, 0.40),             # 3 bilik
    ("pop", 22.72, 0.40),             # 2 tandas
    ("punch", 23.44, 0.34),           # FREEHOLD stamp
    ("punch", 24.32, 0.30),           # NON-BUMI stamp
    ("impact", 25.84, 0.28),          # SEMUA BOLEH BELI!
    ("pageflip", 28.92, 0.38),        # BILIK KEDUA
    ("riser", 33.20, 0.22),           # odometer spin
    ("ding", 33.25, 0.24),            # 1,194 lands
    ("whoosh-deep", 34.72, 0.36),     # panel wipe 3
    ("pageflip", 35.30, 0.38),        # RUANG MAKAN
    ("pop", 37.40, 0.34),
    ("pageflip", 39.60, 0.34),        # RUANG DAPUR
    ("pop", 40.68, 0.34),
    ("pop", 42.64, 0.34),
    ("swish", 44.16, 0.28),           # TANDAS KEDUA
    ("pageflip", 45.92, 0.36),        # BILIK KETIGA
    ("riser", 49.58, 0.26),           # build into the price
    ("kaching", 50.92, 0.42),         # KA-CHING!
    ("pop", 51.80, 0.34),             # BERMINAT?
    ("boing", 52.58, 0.20),           # TEKAN LINK
    ("swish", 54.32, 0.28),           # loan bar
    ("ding", 56.32, 0.22),            # Z
    ("whoosh-deep", 56.42, 0.38),     # panel wipe 4
    ("keys", 57.70, 0.34),            # house keys on the end card
]


def write_scene_files():
    os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
    for f in os.listdir(os.path.join(HERE, "compositions")):
        if f.endswith(".html"):
            os.remove(os.path.join(HERE, "compositions", f))
    for sid, start, dur, body, js in SCENES:
        with open(os.path.join(HERE, "compositions", f"{sid}.html"), "w") as fh:
            fh.write(scene(sid, dur, body, js))


def index_html():
    hosts = []
    for i, (sid, start, dur, _b, _j) in enumerate(SCENES):
        z = 60 if sid == "wipes" else 10 + i
        track = 4 if sid == "wipes" else 2 + (i % 2)
        hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                     f'data-start="{start:.2f}" data-duration="{dur:.2f}" data-track-index="{track}" data-track-kind="graphics" '
                     f'data-width="{W}" data-height="{H}" style="z-index:{z};"></div>')
    sfx = []
    for i, (name, hit, vol) in enumerate(SFX):
        st = max(0.0, hit + 1 / 30 - PEAK[name])
        d = min(DUR[name], TOTAL - st)
        sfx.append(f'      <audio id="sfx{i}" src="assets/sfx/{name}.mp3" data-start="{st:.3f}" data-duration="{d:.3f}" '
                   f'data-volume="{vol}" data-track-index="{8 + i % 4}"></audio>')
    # punch-ins on the small jump cuts (big ones are covered by the panel wipes)
    cuts = [1.10, 2.20, 3.30, 7.62, 13.46, 20.02, 26.39, 28.12, 30.25, 38.18, 40.54, 45.11]
    punch = "\n".join(
        f'      tl.fromTo("#footwrap", {{ scale: 1.07 }}, {{ scale: 1, duration: 0.42, ease: "expo.out", immediateRender: false }}, {c});'
        for c in cuts)
    return f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: absolute; inset: 0; overflow: hidden; }}
      #footwrap {{ position: absolute; inset: 0; transform-origin: 50% 45%; }}
      #footage {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      <div id="footwrap">
        <video id="footage" class="clip" src="assets/footage.mp4" data-start="0" data-duration="{TOTAL}" data-track-index="0" muted playsinline></video>
      </div>
{chr(10).join(hosts)}
      <audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="6"></audio>
      <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{TOTAL}" data-volume="1" data-fade-out="1.6" data-track-index="7"
        data-automation='{{"version":1,"lanes":[{{"target":"volume","points":[{{"t":0,"v":1}},{{"t":56.5,"v":1}},{{"t":57.1,"v":1.7}},{{"t":60,"v":1.7}}]}}]}}'></audio>
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.set("#footwrap", {{ scale: 1 }}, 0);
{punch}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    write_scene_files()
    with open(os.path.join(HERE, "index.html"), "w") as fh:
        fh.write(index_html())
    print(f"built {len(SCENES)} scenes, {len(SFX)} sfx")
