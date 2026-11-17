#!/usr/bin/env python3
"""Generates index.html + compositions/*.html for the Semi-D Gurun "Street Spray" reel.

Look: "Street Spray / Graffiti" — spray-painted tags with overspray mist and paint drips,
slap-sticker captions, stencil numbers, hand-sprayed arrows / crowns / stars on the bare white walls.
Fonts: Sedgwick Ave Display (tags), Rubik Spray Paint (stencil numbers), Archivo Black (stickers).

Edit the tables below (EDL, captions, SFX) and re-run:
    python3 tools/build.py
"""
import json, math, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
TAIL = 2.6  # hold after the last word

# ---------------------------------------------------------------- palette
INK, PINK, LIME, CYAN, ORANGE, VIOLET, PAPER = "#141414", "#FF2E88", "#C6FF1A", "#1EE3FF", "#FF7A00", "#8B3DFF", "#FFFFFF"

# ---------------------------------------------------------------- edit decision list
# parts = [(src_in, src_out)] of speech kept (one continuous handheld take, so picture = same moment
# unless `pics` overrides it with [(src_in, dur)] cut-aways).
EDL = [
    dict(id="s01", parts=[(55.42, 61.00)], pics=[(69.30, 1.20), (56.62, 4.38)]),  # HOOK mana nak cari tau? semi-D cluster RM281K lepas rebate
    dict(id="s02", parts=[(34.20, 39.20)], pics=[(48.90, 1.70), (34.00, 1.50), (3.00, 1.80)]),  # tengok lawa tak lawa ... harga murah-murah ni
    dict(id="s03", parts=[(5.04, 7.20)]),                    # rumah empat bilik, dua tandas, nampak?
    dict(id="s04", parts=[(7.76, 8.96)]),                    # ada tanah tepi
    dict(id="s05", parts=[(10.72, 12.20), (12.72, 15.86)]),  # kita masuk ... ruang tamu, dapat fully sliding sampai kat atas
    dict(id="s06", parts=[(18.90, 19.95)]),                  # ok ni master bedroom
    dict(id="s07", parts=[(24.10, 26.15), (27.00, 27.70)]),  # ni bilik yang kedua ... sangat luas
    dict(id="s08", parts=[(28.55, 30.90), (32.30, 33.78)]),  # sebelah sini kita ada ... tandas yang kedua
    dict(id="s09", parts=[(39.30, 42.36)]),                  # bilik keempat, sesuai buat store sebab tinggi
    dict(id="s10", parts=[(43.86, 46.66)]),                  # bilik yang ketiga lagi luas
    dict(id="s11", parts=[(48.08, 48.82)], pics=[(50.00, 0.74)]),  # yang ni ruang dapur
    dict(id="s12", parts=[(65.30, 66.70)]),                  # LPPSA boleh, loan bank boleh
    dict(id="s13", parts=[(66.72, 69.36)]),                  # ataupun yang berniaga perlukan SSM dan statement bank 6 bulan
    dict(id="s14", parts=[(69.42, 71.85)]),                  # untuk memiliki semi-D dekat Gurun
    dict(id="s15", parts=[(62.38, 64.82)], pics=[(61.00, 2.44 + TAIL)], extra=TAIL),  # CTA yang berminat ... isi borang kat bawah ni
]
# removed: "sekarang kita ada dekat semi-D kluster taman ..." (name unclear), "untuk kluster ada tanah tepi,
# tanah belakang takda", repeated "sliding", unclear "dapat tingkat satu / door bedroom in / satu tandas",
# "boleh buat ... sekali" (unclear), repeated "ruang dapur, boleh consider ruang dapur ...",
# "sini tanah, untuk ruang belakang, sini tanah tepi" (repeat), "tuan-tuan dan puan-puan", every pause.

t = 0.0
for s in EDL:
    s["start"] = round(t, 3)
    offs, acc = [], 0.0
    for a0, a1 in s["parts"]:
        offs.append(round(acc, 3))
        acc += a1 - a0
    s["offs"] = offs
    s["dur"] = round(acc, 3)
    t += s["dur"]
VOICE_END = round(t, 3)
TOTAL = round(VOICE_END + TAIL, 3)
ST = {s["id"]: s["start"] for s in EDL}
EN = {s["id"]: round(s["start"] + s["dur"], 3) for s in EDL}
SEG = {s["id"]: s for s in EDL}


def o(seg, src):
    """source second -> output second (handles multi-part segments)"""
    s = SEG[seg]
    for (a0, a1), off in zip(s["parts"], s["offs"]):
        if src <= a1 + 0.001:
            return round(s["start"] + off + max(0.0, src - a0), 3)
    a0, a1 = s["parts"][-1]
    return round(s["start"] + s["offs"][-1] + (src - a0), 3)


# ---------------------------------------------------------------- captions (word level, source times; 1 = key word)
CAPS = [
    ("s01", [("Mana", 55.45), ("nak", 55.63), ("cari", 55.75), ("tau?", 56.14)], 56.30),
    ("s01", [("Rumah", 56.30), ("semi-D", 56.70, 1), ("cluster", 57.66, 1), ("macam", 58.13), ("ni", 58.36)], 58.56),
    ("s01", [("Harga", 58.56), ("RM281K", 58.90, 1), ("sahaja", 59.80)], 60.30),
    ("s01", [("selepas", 60.32), ("rebate!", 60.60, 1)], 61.00),
    ("s02", [("Tengok,", 34.24), ("lawa", 34.72, 1), ("tak", 35.12), ("lawa?", 35.30, 1)], 35.82),
    ("s02", [("Tak", 35.82), ("kena", 36.06), ("dengan", 36.42), ("harga", 36.58, 1), ("dia", 37.02)], 37.30),
    ("s02", [("Sebab", 37.32), ("apa?", 37.60)], 37.80),
    ("s02", [("Sebab", 37.80), ("ni", 38.02), ("harga", 38.14), ("murah-murah", 38.42, 1), ("ni!", 38.84)], 39.20),
    ("s03", [("Rumah", 5.04), ("empat", 5.52, 1), ("bilik,", 5.76, 1)], 6.16),
    ("s03", [("dua", 6.16, 1), ("tandas,", 6.32, 1), ("nampak?", 6.96)], 7.20),
    ("s04", [("Ada", 7.76), ("tanah", 8.24, 1), ("tepi", 8.62, 1)], 8.96),
    ("s05", [("Kita", 10.72), ("masuk", 11.18), ("sekarang", 11.44), ("dekat", 11.66)], 12.20),
    ("s05", [("ruang", 12.75, 1), ("tamu", 12.98, 1)], 13.36),
    ("s05", [("Dapat", 13.36), ("fully", 13.64, 1), ("sliding", 14.02, 1)], 14.58),
    ("s05", [("sampai", 14.58), ("kat", 15.30), ("atas!", 15.48, 1)], 15.86),
    ("s06", [("Ni", 19.10), ("master", 19.24, 1), ("bedroom", 19.42, 1)], 19.95),
    ("s07", [("Ni", 24.22), ("bilik", 24.32, 1), ("yang", 24.88), ("kedua", 25.14, 1)], 26.15),
    ("s07", [("Sangat", 27.02), ("luas!", 27.40, 1)], 27.70),
    ("s08", [("Sebelah", 28.60), ("sini", 29.66), ("kita", 29.90), ("ada", 30.22)], 30.90),
    ("s08", [("tandas", 32.36, 1), ("yang", 32.84), ("kedua", 33.08, 1)], 33.78),
    ("s09", [("Ni", 39.64), ("bilik", 39.72, 1), ("yang", 39.94), ("keempat", 40.02, 1)], 40.76),
    ("s09", [("Sesuai", 40.76), ("kalau", 41.24), ("buat", 41.38), ("store", 41.56, 1)], 41.80),
    ("s09", [("sebab", 41.80), ("tinggi!", 41.94, 1)], 42.36),
    ("s10", [("Ni", 44.34), ("bilik", 44.46, 1), ("yang", 44.96), ("ketiga", 45.10, 1)], 45.72),
    ("s10", [("lagi", 45.72), ("luas!", 46.20, 1)], 46.66),
    ("s11", [("Yang", 48.10), ("ni", 48.24), ("ruang", 48.36, 1), ("dapur", 48.54, 1)], 48.82),
    ("s12", [("LPPSA", 65.34, 1), ("boleh,", 65.86)], 66.08),
    ("s12", [("loan", 66.08), ("bank", 66.30, 1), ("boleh!", 66.40)], 66.70),
    ("s13", [("Ataupun", 66.74), ("yang", 67.02), ("berniaga", 67.14, 1)], 67.42),
    ("s13", [("perlukan", 67.42), ("SSM", 67.66, 1)], 68.18),
    ("s13", [("dan", 68.18), ("statement", 68.26), ("bank", 68.54), ("6", 68.78, 1), ("bulan", 68.98, 1)], 69.36),
    ("s14", [("Untuk", 69.44), ("memiliki", 69.96)], 70.34),
    ("s14", [("semi-D", 70.34, 1), ("dekat", 70.90), ("Gurun!", 71.50, 1)], 71.85),
    ("s15", [("Yang", 62.40), ("berminat", 62.92, 1), ("macam", 63.28), ("mana?", 63.44)], 63.64),
    ("s15", [("Isi", 63.64, 1), ("sahaja", 63.96), ("borang", 64.22, 1)], 64.34),
    ("s15", [("kat", 64.34), ("bawah", 64.52, 1), ("ni", 64.74)], 64.82),
]

