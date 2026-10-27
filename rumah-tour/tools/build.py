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
HOLD = 2.6                      # end-card hold on a still of the last frame
TOTAL = round(CUT_END + HOLD, 3)
FACES = json.load(open("tools/faces.json"))

# copy the CTA here so it is easy to change
CTA_1, CTA_2, CTA_3 = "CORNER LOT", "MASIH ADA", "DM UNTUK VIEWING"


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
.tag { position:absolute; left:72px; display:flex; align-items:center; gap:20px;
  padding:16px 30px 18px 22px; background:rgba(9,18,30,.66); border:2px solid rgba(255,255,255,.92);
  backdrop-filter:blur(14px); opacity:0; white-space:nowrap; }
.tag::before, .tag::after { content:""; position:absolute; width:16px; height:16px; border:4px solid var(--lime); }
.tag::before { left:-9px; top:-9px; border-right:none; border-bottom:none; }
.tag::after { right:-9px; bottom:-9px; border-left:none; border-top:none; }
.idx { font-family:"Space Mono"; font-weight:700; font-size:30px; color:var(--lime); letter-spacing:.04em; }
.lbl { font-family:"Archivo Black"; font-size:64px; line-height:1; color:#fff; letter-spacing:-.01em; text-transform:uppercase; }
.sub { position:absolute; left:72px; font-family:"Space Mono"; font-weight:700; font-size:32px; color:var(--ink);
  background:var(--lime); padding:8px 16px 9px; letter-spacing:.06em; opacity:0; white-space:nowrap; }
.mono { font-family:"Space Mono"; font-weight:700; letter-spacing:.06em; }
.dim { position:absolute; opacity:0; }
.dim .bar { position:absolute; background:#fff; box-shadow:0 0 12px rgba(0,0,0,.45); }
.dim .cap { position:absolute; background:#fff; }
.dim .pill { position:absolute; font-family:"Space Mono"; font-weight:700; font-size:34px; color:var(--ink);
  background:var(--lime); padding:6px 16px 8px; white-space:nowrap; letter-spacing:.05em; }
"""

ROOT_VARS = ":root{--ink:#0B1626;--lime:#C8FF2E;--glass:rgba(9,18,30,.66);}"


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

    # --- primitives -------------------------------------------------------
    def tag(self, id_, idx, label, t_in, t_out, top=250):
        self.body.append(f'    <div id="{id_}" class="tag" style="top:{top}px"><span class="idx">{idx}</span>'
                         f'<span class="lbl" id="{id_}-l">{label}</span></div>')
        a, b = self.t(t_in), self.t(t_out)
        self.js.append(f'    tl.fromTo("#{id_}", {{opacity:0, clipPath:"inset(0% 100% 0% 0%)"}}, {{opacity:1, clipPath:"inset(0% 0% 0% 0%)", duration:.42, ease:"expo.out"}}, {a});')
        self.js.append(f'    tl.fromTo("#{id_} .idx", {{opacity:0, y:14}}, {{opacity:1, y:0, duration:.3, ease:"power3.out"}}, {r(a + .1)});')
        self.out(id_, b)

    def sub(self, id_, text, t_in, t_out, top):
        self.body.append(f'    <div id="{id_}" class="sub" style="top:{top}px">{text}</div>')
        a = self.t(t_in)
        self.js.append(f'    tl.fromTo("#{id_}", {{opacity:0, x:-24}}, {{opacity:1, x:0, duration:.32, ease:"expo.out"}}, {a});')
        self.out(id_, self.t(t_out))

    def out(self, id_, b, dur=.2):
        self.js.append(f'    tl.to("#{id_}", {{opacity:0, filter:"blur(8px)", duration:{dur}, ease:"power2.in"}}, {r(b - dur)});')
        self.js.append(f'    tl.set("#{id_}", {{visibility:"hidden"}}, {b});')

    def hdim(self, id_, label, t_in, t_out, top, left=90, width=900):
        """Horizontal dimension line with end caps; label pill centred above."""
        self.body.append(
            f'    <div id="{id_}" class="dim" style="left:{left}px;top:{top}px;width:{width}px;height:80px">'
            f'<div class="bar" id="{id_}-bar" style="left:0;top:58px;width:{width}px;height:4px"></div>'
            f'<div class="cap" id="{id_}-c1" style="left:0;top:40px;width:4px;height:40px"></div>'
            f'<div class="cap" id="{id_}-c2" style="left:{width - 4}px;top:40px;width:4px;height:40px"></div>'
            f'<div class="pill" id="{id_}-p" style="left:0;width:{width}px;top:-6px;text-align:center;background:none;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.7)">'
            f'<span style="background:var(--lime);color:var(--ink);padding:6px 16px 8px">{label}</span></div></div>')
        a, b = self.t(t_in), self.t(t_out)
        self.js.append(f'    tl.set("#{id_}", {{opacity:1}}, {a});')
        self.js.append(f'    tl.fromTo("#{id_}-bar", {{scaleX:0}}, {{scaleX:1, duration:.55, ease:"expo.out", transformOrigin:"50% 50%"}}, {a});')
        self.js.append(f'    tl.fromTo(["#{id_}-c1","#{id_}-c2"], {{scaleY:0}}, {{scaleY:1, duration:.25, ease:"power3.out"}}, {r(a + .3)});')
        self.js.append(f'    tl.fromTo("#{id_}-p", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:.3, ease:"expo.out"}}, {r(a + .18)});')
        self.out(id_, b)

    def vdim(self, id_, label, t_in, t_out, left, top, height):
        self.body.append(
            f'    <div id="{id_}" class="dim" style="left:{left}px;top:{top}px;width:90px;height:{height}px">'
            f'<div class="bar" id="{id_}-bar" style="left:18px;top:0;width:4px;height:{height}px"></div>'
            f'<div class="cap" id="{id_}-c1" style="left:0;top:0;width:40px;height:4px"></div>'
            f'<div class="cap" id="{id_}-c2" style="left:0;top:{height - 4}px;width:40px;height:4px"></div>'
            f'<div class="pill" id="{id_}-p" style="left:34px;top:{height // 2 - 26}px">{label}</div></div>')
        a, b = self.t(t_in), self.t(t_out)
        self.js.append(f'    tl.set("#{id_}", {{opacity:1}}, {a});')
        self.js.append(f'    tl.fromTo("#{id_}-bar", {{scaleY:0}}, {{scaleY:1, duration:.6, ease:"expo.out", transformOrigin:"50% 100%"}}, {a});')
        self.js.append(f'    tl.fromTo(["#{id_}-c1","#{id_}-c2"], {{scaleX:0}}, {{scaleX:1, duration:.25, ease:"power3.out"}}, {r(a + .3)});')
        self.js.append(f'    tl.fromTo("#{id_}-p", {{opacity:0, x:-14}}, {{opacity:1, x:0, duration:.3, ease:"expo.out"}}, {r(a + .25)});')
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
.tile .num { font-family:"Archivo Black"; font-size:190px; line-height:.86; color:#fff; display:block; }
.tile .unit { font-family:"Space Mono"; font-weight:700; font-size:34px; color:#fff; letter-spacing:.12em; display:block; margin-top:6px; }
#hk-t2 .num { color:var(--lime); }
.uline { position:absolute; left:26px; right:30px; bottom:8px; height:6px; background:var(--lime); transform-origin:0 50%; }
#hk-stamp { position:absolute; left:560px; top:452px; font-family:"Archivo Black"; font-size:58px; color:var(--ink);
  background:var(--lime); padding:8px 22px 12px; opacity:0; box-shadow:0 10px 30px rgba(0,0,0,.35); white-space:nowrap; }
""")
sc.body.append("""    <div id="hk-row">
      <div class="tile" id="hk-t1"><span class="num">4</span><span class="unit">BILIK</span><div class="uline" id="hk-u1"></div></div>
      <div class="tile" id="hk-t2"><span class="num">5</span><span class="unit">TOILET</span><div class="uline" id="hk-u2"></div></div>
    </div>
    <div id="hk-stamp">PALING RARE</div>""")
e4, l5, rare = ws("hook", "empat"), ws("hook", "lima"), ws("hook", "rare")
sc.js += [
    # frame 0 already shows both tiles (thumbnail); words land as underline + kick
    '    tl.set(["#hk-u1","#hk-u2"], {scaleX:0}, 0);',
    '    tl.fromTo("#hk-t1", {opacity:.0, y:-30}, {opacity:1, y:0, duration:.01}, 0);',
    '    tl.fromTo("#hk-t2", {opacity:.0, y:-30}, {opacity:1, y:0, duration:.01}, 0);',
    f'    tl.to("#hk-u1", {{scaleX:1, duration:.35, ease:"expo.out"}}, {r(e4)});',
    f'    tl.fromTo("#hk-t1 .num", {{scale:1.12}}, {{scale:1, duration:.4, ease:"expo.out", transformOrigin:"0% 100%"}}, {r(e4)});',
    f'    tl.to("#hk-u2", {{scaleX:1, duration:.35, ease:"expo.out"}}, {r(l5)});',
    f'    tl.fromTo("#hk-t2 .num", {{scale:1.12}}, {{scale:1, duration:.4, ease:"expo.out", transformOrigin:"0% 100%"}}, {r(l5)});',
    f'    tl.fromTo("#hk-stamp", {{opacity:0, scale:1.9, rotation:-14}}, {{opacity:1, scale:1, rotation:-6, duration:.28, ease:"power4.out"}}, {r(rare - .05)});',
    # whip exit with the footage
    f'    tl.to(["#hk-row","#hk-stamp"], {{x:-420, opacity:0, duration:.18, ease:"power3.in"}}, {r(sc.end - .18)});',
]
scenes.append(sc)

# ---------------------------------------------------------------- 2. lokasi (s1 + s2)
sc = Scene("lokasi", seg_start("s1"), seg_end("s2"))
sc.css.append("""
#lk-pin { position:absolute; left:72px; top:244px; width:58px; height:80px; opacity:0; }
#lk-head { position:absolute; left:150px; top:236px; opacity:0; }
#lk-head .k { font-family:"Space Mono"; font-weight:700; font-size:30px; color:var(--lime); background:var(--ink); padding:4px 12px 6px; letter-spacing:.12em; display:inline-block; margin-bottom:8px; }
#lk-head .v { font-family:"Archivo Black"; font-size:70px; line-height:1; color:#fff; display:block; text-shadow:0 4px 24px rgba(0,0,0,.5); }
.chip { position:absolute; top:250px; display:flex; align-items:center; gap:14px; padding:14px 26px 16px 18px;
  background:var(--glass); border:2px solid #fff; backdrop-filter:blur(14px); opacity:0; white-space:nowrap; }
.chip .ck { width:40px; height:40px; background:var(--lime); display:flex; align-items:center; justify-content:center; }
.chip .tx { font-family:"Archivo Black"; font-size:54px; color:#fff; line-height:1; }
#lk-corner { position:absolute; left:72px; top:236px; opacity:0; }
#lk-corner .big { position:relative; font-family:"Archivo Black"; font-size:118px; line-height:.95; color:var(--ink); padding:0 4px 10px; display:inline-block; white-space:nowrap; isolation:isolate; }
#lk-hl { position:absolute; left:-18px; right:-22px; top:2%; height:100%; background:var(--lime); z-index:-1; transform-origin:0 50%; }
#lk-avail { display:inline-block; margin-top:14px; font-family:"Space Mono"; font-weight:700; font-size:36px; letter-spacing:.1em;
  color:#fff; background:var(--glass); border:2px solid #fff; padding:8px 18px 10px; opacity:0; }
#lk-avail i { display:inline-block; width:16px; height:16px; border-radius:50%; background:var(--lime); margin-right:14px; font-style:normal; }
#lk-jom { position:absolute; right:150px; top:262px; font-family:"Archivo Black"; font-size:60px; color:var(--ink); background:var(--lime);
  padding:10px 26px 14px; opacity:0; white-space:nowrap; }
""")
CHECK = '<svg width="26" height="26" viewBox="0 0 26 26"><path d="M3 13.5l6.5 6.5L23 6" stroke="#0B1626" stroke-width="4.5" fill="none" stroke-linecap="square"/></svg>'
sc.body.append(f"""    <svg id="lk-pin" viewBox="0 0 58 80"><path d="M29 2C14 2 3 13 3 27c0 19 26 50 26 50s26-31 26-50C55 13 44 2 29 2z" fill="#C8FF2E" stroke="#0B1626" stroke-width="3"/><circle cx="29" cy="27" r="9" fill="#0B1626"/></svg>
    <div id="lk-head"><span class="k" id="lk-k">PERUMAHAN BARU</span><span class="v" id="lk-v">SEBELAH SEKOLAH</span></div>
    <div class="chip" id="lk-c1" style="left:72px"><span class="ck">{CHECK}</span><span class="tx">NON-BUMI</span></div>
    <div class="chip" id="lk-c2" style="left:500px"><span class="ck">{CHECK}</span><span class="tx">BUMI</span></div>
    <div id="lk-corner"><span class="big"><span id="lk-hl"></span>CORNER LOT</span><br><span id="lk-avail"><i></i>MASIH AVAILABLE</span></div>
    <div id="lk-jom">JOM MASUK &#8594;</div>""")
t_peru, t_sek = ws("s1", "perumahan"), ws("s1", "sekolah")
t_nb, t_bl, t_cor, t_mas = ws("s2", "non-bumi"), ws("s2", "bumi"), ws("s2", "corner"), ws("s2", "masih")
t_jom = ws("s2", "jom")
sc.js += [
    f'    tl.fromTo("#lk-pin", {{opacity:0, y:-60}}, {{opacity:1, y:0, duration:.5, ease:"back.out(1.6)"}}, {sc.t(t_peru - .1)});',
    f'    tl.fromTo("#lk-head", {{opacity:0, filter:"blur(8px)"}}, {{opacity:1, filter:"blur(0px)", duration:.2, ease:"power2.out"}}, {sc.t(t_peru)});',
    f'    tl.fromTo("#lk-v", {{opacity:0, x:-20}}, {{opacity:1, x:0, duration:.35, ease:"expo.out"}}, {sc.t(t_sek)});',
    f'    tl.set("#lk-v", {{opacity:0}}, 0);',
]
sc.out("lk-pin", sc.t(t_nb - .05)); sc.out("lk-head", sc.t(t_nb - .05))
sc.js += [
    f'    tl.fromTo("#lk-c1", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", transformOrigin:"0% 50%"}}, {sc.t(t_nb)});',
    f'    tl.fromTo("#lk-c2", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", transformOrigin:"0% 50%"}}, {sc.t(t_bl)});',
]
sc.out("lk-c1", sc.t(t_cor - .02)); sc.out("lk-c2", sc.t(t_cor - .02))
sc.js += [
    f'    tl.set("#lk-hl", {{scaleX:0}}, 0);',
    f'    tl.fromTo("#lk-corner", {{opacity:0, filter:"blur(10px)"}}, {{opacity:1, filter:"blur(0px)", duration:.18, ease:"power2.out"}}, {sc.t(t_cor)});',
    f'    tl.to("#lk-hl", {{scaleX:1, duration:.4, ease:"power3.inOut"}}, {sc.t(t_cor + .12)});',
    f'    tl.fromTo("#lk-avail", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:.35, ease:"expo.out"}}, {sc.t(t_mas)});',
]
sc.out("lk-corner", sc.t(t_jom - .1))
sc.js += [f'    tl.fromTo("#lk-jom", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:.3, ease:"expo.out"}}, {sc.t(t_jom)});',
          f'    tl.to("#lk-jom", {{scale:2.4, opacity:0, duration:.35, ease:"power3.in", transformOrigin:"50% 50%"}}, {r(sc.end - sc.start - .35)});']
scenes.append(sc)

# ---------------------------------------------------------------- 3. luar (s3a + s3b)
sc = Scene("luar", seg_start("s3a"), seg_end("s3b"))
sc.tag("lr-gate", "01", "AUTO GATE", ws("s3a", "auto"), ws("s3a", "porch"))
sc.tag("lr-porch", "02", "PORCH", ws("s3a", "porch"), seg_end("s3b"))
sc.hdim("lr-luas", "LUAS", ws("s3b", "luas"), seg_end("s3b"), top=400, left=120, width=840)
sc.vdim("lr-tinggi", "TINGGI", ws("s3b", "tinggi"), seg_end("s3b"), left=40, top=540, height=560)
scenes.append(sc)

# ---------------------------------------------------------------- 4. dalam (s4..s8)
sc = Scene("dalam", seg_start("s4"), seg_end("s8"))
sc.tag("dl-tamu", "03", "RUANG TAMU", ws("s4", "ruang"), seg_end("s4"))
sc.sub("dl-luas", "PALING LUAS", ws("s4", "paling"), seg_end("s4"), top=372)
sc.tag("dl-stor", "04", "STOR", ws("s5", "ruang"), seg_end("s5"))
sc.tag("dl-kit", "05", 'OPEN <span id="dl-kit-k" style="color:var(--lime)">KITCHEN</span>', ws("s6", "open"), seg_end("s7"))
sc.js.append(f'    tl.fromTo("#dl-kit-k", {{color:"#FFFFFF"}}, {{color:"#C8FF2E", duration:.15}}, {sc.t(ws("s7", "kitchen"))});')
sc.tag("dl-bel", "06", "RUANG BELAKANG", ws("s8", "ruang"), seg_end("s8"))
sc.hdim("dl-15", "&#177; 15 KAKI", ws("s8", "15") - .15, seg_end("s8"), top=410, left=90, width=900)
scenes.append(sc)

# ---------------------------------------------------------------- 5. bilik (s9..s11)
sc = Scene("bilik", seg_start("s9"), seg_end("s11"))
sc.css.append("""
#bk-num { display:inline-block; position:relative; height:64px; overflow:hidden; vertical-align:top; width:84px; }
#bk-reel { position:absolute; left:0; top:0; display:flex; flex-direction:column; }
#bk-reel span { height:64px; line-height:64px; color:var(--lime); }
""")
sc.tag("bk-tag", "07", 'BILIK <span id="bk-num" data-layout-allow-overflow><span id="bk-reel"><span>01</span><span>02</span><span>03</span><span>04</span></span></span>',
       ws("s9", "bilik"), seg_end("s10") - .02)
t4 = ws("s9", "empat")
sc.js.append(f'    tl.fromTo("#bk-reel", {{y:0}}, {{y:-192, duration:.45, ease:"steps(3)"}}, {sc.t(t4 - .3)});')
sc.sub("bk-wc", "+ TOILET SENDIRI", ws("s10", "built"), seg_end("s10") - .02, top=372)
sc.sub("bk-share", "&#10003; TAK SHARING", ws("s10", "tak"), seg_end("s10") - .02, top=432)
sc.tag("bk-tamu", "&#9733;", "BILIK TETAMU", ws("s11", "bilik"), seg_end("s11"))
scenes.append(sc)

# ---------------------------------------------------------------- 6. atas (s12..s14)
sc = Scene("atas", seg_start("s12"), seg_end("s14"))
sc.css.append("""
#at-up { position:absolute; left:72px; top:236px; opacity:0; display:flex; align-items:center; gap:22px; }
#at-up .lbl { font-size:86px; text-shadow:0 6px 28px rgba(0,0,0,.45); }
#at-arrow { width:70px; height:86px; background:var(--lime); clip-path:polygon(50% 0,100% 45%,68% 45%,68% 100%,32% 100%,32% 45%,0 45%); }
#at-level { position:absolute; left:0; top:470px; width:1080px; height:5px; background:var(--lime);
  box-shadow:0 0 18px rgba(200,255,46,.9), 0 0 4px #fff; opacity:0; transform-origin:0 50%; }
#at-lvl-lbl { position:absolute; left:72px; top:392px; opacity:0; }
#at-lvl-lbl .k { font-family:"Space Mono"; font-weight:700; font-size:32px; color:var(--ink); background:var(--lime); padding:6px 16px 8px; letter-spacing:.06em; }
#at-lvl-tag { position:absolute; left:72px; top:250px; opacity:0; font-family:"Archivo Black"; font-size:66px; line-height:1; color:#fff;
  text-shadow:0 4px 24px rgba(0,0,0,.6); white-space:nowrap; }
""")
sc.body.append("""    <div id="at-up"><div id="at-arrow"></div><span class="lbl">TINGKAT ATAS</span></div>
    <div id="at-lvl-tag">SAMA TINGGI SEKOLAH</div>
    <div id="at-level" data-layout-allow-overflow></div>
    <div id="at-lvl-lbl"><span class="k">ARAS = BUMBUNG SEKOLAH</span></div>""")
t_ting = ws("s12", "tingkat")
sc.js += [
    f'    tl.fromTo("#at-up", {{opacity:0, y:50}}, {{opacity:1, y:0, duration:.4, ease:"expo.out"}}, {sc.t(t_ting)});',
    f'    tl.fromTo("#at-arrow", {{y:30}}, {{y:0, duration:.5, ease:"back.out(2)"}}, {sc.t(t_ting)});',
    f'    tl.to("#at-up", {{y:-260, opacity:0, duration:.22, ease:"power3.in"}}, {sc.t(seg_end("s12") - .22)});',
]
t_sama, t_sek = ws("s13", "sama"), ws("s13", "sekolah")
sc.js += [
    f'    tl.fromTo("#at-level", {{opacity:1, scaleX:0}}, {{opacity:1, scaleX:1, duration:.8, ease:"power2.inOut"}}, {sc.t(t_sama - .1)});',
    f'    tl.fromTo("#at-lvl-tag", {{opacity:0, filter:"blur(8px)"}}, {{opacity:1, filter:"blur(0px)", duration:.2, ease:"power2.out"}}, {sc.t(t_sama)});',
    f'    tl.fromTo("#at-lvl-lbl", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:.3, ease:"expo.out"}}, {sc.t(t_sek)});',
]
for i in ("at-level", "at-lvl-tag", "at-lvl-lbl"):
    sc.out(i, sc.t(seg_end("s14")))
scenes.append(sc)

# ---------------------------------------------------------------- 7. akhir (s15 + end card)
sc = Scene("akhir", seg_start("s15"), TOTAL)
sc.css.append("""
#ak-prem { position:absolute; left:72px; top:236px; opacity:0; white-space:nowrap; }
#ak-semi { font-family:"Archivo Black"; font-size:92px; color:var(--lime); display:inline-block; opacity:0; text-shadow:0 6px 28px rgba(0,0,0,.45); }
#ak-pword { font-family:"Archivo Black"; font-size:92px; color:#fff; display:inline-block; text-shadow:0 6px 28px rgba(0,0,0,.45); }
#ak-cta { position:absolute; left:90px; right:90px; top:640px; text-align:center; opacity:0; }
#ak-cta .a { font-family:"Archivo Black"; font-size:128px; line-height:.95; color:#fff; display:block; text-shadow:0 8px 36px rgba(0,0,0,.55); }
#ak-cta .b { font-family:"Archivo Black"; font-size:128px; line-height:.95; color:var(--ink); background:var(--lime); display:inline-block; padding:6px 26px 16px; margin-top:12px; }
#ak-cta .c { font-family:"Space Mono"; font-weight:700; font-size:40px; color:#fff; letter-spacing:.12em; display:block; margin-top:34px; text-shadow:0 2px 14px rgba(0,0,0,.8); }
#ak-scrim { position:absolute; inset:0; background:radial-gradient(ellipse at 50% 45%, rgba(9,18,30,.55), rgba(9,18,30,.15) 70%); opacity:0; }
""")
sc.body.append(f"""    <div id="ak-scrim"></div>
    <div id="ak-prem"><span id="ak-semi">SEMI-</span><span id="ak-pword">PREMIUM</span></div>
    <div id="ak-cta"><span class="a" id="ak-a">{CTA_1}</span><span class="b" id="ak-b">{CTA_2}</span><span class="c" id="ak-c">{CTA_3} &#8594;</span></div>""")
t_prem, t_semi, t_balk = ws("s15", "premium"), ws("s15", "semi"), ws("s15", "balkoni")
sc.js += [
    '    tl.set("#ak-semi", {width:0}, 0);',
    f'    tl.fromTo("#ak-prem", {{opacity:0, scale:1.5}}, {{opacity:1, scale:1, duration:.3, ease:"power4.out", transformOrigin:"0% 50%"}}, {sc.t(t_prem - .03)});',
    f'    tl.to("#ak-semi", {{width:296, opacity:1, duration:.35, ease:"expo.out"}}, {sc.t(t_semi)});',
]
sc.out("ak-prem", sc.t(t_balk - .02))
sc.tag("ak-balk", "08", "BALKONI", t_balk, CUT_END - .05)
cta = sc.t(CUT_END)
sc.js += [
    f'    tl.fromTo("#ak-scrim", {{opacity:0}}, {{opacity:1, duration:.4, ease:"power2.inOut"}}, {r(cta - .1)});',
    f'    tl.set("#ak-cta", {{opacity:1}}, {cta});',
    f'    tl.fromTo("#ak-a", {{opacity:0, y:40, filter:"blur(10px)"}}, {{opacity:1, y:0, filter:"blur(0px)", duration:.4, ease:"expo.out"}}, {cta});',
    f'    tl.fromTo("#ak-b", {{opacity:0, scale:1.6, rotation:-4}}, {{opacity:1, scale:1, rotation:-2, duration:.3, ease:"power4.out"}}, {r(cta + .22)});',
    f'    tl.fromTo("#ak-c", {{opacity:0}}, {{opacity:1, duration:.3, ease:"power2.out"}}, {r(cta + .35)});',
]
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
