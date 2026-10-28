"""Generate the "Headline Storm" Laporan Terkini HyperFrames project (index.html + compositions/*.html).

Edit cuts, copy and timings here, then re-run:  python3 build.py
Output is plain HyperFrames HTML that Studio can still edit.

Look: a storm of tabloid news headlines in the top band above the presenter's head.
White bars with a hard red drop shadow, red and yellow accent bars, each one slamming in
on its spoken word (scale 1.6 -> 1, expo.out) with a three-frame stack shake, a breaking
news ticker along the top, red "BERITA HARTANAH" gust strips between scenes, and every
stack whipping upward on exit. Mechanics follow the registry's headline-slam and
lower-third-bild items.
"""
import json, os

P = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FOOTAGE = os.environ.get("FOOTAGE", "assets/footage.mp4")
LOCATION = os.environ.get("LOCATION", "TAMAN SERI PAGI FASA 2")

# ------------------------------------------------------------------ edit (source seconds)
CUTS = [
    (0.42, 7.70),    # Laporan terkini, jerebu sudah hilang. Penonton-penonton dinasihati ... dengan kadar yang segera.
    (7.90, 11.76),   # Jangan jadi seperti si dia yang datang tapi hilang.
    (11.98, 13.50),  # Rumah ini tidak hilang.
    (13.68, 15.56),  # Rumah ini ada geran, ada kunci.
    (15.74, 18.68),  # Jadi, yang mana berminat tekan link di bio,
    (18.86, 21.35),  # Taman Seri Pagi Fasa 2, Alor Setar.
]
HOLD = 1.3
starts, t = [], 0.0
for a, b in CUTS:
    starts.append(round(t, 3))
    t += b - a
SPEECH_END = round(t, 3)
TOTAL = round(SPEECH_END + HOLD, 2)


def out(src):
    """source second -> output second."""
    for (a, b), s in zip(CUTS, starts):
        if a - 0.05 <= src <= b + 0.05:
            return round(s + (src - a), 3)
    raise ValueError(src)


S_HOOK = (0.0, 3.0)
S_NAS = (3.0, round(starts[1] + 0.68, 3))   # "SEGERA!" holds into "Jangan jadi"
S_AMR = (S_NAS[1], starts[2])
S_RMH = (starts[2], round(starts[4] + 0.6, 3))   # holds through "Jadi," so the checklist reads
S_CTA = (S_RMH[1], TOTAL)

RED, YEL, INKD = "#DD0000", "#FFD400", "#14161A"
SCALE = float(os.environ.get("SCALE", "0.85"))   # overall size of the headline cluster
SHRINK = f'<div class="shrink" style="position:absolute;inset:0;transform:scale({SCALE});transform-origin:540px 178px">'
X0 = 90            # left edge of every stack: clear of the right-hand action rail
FR = 1 / 60        # one frame at 60 fps

CSS = f"""
    #root {{ position: absolute; inset: 0; pointer-events: none; overflow: hidden; }}
    .stage {{ position: absolute; inset: 0; }}
    .hb {{ position: absolute; font-family: 'Oswald', sans-serif; font-weight: 700; text-transform: uppercase;
      white-space: nowrap; line-height: 1.04; letter-spacing: 0.015em; padding: 8px 24px 6px; }}
    .hb-w {{ color: {INKD}; background: #FFFFFF; box-shadow: 12px 12px 0 0 {RED}; }}
    .hb-r {{ color: #FFFFFF; background: {RED}; box-shadow: 9px 9px 0 0 {INKD}; }}
    .hb-y {{ color: {INKD}; background: {YEL}; box-shadow: 12px 12px 0 0 {INKD}; }}
    .hb-k {{ color: #FFFFFF; background: {INKD}; box-shadow: 9px 9px 0 0 {RED}; }}
"""


def bar(eid, kind, x, y, size, text):
    return f'      <div id="{eid}" class="hb hb-{kind}" style="left:{x}px;top:{y}px;font-size:{size}px">{text}</div>'