# ---------------------------------------------------------------- key beats (output seconds)
B = dict(
    rumah=o("s01", 56.30), cluster=o("s01", 57.66), harga=o("s01", 58.56), rm=o("s01", 58.90), selepas=o("s01", 60.32),
    lawa=o("s02", 34.72), kena=o("s02", 36.06), harga2=o("s02", 36.58), sebab=o("s02", 37.32), murah=o("s02", 38.42),
    empat=o("s03", 5.52), dua=o("s03", 6.16), nampak=o("s03", 6.96),
    tanah=o("s04", 8.24),
    ruang=o("s05", 12.75), fully=o("s05", 13.64), sliding=o("s05", 14.02), atas=o("s05", 14.58),
    master=o("s06", 19.24),
    bilik2=o("s07", 24.32), luas2=o("s07", 27.02),
    tandas2=o("s08", 32.36),
    bilik4=o("s09", 39.72), store=o("s09", 40.76), tinggi=o("s09", 41.70),
    bilik3=o("s10", 44.46), luas3=o("s10", 46.20),
    dapur=o("s11", 48.14),
    lppsa=o("s12", 65.34), lppsa_ok=o("s12", 65.86), bank=o("s12", 66.08), bank_ok=o("s12", 66.40),
    niaga=o("s13", 67.14), ssm=o("s13", 67.66), stmt=o("s13", 68.26), bulan=o("s13", 68.78),
    memiliki=o("s14", 69.96), semid=o("s14", 70.34), gurun=o("s14", 71.50),
    berminat=o("s15", 62.92), isi=o("s15", 63.64), borang=o("s15", 64.22), bawah=o("s15", 64.52),
)

# ---------------------------------------------------------------- transitions
WIPES = [ST["s02"], ST["s03"], ST["s12"]]   # full-frame spray-paint wipes (centre time = the cut)


# ---------------------------------------------------------------- sound effects (output time, file, volume, media_start, dur)
# every file is pre-normalised to about -20 LUFS (voice sits at -15), so 0.15-0.4 keeps them under the voice
def fx(at, name, vol=0.3, ms=0.0, dur=None):
    return dict(at=round(max(0.0, at), 3), name=name, vol=vol, ms=ms, dur=dur)


SFX = [
    # hook: cap pops, tag sprays on, sticker slaps, price lands
    fx(0.00, "cap-pop", 0.40),
    fx(0.06, "spray-06", 0.22),
    fx(0.62, "spray-035", 0.16),
    fx(B["rumah"] + 0.02, "sticker-slap", 0.34),
    fx(B["harga"] - 0.30, "can-shake", 0.26, 0.0, 0.35),
    fx(B["rm"] - 0.04, "impact-zoom", 0.30),
    fx(B["rm"] + 0.02, "spray-06", 0.20),
    fx(B["selepas"] + 0.02, "sticker-slap", 0.30),
    # wipe -> lawa
    fx(WIPES[0] - 0.28, "whoosh-fast", 0.26), fx(WIPES[0] - 0.24, "spray-035", 0.18),
    fx(B["lawa"] + 0.02, "spray-06", 0.18),
    fx(B["lawa"] + 0.30, "pop", 0.26), fx(B["lawa"] + 0.45, "pop", 0.22),
    fx(B["kena"] + 0.0, "spray-035", 0.16),
    fx(B["harga2"] + 0.02, "sticker-slap", 0.30),
    fx(B["sebab"] + 0.02, "spray-035", 0.16),
    fx(B["murah"] - 0.32, "can-rattle", 0.22, 0.0, 0.34),
    fx(B["murah"] - 0.03, "whoosh-impact", 0.20, 0.0, 1.2),
    fx(B["murah"] + 0.02, "spray-10", 0.20),
    # wipe -> specs
    fx(WIPES[1] - 0.28, "whoosh-fast", 0.26), fx(WIPES[1] - 0.24, "spray-035", 0.18),
    fx(B["empat"] - 0.02, "spray-035", 0.18), fx(B["empat"] + 0.18, "pop", 0.32),
    fx(B["dua"] - 0.02, "spray-035", 0.18), fx(B["dua"] + 0.18, "pop", 0.32),
    # tanah tepi
    fx(ST["s04"] - 0.05, "whoosh-accent", 0.16),
    fx(B["tanah"] - 0.10, "spray-06", 0.18),
    # ruang tamu
    fx(ST["s05"] - 0.05, "whoosh-accent", 0.16),
    fx(B["ruang"] - 0.02, "spray-06", 0.18),
    fx(B["sliding"] - 0.02, "spray-035", 0.16),
    fx(B["atas"] - 0.06, "spray-06", 0.18),
    fx(B["atas"] + 0.20, "sticker-slap", 0.26),
    # master
    fx(ST["s06"] - 0.05, "whoosh-accent", 0.16),
    fx(B["master"] - 0.06, "spray-06", 0.18), fx(B["master"] + 0.30, "ding", 0.12),
    # bilik 2
    fx(ST["s07"] - 0.05, "whoosh-accent", 0.16),
    fx(B["bilik2"] - 0.02, "spray-06", 0.18),
    fx(B["luas2"] - 0.04, "spray-06", 0.18),
    # tandas 2
    fx(ST["s08"] - 0.05, "whoosh-accent", 0.16),
    fx(B["tandas2"] - 0.04, "spray-06", 0.18), fx(B["tandas2"] + 0.35, "pop", 0.24),
    # bilik 4
    fx(ST["s09"] - 0.05, "whoosh-accent", 0.16),
    fx(B["bilik4"] - 0.02, "spray-06", 0.18),
    fx(B["store"] + 0.02, "sticker-slap", 0.28),
    fx(B["tinggi"] - 0.04, "spray-10", 0.18),
    # bilik 3
    fx(ST["s10"] - 0.05, "whoosh-accent", 0.16),
    fx(B["bilik3"] - 0.02, "spray-06", 0.18),
    fx(B["luas3"] - 0.04, "spray-06", 0.18),
    # dapur
    fx(ST["s11"] - 0.05, "whoosh-accent", 0.16),
    fx(B["dapur"] - 0.10, "spray-035", 0.18),
    # wipe -> loan checklist
    fx(WIPES[2] - 0.28, "whoosh-fast", 0.26), fx(WIPES[2] - 0.24, "spray-035", 0.18),
    fx(B["lppsa"] + 0.02, "sticker-slap", 0.28), fx(B["lppsa_ok"] + 0.02, "spray-035", 0.20),
    fx(B["bank"] + 0.02, "sticker-slap", 0.28), fx(B["bank_ok"] + 0.02, "spray-035", 0.20),
    fx(B["niaga"] + 0.02, "sticker-slap", 0.28), fx(B["ssm"] + 0.10, "spray-035", 0.20),
    fx(B["bulan"] + 0.10, "ding", 0.14),
    fx(B["memiliki"] - 0.05, "whoosh-accent", 0.18),
    fx(B["semid"] - 0.02, "spray-06", 0.18),
    fx(B["gurun"] - 0.04, "sticker-slap", 0.30),
    # CTA
    fx(ST["s15"] - 0.30, "can-shake", 0.24, 0.0, 0.35),
    fx(B["isi"] - 0.04, "sticker-slap", 0.34), fx(B["isi"] + 0.02, "spray-06", 0.18),
    fx(B["bawah"] - 0.02, "spray-035", 0.16),
    fx(VOICE_END + 0.05, "sticker-slap", 0.24),
    fx(VOICE_END + 0.20, "sticker-slap", 0.22),
    fx(VOICE_END + 0.35, "sticker-slap", 0.22),
    fx(VOICE_END + 0.50, "sticker-slap", 0.22),
    fx(VOICE_END + 0.80, "ding", 0.14),
]


