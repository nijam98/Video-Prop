"""Generate the Meera Grand HyperFrames project files (index.html + compositions/*.html).

Edit timings / copy here, then re-run. Output is plain HyperFrames HTML that Studio can edit.
"""
import math, os, sys, json

P = sys.argv[1]
W, H = 1080, 1920

EMERALD = "rgba(8,44,34,0.88)"
GOLD = "#D9B562"
IVORY = "#F7F0DE"

FONTS = """
    @font-face { font-family: 'Limelight'; src: url('assets/fonts/Limelight.woff2') format('woff2'); font-weight: 400; }
    @font-face { font-family: 'Poiret One'; src: url('assets/fonts/PoiretOne.woff2') format('woff2'); font-weight: 400; }
    @font-face { font-family: 'Josefin Sans'; src: url('assets/fonts/JosefinSans-var.woff2') format('woff2'); font-weight: 100 700; }
"""

COMMON_CSS = """
    #root { position: absolute; inset: 0; pointer-events: none; }
    .gold {
      background-image:
        linear-gradient(105deg, rgba(255,255,255,0) 42%, rgba(255,252,235,0.95) 50%, rgba(255,255,255,0) 58%),
        linear-gradient(180deg, #FFF3C8 0%, #EBCB7A 36%, #B98A33 60%, #F4D98F 100%);
      background-size: 300% 100%, 100% 100%;
      background-position: 120% 0, 0 0;
      background-repeat: no-repeat;
      -webkit-background-clip: text; background-clip: text;
      color: transparent;
    }
    .lbl { font-family: 'Poiret One', serif; color: var(--color-ivory, #F7F0DE); letter-spacing: 0.32em; text-transform: uppercase; }
    .body { font-family: 'Josefin Sans', sans-serif; font-weight: 700; color: var(--color-ivory, #F7F0DE); letter-spacing: 0.22em; text-transform: uppercase; }
    .disp { font-family: 'Limelight', serif; letter-spacing: 0.04em; text-transform: uppercase; line-height: 1; }
    .row { position: absolute; left: 0; width: 1080px; display: flex; justify-content: center; align-items: center; white-space: nowrap; }
    .shadow { filter: drop-shadow(0 4px 10px rgba(0,0,0,0.45)); }
    .w { display: inline-block; }
"""


