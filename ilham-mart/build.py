"""Generate the Ilham Mart shoplot HyperFrames project (index.html + compositions/*.html).

Edit cuts, board copy and timings here, then re-run:  python3 build.py
Output is plain HyperFrames HTML that Studio can still edit.

Look: Solari split-flap boards (charcoal tiles, warm-white glyphs, signal-yellow accent row).
The flap mechanics follow the registry block `split-flap-board` (two leaves, theta = 180 p^2).
"""
import json, os

P = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920

# ------------------------------------------------------------------ edit (source seconds)
CUTS = [
    (0.80, 2.76),    # orang Alor Setar yang mana nak cari shoplot
    (3.10, 7.90),    # tiga tingkat untuk dijual, satu dua tiga, tingkat atas ni owner buat sewa bilik
    (8.50, 9.14),    # berdekatan dengan
    (10.02, 10.82),  # Alor Setar Mall
    (11.96, 13.72),  # kawasan perindustrian Tandop
    (14.42, 15.22),  # so yang ni
    (17.00, 17.76),  # bangunan
    (18.42, 19.48),  # Desa Seraya
    (20.50, 23.12),  # yang mana nak tahu detail, isi sahaja
    (23.66, 27.72),  # ... dekat bawah ni, ataupun boleh isi link di bio, bye bye jumpa lagi
]
HOLD = 1.24
starts = []
t = 0.0
for a, b in CUTS:
    starts.append(round(t, 3))
    t += b - a
SPEECH_END = round(t, 3)
TOTAL = round(SPEECH_END + HOLD, 2)

# scene windows (output seconds)
S_HOOK = (0.0, starts[2])
S_LOK = (starts[2], starts[5])
S_BGN = (starts[5], starts[8])
S_CTA = (starts[8], TOTAL)

INK = "#F4EFE2"
YEL = "#FFC21A"