# ---------------------------------------------------------------- camera moves on #cam
def cam_js():
    js = []
    cuts = [s["start"] for s in EDL[1:]]
    # inside multi-part segments the jump cut gets a punch too
    for s in EDL:
        for off in s["offs"][1:]:
            cuts.append(round(s["start"] + off, 3))
    for s in EDL:
        if s.get("pics"):
            acc = 0.0
            for src, d in s["pics"][:-1]:
                acc += d
                cuts.append(round(s["start"] + acc, 3))
    cuts = sorted(set(cuts))
    js.append(f'tl.fromTo("#cam", {{ scale: 1.16 }}, {{ scale: 1.04, duration: 0.7, ease: "expo.out", immediateRender: false }}, 0);')
    for i, c in enumerate(cuts):
        nxt = cuts[i + 1] if i + 1 < len(cuts) else TOTAL
        big = any(abs(c - w) < 0.01 for w in WIPES)
        s0 = 1.22 if big else (1.12 if i % 2 == 0 else 1.09)
        rot = 0 if big else (-1.2 if i % 2 else 1.2)
        js.append(f'tl.fromTo("#cam", {{ scale: {s0}, rotation: {rot} }}, {{ scale: 1.03, rotation: 0, duration: 0.42, ease: "expo.out", immediateRender: false }}, {c:.3f});')
        if nxt - c > 0.6:
            js.append(f'tl.to("#cam", {{ scale: 1.07, duration: {nxt - c - 0.42:.3f}, ease: "none" }}, {c + 0.42:.3f});')
    return "\n      ".join(js)


# ================================================================ shared building blocks
FONTS = """
@font-face { font-family: "Sedgwick Ave Display"; src: url("assets/fonts/sedgwick-ave-display.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Rubik Spray Paint"; src: url("assets/fonts/rubik-spray-paint.woff2") format("woff2"); font-display: block; }
@font-face { font-family: "Archivo Black"; src: url("assets/fonts/archivo-black.woff2") format("woff2"); font-display: block; }
"""

BASE_CSS = f"""
#root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
.abs {{ position: absolute; }}
.b {{ position: relative; }}
svg.dd {{ position: absolute; overflow: visible; }}
svg.dd .sp, svg.dd .dr {{ fill: none; stroke-linecap: round; stroke-linejoin: round; }}
.tag {{ font-family: "Sedgwick Ave Display"; white-space: nowrap; line-height: 0.92; color: {PINK};
  -webkit-text-stroke: 9px {INK}; paint-order: stroke fill; text-shadow: 7px 8px 0 {INK}; letter-spacing: 1px; }}
.sten {{ font-family: "Rubik Spray Paint"; white-space: nowrap; line-height: 0.9; color: {LIME};
  -webkit-text-stroke: 6px {INK}; paint-order: stroke fill; text-shadow: 6px 7px 0 {INK}; }}
.stk {{ position: absolute; font-family: "Archivo Black"; white-space: nowrap; line-height: 1; color: {INK};
  background: {PAPER}; border: 5px solid {INK}; border-radius: 16px; padding: 12px 22px 14px;
  box-shadow: 7px 8px 0 rgba(20,20,20,0.85); }}
.stk.pk {{ background: {PINK}; color: #fff; }}
.stk.lm {{ background: {LIME}; }}
.stk.cy {{ background: {CYAN}; }}
.stk.or {{ background: {ORANGE}; }}
"""


def defs(p):
    """spray filters, prefixed per composition so every comp is self-contained"""
    return f"""<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<filter id="{p}-sp" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="7" xChannelSelector="R" yChannelSelector="G" result="core"/>
  <feGaussianBlur in="core" stdDeviation="1.3" result="soft"/>
  <feGaussianBlur in="core" stdDeviation="11" result="halo"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="1" seed="8" result="dots"/>
  <feColorMatrix in="dots" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  7 0 0 0 -3.75" result="dmask"/>
  <feComposite in="halo" in2="dmask" operator="in" result="speck"/>
  <feComponentTransfer in="halo" result="mist"><feFuncA type="linear" slope="0.30"/></feComponentTransfer>
  <feMerge><feMergeNode in="mist"/><feMergeNode in="speck"/><feMergeNode in="soft"/></feMerge>
</filter>
<filter id="{p}-tg" x="-12%" y="-25%" width="124%" height="150%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="5" result="warp"/>
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="4" xChannelSelector="R" yChannelSelector="G" result="core"/>
  <feGaussianBlur in="core" stdDeviation="0.6" result="soft"/>
  <feGaussianBlur in="core" stdDeviation="9" result="halo"/>
  <feComponentTransfer in="halo" result="mist"><feFuncA type="linear" slope="0.22"/></feComponentTransfer>
  <feMerge><feMergeNode in="mist"/><feMergeNode in="soft"/></feMerge>
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
      var SPR = spring(0.45, 14, 0.8);
      function hh(n, s) { var x = Math.sin(n * 127.1 + (s || 1) * 311.7) * 43758.5453; return (x - Math.floor(x)) * 2 - 1; }
      var renders = [];
      // hand-made "boil": inner wrappers re-jitter 12 times a second, like re-sprayed frames
      function boil(sel, amp, rot, seed) {
        var els = gsap.utils.toArray(sel);
        renders.push(function () {
          var st = Math.floor(tl.time() * 12);
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
      // sticker slap: drops onto the wall from above the lens
      function slap(sel, at, rot) {
        tl.fromTo(sel, { scale: 1.45, opacity: 0, rotation: (rot || 0) + 9 },
          { scale: 1, opacity: 1, rotation: rot || 0, duration: 0.34, ease: "back.out(2.4)", immediateRender: true }, at);
      }
      function pop(sel, at, from, rot) {
        tl.fromTo(sel, { scale: from == null ? 0.2 : from, opacity: 0, rotation: (rot || 0) - 12 },
          { scale: 1, opacity: 1, rotation: rot || 0, duration: 0.8, ease: SPR, immediateRender: true }, at);
      }
      // spray-on reveal of a tag, left to right (nozzle sweep) with a slight settle
      function spray(sel, at, dur) {
        dur = dur || 0.45;
        tl.fromTo(sel, { clipPath: "inset(-40% 104% -40% -6%)", opacity: 1 },
          { clipPath: "inset(-40% -6% -40% -6%)", duration: dur, ease: "power1.inOut", immediateRender: true }, at);
        tl.fromTo(sel, { scale: 1.06 }, { scale: 1, duration: dur + 0.3, ease: "power2.out", immediateRender: false }, at);
        tl.set(sel, { clipPath: "none" }, at + dur + 0.01);
      }
      function sprayUp(sel, at, dur) {
        dur = dur || 0.45;
        tl.fromTo(sel, { clipPath: "inset(104% -20% -6% -20%)", opacity: 1 },
          { clipPath: "inset(-6% -20% -6% -20%)", duration: dur, ease: "power1.inOut", immediateRender: true }, at);
        tl.set(sel, { clipPath: "none" }, at + dur + 0.01);
      }
      // spray stroke draw-on; strokes sharing data-i draw together
      function draw(sel, at, dur) {
        var ps = gsap.utils.toArray(sel + " .sp");
        var n = 0; ps.forEach(function (p) { n = Math.max(n, +(p.getAttribute("data-i") || 0) + 1); });
        var seg = dur / Math.max(1, n * 0.8 + 0.2);
        ps.forEach(function (p) {
          var i = +(p.getAttribute("data-i") || 0), len = p.getTotalLength() + 4;
          gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len, opacity: 0 });
          tl.set(p, { opacity: 1 }, at + i * seg * 0.8);
          tl.to(p, { strokeDashoffset: 0, duration: seg, ease: "power1.inOut" }, at + i * seg * 0.8);
        });
      }
      // wet paint runs: each .dr path creeps down (gravity ease), drop at the end
      function drip(sel, at) {
        gsap.utils.toArray(sel + " .dr").forEach(function (p) {
          var len = p.getTotalLength() + 2, d = +(p.getAttribute("data-d") || 1.2), w = +(p.getAttribute("data-o") || 0);
          gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len, opacity: 0 });
          tl.set(p, { opacity: 1 }, at + w);
          tl.to(p, { strokeDashoffset: 0, duration: d, ease: "power2.out" }, at + w);
        });
      }
      function out(sel, at, d) { tl.to(sel, { opacity: 0, scale: 0.9, duration: d || 0.18, ease: "power2.in" }, at); }
      // stencil counter: digit column rolls to the target row
      function roll(sel, at, n, rowH) {
        tl.fromTo(sel, { y: 0 }, { y: -n * rowH, duration: 0.6, ease: SPR, immediateRender: true }, at);
      }
      function bob(sel, at, n, amp, per) {
        tl.to(sel, { y: amp, duration: per || 0.2, ease: "sine.inOut", yoyo: true, repeat: n * 2 - 1 }, at);
      }
"""


