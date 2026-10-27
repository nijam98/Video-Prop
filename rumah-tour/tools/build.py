"""Generate the HyperFrames project (index.html + compositions/*) from edl.json.

Design: "Blueprint Lime" — architect-style room tags, dimension lines and a laser
level, deep navy glass + lime accent. Graphics live in the top band (y 230-560),
captions in the lower band (y 1190-1330); the speaker's face sits between them.
Run: python3 tools/build.py   (from the project dir)
"""
import json, statistics, html

W, H, FPS = 1080, 1920, 30
EDL = json.load(open("edl.json"))
SEGS = EDL["segments"]
SEG = {s["id"]: s for s in SEGS}
CUT_END = EDL["total"]          # last frame of footage
HOLD = 3.0                      # end-card hold on a still of the last frame
TOTAL = round(CUT_END + HOLD, 3)
FACES = json.load(open("tools/faces.json"))

# copy the CTA here so it is easy to change
CTA_1, CTA_2, CTA_3 = "CORNER LOT", "MASIH ADA", "TEKAN LINK DI BIO"


def r(x):
    return round(x, 3)


def word(seg, prefix, n=0):
    """Output-time (start, end) of the nth word in a segment starting with prefix."""
    hits = [w for w in SEG[seg]["words"] if w["text"].lower().startswith(prefix.lower())]
    w = hits[n]
    return w["start"], w["end"]


def ws(seg, prefix, n=0):
    return word(seg, prefix, n)[0]


def we(seg, prefix, n=0):
    return word(seg, prefix, n)[1]


def face_origin(seg):
    s = SEG[seg]
    xs, ys = [], []
    for e in FACES:
        if s["src_in"] <= e["t"] <= s["src_out"] and e["faces"]:
            b = max(e["faces"], key=lambda b: b[4])
            xs.append(b[0] + b[2] / 2); ys.append(b[1] + b[3] / 2)
    if not xs:
        return "50% 42%"
    return f"{statistics.median(xs) / W * 100:.1f}% {statistics.median(ys) / H * 100:.1f}%"


# ---------------------------------------------------------------- shared CSS
BASE_CSS = """
#root { position:absolute; inset:0; overflow:visible; }
.ch { display:inline-block; white-space:pre; }
.wd { display:inline-block; white-space:nowrap; }
/* blueprint room tag */
.tag { position:absolute; left:72px; display:flex; align-items:center; gap:20px; padding:16px 30px 18px 22px; opacity:0; white-space:nowrap; }
.tag-bg { position:absolute; inset:0; background:rgba(9,18,30,.68); border:2px solid rgba(255,255,255,.92); backdrop-filter:blur(14px); }
.tk { position:absolute; width:16px; height:16px; border:4px solid var(--lime); opacity:0; }
.tk1 { left:-9px; top:-9px; border-right:none; border-bottom:none; }
.tk2 { right:-9px; bottom:-9px; border-left:none; border-top:none; }
.scanw { position:absolute; inset:0; }
.scan { position:absolute; left:-2px; top:-8px; bottom:-8px; width:4px; background:var(--lime); box-shadow:0 0 16px 3px rgba(200,255,46,.85); opacity:0; }
.idx { position:relative; font-family:"Space Mono"; font-weight:700; font-size:30px; line-height:34px; color:var(--lime); letter-spacing:.04em; display:inline-flex; opacity:0; }
.reel { display:inline-block; height:34px; overflow:hidden; vertical-align:top; }
.reelin { display:flex; flex-direction:column; }
.reelin span { height:34px; line-height:34px; }
.lbl { position:relative; font-family:"Archivo Black"; font-size:64px; line-height:1; color:#fff; letter-spacing:-.01em; text-transform:uppercase; }
/* lime block-reveal chip */
.sub { position:absolute; left:72px; font-family:"Space Mono"; font-weight:700; font-size:32px; color:var(--ink);
  padding:8px 16px 9px; letter-spacing:.06em; opacity:0; white-space:nowrap; }
.sub-bg { position:absolute; inset:0; background:var(--lime); }
.sub-tx { position:relative; }
/* architectural dimension line */
.dim { position:absolute; opacity:0; }
.dim .bar { position:absolute; background:#fff; box-shadow:0 0 12px rgba(0,0,0,.45); }
.dim .cap { position:absolute; background:#fff; box-shadow:0 0 8px rgba(0,0,0,.4); }
.dim .spark { position:absolute; width:14px; height:14px; margin:-7px 0 0 -7px; border-radius:50%; background:#fff;
  box-shadow:0 0 14px 5px rgba(200,255,46,.9); opacity:0; }
.dim .pill { position:absolute; font-family:"Space Mono"; font-weight:700; font-size:34px; line-height:40px; color:var(--ink);
  padding:6px 16px 8px; white-space:nowrap; letter-spacing:.05em; }
.dim .pill-bg { position:absolute; inset:0; background:var(--lime); }
.dim .pill-tx { position:relative; display:inline-flex; }
.dim .reel, .dim .reelin span { height:40px; line-height:40px; }
"""

ROOT_VARS = ":root{--ink:#0B1626;--lime:#C8FF2E;--glass:rgba(9,18,30,.66);}"
JUNK = "7#4K2X9A"  # glyphs the index reels flick through (fixed list: deterministic)


def chars(text, cls="ch"):
    """Split text into per-letter spans so letters can stagger."""
    words = text.split(" ")
    out = []
    for i, w in enumerate(words):
        out.append('<span class="wd">' + "".join(f'<span class="{cls}">{html.escape(c)}</span>' for c in w) + "</span>")
        if i + 1 < len(words):
            out.append(f'<span class="{cls}"> </span>')  # breakable space between words
    return "".join(out)


def reel(final, k):
    """A digit that flicks through 3 junk glyphs before landing on its real value."""
    if not final.isalnum():
        return f'<span>{final}</span>'
    glyphs = [JUNK[(k * 3 + j) % len(JUNK)] for j in range(3)] + [final]
    return '<span class="reel" data-motion-blur="off"><span class="reelin">' + "".join(f"<span>{g}</span>" for g in glyphs) + "</span></span>"


