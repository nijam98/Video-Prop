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
# Compact panels (720 px wide), simple fades. Everything sits in the top band, clear of the face.
ZSTEP = (110, 24, 56, 24)
hook_pts = ziggurat(180, 250, 720, 270, step=ZSTEP, chamfer=20)
hook_in = ziggurat(180, 250, 720, 270, inset=10, step=ZSTEP, chamfer=20)
burst = sunburst(540, 520, 300, n=24, opacity=0.16, sid="hk-sb")
hook_body = f"""    <div id="hk-wrap" style="position:absolute;inset:0">
      {panel_svg("hk-panel", hook_pts, hook_in, burst=burst)}
      <div id="hk-l1" class="row lbl" style="top:312px;height:40px;font-size:30px">Rumah semi-D ni</div>
      <div id="hk-l2" class="row shadow" style="top:356px;height:116px"><span id="hk-big" class="disp gold" style="font-size:112px;padding:0 8px">Susah</span></div>
      {rule("hk-rule-l", 494, 250, 390)}
      {rule("hk-rule-r", 494, 690, 830)}
      <div id="hk-l3" class="row body" style="top:476px;height:36px;font-size:32px">Nak dapat</div>
    </div>"""
hook_script = """      // frame 0 is the thumbnail: everything is already on screen.
      tl.fromTo("#hk-big", { backgroundPosition: "120% 0, 0 0" }, { backgroundPosition: "-40% 0, 0 0", duration: 0.7, ease: "power2.inOut" }, 0.3);
      tl.fromTo("#hk-l2", { scale: 1 }, { scale: 1.04, duration: 0.1, ease: "power2.out", transformOrigin: "540px 414px" }, 1.16);
      tl.to("#hk-l2", { scale: 1, duration: 0.3, ease: "power3.out" }, 1.26);
      tl.to("#hk-wrap", { opacity: 0, filter: "blur(6px)", duration: 0.18, ease: "power2.in" }, 1.98);"""
hook_css = ""

# ---------------------------------------------------------------- LOKASI (2.18 - 6.48, local 0 - 4.30)
lk_pts = stepped_corners(180, 258, 720, 304, c=26, s=12)
lk_in = stepped_corners(180, 258, 720, 304, inset=10, c=26, s=12)
lk_burst = sunburst(540, 258, 220, n=18, a0=0, a1=180, opacity=0.14, sid="lk-sb")
lk_body = f"""    <div id="lk-wrap" style="position:absolute;inset:0">
      {panel_svg("lk-panel", lk_pts, lk_in, burst=lk_burst)}
      <div id="lk-l1" class="row lbl" style="top:282px;height:36px;font-size:28px"><span class="w lk-w1">Untuk</span>&nbsp;<span class="w lk-w1">warga</span></div>
      <div id="lk-l2" class="row shadow" style="top:322px;height:76px"><span id="lk-big" class="disp" style="font-size:66px;padding:0 6px">{letters("Sungai Petani", "lk-L")}</span></div>
      <div id="lk-l3" class="lbl" style="position:absolute;left:226px;top:404px;height:34px;font-size:28px;letter-spacing:0.18em">atau berdekatan</div>
      <svg id="lk-route" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0;overflow:visible">
        <line id="lk-line" x1="232" y1="458" x2="604" y2="458" stroke="{GOLD}" stroke-width="2.2" stroke-dasharray="2 10" stroke-linecap="round"/>
        <polygon points="218,450 226,458 218,466 210,458" fill="{GOLD}"/>
        <polygon id="lk-dot" points="232,448 242,458 232,468 222,458" fill="#FFF0BE"/>
      </svg>
      <div id="lk-chip" style="position:absolute;left:618px;top:434px;width:236px;height:48px">
        <div style="position:absolute;inset:0;background:{GOLD};clip-path:polygon(12px 0,224px 0,236px 12px,236px 36px,224px 48px,12px 48px,0 36px,0 12px)"></div>
        <div style="position:absolute;inset:2.5px;background:#0B3529;clip-path:polygon(10px 0,221px 0,231px 10px,231px 33px,221px 43px,10px 43px,0 33px,0 10px)"></div>
        <div class="row body gold" style="left:0;width:236px;top:0;height:48px;font-size:30px;letter-spacing:0.16em;padding-top:4px">Penang</div>
      </div>
      <div id="lk-l4" class="row body" style="top:504px;height:38px;font-size:30px"><span class="w lk-w4">Nak</span>&nbsp;<span class="w lk-w4">cari</span>&nbsp;<span class="w lk-w4 gold">rumah?</span></div>
    </div>"""