ENGINE = r"""
    // Split-flap engine. paint(t) is a pure function of scene time: every cell is rebuilt from t
    // alone, so seeking to any frame gives the same board.
    function SplitFlap(rootSel, rows, opts) {
      var AL = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?:-'";
      var N = AL.length, FD = opts.flip || 0.055, ST = opts.stagger || 0.024, DEG = Math.PI / 180;
      var host = document.querySelector(rootSel);
      var cells = [];
      rows.forEach(function (row, r) {
        var el = host.querySelector("#" + row.id);
        // per key: the first cell that changes, so a lone flipping digit is not delayed by the stagger
        var pad = function (s) { return (s.toUpperCase() + " ".repeat(row.n)).slice(0, row.n); };
        var first = [], last = " ".repeat(row.n);
        row.keys.forEach(function (k) {
          var txt = pad(k[1]), f = 0;
          while (f < row.n && txt.charAt(f) === last.charAt(f)) f++;
          first.push(f); last = txt;
        });
        el.style.gap = row.gap + "px";
        for (var c = 0; c < row.n; c++) {
          var cell = document.createElement("div");
          cell.className = "sf-cell" + (row.yellow ? " sf-y" : "");
          cell.style.width = row.w + "px"; cell.style.height = row.h + "px";
          cell.setAttribute("data-layout-allow-overlap", "");
          cell.setAttribute("data-layout-allow-occlusion", "");
          cell.setAttribute("data-layout-allow-overflow", "");
          function face(cls, top) {
            var f = document.createElement("div"); f.className = "sf-face " + cls;
            f.setAttribute("data-layout-allow-occlusion", "");
            var g = document.createElement("span"); g.className = "sf-glyph";
            // single flap glyphs are mechanism, not reading lines: exempt from the read-time audit
            g.setAttribute("data-layout-ignore", "");
            g.style.height = row.h + "px"; g.style.lineHeight = row.h + "px";
            g.style.fontSize = row.fs + "px"; g.style.top = top + "px";
            f.appendChild(g); cell.appendChild(f); return f;
          }
          var top = face("sf-top", 0), bot = face("sf-bot", -Math.round(row.h / 2));
          var la = face("sf-leaf-a", 0), lb = face("sf-leaf-b", -Math.round(row.h / 2));
          var seam = document.createElement("div"); seam.className = "sf-seam"; cell.appendChild(seam);
          el.appendChild(cell);
          // keyframes -> transitions for this cell
          var prev = " ", tr = [];
          row.keys.forEach(function (k, ki) {
            var ch = (k[1].toUpperCase() + " ".repeat(row.n)).charAt(c);
            if (AL.indexOf(ch) < 0) ch = " ";
            if (k[0] <= 0) { prev = ch; return; }
            if (ch === prev) return;
            var ti = AL.indexOf(ch), pi = AL.indexOf(prev), d = (ti - pi + N) % N, seq = [prev];
            if (d <= 6) {
              // short hop: walk the drum forward through the real neighbours (1 -> 2 -> 3)
              for (var j = 1; j <= d; j++) seq.push(AL.charAt((pi + j) % N));
            } else {
              var n = 3 + ((c * 5 + ki * 3 + r) % 4);
              for (var j = n - 1; j >= 1; j--) seq.push(AL.charAt((ti - j + N * 4) % N));
              seq.push(ch);
            }
            tr.push({ t0: k[0] + (c - first[ki]) * ST, seq: seq });
            prev = ch;
          });
          cells.push({ init: row.keys[0][0] <= 0 ? (row.keys[0][1].toUpperCase() + " ".repeat(row.n)).charAt(c) : " ",
            tr: tr, top: top.firstChild, bot: bot.firstChild, la: la, lb: lb });
        }
      });
      function clear(l) { l.style.opacity = "0"; l.style.transform = ""; l.style.filter = ""; l.firstChild.textContent = ""; }
      function show(l, ch, ang, sh) { l.firstChild.textContent = ch; l.style.opacity = "1"; l.style.transform = "rotateX(" + ang.toFixed(2) + "deg)"; l.style.filter = "brightness(" + sh + ")"; }
      function paint(t) {
        for (var i = 0; i < cells.length; i++) {
          var c = cells[i], cur = c.init, act = null;
          for (var k = 0; k < c.tr.length; k++) {
            var x = c.tr[k];
            if (t < x.t0) break;
            var steps = x.seq.length - 1, raw = (t - x.t0) / FD;
            if (raw >= steps) { cur = x.seq[steps]; continue; }
            act = { x: x, n: Math.floor(raw), p: raw - Math.floor(raw) }; break;
          }
          if (!act || act.p <= 0) {
            var ch = act ? act.x.seq[act.n] : cur;
            c.top.textContent = ch; c.bot.textContent = ch; clear(c.la); clear(c.lb); continue;
          }
          var out = act.x.seq[act.n], inc = act.x.seq[act.n + 1];
          c.top.textContent = inc; c.bot.textContent = out;
          var th = 180 * act.p * act.p, sh = (1 - 0.5 * Math.sin(th * DEG)).toFixed(3);
          if (th < 90) { show(c.la, out, -th, sh); clear(c.lb); } else { clear(c.la); show(c.lb, inc, 180 - th, sh); }
        }
      }
      var time = 0, drv = {};
      Object.defineProperty(drv, "t", { get: function () { return time; }, set: function (v) { time = v; paint(v); } });
      paint(0);
      return drv;
    }
"""

