"""Build the Taman Keriang Permai "Kinetic Type" edit (index.html + compositions/*.html).

Every word is timed from the source transcript through tools_cut.cut_time(), so changing
the cut list in tools_cut.py keeps the type in sync.  Run:  python3 build.py
"""
import json, os, re
from tools_cut import cut_time as C, TOTAL, TAIL

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
TOTAL = round(TOTAL, 2)

INK, PAPER, LIME = "#0D0D0E", "#F6F4EE", "#D2FF3C"

FONT = """
    @font-face { font-family: 'Archivo'; src: url('assets/fonts/Archivo.woff2') format('woff2');
                 font-weight: 100 900; font-stretch: 62% 125%; }
"""

CSS = f"""
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .k {{ position: absolute; font-family: 'Archivo', sans-serif; font-weight: 900; text-transform: uppercase;
          line-height: 0.84; white-space: nowrap; letter-spacing: -0.01em; color: {INK};
          font-variation-settings: 'wdth' 100, 'wght' 900; }}
    .ln {{ display: inline-block; overflow: hidden; vertical-align: top; padding: 0.04em 0 0.02em; }}
    .c {{ display: inline-block; }}
    .tape {{ background: {INK}; color: {PAPER}; padding: 0.07em 0.14em 0.03em; }}
    .lime {{ background: {LIME}; color: {INK}; padding: 0.07em 0.14em 0.03em; }}
    .bare {{ color: {INK}; text-shadow: 0 0 18px rgba(246,244,238,0.55); }}
    .line {{ color: {PAPER}; -webkit-text-stroke: 5px {INK}; }}
    .bar {{ position: absolute; }}
"""


def chars(text):
    out = []
    for ch in text:
        out.append('<span class="c">&nbsp;</span>' if ch == " " else f'<span class="c">{ {"&": "&amp;"}.get(ch, ch)}</span>')
    return "".join(out)


def word(i, text, x, y, size, kind="bare", wdth=100, extra=""):
    return (f'    <div id="{i}" class="k {kind}" style="left:{x}px; top:{y}px; font-size:{size}px; '
            f"font-variation-settings: 'wdth' {wdth}, 'wght' 900; {extra}\"><span class=\"ln\">{chars(text)}</span></div>")


# ---- motion vocabulary (t = seconds inside the scene) ----
def rise(i, t, stagger=0.022):
    return (f'    tl.fromTo("#{i}", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.22, ease: "expo.out" }}, {t:.3f});\n'
            f'    tl.fromTo("#{i} .c", {{ yPercent: 118 }}, {{ yPercent: 0, duration: 0.34, ease: "expo.out", stagger: {stagger} }}, {t:.3f});')


def slam(i, t, origin="0% 50%"):
    return (f'    tl.fromTo("#{i}", {{ scale: 2.5, opacity: 0, filter: "blur(14px)", transformOrigin: "{origin}" }}, '
            f'{{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.26, ease: "expo.out" }}, {t:.3f});')


def stretch(i, t, a=62, b=100, dur=0.55):
    return (f'    tl.fromTo("#{i}", {{ fontVariationSettings: "\'wdth\' {a}, \'wght\' 900" }}, '
            f'{{ fontVariationSettings: "\'wdth\' {b}, \'wght\' 900", duration: {dur}, ease: "expo.out" }}, {t:.3f});\n'
            f'    tl.to("#{i}", {{ opacity: 1, duration: 0.04 }}, {t:.3f});')


def pop(i, t):
    return f'    tl.fromTo("#{i}", {{ scale: 0, rotation: -8, opacity: 0 }}, {{ scale: 1, rotation: 0, opacity: 1, duration: 0.36, ease: "back.out(2.2)" }}, {t:.3f});'


def flip_in(i, t):
    return f'    tl.fromTo("#{i}", {{ rotationX: -95, opacity: 0, transformOrigin: "50% 50% -40px" }}, {{ rotationX: 0, opacity: 1, duration: 0.32, ease: "back.out(1.6)" }}, {t:.3f});'


def flip_out(i, t):
    return f'    tl.to("#{i}", {{ rotationX: 95, opacity: 0, transformOrigin: "50% 50% -40px", duration: 0.18, ease: "power2.in" }}, {t:.3f});'