def poly(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def ziggurat(x0, y0, w, h, inset=0, step=(150, 40, 70, 38), chamfer=28):
    """Stepped (ziggurat) top, chamfered bottom corners. Returns polygon points."""
    s1w, s1h, s2w, s2h = step
    cx = x0 + w / 2
    i = inset
    top = y0 + s1h + s2h + i
    pts = [
        (x0 + i, top),
        (cx - s1w - s2w / 2 + i * 0.4, top),
        (cx - s1w - s2w / 2 + i * 0.4, y0 + s2h + i),
        (cx - s2w / 2 - s1w * 0.35 + i * 0.4, y0 + s2h + i),
        (cx - s2w / 2 - s1w * 0.35 + i * 0.4, y0 + i),
        (cx + s2w / 2 + s1w * 0.35 - i * 0.4, y0 + i),
        (cx + s2w / 2 + s1w * 0.35 - i * 0.4, y0 + s2h + i),
        (cx + s1w + s2w / 2 - i * 0.4, y0 + s2h + i),
        (cx + s1w + s2w / 2 - i * 0.4, top),
        (x0 + w - i, top),
        (x0 + w - i, y0 + h - chamfer - i * 0.4),
        (x0 + w - chamfer - i * 0.4, y0 + h - i),
        (x0 + chamfer + i * 0.4, y0 + h - i),
        (x0 + i, y0 + h - chamfer - i * 0.4),
    ]
    return pts


def stepped_corners(x0, y0, w, h, inset=0, c=34, s=16):
    """Rectangle with inverse stepped corners (classic deco frame)."""
    i = inset
    a, b = c - i * 0.5, s
    L, T, R, B = x0 + i, y0 + i, x0 + w - i, y0 + h - i
    pts = [
        (L + a, T), (R - a, T), (R - a, T + b), (R - b, T + b), (R - b, T + a), (R, T + a),
        (R, B - a), (R - b, B - a), (R - b, B - b), (R - a, B - b), (R - a, B),
        (L + a, B), (L + a, B - b), (L + b, B - b), (L + b, B - a), (L, B - a),
        (L, T + a), (L + b, T + a), (L + b, T + b), (L + a, T + b),
    ]
    return pts


def ticket(x0, y0, w, h, inset=0, notch=34, chamfer=30):
    """Chamfered rectangle with side notches (deco ticket)."""
    i = inset
    L, T, R, B = x0 + i, y0 + i, x0 + w - i, y0 + h - i
    ch = chamfer - i * 0.4
    my = y0 + h / 2
    n = notch - i
    pts = [(L + ch, T), (R - ch, T), (R, T + ch), (R, my - n), (R - n, my), (R, my + n), (R, B - ch),
           (R - ch, B), (L + ch, B), (L, B - ch), (L, my + n), (L + n, my), (L, my - n), (L, T + ch)]
    return pts


def sunburst(cx, cy, r, n=22, a0=180, a1=360, color=GOLD, opacity=0.22, sid="sb"):
    rays = []
    span = (a1 - a0) / n
    for k in range(n):
        if k % 2:
            continue
        t0 = math.radians(a0 + k * span)
        t1 = math.radians(a0 + (k + 1) * span)
        p = [(cx, cy), (cx + r * math.cos(t0), cy + r * math.sin(t0)), (cx + r * math.cos(t1), cy + r * math.sin(t1))]
        rays.append(f'<polygon points="{poly(p)}" />')
    return (f'<g id="{sid}" fill="url(#{sid}-grad)" opacity="{opacity}">' + "".join(rays) + "</g>",
            f'<radialGradient id="{sid}-grad" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}">'
            f'<stop offset="0" stop-color="#FFF0BE" stop-opacity="1"/><stop offset="0.75" stop-color="{color}" stop-opacity="0.7"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')


def panel_svg(pid, pts_outer, pts_inner, pts_inner2=None, burst=None, fill=EMERALD):
    defs = ""
    burst_g = ""
    if burst:
        burst_g, grad = burst
        defs += grad
    defs += f'<clipPath id="{pid}-clip"><polygon points="{poly(pts_outer)}"/></clipPath>'
    inner2 = f'<polygon points="{poly(pts_inner2)}" fill="none" stroke="{GOLD}" stroke-width="1.2" opacity="0.55"/>' if pts_inner2 else ""
    return f'''<svg id="{pid}" class="shadow" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0;overflow:visible">
        <defs>{defs}</defs>
        <polygon points="{poly(pts_outer)}" fill="{fill}"/>
        <g clip-path="url(#{pid}-clip)">{burst_g}</g>
        <polygon points="{poly(pts_outer)}" fill="none" stroke="{GOLD}" stroke-width="3.2"/>
        <polygon points="{poly(pts_inner)}" fill="none" stroke="{GOLD}" stroke-width="1.6" opacity="0.9"/>
        {inner2}
      </svg>'''


def rule(rid, y, x0, x1, diamond=True):
    """Gold hairline with diamond caps, as absolutely positioned SVG."""
    d = ""
    if diamond:
        for x in (x0, x1):
            d += f'<polygon points="{x},{y-9} {x+9},{y} {x},{y+9} {x-9},{y}" fill="{GOLD}"/>'
    return f'''<svg id="{rid}" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0;overflow:visible">
        <line x1="{x0+12}" y1="{y-3}" x2="{x1-12}" y2="{y-3}" stroke="{GOLD}" stroke-width="1.6"/>
        <line x1="{x0+12}" y1="{y+3}" x2="{x1-12}" y2="{y+3}" stroke="{GOLD}" stroke-width="1.6"/>{d}
      </svg>'''


def scene(cid, body, css, script, extra_head=""):
    return f'''<template>
  <style>{FONTS}{COMMON_CSS}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{script}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
'''


def letters(text, cls="L"):
    out = []
    for ch in text:
        if ch == " ":
            out.append('<span class="w" style="width:0.32em"></span>')
        else:
            out.append(f'<span class="w {cls} gold">{ch}</span>')
    return "".join(out)


# ---------------------------------------------------------------- HOOK (0 - 2.18)
hook_pts = ziggurat(96, 232, 888, 432)
hook_in = ziggurat(96, 232, 888, 432, inset=13)
burst = sunburst(540, 664, 560, n=26, opacity=0.26, sid="hk-sb")
hook_body = f'''    <div id="hk-wrap" style="position:absolute;inset:0">
      {panel_svg("hk-panel", hook_pts, hook_in, burst=burst)}
      <div id="hk-l1" class="row lbl" style="top:338px;height:60px;font-size:46px">Rumah semi-D ni</div>
      <div id="hk-l2" class="row shadow" style="top:398px;height:190px"><span id="hk-big" class="disp gold" style="font-size:176px;padding:0 10px">Susah</span></div>
      {rule("hk-rule-l", 618, 150, 300)}
      {rule("hk-rule-r", 618, 780, 930)}
      <div id="hk-l3" class="row body" style="top:592px;height:56px;font-size:46px">Nak dapat</div>
    </div>'''
hook_script = '''      // frame 0 is the thumbnail: everything is already on screen.
      tl.fromTo("#hk-sb", { scale: 0.55, rotation: -10, transformOrigin: "540px 664px" }, { scale: 1, rotation: 0, duration: 1.1, ease: "expo.out" }, 0);
      tl.fromTo("#hk-big", { backgroundPosition: "120% 0, 0 0" }, { backgroundPosition: "-40% 0, 0 0", duration: 0.75, ease: "power2.inOut" }, 0.25);
      // "susah" is spoken at 1.18 s: stamp it
      tl.fromTo("#hk-l2", { scale: 1 }, { scale: 1.08, duration: 0.09, ease: "power2.out", transformOrigin: "540px 495px" }, 1.16);
      tl.to("#hk-l2", { scale: 1, duration: 0.35, ease: "power3.out" }, 1.25);
      tl.fromTo(["#hk-rule-l", "#hk-rule-r"], { scaleX: 0.35, transformOrigin: "50% 50%" }, { scaleX: 1, duration: 0.5, ease: "expo.out" }, 1.16);
      // exit: shutter up into the stepped top
      tl.to("#hk-wrap", { clipPath: "inset(0px 0px 1700px 0px)", duration: 0.22, ease: "power3.in" }, 1.94);
      tl.set("#hk-wrap", { opacity: 0 }, 2.17);'''
hook_css = "    #hk-wrap { clip-path: inset(0px 0px 0px 0px); }"

# ---------------------------------------------------------------- LOKASI (2.18 - 6.48, local 0 - 4.30)
lk_pts = stepped_corners(96, 236, 888, 424)
lk_in = stepped_corners(96, 236, 888, 424, inset=14)
lk_burst = sunburst(540, 236, 300, n=18, a0=0, a1=180, opacity=0.18, sid="lk-sb")
lk_body = f'''    <div id="lk-wrap" style="position:absolute;inset:0">
      {panel_svg("lk-panel", lk_pts, lk_in, burst=lk_burst)}
      <div id="lk-l1" class="row lbl" style="top:282px;height:56px;font-size:42px"><span class="w lk-w1">Untuk</span>&nbsp;<span class="w lk-w1">warga</span></div>
      <div id="lk-l2" class="row shadow" style="top:350px;height:110px"><span id="lk-big" class="disp" style="font-size:94px;padding:0 6px">{letters("Sungai Petani", "lk-L")}</span></div>
      <div id="lk-l3" class="lbl" style="position:absolute;left:150px;top:478px;height:40px;font-size:30px;letter-spacing:0.26em">atau berdekatan</div>
      <svg id="lk-route" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0;overflow:visible">
        <line id="lk-line" x1="166" y1="548" x2="640" y2="548" stroke="{GOLD}" stroke-width="2.4" stroke-dasharray="2 12" stroke-linecap="round"/>
        <polygon points="150,539 159,548 150,557 141,548" fill="{GOLD}"/>
        <polygon id="lk-dot" points="166,536 178,548 166,560 154,548" fill="#FFF0BE"/>
      </svg>
      <div id="lk-chip" style="position:absolute;left:660px;top:516px;width:270px;height:64px">
        <div id="lk-chip-in" style="position:absolute;inset:0;background:{GOLD};clip-path:polygon(16px 0,254px 0,270px 16px,270px 48px,254px 64px,16px 64px,0 48px,0 16px)"></div>
        <div style="position:absolute;inset:3px;background:#0B3529;clip-path:polygon(14px 0,250px 0,264px 14px,264px 44px,250px 58px,14px 58px,0 44px,0 14px)"></div>
        <div class="row body gold" style="left:0;width:270px;top:0;height:64px;font-size:40px;letter-spacing:0.18em;padding-top:6px">Penang</div>
      </div>
      <div id="lk-l4" class="row body" style="top:596px;height:50px;font-size:40px"><span class="w lk-w4">Nak</span>&nbsp;<span class="w lk-w4">cari</span>&nbsp;<span class="w lk-w4 gold">rumah?</span></div>
    </div>'''
lk_script = '''      tl.fromTo("#lk-wrap", { clipPath: "inset(0px 540px 0px 540px)" }, { clipPath: "inset(0px 0px 0px 0px)", duration: 0.42, ease: "expo.out" }, 0);
      tl.fromTo("#lk-sb", { scale: 0.4, transformOrigin: "540px 236px" }, { scale: 1, duration: 1.2, ease: "expo.out" }, 0.05);
      tl.fromTo(".lk-w1", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, stagger: 0.14, ease: "power2.out" }, 0.04);
      // "Sungai Petani" spoken from local 0.66: per-letter reveal
      tl.fromTo(".lk-L", { opacity: 0.0, filter: "blur(7px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, stagger: 0.034, ease: "power3.out" }, 0.62);
      tl.fromTo(".lk-L", { backgroundPosition: "120% 0, 0 0" }, { backgroundPosition: "-40% 0, 0 0", duration: 0.3, ease: "power1.inOut", stagger: 0.035 }, 1.15);
      tl.fromTo("#lk-l3", { opacity: 0, filter: "blur(6px)" }, { opacity: 0.92, filter: "blur(0px)", duration: 0.2, ease: "power2.out" }, 1.22);
      tl.fromTo("#lk-line", { attr: { x2: 166 } }, { attr: { x2: 640 }, duration: 1.0, ease: "power1.inOut" }, 1.55);
      tl.fromTo("#lk-dot", { x: 0 }, { x: 474, duration: 1.0, ease: "power1.inOut" }, 1.55);
      // "Penang" at local 2.58
      tl.fromTo("#lk-chip", { opacity: 0, scale: 0.7, filter: "blur(8px)", transformOrigin: "0% 50%" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "back.out(1.4)" }, 2.54);
      // "nak cari rumah" at 3.10 / 3.50 / 3.88
      tl.fromTo(".lk-w4", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out", stagger: { each: 0.39 } }, 3.08);
      // exit
      tl.to("#lk-wrap", { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power2.in" }, 4.1);'''
lk_css = "    #lk-wrap { clip-path: inset(0px 0px 0px 0px); }"

# ---------------------------------------------------------------- HARTANAH (6.48 - 9.74, local 0 - 3.26)
hp_pts = ziggurat(90, 222, 900, 372, step=(160, 34, 80, 34))
hp_in = ziggurat(90, 222, 900, 372, inset=13, step=(160, 34, 80, 34))
hp_burst = sunburst(540, 600, 520, n=30, opacity=0.28, sid="hp-sb")
hp_body = f'''    <div id="hp-flash" style="position:absolute;inset:0;background:radial-gradient(circle at 50% 30%, rgba(255,250,232,1) 0%, rgba(255,240,200,0.85) 55%, rgba(255,236,190,0.6) 100%);opacity:0"></div>
    <div id="hp-wrap" style="position:absolute;inset:0">
      {panel_svg("hp-panel", hp_pts, hp_in, burst=hp_burst)}
      <div id="hp-l1" class="row shadow" style="top:316px;height:110px"><span id="hp-big" class="disp" style="font-size:98px;padding:0 6px">{letters("Meera Grand", "hp-L")}</span></div>
      {rule("hp-rule", 446, 300, 780)}
      <div id="hp-l2" class="row body" style="top:466px;height:46px;font-size:38px;letter-spacing:0.34em"><span class="w hp-w2">Bukit</span>&nbsp;<span class="w hp-w2">Banyan</span></div>
      <div id="hp-c1" style="position:absolute;left:206px;top:524px;width:240px;height:58px">
        <div style="position:absolute;inset:0;background:{GOLD};clip-path:polygon(14px 0,226px 0,240px 14px,240px 44px,226px 58px,14px 58px,0 44px,0 14px)"></div>
        <div style="position:absolute;inset:3px;background:#0B3529;clip-path:polygon(12px 0,222px 0,234px 12px,234px 40px,222px 52px,12px 52px,0 40px,0 12px)"></div>
        <div class="row body gold" style="left:0;width:240px;top:0;height:58px;font-size:34px;letter-spacing:0.16em;padding-top:5px">Semi-D</div>
      </div>
      <div id="hp-c2" style="position:absolute;left:470px;top:524px;width:404px;height:58px">
        <div style="position:absolute;inset:0;background:{GOLD};clip-path:polygon(14px 0,390px 0,404px 14px,404px 44px,390px 58px,14px 58px,0 44px,0 14px)"></div>
        <div style="position:absolute;inset:3px;background:#0B3529;clip-path:polygon(12px 0,386px 0,398px 12px,398px 40px,386px 52px,12px 52px,0 40px,0 12px)"></div>
        <div class="row body gold" style="left:0;width:404px;top:0;height:58px;font-size:34px;letter-spacing:0.16em;padding-top:5px">Double Storey</div>
      </div>
    </div>'''
hp_script = '''      // vintage flash-powder cut
      tl.fromTo("#hp-flash", { opacity: 0.62 }, { opacity: 0, duration: 0.34, ease: "power2.out" }, 0);
      tl.fromTo("#hp-wrap", { clipPath: "inset(0px 0px 1920px 0px)" }, { clipPath: "inset(0px 0px 0px 0px)", duration: 0.4, ease: "expo.out" }, 0.0);
      tl.fromTo("#hp-sb", { scale: 0.3, rotation: 8, transformOrigin: "540px 600px" }, { scale: 1, rotation: 0, duration: 1.4, ease: "expo.out" }, 0.0);
      // "Meera Grand" spoken at local 0.05 - 0.50: per-letter, a frame apart
      tl.fromTo(".hp-L", { opacity: 0.25, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, stagger: 0.04, ease: "power2.out" }, 0.05);
      tl.fromTo(".hp-L", { backgroundPosition: "120% 0, 0 0" }, { backgroundPosition: "-40% 0, 0 0", duration: 0.3, ease: "power1.inOut", stagger: 0.035 }, 0.6);
      tl.fromTo("#hp-rule", { scaleX: 0, transformOrigin: "540px 446px" }, { scaleX: 1, duration: 0.5, ease: "expo.out" }, 0.62);
      // "Bukit Banyan" at local 0.96 / 1.32
      tl.fromTo(".hp-w2", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.15, stagger: 0.36, ease: "power2.out" }, 0.95);
      // chips: "Semi-D" 1.66, "Double Storey" 2.24
      tl.fromTo("#hp-c1", { opacity: 0, scale: 0.7, filter: "blur(8px)", transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "back.out(1.4)" }, 1.63);
      tl.fromTo("#hp-c2", { opacity: 0, scale: 0.7, filter: "blur(8px)", transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "back.out(1.4)" }, 2.21);
      // exit
      tl.to("#hp-wrap", { clipPath: "inset(0px 0px 1700px 0px)", duration: 0.22, ease: "power3.in" }, 3.02);
      tl.set("#hp-wrap", { opacity: 0 }, 3.25);'''
hp_css = ""

# ---------------------------------------------------------------- CTA (9.74 - 13.5, local 0 - 3.76)
ct_pts = ticket(96, 236, 888, 440)
ct_in = ticket(96, 236, 888, 440, inset=14)
ct_burst = sunburst(540, 676, 480, n=26, opacity=0.2, sid="ct-sb")
chev = ""
for k in range(3):
    y = 606 + k * 20
    chev += f'<polyline class="ct-chev" points="508,{y} 540,{y+18} 572,{y}" fill="none" stroke="{GOLD}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
ct_body = f'''    <div id="ct-wrap" style="position:absolute;inset:0">
      {panel_svg("ct-panel", ct_pts, ct_in, burst=ct_burst)}
      <div id="ct-l1" class="row lbl" style="top:278px;height:56px;font-size:40px;letter-spacing:0.2em"><span class="w ct-w1">Nak</span>&nbsp;<span class="w ct-w1">tahu</span>&nbsp;<span class="w ct-w1">detail</span>&nbsp;<span class="w ct-w1">lanjut?</span></div>
      {rule("ct-rule", 356, 330, 750)}
      <div id="ct-l2" class="row shadow" style="top:384px;height:130px"><span id="ct-big" class="disp gold" style="font-size:112px;padding:0 8px">Isi borang</span></div>
      <div id="ct-l3" class="row body" style="top:530px;height:50px;font-size:38px;letter-spacing:0.3em">Di bawah ni</div>
      <svg id="ct-chevs" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0;overflow:visible">{chev}</svg>
    </div>
    <div id="ct-end" class="row lbl" style="top:278px;height:56px;font-size:38px;letter-spacing:0.24em;opacity:0"><span class="gold" id="ct-end-t">Meera Grand &#9670; Bukit Banyan</span></div>'''
ct_script = '''      tl.fromTo("#ct-wrap", { clipPath: "inset(0px 0px 1920px 0px)" }, { clipPath: "inset(0px 0px 0px 0px)", duration: 0.36, ease: "expo.out" }, 0);
      tl.fromTo("#ct-sb", { scale: 0.4, transformOrigin: "540px 676px" }, { scale: 1, duration: 1.3, ease: "expo.out" }, 0.0);
      // "nak tahu detail lanjut" from grey to ivory, on the words (0.0 / 0.02 / 0.28 / 0.48)
      tl.fromTo(".ct-w1", { opacity: 0.18 }, { opacity: 1, duration: 0.12, ease: "power1.out", stagger: { each: 0.16 } }, 0.0);
      tl.fromTo("#ct-rule", { scaleX: 0, transformOrigin: "540px 356px" }, { scaleX: 1, duration: 0.45, ease: "expo.out" }, 0.45);
      // "isi borang" slams at local 0.98
      tl.fromTo("#ct-l2", { opacity: 0, scale: 1.35, filter: "blur(10px)", transformOrigin: "540px 450px" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out" }, 0.96);
      tl.fromTo("#ct-big", { backgroundPosition: "120% 0, 0 0" }, { backgroundPosition: "-40% 0, 0 0", duration: 0.8, ease: "power2.inOut" }, 1.35);
      // "dekat bawah ni" at local 1.92
      tl.fromTo("#ct-l3", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power2.out" }, 1.9);
      tl.fromTo(".ct-chev", { opacity: 0.12, y: -6 }, { opacity: 1, y: 0, duration: 0.18, ease: "power2.out", stagger: 0.09 }, 2.0);
      tl.to(".ct-chev", { opacity: 0.25, duration: 0.2, ease: "power1.in", stagger: 0.09 }, 2.45);
      tl.to(".ct-chev", { opacity: 1, duration: 0.18, ease: "power2.out", stagger: 0.09 }, 2.75);
      // end lockup with the brass sting
      tl.to("#ct-l1", { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power2.in" }, 1.5);
      tl.fromTo("#ct-end", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power2.out" }, 1.62);'''
ct_css = "    #ct-wrap { clip-path: inset(0px 0px 0px 0px); }"

# ---------------------------------------------------------------- BINGKAI (corner ornaments, whole film)
def corner(x, y, sx, sy, cid):
    # stepped L with a small quarter fan, drawn for the top-left and mirrored
    pts1 = [(0, 120), (0, 0), (120, 0)]
    pts2 = [(14, 120), (14, 30), (30, 30), (30, 14), (120, 14)]
    fan = ""
    for k in range(5):
        a0 = math.radians(5 + k * 18); a1 = math.radians(14 + k * 18)
        r = 44
        fan += f'<polygon points="22,22 {22 + r*math.cos(a0):.1f},{22 + r*math.sin(a0):.1f} {22 + r*math.cos(a1):.1f},{22 + r*math.sin(a1):.1f}" fill="{GOLD}" opacity="0.75"/>'
    return f'''<g id="{cid}" transform="translate({x},{y}) scale({sx},{sy})">
          <polyline points="{poly(pts1)}" fill="none" stroke="{GOLD}" stroke-width="3"/>
          <polyline points="{poly(pts2)}" fill="none" stroke="{GOLD}" stroke-width="1.5"/>
          {fan}
        </g>'''

bk_body = f'''    <svg id="bk-svg" class="shadow" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">
        {corner(58, 196, 1, 1, "bk-tl")}
        {corner(1022, 196, -1, 1, "bk-tr")}
        {corner(58, 1792, 1, -1, "bk-bl")}
        {corner(1022, 1792, -1, -1, "bk-br")}
      </svg>'''
bk_script = '''      tl.fromTo("#bk-svg", { opacity: 0.9 }, { opacity: 0.9, duration: 0.1 }, 0);'''

files = {
    "hook": (hook_body, hook_css, hook_script),
    "lokasi": (lk_body, lk_css, lk_script),
    "hartanah": (hp_body, hp_css, hp_script),
    "cta": (ct_body, ct_css, ct_script),
    "bingkai": (bk_body, "", bk_script),
}
os.makedirs(os.path.join(P, "compositions"), exist_ok=True)
for cid, (body, css, script) in files.items():
    with open(os.path.join(P, "compositions", f"{cid}.html"), "w") as f:
        f.write(scene(cid, body, css, script))

# ---------------------------------------------------------------- ROOT
TOTAL = 13.5
# (id, out_start, media_start, duration)
CUTS = [("v-hook", 0.0, 4.40, 2.18), ("v-lokasi", 2.18, 0.0, 4.30), ("v-hartanah", 6.48, 6.90, 3.26), ("v-cta", 9.74, 10.86, 2.773)]
SCENES = [("hook", 0.0, 2.18), ("lokasi", 2.18, 4.30), ("hartanah", 6.48, 3.26), ("cta", 9.74, TOTAL - 9.74)]
# (id, file, start, duration, volume, fade_out)
SFX = [
    ("sfx-boom", "cinematic-boom.mp3", 0.0, 2.6, 0.42, 0.6),
    ("sfx-glint-1", "coin-shimmer.mp3", 1.09, 0.8, 0.32, 0.2),
    ("sfx-whoosh-1", "trailer-whoosh.mp3", 1.69, 1.4, 0.24, 0.3),
    ("sfx-sparkle", "sparkle.mp3", 3.0, 1.7, 0.16, 0.5),
    ("sfx-swell", "crash-swell.mp3", 3.62, 3.6, 0.2, 0.8),
    ("sfx-click-1", "click-soft.mp3", 4.74, 0.37, 0.4, 0.1),
    ("sfx-flash", "vintage-flash.mp3", 5.84, 1.8, 0.4, 0.4),
    ("sfx-shimmer", "shimmer-success.mp3", 6.5, 2.4, 1.6, 0.6),
    ("sfx-click-2", "click-soft.mp3", 8.12, 0.37, 0.36, 0.1),
    ("sfx-glint-2", "coin-shimmer.mp3", 8.63, 0.8, 0.28, 0.2),
    ("sfx-whoosh-2", "swoosh.mp3", 8.64, 1.9, 0.2, 0.4),
    ("sfx-bell", "desk-bell.mp3", 9.91, 2.4, 0.34, 0.6),
    ("sfx-horn", "horn-hit.mp3", 12.40, 1.1, 0.38, 0.5),
]

voice_fx = json.dumps({"version": 1, "nodes": [
    {"type": "highpass", "id": "v1", "label": "Remove rumble", "params": {"frequency": 80}},
    {"type": "limiter", "id": "v2", "label": "Safety limiter", "params": {"limit": -1}}]}).replace('"', "&quot;")

# bed under the voice, opening up after the last word (12.48 s)
bgm_auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.17}, {"t": 12.45, "v": 0.17}, {"t": 12.75, "v": 0.5}]}]}).replace('"', "&quot;")