def scene(cid, start, dur, body, css, js):
    return f"""<template>
  <style>
{ROOT_VARS}
{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-layout-allow-overlap>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


class Scene:
    """Collects markup + timeline lines for one chapter; times given in film time."""

    def __init__(self, cid, start, end):
        self.cid, self.start, self.end = cid, r(start), r(end)
        self.body, self.css, self.js = [], [], []

    def t(self, abs_t):
        return r(abs_t - self.start)

    def add(self, *lines):
        self.js += ["    " + l for l in lines]

    # --- staged letter helpers -------------------------------------------
    def letters_in(self, sel, a, stagger=.024, y=26):
        self.add(f'tl.fromTo("{sel}", {{opacity:0, y:{y}, filter:"blur(8px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:.42, ease:"expo.out", stagger:{stagger}}}, {r(a)});')

    def letters_out(self, sel, b):
        self.add(f'tl.to("{sel}", {{opacity:0, y:-14, filter:"blur(6px)", duration:.16, ease:"power2.in", stagger:{{each:.01, from:"end"}}}}, {r(b)});')

    # --- blueprint tag ----------------------------------------------------
    def tag(self, id_, idx, label_html, t_in, t_out, top=250):
        idx_html = "".join(reel(c, k) for k, c in enumerate(idx)) if idx.isalnum() else idx
        self.body.append(
            f'    <div id="{id_}" class="tag" style="top:{top}px"><div class="tag-bg" id="{id_}-bg"></div>'
            f'<i class="tk tk1" id="{id_}-k1"></i><i class="tk tk2" id="{id_}-k2"></i>'
            f'<div class="scanw" id="{id_}-sw"><div class="scan" id="{id_}-sc"></div></div>'
            f'<span class="idx" id="{id_}-i">{idx_html}</span><span class="lbl" id="{id_}-l">{label_html}</span></div>')
        a, b = self.t(t_in), self.t(t_out)
        self.add(
            f'tl.set("#{id_}", {{opacity:1}}, {a});',
            # corner ticks slide in from outside and lock
            f'tl.fromTo("#{id_}-k1", {{opacity:0, x:-28, y:-28}}, {{opacity:1, x:0, y:0, duration:.5, ease:"expo.out"}}, {a});',
            f'tl.fromTo("#{id_}-k2", {{opacity:0, x:28, y:28}}, {{opacity:1, x:0, y:0, duration:.5, ease:"expo.out"}}, {a});',
            # glass opens behind a lime scan line
            f'tl.fromTo("#{id_}-bg", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:.55, ease:"power4.inOut"}}, {r(a + .04)});',
            f'tl.fromTo("#{id_}-sw", {{xPercent:0}}, {{xPercent:100, duration:.55, ease:"power4.inOut"}}, {r(a + .04)});',
            f'tl.fromTo("#{id_}-sc", {{opacity:0}}, {{opacity:1, duration:.06}}, {r(a + .04)});',
            f'tl.to("#{id_}-sc", {{opacity:0, duration:.18, ease:"power2.out"}}, {r(a + .52)});',
            # index flicks through glyphs like a readout
            f'tl.fromTo("#{id_}-i", {{opacity:0}}, {{opacity:1, duration:.08}}, {r(a + .12)});',
        )
        if idx.isalnum():
            self.add(f'tl.fromTo("#{id_}-i .reelin", {{y:0}}, {{y:-102, duration:.36, ease:"steps(3)", stagger:.07}}, {r(a + .12)});')
        self.letters_in(f"#{id_}-l .ch", a + .16)
        # exit: letters fold out, glass closes to the right, ticks shrink
        self.letters_out(f"#{id_}-l .ch", b - .32)
        self.add(
            f'tl.to("#{id_}-i", {{opacity:0, duration:.14, ease:"power2.in"}}, {r(b - .3)});',
            f'tl.to("#{id_}-bg", {{clipPath:"inset(0% 0% 0% 100%)", duration:.24, ease:"power3.in"}}, {r(b - .26)});',
            f'tl.to(["#{id_}-k1","#{id_}-k2"], {{opacity:0, scale:.4, duration:.2, ease:"power3.in"}}, {r(b - .22)});',
            f'tl.set("#{id_}", {{visibility:"hidden"}}, {b});',
        )

    # --- lime block-reveal chip ---------------------------------------------
    def sub(self, id_, text, t_in, t_out, top):
        self.body.append(f'    <div id="{id_}" class="sub" style="top:{top}px"><div class="sub-bg" id="{id_}-bg"></div>'
                         f'<span class="sub-tx" id="{id_}-t">{chars(text)}</span></div>')
        a, b = self.t(t_in), self.t(t_out)
        self.add(
            f'tl.set("#{id_}", {{opacity:1}}, {a});',
            f'tl.fromTo("#{id_}-bg", {{scaleX:0}}, {{scaleX:1, duration:.38, ease:"expo.out", transformOrigin:"0% 50%"}}, {a});',
            f'tl.fromTo("#{id_}-t .ch", {{opacity:0, x:-12}}, {{opacity:1, x:0, duration:.26, ease:"power3.out", stagger:.016}}, {r(a + .1)});',
            f'tl.to("#{id_}-t .ch", {{opacity:0, duration:.1, stagger:{{each:.006, from:"end"}}}}, {r(b - .28)});',
            f'tl.to("#{id_}-bg", {{scaleX:0, duration:.22, ease:"power3.in", transformOrigin:"100% 50%"}}, {r(b - .22)});',
            f'tl.set("#{id_}", {{visibility:"hidden"}}, {b});',
        )

    def out(self, id_, b, dur=.2):
        self.add(f'tl.to("#{id_}", {{opacity:0, filter:"blur(8px)", duration:{dur}, ease:"power2.in"}}, {r(b - dur)});',
                 f'tl.set("#{id_}", {{visibility:"hidden"}}, {b});')

    def _pill(self, id_, label, count):
        if count:  # ("&#177; ", ["03","06","09","12","15"], " KAKI")
            pre, vals, post = count
            col = '<span class="reel" data-motion-blur="off"><span class="reelin">' + "".join(f"<span>{v}</span>" for v in vals) + "</span></span>"
            return f'<div class="pill-bg" id="{id_}-pb"></div><span class="pill-tx" id="{id_}-pt">{pre}{col}{post}</span>'
        return f'<div class="pill-bg" id="{id_}-pb"></div><span class="pill-tx" id="{id_}-pt">{chars(label)}</span>'

    def _pill_in(self, id_, a, count):
        self.add(f'tl.fromTo("#{id_}-pb", {{scaleX:0}}, {{scaleX:1, duration:.34, ease:"expo.out", transformOrigin:"0% 50%"}}, {r(a)});')
        if count:
            n = len(count[1]) - 1
            self.add(f'tl.fromTo("#{id_}-pt", {{opacity:0}}, {{opacity:1, duration:.1}}, {r(a + .08)});',
                     f'tl.fromTo("#{id_}-pt .reelin", {{y:0}}, {{y:{-40 * n}, duration:{.09 * n:.2f}, ease:"steps({n})"}}, {r(a + .1)});')
        else:
            self.add(f'tl.fromTo("#{id_}-pt .ch", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:.25, ease:"power3.out", stagger:.02}}, {r(a + .08)});')

    def hdim(self, id_, label, t_in, t_out, top, left=90, width=900, count=None):
        """Horizontal architectural dimension: draws out from the centre, 45-degree end ticks, label block-reveals."""
        mid = width // 2
        self.body.append(
            f'    <div id="{id_}" class="dim" style="left:{left}px;top:{top}px;width:{width}px;height:90px" data-layout-allow-overflow>'
            f'<div class="bar" id="{id_}-bar" style="left:0;top:62px;width:{width}px;height:3px"></div>'
            f'<div class="cap" id="{id_}-c1" style="left:-1px;top:46px;width:4px;height:36px"></div>'
            f'<div class="cap" id="{id_}-c2" style="left:{width - 3}px;top:46px;width:4px;height:36px"></div>'
            f'<div class="spark" id="{id_}-s1" style="left:{mid}px;top:63px"></div><div class="spark" id="{id_}-s2" style="left:{mid}px;top:63px"></div>'
            f'<div class="pill" id="{id_}-p" style="left:{mid}px;top:0;transform:translateX(-50%)">{self._pill(id_, label, count)}</div></div>')
        a, b = self.t(t_in), self.t(t_out)
        self.add(
            f'tl.set("#{id_}", {{opacity:1}}, {a});',
            f'tl.set(["#{id_}-c1","#{id_}-c2"], {{rotation:45, scaleY:0}}, 0);',
            f'tl.fromTo("#{id_}-bar", {{scaleX:0}}, {{scaleX:1, duration:.6, ease:"expo.out", transformOrigin:"50% 50%"}}, {a});',
            f'tl.fromTo("#{id_}-s1", {{x:0, opacity:1}}, {{x:{-mid}, duration:.6, ease:"expo.out"}}, {a});',
            f'tl.fromTo("#{id_}-s2", {{x:0, opacity:1}}, {{x:{mid}, duration:.6, ease:"expo.out"}}, {a});',
            f'tl.to(["#{id_}-s1","#{id_}-s2"], {{opacity:0, scale:2.2, duration:.3, ease:"power2.out"}}, {r(a + .45)});',
            f'tl.to(["#{id_}-c1","#{id_}-c2"], {{scaleY:1, duration:.32, ease:"back.out(2.6)"}}, {r(a + .38)});',
        )
        self._pill_in(id_, a + .22, count)
        self.out(id_, b)

    def vdim(self, id_, label, t_in, t_out, left, top, height):
        self.body.append(
            f'    <div id="{id_}" class="dim" style="left:{left}px;top:{top}px;width:90px;height:{height}px" data-layout-allow-overflow>'
            f'<div class="bar" id="{id_}-bar" style="left:18px;top:0;width:3px;height:{height}px"></div>'
            f'<div class="cap" id="{id_}-c1" style="left:2px;top:-1px;width:36px;height:4px"></div>'
            f'<div class="cap" id="{id_}-c2" style="left:2px;top:{height - 3}px;width:36px;height:4px"></div>'
            f'<div class="spark" id="{id_}-s1" style="left:19px;top:{height}px"></div>'
            f'<div class="pill" id="{id_}-p" style="left:36px;top:{height // 2 - 28}px">{self._pill(id_, label, None)}</div></div>')
        a, b = self.t(t_in), self.t(t_out)
        self.add(
            f'tl.set("#{id_}", {{opacity:1}}, {a});',
            f'tl.set(["#{id_}-c1","#{id_}-c2"], {{rotation:-45, scaleX:0}}, 0);',
            f'tl.fromTo("#{id_}-bar", {{scaleY:0}}, {{scaleY:1, duration:.65, ease:"expo.out", transformOrigin:"50% 100%"}}, {a});',
            f'tl.fromTo("#{id_}-s1", {{y:0, opacity:1}}, {{y:{-height}, duration:.65, ease:"expo.out"}}, {a});',
            f'tl.to("#{id_}-s1", {{opacity:0, scale:2.2, duration:.3, ease:"power2.out"}}, {r(a + .5)});',
            f'tl.to(["#{id_}-c1","#{id_}-c2"], {{scaleX:1, duration:.32, ease:"back.out(2.6)"}}, {r(a + .4)});',
        )
        self._pill_in(id_, a + .28, None)
        self.out(id_, b)

    def html(self):
        return scene(self.cid, self.start, self.end - self.start, "\n".join(self.body), "\n".join(self.css), "\n".join(self.js))


scenes = []
seg_end = lambda s: r(SEG[s]["start"] + SEG[s]["dur"])
seg_start = lambda s: SEG[s]["start"]

# ---------------------------------------------------------------- 1. hook
sc = Scene("hook", 0, seg_end("hook"))
sc.css.append("""
#hk-row { position:absolute; left:72px; top:236px; display:flex; gap:26px; }
.tile { position:relative; padding:14px 30px 18px 26px; background:var(--glass); border:2px solid rgba(255,255,255,.92); backdrop-filter:blur(14px); }
.tile .num { position:relative; font-family:"Archivo Black"; font-size:190px; line-height:.86; color:#fff; display:block; }
.tile .unit { position:relative; font-family:"Space Mono"; font-weight:700; font-size:34px; color:#fff; letter-spacing:.12em; display:block; margin-top:6px; }
#hk-t2 .num { color:var(--lime); }
.uline { position:absolute; left:26px; right:30px; bottom:8px; height:6px; background:var(--lime); transform-origin:0 50%; }
.glw { position:absolute; inset:0; overflow:hidden; }
.gl { position:absolute; top:-30%; bottom:-30%; left:0; width:45%; background:linear-gradient(100deg, rgba(255,255,255,0), rgba(255,255,255,.5) 50%, rgba(255,255,255,0)); }
#hk-stamp { position:absolute; left:560px; top:452px; font-family:"Archivo Black"; font-size:58px; color:var(--ink);
  background:var(--lime); padding:8px 22px 12px; opacity:0; box-shadow:0 10px 30px rgba(0,0,0,.35); white-space:nowrap; }
#hk-ring { position:absolute; left:560px; top:452px; width:420px; height:92px; border:4px solid var(--lime); opacity:0; }
""")
sc.body.append(f"""    <div id="hk-row" data-layout-allow-overflow>
      <div class="tile" id="hk-t1"><div class="glw"><div class="gl" id="hk-g1"></div></div><span class="num">4</span><span class="unit">BILIK</span><div class="uline" id="hk-u1"></div></div>
      <div class="tile" id="hk-t2"><div class="glw"><div class="gl" id="hk-g2"></div></div><span class="num">5</span><span class="unit">TOILET</span><div class="uline" id="hk-u2"></div></div>
    </div>
    <div id="hk-ring"></div>
    <div id="hk-stamp">{chars("PALING RARE")}</div>""")
e4, l5, rare = ws("hook", "empat"), ws("hook", "lima"), ws("hook", "rare")
sc.add(
    # frame 0 already shows both tiles (thumbnail); each spoken number gets a glint, kick and underline
    'tl.set(["#hk-u1","#hk-u2"], {scaleX:0}, 0);',
    'tl.set(["#hk-g1","#hk-g2"], {xPercent:-160, skewX:-18}, 0);',
)
for n, tt in (("1", e4), ("2", l5)):
    sc.add(f'tl.to("#hk-g{n}", {{xPercent:330, duration:.7, ease:"power2.inOut"}}, {r(tt - .05)});',
           f'tl.to("#hk-u{n}", {{scaleX:1, duration:.45, ease:"expo.out"}}, {r(tt)});',
           f'tl.fromTo("#hk-t{n} .num", {{scale:1.14, filter:"blur(4px)"}}, {{scale:1, filter:"blur(0px)", duration:.45, ease:"expo.out", transformOrigin:"0% 100%"}}, {r(tt)});')
sc.add(
    f'tl.fromTo("#hk-stamp", {{opacity:0, scale:2.3, rotation:-16, filter:"blur(10px)"}}, {{opacity:1, scale:1, rotation:-6, filter:"blur(0px)", duration:.3, ease:"power4.out"}}, {r(rare - .06)});',
    f'tl.fromTo("#hk-ring", {{opacity:.95, scale:1, rotation:-6}}, {{opacity:0, scale:1.5, duration:.6, ease:"expo.out"}}, {r(rare + .2)});',
    f'tl.fromTo("#hk-row", {{x:0}}, {{keyframes:[{{x:-9, duration:.035}}, {{x:7, duration:.035}}, {{x:-4, duration:.035}}, {{x:0, duration:.05}}]}}, {r(rare + .2)});',
    # whip exit with the footage
    f'tl.to(["#hk-row","#hk-stamp"], {{x:-420, opacity:0, duration:.18, ease:"power3.in"}}, {r(sc.end - .18)});',
)
scenes.append(sc)

# ---------------------------------------------------------------- 2. lokasi (s1 + s2)
sc = Scene("lokasi", seg_start("s1"), seg_end("s2"))
sc.css.append("""
#lk-pin { position:absolute; left:72px; top:244px; width:58px; height:80px; opacity:0; }
#lk-rip { position:absolute; left:61px; top:316px; width:80px; height:22px; border:3px solid var(--lime); border-radius:50%; opacity:0; }
#lk-head { position:absolute; left:150px; top:236px; opacity:0; }
#lk-head .k { position:relative; font-family:"Space Mono"; font-weight:700; font-size:30px; color:var(--lime); padding:4px 12px 6px; letter-spacing:.12em; display:inline-block; margin-bottom:8px; }
#lk-kbg { position:absolute; inset:0; background:var(--ink); }
#lk-kt { position:relative; }
#lk-v .ch { opacity:0; }
#lk-head .v { font-family:"Archivo Black"; font-size:70px; line-height:1; color:#fff; display:block; text-shadow:0 4px 24px rgba(0,0,0,.5); }
.chip { position:absolute; top:250px; display:flex; align-items:center; gap:14px; padding:14px 26px 16px 18px; opacity:0; white-space:nowrap; }
.chip-bg { position:absolute; inset:0; background:var(--glass); border:2px solid #fff; backdrop-filter:blur(14px); }
.chip .ck { position:relative; width:40px; height:40px; background:var(--lime); display:flex; align-items:center; justify-content:center; }
.chip .ck path { stroke-dasharray:32; }
.chip .tx { position:relative; font-family:"Archivo Black"; font-size:54px; color:#fff; line-height:1; }
#lk-corner { position:absolute; left:72px; top:236px; opacity:0; }
#lk-corner .big { position:relative; font-family:"Archivo Black"; font-size:118px; line-height:.95; color:var(--ink); padding:0 4px 10px; display:inline-block; white-space:nowrap; isolation:isolate; }
#lk-hl { position:absolute; left:-18px; right:-22px; top:2%; height:100%; background:var(--lime); z-index:-1; transform-origin:0 50%; }
#lk-avail { position:relative; display:inline-block; margin-top:14px; font-family:"Space Mono"; font-weight:700; font-size:36px; letter-spacing:.1em;
  color:#fff; padding:8px 18px 10px; }
#lk-abg { position:absolute; inset:0; background:var(--glass); border:2px solid #fff; }
#lk-avail i { position:relative; display:inline-block; width:16px; height:16px; border-radius:50%; background:var(--lime); margin-right:14px; font-style:normal; box-shadow:0 0 12px 2px rgba(200,255,46,.8); }
#lk-at { position:relative; }
#lk-jom { position:absolute; right:150px; top:262px; font-family:"Archivo Black"; font-size:60px; color:var(--ink); padding:10px 26px 14px; opacity:0; white-space:nowrap; }
#lk-jbg { position:absolute; inset:0; background:var(--lime); }
#lk-jt { position:relative; display:inline-block; }
""")
def check(id_):
    return (f'<svg width="26" height="26" viewBox="0 0 26 26"><path id="{id_}" d="M3 13.5l6.5 6.5L23 6" stroke="#0B1626" '
            f'stroke-width="4.5" fill="none" stroke-linecap="square"/></svg>')
sc.body.append(f"""    <div id="lk-rip"></div>
    <svg id="lk-pin" viewBox="0 0 58 80"><path d="M29 2C14 2 3 13 3 27c0 19 26 50 26 50s26-31 26-50C55 13 44 2 29 2z" fill="#C8FF2E" stroke="#0B1626" stroke-width="3"/><circle cx="29" cy="27" r="9" fill="#0B1626"/></svg>
    <div id="lk-head"><span class="k"><span id="lk-kbg"></span><span id="lk-kt">{chars("PERUMAHAN BARU")}</span></span><span class="v" id="lk-v">{chars("SEBELAH SEKOLAH")}</span></div>
    <div class="chip" id="lk-c1" style="left:72px"><div class="chip-bg" id="lk-c1-bg"></div><span class="ck" id="lk-c1-ck">{check("lk-c1-p")}</span><span class="tx" id="lk-c1-t">{chars("NON-BUMI")}</span></div>
    <div class="chip" id="lk-c2" style="left:500px"><div class="chip-bg" id="lk-c2-bg"></div><span class="ck" id="lk-c2-ck">{check("lk-c2-p")}</span><span class="tx" id="lk-c2-t">{chars("BUMI")}</span></div>
    <div id="lk-corner"><span class="big" id="lk-big"><span id="lk-hl"></span>{chars("CORNER LOT")}</span><br><span id="lk-avail"><span id="lk-abg"></span><i id="lk-dot"></i><span id="lk-at">{chars("MASIH AVAILABLE")}</span></span></div>
    <div id="lk-jom"><span id="lk-jbg"></span><span id="lk-jt">{chars("JOM MASUK ")}<span class="ch" id="lk-arr">&#8594;</span></span></div>""")
t_peru, t_sek = ws("s1", "perumahan"), ws("s1", "sekolah")
t_nb, t_bl, t_cor, t_mas = ws("s2", "non-bumi"), ws("s2", "bumi"), ws("s2", "corner"), ws("s2", "masih")
t_jom = ws("s2", "jom")
T = sc.t
sc.add(
    # pin drops, lands with a ripple; the label block-reveals, then the place line types up letter by letter
    f'tl.fromTo("#lk-pin", {{opacity:0, y:-90}}, {{opacity:1, y:0, duration:.55, ease:"bounce.out"}}, {T(t_peru - .15)});',
    f'tl.fromTo("#lk-rip", {{opacity:.9, scale:.2}}, {{opacity:0, scale:1.8, duration:.6, ease:"expo.out"}}, {T(t_peru + .2)});',
    f'tl.set("#lk-head", {{opacity:1}}, {T(t_peru)});',
    f'tl.fromTo("#lk-kbg", {{scaleX:0}}, {{scaleX:1, duration:.4, ease:"expo.out", transformOrigin:"0% 50%"}}, {T(t_peru)});',
    f'tl.fromTo("#lk-kt .ch", {{opacity:0}}, {{opacity:1, duration:.05, stagger:.025}}, {T(t_peru + .1)});',
)
sc.letters_in("#lk-v .ch", T(t_sek), stagger=.03, y=34)
sc.out("lk-pin", T(t_nb - .05)); sc.out("lk-head", T(t_nb - .05))
for cid, tt in (("lk-c1", t_nb), ("lk-c2", t_bl)):
    a_ = T(tt)
    sc.add(f'tl.set("#{cid}", {{opacity:1}}, {a_});',
           f'tl.fromTo("#{cid}-bg", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:.45, ease:"expo.out"}}, {a_});',
           f'tl.fromTo("#{cid}-ck", {{scale:0, rotation:-90}}, {{scale:1, rotation:0, duration:.45, ease:"back.out(2.2)"}}, {r(a_ + .02)});',
           f'tl.fromTo("#{cid}-p", {{strokeDashoffset:32}}, {{strokeDashoffset:0, duration:.32, ease:"power2.out"}}, {r(a_ + .18)});')
    sc.letters_in(f"#{cid}-t .ch", a_ + .08, stagger=.022, y=20)
sc.out("lk-c1", T(t_cor - .02)); sc.out("lk-c2", T(t_cor - .02))
sc.add(
    'tl.set("#lk-hl", {scaleX:0}, 0);',
    f'tl.set("#lk-corner", {{opacity:1}}, {T(t_cor - .05)});',
    f'tl.to("#lk-hl", {{scaleX:1, duration:.42, ease:"power4.inOut"}}, {T(t_cor - .05)});',
    'tl.set("#lk-avail", {opacity:0}, 0);',
    f'tl.set("#lk-avail", {{opacity:1}}, {T(t_mas)});',
    f'tl.fromTo("#lk-abg", {{scaleX:0}}, {{scaleX:1, duration:.4, ease:"expo.out", transformOrigin:"0% 50%"}}, {T(t_mas)});',
    f'tl.fromTo("#lk-dot", {{scale:0}}, {{scale:1, duration:.4, ease:"back.out(3)"}}, {T(t_mas + .08)});',
    f'tl.fromTo("#lk-at .ch", {{opacity:0}}, {{opacity:1, duration:.05, stagger:.022}}, {T(t_mas + .12)});',
)
sc.letters_in("#lk-big .ch", T(t_cor + .14), stagger=.03, y=40)
sc.out("lk-corner", T(t_jom - .1))
sc.add(
    f'tl.set("#lk-jom", {{opacity:1}}, {T(t_jom)});',
    f'tl.fromTo("#lk-jbg", {{scaleX:0}}, {{scaleX:1, duration:.38, ease:"expo.out", transformOrigin:"100% 50%"}}, {T(t_jom)});',
    f'tl.fromTo("#lk-jt .ch", {{opacity:0, x:18}}, {{opacity:1, x:0, duration:.3, ease:"expo.out", stagger:.02}}, {T(t_jom + .08)});',
    f'tl.fromTo("#lk-arr", {{x:0}}, {{x:14, duration:.5, ease:"power2.inOut"}}, {T(t_jom + .55)});',
    f'tl.to("#lk-jom", {{scale:2.6, opacity:0, filter:"blur(6px)", duration:.35, ease:"power3.in", transformOrigin:"50% 50%"}}, {r(sc.end - sc.start - .35)});',
)
scenes.append(sc)

# ---------------------------------------------------------------- 3. luar (s3a + s3b)
sc = Scene("luar", seg_start("s3a"), seg_end("s3b"))
sc.tag("lr-gate", "01", chars("AUTO GATE"), ws("s3a", "auto"), ws("s3a", "porch"))
sc.tag("lr-porch", "02", chars("PORCH"), ws("s3a", "porch"), seg_end("s3b"))
sc.hdim("lr-luas", "LUAS", ws("s3b", "luas"), seg_end("s3b"), top=400, left=120, width=840)
sc.vdim("lr-tinggi", "TINGGI", ws("s3b", "tinggi"), seg_end("s3b"), left=40, top=540, height=560)
scenes.append(sc)

# ---------------------------------------------------------------- 4. dalam (s4..s8)
sc = Scene("dalam", seg_start("s4"), seg_end("s8"))
sc.tag("dl-tamu", "03", chars("RUANG TAMU"), ws("s4", "ruang"), ws("s5", "ruang"))
sc.sub("dl-luas", "PALING LUAS", ws("s4", "paling"), ws("s5", "ruang"), top=372)
sc.tag("dl-stor", "04", chars("STOR"), ws("s5", "ruang"), ws("s6", "open"))
sc.tag("dl-kit", "05", chars("OPEN ") + '<span id="dl-kit-k">' + chars("KITCHEN") + '</span>', ws("s6", "open"), seg_end("s7"))
sc.js.append(f'    tl.fromTo("#dl-kit-k", {{color:"#FFFFFF"}}, {{color:"#C8FF2E", duration:.15}}, {sc.t(ws("s7", "kitchen"))});')
sc.tag("dl-bel", "06", chars("RUANG BELAKANG"), ws("s8", "ruang"), seg_end("s8"))
sc.hdim("dl-15", "", ws("s8", "15") - .6, seg_end("s8"), top=410, left=90, width=900, count=("\u00b1\u00a0", ["00", "03", "06", "09", "12", "15"], "\u00a0KAKI"))
scenes.append(sc)

# ---------------------------------------------------------------- 5. bilik (s9..s11)
sc = Scene("bilik", seg_start("s9"), seg_end("s11"))
sc.css.append("""
#bk-num { display:inline-block; position:relative; height:64px; overflow:hidden; vertical-align:top; width:84px; }
#bk-reel { position:absolute; left:0; top:0; display:flex; flex-direction:column; }
#bk-reel span { height:64px; line-height:64px; color:var(--lime); }
""")
sc.tag("bk-tag", "07", chars("BILIK ") + '<span id="bk-num" data-layout-allow-overflow data-motion-blur="off"><span id="bk-reel"><span>01</span><span>02</span><span>03</span><span>04</span></span></span>',
       ws("s9", "bilik"), seg_end("s10") - .02)
t4 = ws("s9", "empat")
sc.js.append(f'    tl.fromTo("#bk-reel", {{y:0}}, {{y:-192, duration:.45, ease:"steps(3)"}}, {sc.t(t4 - .3)});')
sc.sub("bk-wc", "+ TOILET SENDIRI", ws("s10", "built"), seg_end("s10") - .02, top=372)
sc.sub("bk-share", "\u2713 TAK SHARING", ws("s10", "tak"), seg_end("s10") - .02, top=432)
sc.tag("bk-tamu", "\u2605", chars("BILIK TETAMU"), seg_start("s11") + .1, seg_end("s11"))
scenes.append(sc)

# ---------------------------------------------------------------- 6. atas (s12..s14)
sc = Scene("atas", seg_start("s12"), seg_end("s14"))
sc.css.append("""
#at-up { position:absolute; left:72px; top:236px; display:flex; align-items:center; gap:22px; }
#at-up .lbl { font-size:86px; text-shadow:0 6px 28px rgba(0,0,0,.45); }
#at-arw { position:relative; width:70px; height:86px; }
.chev { position:absolute; left:0; top:0; width:70px; height:86px; background:var(--lime); opacity:0;
  clip-path:polygon(50% 0,100% 45%,68% 45%,68% 100%,32% 100%,32% 45%,0 45%); }
#at-level { position:absolute; left:0; top:470px; width:1080px; height:5px; background:var(--lime);
  box-shadow:0 0 18px rgba(200,255,46,.9), 0 0 4px #fff; opacity:0; transform-origin:0 50%; }
#at-headw { position:absolute; left:0; top:472px; width:1080px; height:1px; }
#at-head { position:absolute; left:-14px; top:-14px; width:28px; height:28px; border-radius:50%; background:#fff;
  box-shadow:0 0 22px 10px rgba(200,255,46,.95), 0 0 60px 20px rgba(200,255,46,.45); opacity:0; }
#at-lvl-lbl { position:absolute; left:72px; top:392px; font-family:"Space Mono"; font-weight:700; font-size:32px; color:var(--ink);
  padding:6px 16px 8px; letter-spacing:.06em; white-space:nowrap; opacity:0; }
#at-lbg { position:absolute; inset:0; background:var(--lime); }
#at-lt { position:relative; }
#at-ul .ch, #at-lvl-tag .ch { opacity:0; }
#at-lvl-tag { position:absolute; left:72px; top:250px; font-family:"Archivo Black"; font-size:66px; line-height:1; color:#fff;
  text-shadow:0 4px 24px rgba(0,0,0,.6); white-space:nowrap; }
""")
sc.body.append(f"""    <div id="at-up"><div id="at-arw"><div class="chev" id="at-c1"></div><div class="chev" id="at-c2"></div><div class="chev" id="at-c3"></div></div><span class="lbl" id="at-ul">{chars("TINGKAT ATAS")}</span></div>
    <div id="at-lvl-tag">{chars("SAMA TINGGI SEKOLAH")}</div>
    <div id="at-level" data-layout-allow-overflow></div>
    <div id="at-headw" data-layout-allow-overflow><div id="at-head"></div></div>
    <div id="at-lvl-lbl"><span id="at-lbg"></span><span id="at-lt">{chars("ARAS = BUMBUNG SEKOLAH")}</span></div>""")
t_ting = seg_start("s12") + .25
T = sc.t
sc.add(
    # three chevrons rise one after another, the last one stays
    f'tl.fromTo("#at-c1", {{opacity:.35, y:60}}, {{opacity:0, y:-40, duration:.45, ease:"power2.out"}}, {T(t_ting - .1)});',
    f'tl.fromTo("#at-c2", {{opacity:.6, y:60}}, {{opacity:0, y:-20, duration:.45, ease:"power2.out"}}, {T(t_ting - .02)});',
    f'tl.fromTo("#at-c3", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.55, ease:"back.out(2)"}}, {T(t_ting + .06)});',
)
sc.letters_in("#at-ul .ch", T(t_ting + .1), stagger=.03, y=40)
sc.add(f'tl.to("#at-up", {{y:-260, opacity:0, duration:.22, ease:"power3.in"}}, {T(seg_end("s12") - .22)});')
t_sama, t_sek = ws("s13", "sama"), ws("s13", "sekolah")
lv = T(t_sama - .1)
sc.add(
    # laser level: a glowing head draws the line across the frame, then flares out
    f'tl.fromTo("#at-level", {{opacity:1, scaleX:0}}, {{opacity:1, scaleX:1, duration:.85, ease:"power2.inOut"}}, {lv});',
    f'tl.fromTo("#at-headw", {{x:0}}, {{x:1080, duration:.85, ease:"power2.inOut"}}, {lv});',
    f'tl.fromTo("#at-head", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.15}}, {lv});',
    f'tl.to("#at-head", {{opacity:0, scale:3, duration:.35, ease:"power2.out"}}, {r(lv + .8)});',
    f'tl.fromTo("#at-level", {{boxShadow:"0 0 40px rgba(200,255,46,1), 0 0 8px #fff"}}, {{boxShadow:"0 0 18px rgba(200,255,46,.9), 0 0 4px #fff", duration:.6, ease:"power2.out"}}, {r(lv + .85)});',
    f'tl.set("#at-lvl-lbl", {{opacity:1}}, {T(t_sek)});',
    f'tl.fromTo("#at-lbg", {{scaleX:0}}, {{scaleX:1, duration:.4, ease:"expo.out", transformOrigin:"0% 50%"}}, {T(t_sek)});',
    f'tl.fromTo("#at-lt .ch", {{opacity:0}}, {{opacity:1, duration:.04, stagger:.018}}, {T(t_sek + .1)});',
)
sc.letters_in("#at-lvl-tag .ch", T(t_sama), stagger=.025, y=30)
for i in ("at-level", "at-lvl-tag", "at-lvl-lbl"):
    sc.out(i, T(seg_end("s14")))
scenes.append(sc)

# ---------------------------------------------------------------- 7. akhir (s15 + end card)
sc = Scene("akhir", seg_start("s15"), TOTAL)
sc.css.append("""
#ak-prem { position:absolute; left:72px; top:236px; white-space:nowrap; display:flex; }
#ak-semi { font-family:"Archivo Black"; font-size:92px; color:var(--lime); display:inline-block; overflow:hidden; white-space:nowrap; text-shadow:0 6px 28px rgba(0,0,0,.45); }
#ak-pword { font-family:"Archivo Black"; font-size:92px; color:#fff; display:inline-block; text-shadow:0 6px 28px rgba(0,0,0,.45); }
#ak-cta { position:absolute; left:90px; right:90px; top:640px; text-align:center; opacity:0; }
#ak-cta .a { font-family:"Archivo Black"; font-size:128px; line-height:.95; color:#fff; display:block; text-shadow:0 8px 36px rgba(0,0,0,.55); }
#ak-cta .b { position:relative; font-family:"Archivo Black"; font-size:128px; line-height:.95; color:var(--ink); display:inline-block; padding:6px 26px 16px; margin-top:12px; }
#ak-bbg { position:absolute; inset:0; background:var(--lime); box-shadow:0 14px 40px rgba(0,0,0,.35); }
#ak-bt { position:relative; }
#ak-cta .c { font-family:"Space Mono"; font-weight:700; font-size:40px; color:#fff; letter-spacing:.12em; display:block; margin-top:34px; text-shadow:0 2px 14px rgba(0,0,0,.8); }
#ak-pword .ch, #ak-semi .ch, #ak-a .ch, #ak-bt .ch, #ak-c .ch { opacity:0; }
#ak-scrim { position:absolute; inset:0; background:radial-gradient(ellipse at 50% 45%, rgba(9,18,30,.55), rgba(9,18,30,.15) 70%); opacity:0; }
""")
sc.body.append(f"""    <div id="ak-scrim"></div>
    <div id="ak-prem"><span id="ak-semi">{chars("SEMI-")}</span><span id="ak-pword">{chars("PREMIUM")}</span></div>
    <div id="ak-cta"><span class="a" id="ak-a">{chars(CTA_1)}</span><span class="b" id="ak-b"><span id="ak-bbg"></span><span id="ak-bt">{chars(CTA_2)}</span></span><span class="c" id="ak-c">{chars(CTA_3 + " ")}<span class="ch" id="ak-arr">&#8594;</span></span></div>""")
t_prem, t_semi, t_balk = ws("s15", "premium"), ws("s15", "semi"), ws("s15", "balkoni")
T = sc.t
sc.add(
    'tl.set("#ak-semi", {width:0}, 0);',
    # PREMIUM slams in letter by letter; on "semi-" the lime prefix pushes it right
    f'tl.fromTo("#ak-pword .ch", {{opacity:0, scale:1.8, filter:"blur(10px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:.32, ease:"power4.out", stagger:.03, transformOrigin:"50% 70%"}}, {T(t_prem - .06)});',
    f'tl.to("#ak-semi", {{width:296, duration:.4, ease:"expo.out"}}, {T(t_semi)});',
    f'tl.fromTo("#ak-semi .ch", {{opacity:0, y:-50}}, {{opacity:1, y:0, duration:.4, ease:"back.out(2)", stagger:.04}}, {T(t_semi + .02)});',
)
sc.out("ak-prem", T(t_balk - .02))
sc.tag("ak-balk", "08", chars("BALKONI"), t_balk, CUT_END - .05)
cta = T(CUT_END)
sc.add(
    f'tl.fromTo("#ak-scrim", {{opacity:0}}, {{opacity:1, duration:.4, ease:"power2.inOut"}}, {r(cta - .1)});',
    f'tl.set("#ak-cta", {{opacity:1}}, {cta});',
    f'tl.fromTo("#ak-bbg", {{scaleX:0}}, {{scaleX:1, duration:.45, ease:"expo.out", transformOrigin:"50% 50%"}}, {r(cta + .2)});',
    f'tl.fromTo("#ak-b", {{rotation:0}}, {{rotation:-2, duration:.5, ease:"back.out(2)"}}, {r(cta + .2)});',
    f'tl.fromTo("#ak-bt .ch", {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:.3, ease:"power4.out", stagger:.03}}, {r(cta + .32)});',
    f'tl.fromTo("#ak-c .ch", {{opacity:0}}, {{opacity:1, duration:.03, stagger:.022}}, {r(cta + .3)});',
    f'tl.fromTo("#ak-arr", {{x:0}}, {{x:16, duration:.45, ease:"power2.inOut"}}, {r(cta + 1.0)});',
)
sc.letters_in("#ak-a .ch", cta, stagger=.035, y=60)
scenes.append(sc)

# ---------------------------------------------------------------- captions
groups = []
for s in SEGS:
    cur = []
    for i, w in enumerate(s["words"]):
        cur.append(w)
        nxt = s["words"][i + 1] if i + 1 < len(s["words"]) else None
        punct = w["text"][-1] in ",.?!"
        gap = nxt and nxt["start"] - w["end"] >= .15
        if not nxt or punct or gap or len(cur) >= 4:
            groups.append(cur); cur = []
cap_body, cap_js = [], []
for gi, g in enumerate(groups):
    g_start = max(0.12, g[0]["start"] - .05)
    nxt_start = groups[gi + 1][0]["start"] - .05 if gi + 1 < len(groups) else CUT_END
    g_end = r(min(g[-1]["end"] + .25, nxt_start, CUT_END))
    spans = " ".join(f'<span class="cw" id="c{gi}w{wi}">{html.escape(w["text"].rstrip(",."))}</span>' for wi, w in enumerate(g))
    cap_body.append(f'    <div class="cg" id="cg{gi}">{spans}</div>')
    cap_js.append(f'    tl.fromTo("#cg{gi}", {{opacity:0, y:14}}, {{opacity:1, y:0, duration:.14, ease:"power3.out"}}, {r(g_start)});')
    for wi, w in enumerate(g):
        cap_js.append(f'    tl.set("#c{gi}w{wi}", {{color:"#C8FF2E", scale:1.06}}, {r(w["start"])});')
        if wi + 1 < len(g):
            cap_js.append(f'    tl.set("#c{gi}w{wi}", {{color:"#FFFFFF", scale:1}}, {r(g[wi + 1]["start"])});')
    cap_js.append(f'    tl.to("#cg{gi}", {{opacity:0, duration:.1, ease:"power2.in"}}, {r(g_end - .1)});')
    cap_js.append(f'    tl.set("#cg{gi}", {{opacity:0, visibility:"hidden"}}, {g_end});')
cap_css = """
.cg { position:absolute; left:60px; width:840px; top:1196px; text-align:center; opacity:0; overflow:visible; }
.cw { display:inline-block; font-family:"Outfit"; font-weight:800; font-size:66px; line-height:1.12; color:#fff; margin:0 8px;
  -webkit-text-stroke:7px rgba(11,22,38,.9); paint-order:stroke fill; text-shadow:0 4px 22px rgba(0,0,0,.55); transform-origin:50% 70%; }
"""
captions_html = scene("captions", 0, TOTAL, "\n".join(cap_body), cap_css, "\n".join(cap_js))

# ---------------------------------------------------------------- root: footage, transforms, audio
vids, root_js = [], []
PUNCH = {"hook": 1.0, "s1": 1.0, "s2": 1.0, "s3a": 1.0, "s3b": 1.1, "s4": 1.0, "s5": 1.12, "s6": 1.0, "s7": 1.12,
         "s8": 1.0, "s9": 1.0, "s10": 1.1, "s11": 1.0, "s12": 1.0, "s13": 1.0, "s14": 1.12, "s15": 1.0}
for i, s in enumerate(SEGS):
    sid = s["id"]
    vids.append(f'    <div class="vw" id="w-{sid}" style="z-index:{i + 1}">'
                f'<video id="v-{sid}" class="clip" src="assets/footage.mp4" data-start="{s["start"]}" data-duration="{s["dur"]}" '
                f'data-media-start="{s["src_in"]}" data-track-index="0" data-has-audio="true" data-volume="1.6" '
                f'data-fade-in="0.02" data-fade-out="0.03" data-audio-group="voice" playsinline></video></div>')
    root_js.append(f'    tl.set("#w-{sid}", {{scale:{PUNCH[sid]}, transformOrigin:"{face_origin(sid)}"}}, 0);')

# hook: punch on "rare", whip out to the left
rare = ws("hook", "rare")
root_js += [
    f'    tl.to("#w-hook", {{scale:1.12, duration:.25, ease:"expo.out"}}, {r(rare - .03)});',
    f'    tl.to("#w-hook", {{x:-150, scale:1.3, duration:.16, ease:"power3.in"}}, {r(seg_end("hook") - .16)});',
    f'    tl.fromTo("#w-s1", {{x:150, scale:1.3}}, {{x:0, scale:1, duration:.4, ease:"expo.out"}}, {seg_start("s1")});',
    # corner-lot punch, then push into the house on "Jom"
    f'    tl.to("#w-s2", {{scale:1.1, duration:.25, ease:"expo.out"}}, {r(ws("s2", "corner") - .03)});',
    f'    tl.to("#w-s2", {{scale:1.45, duration:.45, ease:"power3.in"}}, {r(seg_end("s2") - .45)});',
    f'    tl.fromTo("#w-s3a", {{scale:1.35}}, {{scale:1, duration:.55, ease:"expo.out"}}, {seg_start("s3a")});',
    # floor change: vertical whip up
    f'    tl.to("#w-s12", {{y:-150, scale:1.3, duration:.16, ease:"power3.in"}}, {r(seg_end("s12") - .16)});',
    f'    tl.fromTo("#w-s13", {{y:150, scale:1.3}}, {{y:0, scale:1, duration:.4, ease:"expo.out"}}, {seg_start("s13")});',
    f'    tl.to("#w-s15", {{scale:1.1, duration:.25, ease:"expo.out"}}, {r(ws("s15", "premium") - .03)});',
]
# B-roll: the back door opening onto the yard, under "lebih kurang dalam 15 kaki lagi"
b_in = ws("s8", "lebih")
b_dur = r(seg_end("s8") - b_in)
broll = (f'    <div class="vw" id="w-broll" style="z-index:40"><video id="v-broll" class="clip" src="assets/footage.mp4" '
         f'data-start="{b_in}" data-duration="{b_dur}" data-media-start="50.75" data-track-index="1" muted playsinline></video></div>')
root_js.append(f'    tl.fromTo("#w-broll", {{scale:1.15}}, {{scale:1.0, duration:{b_dur}, ease:"none", transformOrigin:"50% 60%"}}, {b_in});')
endcard = (f'    <div class="vw" id="w-end" style="z-index:41"><img id="i-end" class="clip" src="assets/endframe.jpg" '
           f'data-start="{CUT_END}" data-duration="{HOLD}" data-track-index="1" alt=""></div>')
root_js.append(f'    tl.fromTo("#w-end", {{scale:1.0}}, {{scale:1.08, duration:{HOLD}, ease:"power1.out", transformOrigin:"50% 50%"}}, {CUT_END});')

# ---------- sound
def sfx(name, file, at, vol, peak):
    return dict(id=name, file=file, start=r(max(0, at - peak + 1 / FPS)), vol=vol)

PK = {"whoosh": .162, "whoosh-short": .162, "whoosh-hi": .14, "whoosh-low": .193, "whoosh-cinematic": 2.503, "pop": .12,
      "pop-hi": .107, "click-soft": .073, "tick": .064, "ping": .324, "impact-bass-1": .073, "impact-bass-2": 1.986,
      "sparkle": .027, "key-press": .076}
cues = [
    ("pop", ws("hook", "empat"), .45), ("pop-hi", ws("hook", "lima"), .45), ("impact-bass-1", rare, .22),
    ("whoosh", seg_end("hook") - .05, .38),
    ("click-soft", ws("s1", "perumahan"), .6),
    ("pop", t_nb, .45), ("pop-hi", t_bl, .45), ("whoosh-hi", t_cor + .12, .3), ("ping", t_mas, .4),
    ("whoosh-cinematic", seg_start("s3a") + .02, .3),
    ("click-soft", ws("s3a", "auto"), .6), ("tick", ws("s3a", "porch"), .9),
    ("whoosh-short", ws("s3b", "luas"), .22), ("tick", ws("s3b", "luas") + .3, .9), ("tick", ws("s3b", "tinggi") + .3, .9),
    ("click-soft", ws("s4", "ruang"), .6), ("click-soft", ws("s5", "ruang"), .55),
    ("whoosh-hi", ws("s6", "open"), .25), ("click-soft", ws("s8", "ruang"), .6),
    ("whoosh-low", b_in, .3), ("ping", ws("s8", "15"), .38),
    ("click-soft", ws("s9", "bilik"), .6), ("key-press", t4 - .3, .9), ("key-press", t4 - .15, .9), ("key-press", t4, .9),
    ("pop", ws("s10", "built"), .45), ("pop-hi", ws("s10", "tak"), .45), ("sparkle", ws("s11", "bilik"), .12),
    ("whoosh-low", seg_end("s12") - .05, .38), ("whoosh-short", t_sama, .25), ("ping", t_sek, .35),
    ("impact-bass-2", t_prem, .2), ("pop", t_semi, .5), ("click-soft", t_balk, .6),
    ("whoosh", CUT_END - .05, .35), ("impact-bass-1", CUT_END + .22, .2),
]
import subprocess
DUR = {n: float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"assets/sfx/{n}.mp3"],capture_output=True,text=True).stdout) for n in PK}
audios = []
for i, (name, at, vol) in enumerate(cues):
    c = sfx(name, f"assets/sfx/{name}.mp3", at, vol, PK[name])
    dur = r(min(DUR[name], TOTAL - c["start"]))
    audios.append(f'    <audio id="sfx{i:02d}" src="{c["file"]}" data-start="{c["start"]}" data-duration="{dur}" data-track-index="{10 + i}" '
                  f'data-volume="{vol}" data-audio-group="sfx"></audio>')