COMMON_CSS = f"""
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .house {{
      position: absolute; border-radius: 18px;
      background: linear-gradient(180deg, rgba(22,23,26,0.94) 0%, rgba(12,12,14,0.94) 100%);
      box-shadow: 0 22px 44px rgba(0,0,0,0.5), inset 0 0 0 1.5px rgba(255,255,255,0.07);
    }}
    .hdr {{ position: absolute; height: 34px; display: flex; align-items: center; justify-content: space-between;
      font-family: 'Space Mono', monospace; font-weight: 700; font-size: 28px; letter-spacing: 0.14em; color: {INK}; }}
    .hdr .tag {{ display: flex; align-items: center; gap: 14px; }}
    .hdr .dot {{ width: 16px; height: 16px; background: {YEL}; border-radius: 3px; }}
    .hdr .num {{ color: {YEL}; }}
    .sfrow {{ position: absolute; display: flex; }}
    .sf-cell {{ position: relative; flex: 0 0 auto; perspective: 700px; border-radius: 7px; background: #0b0b0d;
      box-shadow: 0 6px 12px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.05); }}
    .sf-face {{ position: absolute; left: 0; width: 100%; height: 50%; overflow: hidden;
      background: linear-gradient(180deg, #2a2b30 0%, #1c1d21 100%); }}
    .sf-top, .sf-leaf-a {{ top: 0; border-radius: 7px 7px 0 0; }}
    .sf-bot, .sf-leaf-b {{ top: 50%; border-radius: 0 0 7px 7px; background: linear-gradient(180deg, #1a1b1f 0%, #25262b 100%); }}
    .sf-leaf-a {{ transform-origin: 50% 100%; z-index: 3; backface-visibility: hidden; }}
    .sf-leaf-b {{ transform-origin: 50% 0%; z-index: 3; backface-visibility: hidden; }}
    .sf-y .sf-face {{ background: linear-gradient(180deg, #FFCB33 0%, #F2B705 100%); }}
    .sf-y .sf-bot, .sf-y .sf-leaf-b {{ background: linear-gradient(180deg, #E9AE00 0%, #FFC21A 100%); }}
    .sf-glyph {{ position: absolute; left: 0; width: 100%; display: block; text-align: center;
      font-family: 'Oswald', sans-serif; font-weight: 700; color: {INK}; white-space: pre; }}
    .sf-y .sf-glyph {{ color: #131313; }}
    .sf-seam {{ position: absolute; left: 0; top: 50%; width: 100%; height: 3px; margin-top: -1.5px; background: #050506; z-index: 4; }}
    .sf-y .sf-seam {{ background: #6b4d00; }}
"""


def scene(cid, body, css, rows, script, dur, flip=0.055, stagger=0.024):
    return f'''<template>
  <style>{COMMON_CSS}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    (function () {{
{ENGINE}
      const tl = gsap.timeline({{ paused: true }});
      const rows = {json.dumps(rows)};
      const drv = SplitFlap('[data-composition-id="{cid}"]', rows, {{ flip: {flip}, stagger: {stagger} }});
      // an accent row that is still blank stays hidden until it lands
      rows.forEach(function (r) {{
        if (r.yellow && r.keys[0][0] > 0.3) tl.fromTo("#" + r.id, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.08, ease: "none" }}, r.keys[0][0] - 0.06);
      }});
      tl.to(drv, {{ t: {dur}, duration: {dur}, ease: "none" }}, 0);
{script}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
'''


def board(pfx, x, y, w, rows_spec, header, num, pad=22):
    """Housing + header + rows. rows_spec: list of dict(id, n, w, h, fs, gap, yellow, keys)."""
    inner = []
    cy = y + pad + 34 + 12
    for r in rows_spec:
        rw = r["n"] * r["w"] + (r["n"] - 1) * r["gap"]
        inner.append(f'      <div id="{r["id"]}" class="sfrow" style="left:{x + pad}px;top:{cy}px;width:{rw}px;height:{r["h"]}px"></div>')
        cy += r["h"] + r.get("after", 10)
    h = cy - r.get("after", 10) - y + pad
    html = f'''    <div id="{pfx}-wrap" style="position:absolute;inset:0">
      <div id="{pfx}-house" class="house" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>
      <div id="{pfx}-hdr" class="hdr" style="left:{x + pad + 2}px;top:{y + pad - 2}px;width:{w - 2 * pad - 4}px">
        <span class="tag"><span class="dot"></span><span id="{pfx}-label">{header}</span></span><span class="num">{num}</span>
      </div>
''' + "\n".join(inner) + "\n    </div>"
    return html, h