def jit(pts, seed, amp=3.0):
    """jitter a polyline for a hand-sprayed wobble -> smooth path string"""
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


def ring(cx, cy, rx, ry, seed, turns=1.15, n=26, amp=4):
    """loose hand-sprayed ellipse that overshoots its start, like a can swung round"""
    pts = []
    for k in range(n + 1):
        a = -math.pi * 0.6 + 2 * math.pi * turns * k / n
        sc = 1 + 0.06 * math.sin(k * 0.7 + seed)
        pts.append((cx + rx * sc * math.cos(a), cy + ry * sc * math.sin(a)))
    return jit(pts, seed, amp)


def strokes(p, w, h, paths, extra="", filt="sp"):
    """spray svg: paths = [(d, data-i, color, width)]"""
    body = ""
    for d, i, c, ww in paths:
        body += f'<path class="sp" data-i="{i}" d="{d}" stroke="{c}" stroke-width="{ww}"/>'
    return (f'<svg class="dd" viewBox="0 0 {w} {h}" style="left:0;top:0;width:{w}px;height:{h}px;filter:url(#{p}-{filt})">'
            f'{extra}{body}</svg>')


def drips(p, w, h, xs, color, seed, y0=0, wmin=8, wmax=14, lmin=40, lmax=120):
    """paint runs hanging from y0: one per x; data-d = run time, data-o = delay"""
    def h_(n):
        x = math.sin(n * 91.7 + seed * 211.3) * 43758.5453
        return x - math.floor(x)
    body = ""
    for k, x in enumerate(xs):
        L = lmin + (lmax - lmin) * h_(k * 3)
        ww = wmin + (wmax - wmin) * h_(k * 3 + 1)
        d = f"M{x:.1f} {y0:.1f} L{x + (h_(k * 3 + 2) - 0.5) * 3:.1f} {y0 + L:.1f}"
        body += (f'<path class="dr" data-d="{0.9 + 0.9 * h_(k * 5):.2f}" data-o="{0.1 + 0.35 * h_(k * 7):.2f}" d="{d}" '
                 f'stroke="{color}" stroke-width="{ww:.1f}"/>')
    return (f'<svg class="dd" viewBox="0 0 {w} {h}" style="left:0;top:0;width:{w}px;height:{h}px;filter:url(#{p}-tg)">'
            f'{body}</svg>')


def wrap(id_, left, top, w, h, inner, extra_style=""):
    return (f'<div class="abs" id="{id_}" style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;{extra_style}">'
            f'<div class="b" style="width:{w}px;height:{h}px">{inner}</div></div>')


def tag(id_, text, left, top, size, color=PINK, rot=0, extra=""):
    return (f'<div class="abs tag" id="{id_}" style="left:{left}px;top:{top}px;font-size:{size}px;color:{color};'
            f'rotate:{rot}deg;filter:url(#__P__-tg);{extra}"><div class="b">{text}</div></div>')


def sten(id_, text, left, top, size, color=LIME, rot=0):
    return (f'<div class="abs sten" id="{id_}" style="left:{left}px;top:{top}px;font-size:{size}px;color:{color};'
            f'rotate:{rot}deg;filter:url(#__P__-tg)"><div class="b">{text}</div></div>')


def stk(id_, html, left, top, size=46, kind="", rot=0):
    return (f'<div class="stk {kind}" id="{id_}" style="left:{left}px;top:{top}px;font-size:{size}px;rotate:{rot}deg">{html}</div>')


# ----- doodle shapes (local coords)
def arrow(x0, y0, x1, y1, seed, head=46, bend=0.18):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    cx, cy = mx + nx * L * bend, my + ny * L * bend
    shaft = jit([(x0, y0), (cx, cy), (x1, y1)], seed, 3)
    # head direction = tangent at end
    tx, ty = x1 - cx, y1 - cy
    tl_ = math.hypot(tx, ty) or 1
    tx, ty = tx / tl_, ty / tl_
    def rot(vx, vy, a):
        return vx * math.cos(a) - vy * math.sin(a), vx * math.sin(a) + vy * math.cos(a)
    h1 = rot(-tx, -ty, 0.55)
    h2 = rot(-tx, -ty, -0.55)
    hp = jit([(x1 + h1[0] * head, y1 + h1[1] * head), (x1, y1), (x1 + h2[0] * head, y1 + h2[1] * head)], seed + 1, 2)
    return shaft, hp


def crown(w, h, seed):
    return jit([(w * 0.05, h * 0.95), (w * 0.0, h * 0.25), (w * 0.27, h * 0.6), (w * 0.5, h * 0.05),
                (w * 0.73, h * 0.6), (w * 1.0, h * 0.25), (w * 0.95, h * 0.95), (w * 0.05, h * 0.95)], seed, 3)


def star(cx, cy, r, seed):
    pts = []
    for k in range(11):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return jit(pts, seed, 2)


def check(w, h, seed):
    return jit([(w * 0.05, h * 0.55), (w * 0.38, h * 0.92), (w * 0.95, h * 0.06)], seed, 2)


def comp(cid, dur, css, body, js, p):
    body = body.replace("__P__", p)
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


def scene(cid, segs):
    s = ST[segs[0]]
    e = EN[segs[-1]] if segs[-1] != "s15" else TOTAL
    return s, round(e - s, 3), (lambda x: round(x - s, 3))


# ================================================================ scenes
def scene_hook():
    p = "hk"
    s, d, rel = scene("hook", ["s01"])
    ul = jit([(10, 30), (180, 18), (360, 30), (540, 16), (700, 26)], 3, 4)
    cr = crown(170, 110, 7)
    ring_d = ring(345, 115, 360, 118, 11)
    dr_mana = drips(p, 700, 200, [70, 160, 300, 455, 610], PINK, 2, y0=4)
    dr_price = drips(p, 700, 200, [50, 180, 300, 430, 560, 650], LIME, 5, y0=4, lmin=50, lmax=150)
    body = (
        tag("hk-mana", "MANA NAK<br>CARI?", 140, 350, 140, PINK, -4)
        + wrap("hk-mdr", 150, 582, 700, 200, dr_mana)
        + wrap("hk-ul", 138, 606, 720, 60, strokes(p, 720, 60, [(ul, 0, LIME, 16)]))
        + stk("hk-semid", "SEMI-D CLUSTER", 140, 696, 50, "", -3)
        + stk("hk-gurun", "GURUN, KEDAH", 560, 780, 36, "cy", 4)
        + wrap("hk-ring", 110, 296, 700, 240, strokes(p, 700, 240, [(ring_d, 0, PINK, 15)]))
        + sten("hk-rm", "RM281K", 140, 340, 160, LIME, -3)
        + wrap("hk-pdr", 150, 478, 700, 200, dr_price)
        + wrap("hk-crown", 660, 250, 170, 110, strokes(p, 170, 110, [(cr, 0, "#FFD400", 13)]))
        + stk("hk-reb", "*selepas rebate", 470, 580, 42, "pk", -5)
    )
    js = f"""
      // frame 0 already reads: the tag is sprayed, the underline and drips run
      tl.fromTo("#hk-mana", {{ scale: 1.12, transformOrigin: "0% 50%" }}, {{ scale: 1, duration: 0.7, ease: SPR }}, 0);
      draw("#hk-ul", 0.30, 0.45);
      drip("#hk-mdr", 0.05);
      slap("#hk-semid", {rel(B['rumah']):.3f}, -3);
      slap("#hk-gurun", {rel(B['cluster']):.3f}, 4);
      out(["#hk-mana", "#hk-mdr", "#hk-ul", "#hk-semid", "#hk-gurun"], {rel(B['harga']) - 0.05:.3f}, 0.16);
      spray("#hk-rm", {rel(B['rm']) - 0.12:.3f}, 0.42);
      tl.fromTo("#hk-rm", {{ scale: 1.5 }}, {{ scale: 1, duration: 0.5, ease: "back.out(2)", immediateRender: false }}, {rel(B['rm']) - 0.12:.3f});
      drip("#hk-pdr", {rel(B['rm']) + 0.25:.3f});
      draw("#hk-crown", {rel(B['rm']) + 0.35:.3f}, 0.4);
      draw("#hk-ring", {rel(B['rm']) + 0.55:.3f}, 0.45);
      slap("#hk-reb", {rel(B['selepas']):.3f}, -5);
      boil("#hk-mana .b, #hk-ul .b, #hk-ring .b, #hk-crown .b, #hk-rm .b", 1.2, 0.35, 3);
"""
    SCENES.append(("hook", s, d, comp("hook", d, "", body, js, p)))