class Scene:
    def __init__(self, cid, win):
        self.cid, self.win, self.dur = cid, win, round(win[1] - win[0], 3)
        self.bars, self.s, self.ids = [], [], []

    def add(self, eid, kind, x, y, size, text, at=None, rot=0.0, shake=1.0):
        """A headline bar. at=None: already landed at scene start (frame-0 thumbnail)."""
        self.bars.append(bar(eid, kind, x, y, size, text))
        self.ids.append(eid)
        if at is None:
            self.s.append(f'tl.set("#{eid}", {{ rotation: {rot}, transformOrigin: "0% 50%" }}, 0);')
            return
        at = max(0.0, at)
        self.s.append(f'tl.fromTo("#{eid}", {{ scale: 1.6, opacity: 0, rotation: {rot * 3:.2f}, transformOrigin: "30% 50%" }}, '
                      f'{{ scale: 1, rotation: {rot}, duration: 0.3, ease: "expo.out" }}, {at:.3f});')
        self.s.append(f'tl.to("#{eid}", {{ opacity: 1, duration: 0.05, ease: "none" }}, {at:.3f});')
        land = at + 0.2
        k = shake
        for i, (dx, dy) in enumerate([(9 * k, -5 * k), (-6 * k, 4 * k), (0, 0)]):
            self.s.append(f'tl.to("#{self.cid}-stage", {{ x: {dx:.1f}, y: {dy:.1f}, duration: {2 * FR:.4f}, ease: "power2.out" }}, {land + i * 2 * FR:.4f});')

    def rip(self, eid, at):
        """The bar is torn off upward (the 'hilang' gag)."""
        self.ids.remove(eid)
        self.s.append(f'tl.to("#{eid}", {{ y: -520, rotation: -24, opacity: 0, duration: 0.32, ease: "power4.in" }}, {at:.3f});')

    def exit(self, whip=True):
        if not whip:
            return
        t0 = self.dur - 0.36
        for i, eid in enumerate(reversed(self.ids)):
            self.s.append(f'tl.to("#{eid}", {{ x: -1300, duration: 0.3, ease: "power4.in" }}, {t0 + i * 0.03:.3f});')

    def html(self, extra_body="", extra_script=()):
        script = self.s + list(extra_script)
        return f'''<template>
  <style>{CSS}
  </style>
  <div id="root" data-composition-id="{self.cid}" data-width="{W}" data-height="{H}">
    {SHRINK}
    <div id="{self.cid}-stage" class="stage" data-layout-allow-overlap data-layout-allow-overflow>
{chr(10).join(self.bars)}
{extra_body}
    </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join("      " + l for l in script)}
      window.__timelines["{self.cid}"] = tl;
    }})();
  </script>
</template>
'''


def L(src, s0):
    return out(src) - s0


# ------------------------------------------------------------------ 1. HOOK (frame 0 = thumbnail: headline already up)
hk = Scene("hook", S_HOOK)
hk.add("hk-tag", "r", X0, 262, 44, "EKSKLUSIF", None, -1.5)
hk.add("hk-1", "w", X0, 344, 104, "LAPORAN TERKINI", None, 0)
hk.add("hk-2", "k", X0, 500, 60, "JEREBU", L(1.53, 0) - 0.04, 1.5, 0.6)
hk.add("hk-3", "y", X0, 590, 100, "SUDAH HILANG!", L(2.10, 0) - 0.04, -2.5, 1.2)
hk.exit()

# ------------------------------------------------------------------ 2. NASIHAT
N0 = S_NAS[0]
ns = Scene("nasihat", S_NAS)
ns.add("ns-tag", "r", X0, 262, 44, "NASIHAT KEPADA PENONTON", 0.05, -1.5, 0.5)
ns.add("ns-1", "w", X0, 344, 104, "BELI RUMAH INI", L(5.20, N0), 1.0, 1.0)
ns.add("ns-2", "k", X0, 500, 54, "KADAR?", L(6.68, N0) - 0.06, -1.0, 0.5)
ns.add("ns-3", "y", X0 + 250, 486, 150, "SEGERA!", L(7.28, N0) - 0.08, 3.0, 2.0)
ns.exit()