def row(rid, n, w, h, fs, keys, gap=6, yellow=False, after=10):
    return dict(id=rid, n=n, w=w, h=h, fs=fs, gap=gap, yellow=yellow, keys=keys, after=after)


def out(src):
    """source second -> output second."""
    for (a, b), s in zip(CUTS, starts):
        if a - 0.05 <= src <= b + 0.05:
            return round(s + (src - a), 3)
    raise ValueError(src)


BX, BW = 92, 842   # board housing x / width: clear of the right-hand action rail

# ------------------------------------------------------------------ 1. HOOK (frame 0 is the thumbnail)
hk_rows = [
    row("hk-r1", 10, 68, 104, 80, [[0, "SHOPLOT"], [out(3.18) - 0.02, "3 TINGKAT"], [out(4.72) - 0.04, "TINGKAT 1"],
                                   [out(5.34) - 0.04, "TINGKAT 2"], [out(5.62) - 0.04, "TINGKAT 3"], [out(5.90) - 0.02, "BILIK SEWA"]], gap=11),
    row("hk-r2", 12, 57, 76, 56, [[0, "UNTUK DIJUAL"], [out(5.90) + 0.12, "TINGKAT ATAS"]], gap=9, yellow=True),
]
hk_body, hk_h = board("hk", BX, 0, BW, hk_rows, "ALOR SETAR", "01")
HK_Y = 1300 - hk_h
hk_body, _ = board("hk", BX, HK_Y, BW, hk_rows, "ALOR SETAR", "01")
hk_script = f"""      // the board is already up at frame 0; it only clears at the scene end
      tl.to("#hk-wrap", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {S_HOOK[1] - S_HOOK[0] - 0.13:.3f});"""

# ------------------------------------------------------------------ 2. LOKASI
L0 = S_LOK[0]
lk_rows = [
    row("lk-r1", 15, 50, 72, 52, [[0.08, "ALOR SETAR MALL"]], gap=6),
    row("lk-r2", 15, 50, 72, 52, [[out(12.00) - L0 - 0.02, "KAWASAN"]], gap=6),
    row("lk-r3", 15, 50, 72, 52, [[out(12.64) - L0 - 0.02, "PERINDUSTRIAN"]], gap=6),
    row("lk-r4", 6, 50, 72, 52, [[out(13.30) - L0 - 0.06, "TANDOP"]], gap=6, yellow=True),
]
lk_body, lk_h = board("lk", BX, 0, BW, lk_rows, "BERDEKATAN", "02")
LK_Y = 1300 - lk_h
lk_body, _ = board("lk", BX, LK_Y, BW, lk_rows, "BERDEKATAN", "02")
lk_script = f"""      tl.fromTo("#lk-wrap", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "power2.out" }}, 0);
      tl.to("#lk-wrap", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {S_LOK[1] - S_LOK[0] - 0.13:.3f});"""

# ------------------------------------------------------------------ 3. BANGUNAN
B0 = S_BGN[0]
bg_rows = [
    row("bg-r1", 11, 64, 96, 72, [[0.08, "BANGUNAN"]], gap=9),
    row("bg-r2", 11, 64, 96, 72, [[out(18.44) - B0 - 0.06, "DESA SERAYA"]], gap=9, yellow=True),
]
bg_body, bg_h = board("bg", BX, 0, BW, bg_rows, "LOKASI", "03")
BG_Y = 1300 - bg_h
bg_body, _ = board("bg", BX, BG_Y, BW, bg_rows, "LOKASI", "03")
bg_script = f"""      tl.fromTo("#bg-wrap", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1, ease: "power2.out" }}, 0);
      tl.to("#bg-wrap", {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, {S_BGN[1] - S_BGN[0] - 0.13:.3f});"""