def scene_lawa():
    p = "lw"
    s, d, rel = scene("lawa", ["s02"])
    sts = "".join(wrap(f"lw-st{i}", x, y, 90, 90, strokes(p, 90, 90, [(star(45, 45, 40, 20 + i), 0, c, 9)]))
                  for i, (x, y, c) in enumerate([(470, 270, "#FFD400"), (560, 380, CYAN), (130, 470, LIME)]))
    neq1 = jit([(10, 30), (110, 24)], 31, 2)
    neq2 = jit([(10, 70), (110, 64)], 32, 2)
    neq3 = jit([(85, 0), (35, 100)], 33, 2)
    burst = jit([(x, y) for k in range(17) for (x, y) in [(380 + (300 if k % 2 == 0 else 200) * math.cos(-math.pi / 2 + k * math.pi / 8),
                                                            150 + (150 if k % 2 == 0 else 100) * math.sin(-math.pi / 2 + k * math.pi / 8))]], 41, 6)
    dr = drips(p, 760, 200, [90, 230, 400, 560, 690], ORANGE, 9, y0=4, lmin=60, lmax=160)
    body = (
        tag("lw-lawa", "LAWA!", 140, 330, 166, PINK, -6)
        + sts
        + wrap("lw-neq", 520, 330, 120, 100, strokes(p, 120, 100, [(neq1, 0, INK, 14), (neq2, 0, INK, 14), (neq3, 1, PINK, 14)]))
        + stk("lw-price", "RM281K", 640, 340, 54, "lm", 5)
        + tag("lw-q", "?", 690, 520, 200, CYAN, 10)
        + wrap("lw-burst", 120, 290, 760, 300, strokes(p, 760, 300, [(burst, 0, "#FFD400", 14)]))
        + tag("lw-murah", "MURAH-<br>&nbsp;&nbsp;MURAH!", 140, 320, 146, ORANGE, -5)
        + wrap("lw-dr", 160, 600, 760, 200, dr)
    )
    js = f"""
      spray("#lw-lawa", {rel(B['lawa']) - 0.05:.3f}, 0.35);
      pop("#lw-st0", {rel(B['lawa']) + 0.15:.3f}); pop("#lw-st1", {rel(B['lawa']) + 0.25:.3f}); pop("#lw-st2", {rel(B['lawa']) + 0.35:.3f});
      tl.to(["#lw-st0 .dd", "#lw-st1 .dd", "#lw-st2 .dd"], {{ scale: 0.75, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 1, transformOrigin: "50% 50%" }}, {rel(B['lawa']) + 0.6:.3f});
      out(["#lw-st0", "#lw-st1", "#lw-st2"], {rel(B['kena']) - 0.08:.3f}, 0.12);
      draw("#lw-neq", {rel(B['kena']):.3f}, 0.4);
      slap("#lw-price", {rel(B['harga2']):.3f}, 5);
      sprayUp("#lw-q", {rel(B['sebab']):.3f}, 0.3);
      tl.to("#lw-q", {{ rotation: -8, duration: 0.12, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {rel(B['sebab']) + 0.3:.3f});
      out(["#lw-lawa", "#lw-neq", "#lw-price", "#lw-q"], {rel(B['murah']) - 0.18:.3f}, 0.15);
      draw("#lw-burst", {rel(B['murah']) - 0.06:.3f}, 0.35);
      spray("#lw-murah", {rel(B['murah']) - 0.04:.3f}, 0.4);
      tl.fromTo("#lw-murah", {{ scale: 1.45 }}, {{ scale: 1, duration: 0.5, ease: "back.out(2.2)", immediateRender: false }}, {rel(B['murah']) - 0.04:.3f});
      drip("#lw-dr", {rel(B['murah']) + 0.25:.3f});
      boil("#lw-lawa .b, #lw-neq .b, #lw-q .b, #lw-burst .b, #lw-murah .b", 1.2, 0.35, 5);
"""
    SCENES.append(("lawa", s, d, comp("lawa", d, "", body, js, p)))


def scene_specs():
    p = "sx"
    s, d, rel = scene("specs", ["s03"])
    css = f"""
.cnt {{ position:absolute; width:250px; height:250px; }}
.win {{ position:absolute; left:0; right:0; top:22px; height:180px; overflow:hidden; }}
.col {{ position:absolute; left:0; right:0; top:0; text-align:center; }}
.col div {{ height:180px; font-family:"Rubik Spray Paint"; font-size:200px; line-height:180px; color:{LIME};
  -webkit-text-stroke:6px {INK}; paint-order:stroke fill; text-shadow:6px 7px 0 {INK}; }}
.lbl {{ position:absolute; left:0; right:0; top:206px; text-align:center; }}
"""
    def counter(id_, left, n, color, label, seed, ringcol):
        rg = ring(125, 110, 112, 108, seed)
        digits = "".join(f'<div style="color:{color}">{k}</div>' for k in range(n + 1))
        return (f'<div class="cnt" id="{id_}" style="left:{left}px;top:280px">'
                + wrap(id_ + "r", 0, 0, 250, 230, strokes(p, 250, 230, [(rg, 0, ringcol, 13)]))
                + f'<div class="win"><div class="col" id="{id_}c" data-layout-allow-safe-zone>{digits}</div></div>'
                + f'<div class="lbl"><span class="stk" style="position:relative;font-size:46px;rotate:-2deg">{label}</span></div></div>')
    body = counter("sx-a", 140, 4, LIME, "BILIK", 51, PINK) + counter("sx-b", 520, 2, CYAN, "TANDAS", 53, "#FFD400")
    js = f"""
      gsap.set(["#sx-a", "#sx-b"], {{ opacity: 0 }});
      tl.set("#sx-a", {{ opacity: 1 }}, {rel(B['empat']) - 0.04:.3f});
      draw("#sx-ar", {rel(B['empat']) - 0.04:.3f}, 0.3);
      roll("#sx-ac", {rel(B['empat']) + 0.02:.3f}, 4, 180);
      tl.set("#sx-b", {{ opacity: 1 }}, {rel(B['dua']) - 0.04:.3f});
      draw("#sx-br", {rel(B['dua']) - 0.04:.3f}, 0.3);
      roll("#sx-bc", {rel(B['dua']) + 0.02:.3f}, 2, 180);
      tl.fromTo(["#sx-a .lbl", "#sx-b .lbl"], {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, ease: "back.out(2)", stagger: {B['dua'] - B['empat']:.3f} }}, {rel(B['empat']) + 0.2:.3f});
      boil("#sx-ar .b, #sx-br .b", 1.3, 0.4, 7);
"""
    SCENES.append(("specs", s, d, comp("specs", d, css, body, js, p)))


def scene_tepi():
    p = "tp"
    s, d, rel = scene("tepi", ["s04"])
    sh, hd = arrow(560, 30, 90, 330, 61, 60, -0.25)
    body = (
        tag("tp-tag", "TANAH TEPI", 300, 335, 116, CYAN, -3)
        + wrap("tp-arr", 160, 430, 640, 380, strokes(p, 640, 380, [(sh, 0, "#FFD400", 18), (hd, 1, "#FFD400", 18)]))
        + stk("tp-ok", "ADA ✓", 600, 600, 50, "lm", 6)
    )
    js = f"""
      spray("#tp-tag", 0.02, 0.35);
      draw("#tp-arr", {rel(B['tanah']) - 0.08:.3f}, 0.4);
      slap("#tp-ok", {rel(B['tanah']) + 0.25:.3f}, 6);
      boil("#tp-tag .b, #tp-arr .b", 1.2, 0.35, 9);
"""
    SCENES.append(("tepi", s, d, comp("tepi", d, "", body, js, p)))