lk_script = """      tl.fromTo("#lk-wrap", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out" }, 0);
      tl.fromTo(".lk-w1", { opacity: 0 }, { opacity: 1, duration: 0.14, stagger: 0.14, ease: "power2.out" }, 0.04);
      tl.fromTo(".lk-L", { opacity: 0 }, { opacity: 1, duration: 0.16, stagger: 0.03, ease: "power2.out" }, 0.64);
      tl.fromTo(".lk-L", { backgroundPosition: "120% 0, 0 0" }, { backgroundPosition: "-40% 0, 0 0", duration: 0.3, ease: "power1.inOut", stagger: 0.03 }, 1.2);
      tl.fromTo("#lk-l3", { opacity: 0 }, { opacity: 0.92, duration: 0.2, ease: "power2.out" }, 1.22);
      tl.fromTo("#lk-line", { attr: { x2: 232 } }, { attr: { x2: 604 }, duration: 1.0, ease: "power1.inOut" }, 1.55);
      tl.fromTo("#lk-dot", { x: 0 }, { x: 372, duration: 1.0, ease: "power1.inOut" }, 1.55);
      tl.fromTo("#lk-chip", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power2.out" }, 2.56);
      tl.fromTo(".lk-w4", { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "power2.out", stagger: { each: 0.39 } }, 3.08);
      tl.to("#lk-wrap", { opacity: 0, filter: "blur(6px)", duration: 0.14, ease: "power2.in" }, 4.15);"""
lk_css = ""

# ---------------------------------------------------------------- HARTANAH (6.48 - 9.74, local 0 - 3.26)
hp_pts = ziggurat(180, 246, 720, 290, step=ZSTEP, chamfer=20)
hp_in = ziggurat(180, 246, 720, 290, inset=10, step=ZSTEP, chamfer=20)
hp_burst = sunburst(540, 536, 320, n=26, opacity=0.18, sid="hp-sb")
def chip(cid, x, y, w, h, text):
    c = 10
    return f"""<div id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px">
        <div style="position:absolute;inset:0;background:{GOLD};clip-path:polygon({c}px 0,{w-c}px 0,{w}px {c}px,{w}px {h-c}px,{w-c}px {h}px,{c}px {h}px,0 {h-c}px,0 {c}px)"></div>
        <div style="position:absolute;inset:2.5px;background:#0B3529;clip-path:polygon({c-2}px 0,{w-c-3}px 0,{w-5}px {c-2}px,{w-5}px {h-c-3}px,{w-c-3}px {h-5}px,{c-2}px {h-5}px,0 {h-c-3}px,0 {c-2}px)"></div>
        <div class="row body gold" style="left:0;width:{w}px;top:0;height:{h}px;font-size:28px;letter-spacing:0.14em;padding-top:4px">{text}</div>
      </div>"""
hp_body = f"""    <div id="hp-flash" style="position:absolute;inset:0;background:rgba(255,246,225,1);opacity:0"></div>
    <div id="hp-wrap" style="position:absolute;inset:0">
      {panel_svg("hp-panel", hp_pts, hp_in, burst=hp_burst)}
      <div id="hp-l1" class="row shadow" style="top:312px;height:80px"><span id="hp-big" class="disp" style="font-size:72px;padding:0 6px">{letters("Meera Grand", "hp-L")}</span></div>
      {rule("hp-rule", 404, 380, 700)}
      <div id="hp-l2" class="row body" style="top:418px;height:36px;font-size:28px;letter-spacing:0.32em"><span class="w hp-w2">Bukit</span>&nbsp;<span class="w hp-w2">Banyan</span></div>
      {chip("hp-c1", 296, 466, 180, 46, "Semi-D")}
      {chip("hp-c2", 492, 466, 292, 46, "Double Storey")}
    </div>"""
hp_script = """      tl.fromTo("#hp-flash", { opacity: 0.35 }, { opacity: 0, duration: 0.25, ease: "power2.out" }, 0);
      tl.fromTo("#hp-wrap", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out" }, 0.0);
      tl.fromTo(".hp-L", { opacity: 0.2 }, { opacity: 1, duration: 0.16, stagger: 0.04, ease: "power2.out" }, 0.05);
      tl.fromTo(".hp-L", { backgroundPosition: "120% 0, 0 0" }, { backgroundPosition: "-40% 0, 0 0", duration: 0.3, ease: "power1.inOut", stagger: 0.035 }, 0.6);
      tl.fromTo("#hp-rule", { scaleX: 0, transformOrigin: "540px 404px" }, { scaleX: 1, duration: 0.4, ease: "power3.out" }, 0.62);
      tl.fromTo(".hp-w2", { opacity: 0 }, { opacity: 1, duration: 0.15, stagger: 0.36, ease: "power2.out" }, 0.95);
      tl.fromTo("#hp-c1", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power2.out" }, 1.64);
      tl.fromTo("#hp-c2", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power2.out" }, 2.22);
      tl.to("#hp-wrap", { opacity: 0, filter: "blur(6px)", duration: 0.18, ease: "power2.in" }, 3.05);"""