def out_left(ids, t):
    sel = ", ".join(f"#{i}" for i in ids)
    return f'    tl.to("{sel}", {{ x: -1300, duration: 0.26, ease: "power3.in", stagger: 0.025 }}, {t:.3f});'


def out_up(ids, t):
    sel = ", ".join(f"#{i}" for i in ids)
    return f'    tl.to("{sel}", {{ yPercent: -60, opacity: 0, duration: 0.2, ease: "power3.in", stagger: 0.02 }}, {t:.3f});'


def out_squash(ids, t):
    sel = ", ".join(f"#{i}" for i in ids)
    return f'    tl.to("{sel}", {{ scaleY: 0, transformOrigin: "50% 0%", duration: 0.18, ease: "power3.in", stagger: 0.02 }}, {t:.3f});'


def scene(sid, dur, body, js):
    return f"""<template>
  <style>{FONT}{CSS}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-layout-allow-overlap data-layout-allow-overflow>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


SCENES = []


HIDDEN = {"h3", "u4", "s3", "r1b", "r3b", "o3", "c4", "tn1", "tn2", "tn3", "tn4", "u5", "l4", "l5"}


def add(sid, start, end, items, moves):
    """moves: list of callables f(rel) -> js, where rel(t_cut) = t_cut - start."""
    rel = lambda t: max(0.0, t - start)
    body = "\n".join(items)
    for i in HIDDEN:
        body = re.sub(rf'(<div id="{i}" class="[^"]*" style=")', r'\1opacity:0; ', body)
    SCENES.append((sid, start, end - start, body, "\n".join(m(rel) for m in moves)))


VOICE_END = round(TOTAL - (TAIL[1] - TAIL[0]), 3)
X = 84  # left margin (TikTok/IG safe), text stays left of the right rail (x < 950)

# 1. HOOK  "Rumah ni akan bebas banjir, jangan risau"
add("hook", 0.0, 2.72, [
    word("h1", "rumah ni akan", X, 330, 84),
    word("h2", "bebas", X, 432, 220, "lime"),
    word("h3", "banjir", X, 640, 196, "tape", wdth=104),
    word("h4", "jangan risau", X, 862, 74),
], [
    lambda r: rise("h1", 0.0, 0.04),
    lambda r: slam("h2", r(C(43.72))),
    lambda r: stretch("h3", r(C(44.64)), 62, 104),
    lambda r: rise("h4", r(C(44.96)), 0.03),
    lambda r: out_left(["h4", "h3", "h2", "h1"], 2.52),
])

# 2. INTRO + SIAP  "Ok, progres terkini Taman Keriang Permai Changlun, siap ..."
add("intro", 2.72, 7.21, [
    word("i1", "progres terkini", X, 330, 56, "tape"),
    word("i2", "taman", X, 420, 156),
    word("i3", "keriang", X, 556, 156),
    word("i4", "permai", X, 692, 156),
    word("i5", "changlun, kedah", X, 860, 70, "lime"),
    word("i6", "siap", X, 470, 300, "line"),
    '    <div id="i7" class="bar" style="left:84px; top:760px; width:640px; height:26px; background:' + LIME + ';"></div>',
], [
    lambda r: rise("i1", r(C(0.38))),
    lambda r: slam("i2", r(C(1.00))),
    lambda r: slam("i3", r(C(1.30))),
    lambda r: slam("i4", r(C(1.74))),
    lambda r: rise("i5", r(C(2.08)), 0.02),
    lambda r: out_left(["i1", "i2", "i3", "i4", "i5"], r(C(2.92)) - 0.32),
    lambda r: slam("i6", r(C(2.94))),
    lambda r: f'    tl.to("#i6", {{ color: "{INK}", duration: 0.08 }}, {r(C(3.42)):.3f});',
    lambda r: f'    tl.fromTo("#i7", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.5, ease: "expo.out" }}, {r(C(3.42)):.3f});',
    lambda r: out_squash(["i6", "i7"], 4.30),
])

# 3. HAMPIR SIAP 80%
add("progress", 7.21, 10.07, [
    word("p1", "dan rumah pun dah", X, 330, 62),
    word("p2", "hampir siap", X, 420, 112, "tape"),
    word("p3", "lebih kurang", X, 576, 50),
    word("p4", "<span id='p4n'>0</span>%", X, 640, 330, "lime", wdth=92),
    '    <div id="p5" class="bar" style="left:84px; top:1010px; width:860px; height:30px; border:5px solid ' + INK + ';"></div>',
    '    <div id="p6" class="bar" style="left:84px; top:1010px; width:688px; height:30px; background:' + INK + ';"></div>',
], [
    lambda r: f'    tl.fromTo("#p1 .c", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, stagger: 0.042 }}, {r(C(5.28)):.3f});',
    lambda r: rise("p2", r(C(7.05))),
    lambda r: rise("p3", r(C(7.64)), 0.015),
    lambda r: slam("p4", r(C(7.90))),
    lambda r: f'    const n80 = {{ v: 0 }};\n    tl.fromTo(n80, {{ v: 0 }}, {{ v: 80, duration: 0.6, ease: "power2.out", onUpdate: () => {{ document.querySelector("#p4n").textContent = Math.round(n80.v); }} }}, {r(C(7.90)):.3f});',
    lambda r: f'    tl.fromTo("#p5", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {r(C(7.90)):.3f});',
    lambda r: f'    tl.fromTo("#p6", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.6, ease: "power2.out" }}, {r(C(7.90)):.3f});',
    lambda r: out_left(["p1", "p2", "p3", "p4", "p5", "p6"], 2.62),
])
# fix the counter markup: chars() would split the span, so build it by hand
SCENES[-1] = (SCENES[-1][0], SCENES[-1][1], SCENES[-1][2],
              SCENES[-1][3].replace(word("p4", "<span id='p4n'>0</span>%", X, 640, 330, "lime", wdth=92),
                                    f'    <div id="p4" class="k lime" style="left:{X}px; top:640px; font-size:330px; font-variation-settings: \'wdth\' 92, \'wght\' 900;"><span class="ln"><span id="p4n" class="c">0</span><span class="c">%</span></span></div>'),
              SCENES[-1][4])

# 4. UNIT TAK BANYAK / HAMPIR SEPARUH DAH
add("units", 10.07, 12.66, [
    word("u1", "unit", X, 330, 84),
    word("u2", "tak banyak", X, 426, 124, "tape"),
    word("u3", "hampir", X, 420, 120),
    word("u4", "separuh", X, 550, 172, "lime"),
    word("u5", "dah!", X, 766, 116, "tape"),
], [
    lambda r: rise("u1", r(C(9.32))),
    lambda r: slam("u2", r(C(9.60))),
    lambda r: out_up(["u1", "u2"], r(C(10.40)) - 0.2),
    lambda r: rise("u3", r(C(10.40))),
    lambda r: stretch("u4", r(C(10.60)), 62, 100),
    lambda r: pop("u5", r(C(11.10))),
    lambda r: out_left(["u3", "u4", "u5"], 2.42),
])

# 5. SPEK  "Rumah medium cost, 3 bilik, 2 tandas"
add("spek", 12.66, 16.03, [
    word("s1", "rumah", X, 330, 72),
    word("s2", "medium", X, 418, 160, "tape"),
    word("s3", "cost", X, 584, 160, "lime"),
    word("s4", "3", X, 360, 380),
    word("s5", "bilik", 330, 470, 110, "tape"),
    word("s6", "2", X, 720, 380),
    word("s7", "tandas", 330, 830, 110, "lime"),
], [
    lambda r: rise("s1", r(C(15.20))),
    lambda r: slam("s2", r(C(15.46))),
    lambda r: stretch("s3", r(C(15.92)), 62, 100),
    lambda r: out_left(["s1", "s2", "s3"], r(C(16.38)) - 0.3),
    lambda r: slam("s4", r(C(16.38)), "50% 50%"),
    lambda r: rise("s5", r(C(16.86))),
    lambda r: slam("s6", r(C(17.56)), "50% 50%"),
    lambda r: rise("s7", r(C(17.84))),
    lambda r: out_left(["s4", "s5", "s6", "s7"], 3.12),
])

# 6. END LOT / CORNER LOT ADA LAGI
add("lots", C(19.96), C(36.30), [
    word("l1", "unit", X, 330, 84),
    word("l2", "end lot", X, 426, 176, "tape"),
    word("l4", "corner lot", X, 426, 176, "tape", wdth=72),
    word("l3", "ada lagi", X, 632, 96, "lime"),
    word("l5", "pun ada lagi", X, 632, 96, "lime"),
], [
    lambda r: rise("l1", r(C(20.02))),
    lambda r: slam("l2", r(C(20.14))),
    lambda r: rise("l3", r(C(20.34))),
    lambda r: flip_out("l2", r(C(21.02)) - 0.16),
    lambda r: flip_in("l4", r(C(21.02))),
    lambda r: flip_out("l3", r(C(21.56)) - 0.16),
    lambda r: flip_in("l5", r(C(21.56))),
    lambda r: out_left(["l1", "l4", "l5"], 2.12),
])

# 6b. TANAH BELAKANG  "Ada lagi unit, ada tanah [belakang]" -- kept small, in the sky, so the houses read first
add("tanah", C(36.30), C(23.14), [
    word("g1", "unit ada tanah belakang", X, 300, 46, "tape"),
    word("g2", "masih available", X, 362, 46, "lime"),
], [
    lambda r: rise("g1", r(C(36.32)), 0.012),
    lambda r: rise("g2", r(C(37.30)), 0.015),
    lambda r: out_up(["g1", "g2"], r(C(38.76)) - 0.2),
])

# 7. TOUR  master bedroom / bilik kedua / bilik ketiga / ruang makan & dapur
add("tour", C(23.14), C(39.24), [
    word("t0", "tour rumah", X, 300, 44, "tape"),
    word("tn1", "01", 420, 300, 44, "lime"),
    word("tn2", "02", 420, 300, 44, "lime"),
    word("tn3", "03", 420, 300, 44, "lime"),
    word("tn4", "04", 420, 300, 44, "lime"),
    word("r1a", "master", X, 380, 150),
    word("r1b", "bedroom", X, 516, 150, "tape"),
    word("r2a", "bilik", X, 380, 150),
    word("r2b", "kedua", X, 516, 150, "lime"),
    word("r3a", "bilik", X, 380, 150),
    word("r3b", "ketiga", X, 516, 150, "tape"),
    word("r4a", "ruang", X, 380, 150),
    word("r4b", "makan", X, 516, 150, "lime"),
    word("r5", "& dapur", X, 700, 104, "tape"),
], [
    lambda r: rise("t0", 0.02),
    lambda r: pop("tn1", 0.12),
    lambda r: slam("r1a", r(C(23.44))),
    lambda r: stretch("r1b", r(C(23.88)), 62, 100, 0.35),
    lambda r: out_up(["r1a", "r1b", "tn1"], r(C(24.96)) - 0.22),
    lambda r: pop("tn2", r(C(24.96))),
    lambda r: slam("r2a", r(C(24.96))),
    lambda r: rise("r2b", r(C(25.74))),
    lambda r: out_up(["r2a", "r2b", "tn2"], r(C(27.68)) - 0.22),
    lambda r: pop("tn3", r(C(27.68))),
    lambda r: slam("r3a", r(C(27.68))),
    lambda r: stretch("r3b", r(C(28.36)), 62, 100, 0.45),
    lambda r: out_up(["r3a", "r3b", "tn3"], r(C(29.80)) - 0.22),
    lambda r: pop("tn4", r(C(29.80))),
    lambda r: slam("r4a", r(C(29.80))),
    lambda r: rise("r4b", r(C(30.04))),
    lambda r: slam("r5", r(C(31.08))),
    lambda r: out_left(["t0", "tn4", "r4a", "r4b", "r5"], 5.78),
])

# 8. CHANGLUN  "Yang memang minat nak cari rumah kat Changlun, Taman Keriang Permai"
add("outro", C(39.24), C(13.44), [
    word("o1", "yang memang minat", X, 330, 58),
    word("o2", "nak cari rumah kat", X, 396, 58),
    word("o3", "changlun?", X, 480, 160, "lime", wdth=84),
    word("o4", "taman keriang permai", X, 680, 66, "tape"),
], [
    lambda r: f'    tl.fromTo("#o1 .c", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, stagger: 0.026 }}, {r(C(39.28)):.3f});',
    lambda r: f'    tl.fromTo("#o2 .c", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, stagger: 0.03 }}, {r(C(39.74)):.3f});',
    lambda r: stretch("o3", r(C(40.34)), 62, 84),
    lambda r: rise("o4", r(C(40.66)), 0.018),
    lambda r: out_left(["o1", "o2", "o3", "o4"], 2.38),
])

# 9. CTA  "Macam biasa, tekan link dekat bio ni"  ->  KLIK LINK DI BIO
add("cta", C(13.44), TOTAL, [
    word("c1", "macam biasa", X, 330, 62),
    word("c2", "klik", X, 410, 210),
    word("c3", "link", X, 610, 210, "tape"),
    word("c4", "di bio", X, 830, 210, "lime"),
    word("c5", "@nazpropertyy", X, 1070, 54, "tape"),
], [
    lambda r: f'    tl.fromTo("#c1 .c", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01, stagger: 0.03 }}, {r(C(13.46)):.3f});',
    lambda r: slam("c2", r(C(13.92))),
    lambda r: slam("c3", r(C(14.16))),
    lambda r: stretch("c4", r(C(14.56)), 62, 100),
    lambda r: rise("c5", r(C(14.56)) + 0.45),
    lambda r: f'    tl.to("#c4", {{ scale: 1.06, transformOrigin: "0% 50%", duration: 0.16, ease: "power2.out", yoyo: true, repeat: 3 }}, {r(C(14.56)) + 0.9:.3f});',
])

# Type-wall transitions over the big cuts: a full-frame panel with one giant stretching word
WALLS = [
    (2.72, "progres", INK, LIME),
    (12.66, "spek", LIME, INK),
    (C(23.14), "jom masuk", INK, LIME),
    (C(39.24), "changlun", LIME, INK),
]

# punch-in settle on the smaller jump cuts
PUNCH = [C(s) for s in (43.66, 2.89, 5.26, 7.03, 9.29, 19.96, 37.18, 24.54, 27.64, 29.58, 31.04, 13.44)] + [VOICE_END]

# sound effects: (time the hit lands, file, volume)
SFX = [
    (0.05, "whoosh-short", 0.25),
    (C(43.72), "pop", 0.40), (C(44.64), "whoosh-short", 0.32),
    (2.72, "whoosh", 0.42),
    (C(1.00), "click", 0.40), (C(1.30), "click", 0.40), (C(1.74), "click", 0.40), (C(2.08), "pop", 0.30),
    (C(2.94), "pop", 0.42), (C(3.42), "ping", 0.22),
    (C(7.05), "whoosh-short", 0.28), (C(7.90), "click-soft", 0.40), (C(7.90) + 0.2, "click-soft", 0.35), (C(7.90) + 0.4, "click-soft", 0.35),
    (C(7.90) + 0.62, "ping", 0.25),
    (C(9.60), "pop", 0.38), (C(10.60), "whoosh-short", 0.30), (C(11.10), "pop", 0.42),
    (12.66, "whoosh", 0.42),
    (C(15.46), "click", 0.38), (C(15.92), "whoosh-short", 0.28), (C(16.38), "pop", 0.38), (C(17.56), "pop", 0.38),
    (C(20.14), "pop", 0.38), (C(21.02), "whoosh-short", 0.30), (C(21.56), "click-soft", 0.35),
    (C(23.14), "whoosh", 0.42),
    (C(36.32), "click-soft", 0.30), (C(37.30), "click-soft", 0.30),
    (C(23.88), "click", 0.36), (C(24.96), "click", 0.36), (C(27.68), "click", 0.36), (C(29.80), "click", 0.36), (C(31.08), "pop", 0.32),
    (C(39.24), "whoosh", 0.42),
    (C(40.34), "whoosh-short", 0.30),
    (C(13.92), "click", 0.46), (C(14.16), "click", 0.46), (C(14.56), "pop", 0.46), (C(14.56) + 0.9, "sparkle", 0.25),
]


def walls_scene():
    body, js = [], []
    for i, (t, txt, bg, fg) in enumerate(WALLS):
        body.append(f'    <div id="wl{i}" class="bar" style="left:0; top:0; width:{W}px; height:{H}px; background:{bg}; clip-path: inset(100% 0 0 0);">')
        body.append(f'      <div id="ww{i}" class="k" style="left:0; top:{H // 2 - 130}px; width:{W}px; text-align:center; font-size:{int(min(260, 940 / (len(txt) * 0.74)))}px; color:{fg};">{txt}</div>')
        body.append('    </div>')
        js.append(f'    tl.fromTo("#wl{i}", {{ clipPath: "inset(100% 0 0 0)" }}, {{ clipPath: "inset(0% 0 0 0)", duration: 0.16, ease: "power3.in", immediateRender: false }}, {t - 0.17:.3f});')
        js.append(f'    tl.fromTo("#ww{i}", {{ fontVariationSettings: "\'wdth\' 62, \'wght\' 900", scale: 0.86 }}, {{ fontVariationSettings: "\'wdth\' 112, \'wght\' 900", scale: 1.04, duration: 0.42, ease: "power2.out", immediateRender: false }}, {t - 0.14:.3f});')
        js.append(f'    tl.to("#wl{i}", {{ clipPath: "inset(0% 0 100% 0)", duration: 0.2, ease: "power3.out" }}, {t + 0.06:.3f});')
    return scene("walls", TOTAL, "\n".join(body), "\n".join(js))


def index():
    hosts = []
    for i, (sid, st, du, _, _) in enumerate(SCENES):
        hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st}" data-duration="{du:.2f}" data-track-index="{2 + i % 2}" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{10 + i};"></div>')
    sfx, lanes = [], []
    for i, (t, f, v) in sorted(enumerate(SFX), key=lambda x: x[1][0]):
        start = max(0.0, t - SFX_PEAK.get(f, 0.0) + 1 / 60)
        dur = min(SFX_DUR[f], TOTAL - start)
        lane = next((k for k, end in enumerate(lanes) if end <= start), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = start + dur
        sfx.append(f'      <audio id="sfx{i}" src="assets/sfx/{f}.mp3" data-start="{start:.3f}" data-duration="{dur:.3f}" data-volume="{v}" data-track-index="{8 + lane}"></audio>')
    punch = '      tl.set("#footwrap", { scale: 1 }, 0);\n' + "\n".join(
        f'      tl.fromTo("#footwrap", {{ scale: 1.07 }}, {{ scale: 1, duration: 0.4, ease: "expo.out", immediateRender: false }}, {t});' for t in PUNCH)
    voice_end = VOICE_END
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
      <div id="walls" data-composition-id="walls" data-composition-src="compositions/walls.html" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:50;"></div>
      <audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="6"></audio>
      <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{TOTAL}" data-volume="1" data-fade-out="1.2" data-track-index="7"
        data-automation='{{"version":1,"lanes":[{{"target":"volume","points":[{{"t":0,"v":0.085}},{{"t":{voice_end - 0.1},"v":0.085}},{{"t":{voice_end + 0.35},"v":0.3}},{{"t":{TOTAL},"v":0.3}}]}}]}}'></audio>
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{punch}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


SFX_PEAK = {}
SFX_DUR = {"pop": 0.72, "whoosh-short": 0.57, "click-soft": 0.37, "ping": 1.32, "whoosh": 0.57, "impact-bass-1": 2.12, "sparkle": 1.8, "click": 0.37}
if os.path.exists(os.path.join(HERE, "sfx_peaks.json")):
    SFX_PEAK = json.load(open(os.path.join(HERE, "sfx_peaks.json")))

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
    for sid, st, du, body, js in SCENES:
        open(os.path.join(HERE, "compositions", f"{sid}.html"), "w").write(scene(sid, du, body, js))
    open(os.path.join(HERE, "compositions", "walls.html"), "w").write(walls_scene())
    open(os.path.join(HERE, "index.html"), "w").write(index())
    json.dump({"id": "kinetic", "name": "kinetic"}, open(os.path.join(HERE, "meta.json"), "w"))
    print("built", len(SCENES) + 1, "scenes, total", TOTAL)