def scene_tamu():
    p = "tm"
    s, d, rel = scene("tamu", ["s05"])
    lr1, lr1h = arrow(250, 70, 30, 70, 71, 40, 0.0)
    lr2, lr2h = arrow(290, 70, 510, 70, 72, 40, 0.0)
    up, uph = arrow(70, 470, 70, 30, 73, 50, 0.04)
    dr = drips(p, 700, 160, [60, 200, 380, 520], PINK, 13, y0=4)
    body = (
        tag("tm-tag", "RUANG TAMU", 135, 335, 126, PINK, -4)
        + wrap("tm-dr", 145, 445, 700, 160, dr)
        + wrap("tm-lr", 150, 470, 540, 140, strokes(p, 540, 140, [(lr1, 0, CYAN, 15), (lr1h, 1, CYAN, 15), (lr2, 0, CYAN, 15), (lr2h, 1, CYAN, 15)]))
        + stk("tm-fs", "FULL SLIDING", 180, 600, 48, "cy", -2)
        + wrap("tm-up", 720, 250, 140, 500, strokes(p, 140, 500, [(up, 0, "#FFD400", 18), (uph, 1, "#FFD400", 18)]))
        + stk("tm-atas", "SAMPAI ATAS!", 470, 690, 44, "lm", 4)
    )
    js = f"""
      gsap.set("#tm-tag", {{ opacity: 0 }});
      spray("#tm-tag", {rel(B['ruang']) - 0.05:.3f}, 0.4);
      drip("#tm-dr", {rel(B['ruang']) + 0.3:.3f});
      draw("#tm-lr", {rel(B['sliding']) - 0.06:.3f}, 0.35);
      tl.to("#tm-lr .dd", {{ scaleX: 1.08, duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut", transformOrigin: "50% 50%" }}, {rel(B['sliding']) + 0.35:.3f});
      slap("#tm-fs", {rel(B['fully']):.3f}, -2);
      draw("#tm-up", {rel(B['atas']) - 0.1:.3f}, 0.4);
      slap("#tm-atas", {rel(B['atas']) + 0.2:.3f}, 4);
      boil("#tm-tag .b, #tm-lr .b, #tm-up .b", 1.2, 0.35, 11);
"""
    SCENES.append(("tamu", s, d, comp("tamu", d, "", body, js, p)))


def scene_master():
    p = "ms"
    s, d, rel = scene("master", ["s06"])
    cr = crown(260, 160, 17)
    body = (
        wrap("ms-crown", 170, 270, 260, 160, strokes(p, 260, 160, [(cr, 0, "#FFD400", 16)]))
        + tag("ms-tag", "MASTER", 135, 420, 146, "#FFD400", -5)
        + stk("ms-bed", "BEDROOM", 470, 560, 52, "pk", 4)
    )
    js = f"""
      spray("#ms-tag", {rel(B['master']) - 0.12:.3f}, 0.32);
      draw("#ms-crown", {rel(B['master']) + 0.08:.3f}, 0.32);
      slap("#ms-bed", {rel(B['master']) + 0.22:.3f}, 4);
      boil("#ms-crown .b, #ms-tag .b", 1.2, 0.35, 13);
"""
    SCENES.append(("master", s, d, comp("master", d, "", body, js, p)))


def room_scene(cid, p, segk, title, color, beat, extra_body, extra_js, seed):
    s, d, rel = scene(cid, [segk])
    dr = drips(p, 640, 160, [70, 230, 420, 560], color, seed, y0=4)
    body = tag(f"{p}-tag", title, 135, 335, 136, color, -4) + wrap(f"{p}-dr", 145, 452, 640, 160, dr) + extra_body
    js = f"""
      gsap.set("#{p}-tag", {{ opacity: 0 }});
      spray("#{p}-tag", {rel(B[beat]) - 0.06:.3f}, 0.38);
      drip("#{p}-dr", {rel(B[beat]) + 0.3:.3f});
{extra_js(rel)}
      boil(".abs > .b", 1.1, 0.3, {seed});
"""
    SCENES.append((cid, s, d, comp(cid, d, "", body, js, p)))


def scene_rooms():
    # bilik 2: "sangat luas" -> arrows burst sideways
    l1, l1h = arrow(330, 60, 40, 60, 81, 44, 0.0)
    l2, l2h = arrow(370, 60, 660, 60, 82, 44, 0.0)
    room_scene("bilik2", "b2", "s07", "BILIK 2", LIME, "bilik2",
               wrap("b2-lr", 110, 520, 700, 120, strokes("b2", 700, 120, [(l1, 0, PINK, 16), (l1h, 1, PINK, 16), (l2, 0, PINK, 16), (l2h, 1, PINK, 16)]))
               + stk("b2-luas", "SANGAT LUAS!", 300, 640, 50, "pk", -3),
               lambda rel: f"""      draw("#b2-lr", {rel(B['luas2']) - 0.1:.3f}, 0.3);
      tl.fromTo("#b2-lr .dd", {{ scaleX: 0.7 }}, {{ scaleX: 1.08, duration: 0.5, ease: "back.out(2)", transformOrigin: "50% 50%", immediateRender: false }}, {rel(B['luas2']) - 0.1:.3f});
      slap("#b2-luas", {rel(B['luas2']):.3f}, -3);""", 21)
    # tandas 2: sprayed water drop
    drop = jit([(60, 0), (20, 80), (14, 120), (35, 155), (60, 162), (85, 155), (106, 120), (100, 80), (60, 0)], 91, 2)
    room_scene("tandas2", "t2", "s08", "TANDAS 2", CYAN, "tandas2",
               wrap("t2-drop", 700, 330, 120, 170, strokes("t2", 120, 170, [(drop, 0, CYAN, 13)])),
               lambda rel: f"""      draw("#t2-drop", {rel(B['tandas2']) + 0.3:.3f}, 0.35);
      tl.to("#t2-drop", {{ y: 18, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }}, {rel(B['tandas2']) + 0.7:.3f});""", 23)
    # bilik 4: tall double arrow + store sticker
    vu, vuh = arrow(60, 260, 60, 20, 101, 46, 0.0)
    vd, vdh = arrow(60, 300, 60, 540, 102, 46, 0.0)
    room_scene("bilik4", "b4", "s09", "BILIK 4", ORANGE, "bilik4",
               wrap("b4-h", 740, 250, 120, 560, strokes("b4", 120, 560, [(vu, 0, LIME, 16), (vuh, 1, LIME, 16), (vd, 0, LIME, 16), (vdh, 1, LIME, 16)]))
               + tag("b4-tg", "TINGGI!", 640, 830, 92, LIME, -90, "transform-origin:0 0;")
               + stk("b4-store", "SESUAI BUAT STORE", 130, 590, 40, "", -2),
               lambda rel: f"""      slap("#b4-store", {rel(B['store']):.3f}, -2);
      draw("#b4-h", {rel(B['tinggi']) - 0.1:.3f}, 0.4);
      gsap.set("#b4-tg", {{ opacity: 0 }});
      tl.fromTo("#b4-tg", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)", immediateRender: false }}, {rel(B['tinggi']) + 0.1:.3f});""", 25)
    # bilik 3: "lagi luas" -> arrows push outward to four corners
    a1 = arrow(300, 150, 60, 20, 111, 38, 0.0)
    a2 = arrow(360, 150, 600, 20, 112, 38, 0.0)
    a3 = arrow(300, 190, 60, 320, 113, 38, 0.0)
    a4 = arrow(360, 190, 600, 320, 114, 38, 0.0)
    ps = []
    for k, (sh, hd) in enumerate([a1, a2, a3, a4]):
        ps += [(sh, 0, "#FFD400", 14), (hd, 1, "#FFD400", 14)]
    room_scene("bilik3", "b3", "s10", "BILIK 3", VIOLET, "bilik3",
               wrap("b3-x", 130, 470, 660, 340, strokes("b3", 660, 340, ps))
               + stk("b3-luas", "LAGI LUAS!", 300, 600, 52, "lm", 3),
               lambda rel: f"""      draw("#b3-x", {rel(B['luas3']) - 0.15:.3f}, 0.3);
      tl.fromTo("#b3-x .dd", {{ scale: 0.6 }}, {{ scale: 1.05, duration: 0.5, ease: "back.out(2)", transformOrigin: "50% 50%", immediateRender: false }}, {rel(B['luas3']) - 0.15:.3f});
      slap("#b3-luas", {rel(B['luas3']) + 0.05:.3f}, 3);""", 27)
    # dapur: steam squiggles
    st = [jit([(20 + k * 60, 150), (5 + k * 60, 110), (35 + k * 60, 75), (10 + k * 60, 35), (30 + k * 60, 0)], 121 + k, 3) for k in range(3)]
    room_scene("dapur", "dp", "s11", "DAPUR", "#FFD400", "dapur",
               wrap("dp-st", 600, 260, 200, 160, strokes("dp", 200, 160, [(st[0], 0, CYAN, 11), (st[1], 0, CYAN, 11), (st[2], 0, CYAN, 11)])),
               lambda rel: f"""      draw("#dp-st", {rel(B['dapur']) + 0.05:.3f}, 0.3);""", 29)