hp_css = ""

# ---------------------------------------------------------------- CTA (9.74 - 13.5, local 0 - 3.76)
# A profile card that mirrors the TikTok bio: name, handle, bio lines, link.
ct_pts = stepped_corners(150, 262, 780, 352, c=26, s=12)
ct_in = stepped_corners(150, 262, 780, 352, inset=10, c=26, s=12)
ct_body = f"""    <div id="ct-wrap" style="position:absolute;inset:0">
      {panel_svg("ct-panel", ct_pts, ct_in, fill="rgba(10,10,10,0.9)")}
      <div id="ct-tab" style="position:absolute;left:260px;top:240px;width:560px;height:46px;background:#0B3529;border:2px solid {GOLD}"></div>
      <div id="ct-tab1" class="row body" style="top:240px;height:46px;font-size:28px;letter-spacing:0.12em;padding-top:4px">Nak tahu detail lanjut?</div>
      <div id="ct-tab2" class="row body gold" style="top:240px;height:46px;font-size:28px;letter-spacing:0.2em;padding-top:4px;opacity:0">Klik link di bio</div>
      <div id="ct-avatar" style="position:absolute;left:196px;top:314px;width:92px;height:92px;border-radius:50%;border:2.5px solid {GOLD};background:#0B3529;display:flex;align-items:center;justify-content:center">
        <span class="disp gold" style="font-size:52px;padding-top:6px">N</span>
      </div>
      <div id="ct-name" style="position:absolute;left:312px;top:318px;height:52px;font-family:'Josefin Sans',sans-serif;font-weight:700;font-size:46px;color:#fff;white-space:nowrap">NAZProperty</div>
      <div id="ct-handle" style="position:absolute;left:312px;top:370px;height:34px;font-family:'Josefin Sans',sans-serif;font-weight:600;font-size:28px;color:#A8A8A8;white-space:nowrap">@nazpropertyy &middot; Verified business</div>
      <svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><line x1="196" y1="428" x2="884" y2="428" stroke="{GOLD}" stroke-width="1.4" opacity="0.7"/></svg>
      <div id="ct-bio1" style="position:absolute;left:196px;top:444px;height:38px;font-family:'Josefin Sans',sans-serif;font-weight:600;font-size:30px;color:#EDEDED;white-space:nowrap">Untuk mudahkan urusan boleh</div>
      <div id="ct-bio2" style="position:absolute;left:196px;top:484px;height:38px;font-family:'Josefin Sans',sans-serif;font-weight:600;font-size:30px;color:#EDEDED;white-space:nowrap">klik link bawah ini <span id="ct-hand" style="display:inline-block;font-family:'Noto Color Emoji';font-size:28px">&#128071;</span></div>
      <div id="ct-link" style="position:absolute;left:196px;top:534px;height:42px;font-family:'Josefin Sans',sans-serif;font-weight:700;font-size:32px;color:#fff;white-space:nowrap">nijam98.github.io/Video-Prop</div>
      <svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><line id="ct-ul" x1="196" y1="578" x2="672" y2="578" stroke="{GOLD}" stroke-width="3"/></svg>
    </div>"""
ct_script = """      tl.fromTo("#ct-wrap", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power2.out" }, 0);
      // "isi" at local 0.98: the tab flips to the CTA
      tl.to("#ct-tab1", { opacity: 0, duration: 0.15, ease: "power2.in" }, 0.9);
      tl.fromTo("#ct-tab2", { opacity: 0 }, { opacity: 1, duration: 0.18, ease: "power2.out" }, 1.0);
      tl.fromTo(["#ct-bio1", "#ct-bio2"], { opacity: 0 }, { opacity: 1, duration: 0.2, stagger: 0.25, ease: "power2.out" }, 1.0);
      tl.fromTo("#ct-link", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power2.out" }, 1.6);
      tl.fromTo("#ct-ul", { scaleX: 0, transformOrigin: "196px 578px" }, { scaleX: 1, duration: 0.45, ease: "power3.out" }, 1.75);
      tl.fromTo("#ct-hand", { y: 0 }, { y: 6, duration: 0.2, ease: "power1.inOut", yoyo: true, repeat: 3 }, 1.9);"""
ct_css = ""

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