vids = ""
for k, (vid, s, ms, d) in enumerate(CUTS):
    vids += f'''        <video id="{vid}" class="clip" src="assets/footage.mp4" playsinline data-has-audio="true"
          data-start="{s}" data-duration="{d}" data-media-start="{ms}" data-track-index="{k % 2}"
          data-fade-in="0.02" data-fade-out="0.03" data-volume="1" data-fx-chain="{voice_fx}"
          style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover"></video>
'''
last_end = CUTS[-1][1] + CUTS[-1][3]
vids += f'''        <img id="v-hold" class="clip" src="assets/last-frame.jpg" alt="" data-start="{round(last_end - 0.03, 3)}" data-duration="{round(TOTAL - last_end + 0.03, 3)}" data-track-index="2"
          style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover" />
'''
hosts = ""
for k, (cid, s, d) in enumerate(SCENES):
    hosts += f'''      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{s}" data-duration="{round(d, 3)}" data-track-index="{2 + k % 2}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index:{20 + k}"></div>
'''
hosts += f'''      <div id="bingkai" data-composition-id="bingkai" data-composition-src="compositions/bingkai.html"
        data-start="0" data-duration="{TOTAL}" data-track-index="4" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index:30"></div>
'''
auds = f'''      <audio id="bgm" class="clip" src="assets/bgm/electro-swing.m4a" data-start="0" data-duration="{TOTAL}" data-track-index="5"
        data-volume="1" data-fade-out="0.8" data-automation="{bgm_auto}"></audio>
'''
lanes_end = []
for k, (aid, fn, s, d, vol, fo) in enumerate(SFX):
    lane = next((i for i, e in enumerate(lanes_end) if e <= s), None)
    if lane is None:
        lanes_end.append(0); lane = len(lanes_end) - 1
    lanes_end[lane] = s + d
    auds += f'''      <audio id="{aid}" class="clip" src="assets/sfx/{fn}" data-start="{s}" data-duration="{d}" data-track-index="{6 + lane}"
        data-volume="{vol}" data-fade-out="{fo}"></audio>
'''

variables = json.dumps([
    {"id": "color-gold", "type": "color", "label": "Gold", "default": GOLD},
    {"id": "color-ivory", "type": "color", "label": "Ivory", "default": IVORY},
    {"id": "color-emerald", "type": "color", "label": "Emerald", "default": "#082C22"},
])
index = f'''<!doctype html>
<html lang="ms" data-resolution="portrait" data-composition-variables='{variables}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #cam {{ position: absolute; inset: 0; overflow: hidden; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="cam" data-layout-allow-overflow>
        <div id="cam-move" style="position:absolute;inset:0">
{vids}        </div>
      </div>
{hosts}{auds}    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // jump cut inside the gym (9.74 s): hard punch-in hides the removed pause
      tl.set("#cam-move", {{ scale: 1, transformOrigin: "35% 30%" }}, 0);
      tl.set("#cam-move", {{ scale: 1.09, transformOrigin: "35% 30%" }}, 9.74);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
with open(os.path.join(P, "index.html"), "w") as f:
    f.write(index)
print("ok")