def scene_loan():
    p = "ln"
    s, d, rel = scene("loan", ["s12", "s13", "s14"])
    css = f"""
.row {{ position:absolute; left:130px; display:flex; align-items:center; gap:18px; }}
.chk {{ position:relative; width:84px; height:84px; }}
#ln-sub {{ position:absolute; left:250px; top:610px; font-family:"Archivo Black"; font-size:36px; color:{INK}; white-space:nowrap;
  background:#FFD400; border:4px solid {INK}; border-radius:12px; padding:8px 16px; box-shadow:5px 6px 0 rgba(20,20,20,0.85); rotate:-2deg; }}
"""
    def row(id_, top, label, kind, rot, seed):
        ck = check(84, 84, seed)
        return (f'<div class="row" id="{id_}" style="top:{top}px">'
                f'<div class="stk {kind}" style="position:relative;font-size:52px;rotate:{rot}deg">{label}</div>'
                f'<div class="chk">' + wrap(id_ + "k", 0, 0, 84, 84, strokes(p, 84, 84, [(check(84, 84, seed), 0, LIME, 15)])) + '</div></div>')
    pin = jit([(60, 150), (18, 70), (22, 30), (60, 6), (98, 30), (102, 70), (60, 150)], 131, 2)
    pin_dot = ring(60, 52, 18, 18, 132, 1.05, 12, 1)
    body = (
        row("ln-r1", 290, "LPPSA", "", -2, 141)
        + row("ln-r2", 410, "LOAN BANK", "cy", 2, 142)
        + row("ln-r3", 530, "BERNIAGA", "pk", -1, 143)
        + '<div id="ln-sub">SSM + statement bank 6 bulan</div>'
        + tag("ln-semid", "SEMI-D", 150, 345, 164, LIME, -5)
        + wrap("ln-pin", 150, 540, 120, 160, strokes(p, 120, 160, [(pin, 0, PINK, 13), (pin_dot, 1, PINK, 11)]))
        + tag("ln-gurun", "GURUN", 280, 520, 140, PINK, -3)
    )
    js = f"""
      gsap.set(["#ln-r1", "#ln-r2", "#ln-r3", "#ln-sub", "#ln-semid", "#ln-gurun", "#ln-pin"], {{ opacity: 0 }});
      slap("#ln-r1", {rel(B['lppsa']):.3f}, 0); draw("#ln-r1k", {rel(B['lppsa_ok']):.3f}, 0.25);
      slap("#ln-r2", {rel(B['bank']):.3f}, 0); draw("#ln-r2k", {rel(B['bank_ok']):.3f}, 0.25);
      slap("#ln-r3", {rel(B['niaga']):.3f}, 0);
      slap("#ln-sub", {rel(B['ssm']):.3f}, -2); draw("#ln-r3k", {rel(B['ssm']) + 0.1:.3f}, 0.25);
      tl.fromTo("#ln-sub", {{ scale: 1 }}, {{ scale: 1.06, duration: 0.18, yoyo: true, repeat: 1, ease: "sine.inOut", immediateRender: false }}, {rel(B['bulan']):.3f});
      tl.to(["#ln-r1", "#ln-r2", "#ln-r3", "#ln-sub"], {{ x: -900, duration: 0.3, ease: "power3.in", stagger: 0.04 }}, {rel(B['memiliki']) - 0.2:.3f});
      spray("#ln-semid", {rel(B['semid']) - 0.06:.3f}, 0.4);
      draw("#ln-pin", {rel(B['gurun']) - 0.2:.3f}, 0.3);
      tl.set("#ln-pin", {{ opacity: 1 }}, {rel(B['gurun']) - 0.2:.3f});
      tl.fromTo("#ln-pin", {{ y: -60 }}, {{ y: 0, duration: 0.5, ease: "bounce.out", immediateRender: false }}, {rel(B['gurun']) - 0.2:.3f});
      spray("#ln-gurun", {rel(B['gurun']) - 0.04:.3f}, 0.3);
      boil("#ln-semid .b, #ln-gurun .b, #ln-pin .b, .chk .b", 1.1, 0.3, 31);
"""
    SCENES.append(("loan", s, d, comp("loan", d, css, body, js, p)))


def scene_cta():
    p = "ct"
    s, d, rel = scene("cta", ["s15"])
    arrs = ""
    for i, x in enumerate([190, 420, 650]):
        sh, hd = arrow(60, 10, 60, 190, 151 + i, 44, 0.08 if i % 2 else -0.08)
        arrs += wrap(f"ct-a{i}", x, 580, 120, 210, strokes(p, 120, 210, [(sh, 0, LIME, 16), (hd, 1, LIME, 16)]))
    body = (
        tag("ct-min", "BERMINAT?", 140, 322, 124, CYAN, -4)
        + stk("ct-btn", "ISI BORANG ↓", 160, 470, 74, "pk", -2)
        + arrs
        + stk("ct-s1", "SEMI-D CLUSTER", 130, 985, 40, "", -3)
        + stk("ct-s2", "4 BILIK · 2 TANDAS", 300, 1060, 40, "cy", 2)
        + stk("ct-s3", "RM281K*", 130, 1140, 46, "lm", -2)
        + stk("ct-s4", "LPPSA / LOAN BANK", 400, 1146, 36, "", 3)
    )
    pulse_n = max(1, int((d - rel(B['isi']) - 0.6) / 0.5))
    bob_n = max(1, int((d - rel(B['bawah']) - 0.4) / 0.4))
    js = f"""
      gsap.set(["#ct-min", "#ct-btn"], {{ opacity: 0 }});
      spray("#ct-min", {rel(B['berminat']) - 0.08:.3f}, 0.4);
      slap("#ct-btn", {rel(B['isi']) - 0.04:.3f}, -2);
      tl.to("#ct-btn", {{ scale: 1.06, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: {pulse_n * 2 - 1} }}, {rel(B['isi']) + 0.5:.3f});
      ["#ct-a0", "#ct-a1", "#ct-a2"].forEach(function (a, i) {{
        draw(a, {rel(B['bawah']) - 0.12:.3f} + i * 0.07, 0.3);
        bob(a, {rel(B['bawah']) + 0.35:.3f} + i * 0.06, {bob_n}, 20, 0.2);
      }});
      // summary stickers take over the caption band once the voice ends
      slap("#ct-s1", {VOICE_END - s + 0.05:.3f}, -3);
      slap("#ct-s2", {VOICE_END - s + 0.20:.3f}, 2);
      slap("#ct-s3", {VOICE_END - s + 0.35:.3f}, -2);
      slap("#ct-s4", {VOICE_END - s + 0.50:.3f}, 3);
      boil("#ct-min .b, #ct-a0 .b, #ct-a1 .b, #ct-a2 .b", 1.2, 0.35, 33);
"""
    SCENES.append(("cta", s, d, comp("cta", d, "", body, js, p)))