# music: bed under the voice, opens up in gaps/transitions and at the end
LOW, MID, HIGH = .13, .3, .6
pts = [(0, LOW)]
for tt in (seg_end("hook"), seg_end("s2"), seg_end("s12")):
    pts += [(tt - .35, LOW), (tt, MID), (tt + .45, LOW)]
last_word = SEGS[-1]["words"][-1]["end"]
pts += [(last_word, LOW), (last_word + .4, HIGH), (TOTAL, HIGH)]
lane = {"version": 1, "lanes": [{"target": "volume", "points": [{"t": r(t), "v": v} for t, v in pts]}]}
music = (f'    <audio id="music" src="assets/music/bed.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="2" '
         f'data-volume="1" data-fade-out="1.2" data-audio-group="music" '
         f'data-automation="{html.escape(json.dumps(lane))}"></audio>')
voice_fx = {"version": 1, "nodes": [
    {"type": "highpass", "id": "v1", "label": "Remove rumble", "params": {"frequency": 85}},
    {"type": "peaking", "id": "v2", "label": "Less boomy room", "params": {"frequency": 250, "gain": -2.5, "q": 1}},
    {"type": "peaking", "id": "v3", "label": "Clarity", "params": {"frequency": 3200, "gain": 2.5, "q": 1}},
    {"type": "compressor", "id": "v4", "label": "Even level", "params": {"threshold": -20, "ratio": 3, "attack": 0.005, "release": 0.12}},
    {"type": "gain", "id": "v6", "label": "Makeup gain", "params": {"gain": 6}},
    {"type": "limiter", "id": "v5", "label": "No clipping", "params": {"limit": -1.5}}]}