# ------------------------------------------------------------------ 4. CTA (the real profile screenshot + split-flap tab)
C0 = S_CTA[0]
CX, CWID = 110, 820
SC = CWID / 1206                      # screenshot (1206x822 after crop) -> card width
IMG_H = round(822 * SC)
TAB_Y, IMG_Y = 246, 360
ct_rows = [row("ct-r1", 16, 44, 66, 46, [[0.06, "NAK TAHU DETAIL?"], [out(21.74) - C0 - 0.02, "KLIK LINK DI BIO"]], gap=6)]
ct_tab_w = 16 * 44 + 15 * 6
tab_x = CX + (CWID - ct_tab_w) // 2
ct_link_t = out(25.74) - C0
flip_at = out(21.74) - C0
# the link line in the screenshot (source px, after the crop) -> frame px
lk_x0, lk_x1, lk_y0, lk_y1 = 30, 780, 664, 720
HX, HY = CX + round(lk_x0 * SC), IMG_Y + round(lk_y0 * SC)
HW, HH = round((lk_x1 - lk_x0) * SC), round((lk_y1 - lk_y0) * SC)
ct_body = f"""    <div id="ct-wrap" style="position:absolute;inset:0">
      <div id="ct-tabhouse" class="house" style="left:{CX}px;top:{TAB_Y}px;width:{CWID}px;height:102px"></div>
      <div id="ct-r1" class="sfrow" style="left:{tab_x}px;top:{TAB_Y + 18}px;width:{ct_tab_w}px;height:66px"></div>
      <div id="ct-card" style="position:absolute;left:{CX}px;top:{IMG_Y}px;width:{CWID}px;height:{IMG_H}px;border-radius:22px;overflow:hidden;background:#000;box-shadow:0 22px 44px rgba(0,0,0,0.5), 0 0 0 2px rgba(255,194,26,0.55)">
        <img id="ct-shot" src="assets/cta-profile.jpg" alt="Profil TikTok NAZProperty" style="position:absolute;left:0;top:0;width:{CWID}px;height:{IMG_H}px" />
      </div>
      <div id="ct-hl" style="position:absolute;left:{HX - 8}px;top:{HY - 6}px;width:{HW + 16}px;height:{HH + 12}px;border:4px solid {YEL};border-radius:14px;box-shadow:0 0 18px rgba(255,194,26,0.45)"></div>
    </div>"""
ct_script = f"""      tl.fromTo("#ct-wrap", {{ opacity: 0, y: -16 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, 0);
      tl.fromTo("#ct-card", {{ opacity: 0, y: 24, scale: 0.97 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out" }}, 0.12);
      // "link di bio": the link line in the profile gets a yellow frame
      tl.fromTo("#ct-hl", {{ opacity: 0, scale: 1.08 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {ct_link_t - 0.05:.3f});
      tl.fromTo("#ct-hl", {{ boxShadow: "0 0 18px rgba(255,194,26,0.45)" }}, {{ boxShadow: "0 0 30px rgba(255,194,26,0.85)", duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: 3 }}, {ct_link_t + 0.3:.3f});"""

# ------------------------------------------------------------------ write scenes
os.makedirs(os.path.join(P, "compositions"), exist_ok=True)
for cid, body, rows, script, win in [
    ("hook", hk_body, hk_rows, hk_script, S_HOOK),
    ("lokasi", lk_body, lk_rows, lk_script, S_LOK),
    ("bangunan", bg_body, bg_rows, bg_script, S_BGN),
    ("cta", ct_body, ct_rows, ct_script, S_CTA),
]:
    with open(os.path.join(P, "compositions", f"{cid}.html"), "w") as f:
        f.write(scene(cid, body, "", rows, script, round(win[1] - win[0], 3)))

# ------------------------------------------------------------------ root
FX = json.dumps({"version": 1, "nodes": [
    {"type": "highpass", "id": "v1", "label": "Remove rumble", "params": {"frequency": 90}},
    {"type": "limiter", "id": "v2", "label": "Safety limiter", "params": {"limit": -1}}]}).replace('"', "&quot;")