def scene_captions():
    p, s = "cp", 0.0
    d = VOICE_END
    css = f"""
.cap {{ position:absolute; left:116px; width:664px; bottom:{H - 1240}px; text-align:center; visibility:hidden; }}
.cs {{ display:inline-block; font-family:"Archivo Black"; font-size:54px; line-height:1.16; color:{INK};
  background:{PAPER}; border:5px solid {INK}; border-radius:18px; padding:10px 22px 14px; box-shadow:7px 8px 0 rgba(20,20,20,0.85); }}
.w {{ display:inline-block; position:relative; margin:0 1px; padding:0 6px; border-radius:8px; }}
.w.k {{ color:{PINK}; }}
"""
    body, js = "", ""
    for ci, (seg, words, end_src) in enumerate(CAPS):
        t0 = o(seg, words[0][1])
        t1 = o(seg, end_src)
        nxt = CAPS[ci + 1] if ci + 1 < len(CAPS) else None
        if nxt:
            t1 = min(t1, o(nxt[0], nxt[1][0][1]) - 0.035)
        if seg == "s15" and nxt is None:
            t1 = VOICE_END
        spans = ""
        for wi, w in enumerate(words):
            k = len(w) > 2 and w[2]
            spans += (" " if wi else "") + f'<span class="w{" k" if k else ""}" id="cp{ci}w{wi}">{w[0]}</span>'
        rot = [-2, 1.5, -1, 2][ci % 4]
        body += f'<div class="cap" id="cp{ci}"><div class="cs" id="cp{ci}s" style="rotate:{rot}deg">{spans}</div></div>\n'
        js += f'      tl.set("#cp{ci}", {{ visibility: "visible" }}, {max(0, t0 - 0.03):.3f}); tl.set("#cp{ci}", {{ visibility: "hidden" }}, {t1:.3f});\n'
        js += (f'      tl.fromTo("#cp{ci}s", {{ scale: 1.25, rotation: {rot + 5} }}, {{ scale: 1, rotation: {rot}, duration: 0.26, '
               f'ease: "back.out(2.4)", immediateRender: false }}, {max(0, t0 - 0.03):.3f});\n')
        for wi, w in enumerate(words):
            wt = max(t0, o(seg, w[1]))
            we = max(t0, o(seg, words[wi + 1][1])) if wi + 1 < len(words) else t1
            # active word: lime marker swipe behind it while it is spoken
            js += (f'      tl.set("#cp{ci}w{wi}", {{ backgroundColor: "{LIME}" }}, {max(0, wt - 0.04):.3f}); '
                   f'tl.set("#cp{ci}w{wi}", {{ backgroundColor: "rgba(0,0,0,0)" }}, {max(0, we - 0.04):.3f});\n')
            js += (f'      tl.fromTo("#cp{ci}w{wi}", {{ scale: 1.14 }}, '
                   f'{{ scale: 1, duration: 0.18, ease: "power2.out", immediateRender: false }}, {max(0, wt - 0.04):.3f});\n')
    SCENES.append(("captions", s, d, comp("captions", d, css, body, js, p)))


def wipe_comp():
    p = "sw"
    d = 0.62
    paths = [(jit([(-200, 1500), (300, 1150), (700, 760), (1300, 300)], 81, 30), 0, PINK, 420),
             (jit([(-200, 2150), (400, 1600), (800, 1150), (1300, 800)], 82, 30), 0, LIME, 440),
             (jit([(-200, 950), (300, 600), (700, 250), (1300, -250)], 83, 30), 0, CYAN, 420),
             (jit([(-200, 2600), (500, 2050), (900, 1650), (1300, 1350)], 84, 30), 0, "#FFD400", 400)]
    body = wrap("sw-s", 0, 0, W, H, strokes(p, W, H, paths))
    js = """
      var ps = gsap.utils.toArray("#sw-s .sp");
      ps.forEach(function (p, i) {
        var len = p.getTotalLength() + 4;
        gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len });
        tl.to(p, { strokeDashoffset: 0, duration: 0.26, ease: "power2.in" }, i * 0.03);
      });
      tl.to("#sw-s", { opacity: 0, scale: 1.12, duration: 0.24, ease: "power2.out" }, 0.36);
"""
    return d, comp("wipe", d, "", body, js, p)


# ================================================================ index.html
def build():
    scene_hook(); scene_lawa(); scene_specs(); scene_tepi(); scene_tamu(); scene_master(); scene_rooms()
    scene_loan(); scene_cta(); scene_captions()
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    for cid, s, d, html in SCENES:
        with open(os.path.join(ROOT, "compositions", f"{cid}.html"), "w") as f:
            f.write(html)
    sw_d, sw_html = wipe_comp()
    with open(os.path.join(ROOT, "compositions", "wipe.html"), "w") as f:
        f.write(sw_html)

    vids, auds, comps = [], [], []
    vi = 0
    chain = json.dumps({"version": 1, "nodes": [
        {"type": "highpass", "id": "vo1", "label": "Remove rumble", "params": {"frequency": 85}},
        {"type": "peaking", "id": "vo2", "label": "Presence", "params": {"frequency": 3200, "gain": 2, "q": 1}},
        {"type": "limiter", "id": "vo3", "params": {"limit": -1}}]}).replace('"', "&quot;")
    for sg in EDL:
        extra = sg.get("extra", 0)
        if sg.get("pics"):
            pics, acc = [], 0.0
            for src, dd in sg["pics"]:
                pics.append((round(sg["start"] + acc, 3), round(dd, 3), src))
                acc += dd
        else:
            pics = []
            for (a0, a1), off in zip(sg["parts"], sg["offs"]):
                pics.append((round(sg["start"] + off, 3), round(a1 - a0, 3), a0))
            if extra:
                st_, dd, src = pics[-1]
                pics[-1] = (st_, round(dd + extra, 3), src)
        for st_, dd, src in pics:
            vi += 1
            vids.append(f'        <video id="v{vi}" class="clip" src="assets/footage.mp4" muted playsinline data-start="{st_}" '
                        f'data-duration="{dd}" data-media-start="{src}" data-track-index="0"></video>')
        for k, ((a0, a1), off) in enumerate(zip(sg["parts"], sg["offs"])):
            auds.append(f'      <audio id="vo-{sg["id"]}-{k}" src="assets/voice.wav" data-start="{round(sg["start"] + off, 3)}" '
                        f'data-duration="{round(a1 - a0, 3)}" data-media-start="{a0}" data-volume="1.0" data-fade-in="0.012" '
                        f'data-fade-out="0.02" data-fx-chain="{chain}" data-track-index="10"></audio>')
    lanes = {"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0.32}, {"t": 0.35, "v": 0.2}, {"t": VOICE_END, "v": 0.2},
        {"t": VOICE_END + 0.35, "v": 0.5}, {"t": TOTAL - 0.8, "v": 0.5}, {"t": TOTAL, "v": 0.0}]}]}
    mfx = {"version": 1, "nodes": [
        {"type": "peaking", "id": "mu1", "label": "Make room for the voice", "params": {"frequency": 2500, "gain": -5, "q": 0.8}},
        {"type": "peaking", "id": "mu2", "label": "Clear low mids", "params": {"frequency": 300, "gain": -3, "q": 1}}]}
    auds.append(f'      <audio id="music" src="assets/music/bed-boombap.mp3" data-start="0" data-duration="{TOTAL}" '
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
        lane = next(l for l in range(20, 60) if lane_end.get(l, -1) <= e["at"])
        lane_end[lane] = e["at"] + dd
        auds.append(f'      <audio id="fx{i:02d}" src="assets/sfx/{e["name"]}.mp3" data-start="{e["at"]}" data-duration="{dd:.3f}"{ms} '
                    f'data-volume="{e["vol"]}"{fo} data-track-index="{lane}"></audio>')
    for cid, s, d, _ in SCENES:
        z, tr, kind = (6, 3, "captions") if cid == "captions" else (5, 2, "graphics")
        comps.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s:.3f}" '
                     f'data-duration="{d:.3f}" data-width="{W}" data-height="{H}" data-track-index="{tr}" data-track-kind="{kind}" style="z-index:{z}"></div>')
    for i, at in enumerate(WIPES):
        comps.append(f'      <div id="wipe-{i + 1}" data-composition-id="wipe" data-composition-src="compositions/wipe.html" '
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
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #141414; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 42%; z-index: 1; }}
      #cam video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #vign {{ position: absolute; inset: 0; z-index: 2; pointer-events: none;
        background: linear-gradient(180deg, rgba(10,10,10,0.30) 0%, rgba(10,10,10,0) 24%, rgba(10,10,10,0) 55%, rgba(10,10,10,0.28) 100%); }}
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
      gsap.set("#cam", {{ scale: 1, rotation: 0 }});
      {cam_js()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(html)
    print(f"voice {VOICE_END}s, total {TOTAL}s")
    print("segments:", {k: v for k, v in ST.items()})


if __name__ == "__main__":
    build()