master_sfx = {"version": 1, "nodes": [{"type": "limiter", "id": "x1", "params": {"limit": -3}}]}
groups_html = (f'    <hf-audio-group id="voice" data-fx-chain="{html.escape(json.dumps(voice_fx))}"></hf-audio-group>\n'
               f'    <hf-audio-group id="sfx" data-fx-chain="{html.escape(json.dumps(master_sfx))}"></hf-audio-group>\n'
               f'    <hf-audio-group id="music"></hf-audio-group>')

hosts = []
for k, s in enumerate(scenes):
    hosts.append(f'    <div id="{s.cid}" data-composition-id="{s.cid}" data-composition-src="compositions/{s.cid}.html" '
                 f'data-start="{s.start}" data-duration="{r(s.end - s.start)}" data-track-index="{6 + k % 2}" '
                 f'data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{100 + k}"></div>')
    open(f"compositions/{s.cid}.html", "w").write(s.html())
open("compositions/captions.html", "w").write(captions_html)
hosts.append(f'    <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" '
             f'data-start="0" data-duration="{TOTAL}" data-track-index="8" data-track-kind="captions" '
             f'data-width="{W}" data-height="{H}" style="z-index:200"></div>')

index = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:{W}px; height:{H}px; overflow:hidden; background:#0B1626; }}
      #root {{ width:100%; height:100%; position:relative; }}
      #bg {{ position:absolute; inset:0; background:#0B1626; }}
      .vw {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; overflow:hidden; }}
      .vw video, .vw img {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; object-fit:cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}" data-motion-blur="on">
      <div id="bg"></div>
{chr(10).join(vids)}
{broll}
{endcard}
{chr(10).join(hosts)}
{music}
{chr(10).join(audios)}
{groups_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(root_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(index)
print("total", TOTAL, "caption groups", len(groups), "sfx", len(cues))