# ------------------------------------------------------------------ 3. AMARAN (the "hilang" bar is torn away)
A0 = S_AMR[0]
am = Scene("amaran", S_AMR)
am.add("am-tag", "r", X0, 262, 44, "AMARAN!", None, -2.0)
am.add("am-1", "w", X0, 344, 90, "JANGAN JADI SI DIA", 0.08, 1.0, 1.0)
am.add("am-2", "k", X0, 492, 76, "DATANG...", L(10.38, A0) - 0.04, -1.5, 0.8)
am.add("am-3", "y", X0 + 380, 492, 76, "TAPI HILANG", L(10.90, A0) - 0.04, 2.0, 1.0)
am.rip("am-3", L(11.40, A0))
am.exit()

# ------------------------------------------------------------------ 4. RUMAH INI
R0 = S_RMH[0]
rm = Scene("rumah", S_RMH)
rm.add("rm-tag", "r", X0, 262, 44, "STATUS RUMAH", 0.05, -1.5, 0.5)
rm.add("rm-1", "w", X0, 344, 110, "RUMAH INI", 0.30, -1.0, 1.0)
rm.add("rm-2", "r", X0, 506, 66, "TIDAK HILANG ✓", L(12.56, R0) - 0.04, 1.5, 0.8)
rm.add("rm-3", "w", X0, 618, 66, "✓ ADA GERAN", L(14.56, R0) - 0.08, -2.0, 1.0)
rm.add("rm-4", "y", X0 + 468, 618, 66, "✓ ADA KUNCI", L(15.39, R0) - 0.1, 2.0, 1.2)
rm.exit()

# ------------------------------------------------------------------ 5. CTA (headline + the real profile screenshot)
C0 = S_CTA[0]
ct = Scene("cta", S_CTA)
t_tekan = L(17.67, C0)
ct.add("ct-q", "r", X0, 262, 56, "YANG MANA BERMINAT?", 0.05, -1.5, 0.6)
ct.rip("ct-q", t_tekan - 0.2)
ct.add("ct-1", "w", X0, 262, 88, "TEKAN LINK DI BIO ▸", t_tekan - 0.04, -1.0, 1.4)
ct.add("ct-loc", "r", X0, 398, 40, f"{LOCATION} · ALOR SETAR", L(19.24, C0) - 0.04, 1.0, 0.6)
CW = 600
CX = (W - CW) // 2 + 20
SC = CW / 1206
IMG_H = round(822 * SC)
IMG_Y = 480
lk_x0, lk_x1, lk_y0, lk_y1 = 30, 780, 664, 720       # the link line in the screenshot (source px)
HX, HY = CX + round(lk_x0 * SC), IMG_Y + round(lk_y0 * SC)
HW, HH = round((lk_x1 - lk_x0) * SC), round((lk_y1 - lk_y0) * SC)
card = f'''      <div id="ct-card" style="position:absolute;left:{CX}px;top:{IMG_Y}px;width:{CW + 16}px;height:{IMG_H + 16}px;background:#FFFFFF;padding:8px;box-shadow:14px 14px 0 0 {RED}">
        <img id="ct-shot" src="assets/cta-profile.jpg" alt="Profil TikTok NAZProperty" style="display:block;width:{CW}px;height:{IMG_H}px" />
      </div>
      <div id="ct-hl" style="position:absolute;left:{HX - 2}px;top:{HY + 2}px;width:{HW + 16}px;height:{HH + 12}px;border:5px solid {YEL};box-shadow:0 0 0 3px {RED};opacity:0"></div>'''
ct_extra = [
    f'tl.fromTo("#ct-card", {{ scale: 1.5, opacity: 0, rotation: -6, transformOrigin: "50% 50%" }}, {{ scale: 1, rotation: -1.5, duration: 0.34, ease: "expo.out" }}, 0.3);',
    'tl.to("#ct-card", { opacity: 1, duration: 0.05, ease: "none" }, 0.3);',
    f'tl.set("#ct-hl", {{ rotation: -1.5, transformOrigin: "{CX + (CW + 16) / 2 - HX + 2:.0f}px {IMG_Y + (IMG_H + 16) / 2 - HY - 2:.0f}px" }}, 0);',
    f'tl.fromTo("#ct-hl", {{ opacity: 0, scale: 1.25 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.4)" }}, {L(18.09, C0):.3f});',
    f'tl.fromTo("#ct-hl", {{ borderColor: "{YEL}" }}, {{ borderColor: "#FFFFFF", duration: 0.2, ease: "none", yoyo: true, repeat: 9 }}, {L(18.09, C0) + 0.3:.3f});',
]
for i, (dx, dy) in enumerate([(10, -6), (-7, 4), (0, 0)]):
    ct_extra.append(f'tl.to("#cta-stage", {{ x: {dx}, y: {dy}, duration: {2 * FR:.4f}, ease: "power2.out" }}, {0.5 + i * 2 * FR:.4f});')