vids = []
names = ["hook", "tiga-tingkat", "berdekatan", "mall", "tandop", "yang-ni", "bangunan", "desa-seraya", "detail", "link-bio"]
for i, ((a, b), s) in enumerate(zip(CUTS, starts)):
    vids.append(f'''        <video id="v-{names[i]}" class="clip" src="assets/footage.mp4" playsinline data-has-audio="true"
          data-start="{s}" data-duration="{round(b - a, 3)}" data-media-start="{a}" data-track-index="{i % 2}"
          data-fade-in="0.02" data-fade-out="0.03" data-volume="1.35" data-fx-chain="{FX}"
          style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover"></video>''')
vids.append(f'''        <img id="v-hold" class="clip" src="assets/last-frame.jpg" alt="" data-start="{SPEECH_END}" data-duration="{round(TOTAL - SPEECH_END, 3)}" data-track-index="2"
          style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover" />''')

scenes = [("hook", S_HOOK, 3), ("lokasi", S_LOK, 4), ("bangunan", S_BGN, 3), ("cta", S_CTA, 4)]
hosts = []
for z, (cid, (a, b), tr) in enumerate(scenes):
    hosts.append(f'''      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="{tr}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index:{20 + z}"></div>''')

# sound: real split-flap clatter on each board change, two soft whooshes, one pop
def sfx(id_, f, s, d, v, tr):
    return (f'      <audio id="{id_}" class="clip" src="assets/sfx/{f}" data-start="{s:.3f}" data-duration="{d}" '
            f'data-track-index="{tr}" data-volume="{v}" data-fade-out="0.15"></audio>')

flaps = [
    (out(3.18) - 0.02, 0.55), (out(4.72) - 0.04, 0.5), (out(5.34) - 0.04, 0.22), (out(5.62) - 0.04, 0.22),
    (out(5.90) - 0.02, 0.75),
    (L0 + 0.08, 0.7), (out(12.00) - 0.02, 0.45), (out(12.64) - 0.02, 0.6), (out(13.30) - 0.06, 0.45),
    (B0 + 0.08, 0.55), (out(18.44) - 0.06, 0.6),
    (C0 + 0.06, 0.8), (out(21.74) - 0.02, 0.8),
]
audio = []
for k, (s, d) in enumerate(flaps):
    audio.append(sfx(f"sfx-flap-{k + 1}", f"flap-{k % 5 + 1}.mp3", s, d, 0.38 if d > 0.3 else 0.3, 6 + k % 2))
audio.append(sfx("sfx-whoosh-1", "whoosh-short.mp3", L0 - 0.08, 0.5, 0.14, 8))
audio.append(sfx("sfx-whoosh-2", "whoosh-cinematic.mp3", C0 - 0.12, 1.2, 0.16, 8))
audio.append(sfx("sfx-pop", "pop.mp3", out(25.74) - 0.0, 0.4, 0.22, 8))

bgm = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0.18}, {"t": SPEECH_END - 0.2, "v": 0.18}, {"t": SPEECH_END + 0.3, "v": 0.5}]}]}).replace('"', "&quot;")

cam = []
for i, s in enumerate(starts):
    cam.append(f'      tl.set("#cam-move", {{ scale: {1.0 if i % 2 == 0 else 1.06} }}, {s});')

index = f'''<!doctype html>
<html lang="ms" data-resolution="portrait" data-composition-variables='[{{"id": "color-accent", "type": "color", "label": "Accent", "default": "{YEL}"}}, {{"id": "color-ink", "type": "color", "label": "Ink", "default": "{INK}"}}]'>
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
      tl.set("#cam-move", {{ transformOrigin: "50% 42%" }}, 0);
{chr(10).join(cam)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
with open(os.path.join(P, "index.html"), "w") as f:
    f.write(index)
print("total", TOTAL, "starts", starts, "speech_end", SPEECH_END)
print("hook y", HK_Y, "lok y", LK_Y, "bgn y", BG_Y)