# ------------------------------------------------------------------ 0. TICKER + gust strips (whole film)
TICK = "JEREBU SUDAH HILANG  ◆  RUMAH ADA GERAN  ◆  ADA KUNCI  ◆  TEKAN LINK DI BIO  ◆  ALOR SETAR  ◆  "
GUSTS = [S_NAS[0], S_AMR[0], S_RMH[0], S_CTA[0]]
tk_body = f'''    <div id="tk" class="stage">
      <div id="tk-strip" style="position:absolute;left:{X0 + 236}px;top:178px;width:{W - 2 * X0 - 236}px;height:56px;background:#FFFFFF;overflow:hidden;box-shadow:8px 8px 0 0 {INKD}" data-layout-allow-overflow>
        <div id="tk-text" style="position:absolute;left:18px;top:4px;font-family:'Oswald',sans-serif;font-weight:700;font-size:34px;line-height:48px;color:{INKD};white-space:nowrap" data-layout-ignore>{TICK * 4}</div>
      </div>
      <div id="tk-tag" class="hb hb-r" style="left:{X0}px;top:178px;font-size:34px;line-height:40px;box-shadow:8px 8px 0 0 {INKD}">BERITA TERKINI</div>
''' + "\n".join(
    f'''      <div id="gust-{i}" style="position:absolute;left:0;top:{300 + (i % 2) * 150}px;width:1700px;height:120px;background:{RED};opacity:0;
        font-family:'Oswald',sans-serif;font-weight:700;font-size:72px;line-height:120px;color:#FFFFFF;white-space:nowrap;box-shadow:0 14px 0 0 {INKD}" data-layout-ignore>BERITA HARTANAH ◆ BERITA HARTANAH ◆ BERITA HARTANAH</div>'''
    for i in range(len(GUSTS))) + "\n    </div>"
tk_s = [
    'tl.fromTo("#tk-text", { x: 0 }, { x: -' + str(int(TOTAL * 80)) + f', duration: {TOTAL}, ease: "none" }}, 0);',
    'tl.fromTo("#tk-tag", { opacity: 1 }, { opacity: 0.55, duration: 0.4, ease: "steps(1)", yoyo: true, repeat: 3 }, 0.2);',
]
for i, g in enumerate(GUSTS):
    a = g - 0.2
    tk_s.append(f'tl.fromTo("#gust-{i}", {{ x: 1450, rotation: -7, opacity: 1 }}, {{ x: -1800, opacity: 1, duration: 0.42, ease: "power2.inOut" }}, {a:.3f});')
    tk_s.append(f'tl.set("#gust-{i}", {{ opacity: 0 }}, {a + 0.43:.3f});')
tk_html = f'''<template>
  <style>{CSS}
  </style>
  <div id="root" data-composition-id="ticker" data-width="{W}" data-height="{H}">
    {SHRINK}
{tk_body}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join("      " + l for l in tk_s)}
      window.__timelines["ticker"] = tl;
    }})();
  </script>
</template>
'''

# ------------------------------------------------------------------ write scenes
os.makedirs(os.path.join(P, "compositions"), exist_ok=True)
files = {
    "hook": hk.html(), "nasihat": ns.html(), "amaran": am.html(), "rumah": rm.html(),
    "cta": ct.html(card, ct_extra), "ticker": tk_html,
}
for cid, html in files.items():
    with open(os.path.join(P, "compositions", f"{cid}.html"), "w") as f:
        f.write(html)

HOSTS = [("hook", S_HOOK, 3), ("nasihat", S_NAS, 4), ("amaran", S_AMR, 3), ("rumah", S_RMH, 4), ("cta", S_CTA, 3),
         ("ticker", (0.0, TOTAL), 9)]

# ------------------------------------------------------------------ root
FX = json.dumps({"version": 1, "nodes": [
    {"type": "highpass", "id": "v1", "label": "Remove rumble", "params": {"frequency": 90}},
    {"type": "limiter", "id": "v2", "label": "Safety limiter", "params": {"limit": -1}}]}).replace('"', "&quot;")

names = ["laporan", "jangan", "tidak-hilang", "geran-kunci", "link-bio", "lokasi"]
vids = []
for i, ((a, b), s) in enumerate(zip(CUTS, starts)):
    vids.append(f'''        <video id="v-{names[i]}" class="clip" src="{FOOTAGE}" playsinline data-has-audio="true"
          data-start="{s}" data-duration="{round(b - a, 3)}" data-media-start="{a}" data-track-index="{i % 2}"
          data-fade-in="0.02" data-fade-out="0.03" data-volume="1.35" data-fx-chain="{FX}"
          style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover"></video>''')
vids.append(f'''        <img id="v-hold" class="clip" src="assets/last-frame.jpg" alt="" data-start="{SPEECH_END}" data-duration="{round(TOTAL - SPEECH_END, 3)}" data-track-index="2"
          style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover" />''')

hosts = []
for z, (cid, (a, b), tr) in enumerate(HOSTS):
    hosts.append(f'''      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="{tr}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index:{20 + z}"></div>''')


def sfx(id_, f, s, d, v, tr):
    return (f'      <audio id="{id_}" class="clip" src="assets/sfx/{f}" data-start="{max(0, s):.3f}" data-duration="{d}" '
            f'data-track-index="{tr}" data-volume="{v}" data-fade-out="0.12"></audio>')


slam = lambda i, src, v=0.2: sfx(f"sfx-slam-{i}", "impact-bass-1.mp3" if i % 2 else "impact-bass-2.mp3", out(src) + 0.1, 0.6, v, 6 + i % 2)
audio = [
    slam(1, 2.10, 0.24),
    sfx("sfx-gust-1", "whoosh.mp3", S_NAS[0] - 0.22, 0.5, 0.2, 8),
    slam(2, 5.20, 0.18),
    slam(3, 7.28, 0.32),
    sfx("sfx-gust-2", "whoosh.mp3", S_AMR[0] - 0.22, 0.5, 0.2, 8),
    slam(4, 10.90, 0.16),
    sfx("sfx-rip", "whoosh-short.mp3", out(11.40), 0.5, 0.22, 8),
    sfx("sfx-gust-3", "whoosh.mp3", S_RMH[0] - 0.22, 0.5, 0.2, 9),
    sfx("sfx-tick-1", "pop.mp3", out(14.56) - 0.06, 0.5, 0.24, 8),
    sfx("sfx-tick-2", "pop.mp3", out(15.39) - 0.08, 0.5, 0.24, 9),
    sfx("sfx-gust-4", "whoosh-cinematic.mp3", S_CTA[0] - 0.22, 1.0, 0.14, 8),
    slam(5, 17.67, 0.22),
    sfx("sfx-link", "chime.mp3", out(18.09), 1.2, 0.18, 9),
    sfx("sfx-lokasi", "ping.mp3", out(19.24), 0.8, 0.16, 8),
]

bgm = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.16}, {"t": SPEECH_END - 0.2, "v": 0.16}, {"t": SPEECH_END + 0.3, "v": 0.5}]}]}).replace('"', "&quot;")

cam = [f'      tl.set("#cam-move", {{ scale: {1.0 if i % 2 == 0 else 1.06} }}, {s});' for i, s in enumerate(starts)]

index = f'''<!doctype html>
<html lang="ms" data-resolution="portrait">
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
{chr(10).join(vids)}
        </div>
      </div>
{chr(10).join(hosts)}
      <audio id="bgm" class="clip" src="assets/bgm/reminder.m4a" data-start="0" data-duration="{TOTAL}" data-track-index="5"
        data-volume="1" data-fade-out="0.9" data-automation="{bgm}"></audio>
{chr(10).join(audio)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // jump cuts: alternate a small punch-in so each cut reads as intentional
      tl.set("#cam-move", {{ transformOrigin: "50% 60%" }}, 0);
{chr(10).join(cam)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
with open(os.path.join(P, "index.html"), "w") as f:
    f.write(index)
print("total", TOTAL, "scenes", S_HOOK, S_NAS, S_AMR, S_RMH, S_CTA, "card", IMG_Y, IMG_Y + IMG_H + 16)
