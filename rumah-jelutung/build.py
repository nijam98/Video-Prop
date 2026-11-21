#!/usr/bin/env python3
"""Generate index.html (HyperFrames composition) from the edit decision list.

Usage:  python3 build.py            -> index.html (final, no guides)
        python3 build.py --guides   -> index.html with TikTok/IG safe-zone guides
All times in SEGMENTS / OVERLAYS are SOURCE times (seconds in assets/tour.mp4);
they are mapped to output time automatically.
"""
import json, sys, html

GUIDES = "--guides" in sys.argv
W, H = 1080, 1920
# Combined TikTok + Instagram Reels safe area (px, 1080x1920)
SAFE = dict(top=260, bottom=1420, left=72, right=920)

# ---- Edit decision list: (src_in, src_out, punch_scale) ------------------
# Hook first (strongest line), then the tour in order. Repeats/fillers/pauses removed.
SEGMENTS = [
    (7.50, 11.95, 1.00),   # HOOK: "Rumah ni ... owner beli tak pernah buat apa, tak pernah duduk."
    (1.55, 5.35, 1.00),    # "Dalam ni, Fasa 2 Taman Jelutong (Changlun), 23 x 70."
    (5.60, 7.25, 1.06),    # "Ni ruang tamu. Dapat semua macam ni."
    (14.70, 18.05, 1.00),  # "Yang ni master bedroom. Ini satu toilet, nampak?"
    (19.40, 20.90, 1.08),  # "Ada plastik lagi."
    (23.74, 27.35, 1.00),  # "Cuma owner letak barang sahaja. Yang ni bilik yang keempat."
    (28.22, 31.52, 1.00),  # "Okey, yang ni ruang dapur. Ruang dapur pun nak kata baru."
    (34.45, 39.55, 1.00),  # "Ni bilik kedua. Bilik kedua tinggi. Sesuai kalau nak buat loteng."
    (39.92, 41.05, 1.06),  # "Yang ni bilik ketiga."
    (43.46, 45.28, 1.00),  # "... toilet yang kedua."
    (47.76, 52.30, 1.00),  # "Ruang tanah belakang ni ada siap dengan tile ... lebihan 5 kaki."
    (53.05, 55.32, 1.06),  # "Total keluasan rumah ni 1,600 sqft."
    (55.38, 59.98, 1.00),  # "Yang mana berminat ... LPPSA, loan bank ... pun boleh."
    (60.72, 62.20, 1.00),  # "Rumah memang cantik."
    (62.44, 66.26, 1.06),  # "Mai kutip balik, buat renovate, masuk idea sendiri."
    (67.50, 70.30, 1.00),  # "Yang penting, isi sahaja ... dekat bawah ni."
]


def out_t(src):
    """Map a source time to output time (must fall inside a kept segment)."""
    t = 0.0
    for a, b, _ in SEGMENTS:
        if a - 1e-6 <= src <= b + 1e-6:
            return round(t + (src - a), 3)
        t += b - a
    raise ValueError(f"source time {src} is not in any kept segment")


def seg_bounds(i):
    t = sum(b - a for a, b, _ in SEGMENTS[:i])
    a, b, _ = SEGMENTS[i]
    return round(t, 3), round(t + b - a, 3)


TOTAL = round(sum(b - a for a, b, _ in SEGMENTS), 3)

# ---- Overlays (source times) --------------------------------------------
# kind: label (kicker + written script + swash), chip, stat, photo, list, cta, hook
OVERLAYS = [
    # Hook
    dict(kind="hook", src=(7.62, 11.80), kicker="Dijual · Changlun", text="Tak pernah|diduduki"),
    dict(kind="chip", src=(8.62, 11.80), text="Masih berbalut plastik", pos=(72, 1280)),
    # Location + exterior photo
    dict(kind="photo", src=(1.70, 5.30), img="assets/photos/luar2.jpg", box=(580, 300, 310, 440), rot=2.5),
    dict(kind="label", src=(1.70, 5.30), kicker="Lokasi · Changlun", text="Taman Jelutong", pos=(72, 960)),
    dict(kind="chip", src=(2.10, 5.30), text="Fasa 2, Changlun", pos=(72, 1170)),
    dict(kind="chip", src=(2.90, 5.30), text="Menghadap surau", pos=(72, 1255)),
    dict(kind="chip", src=(4.10, 5.30), text="Tanah 23 × 70 kaki", pos=(72, 1340)),
    # Rooms
    dict(kind="label", src=(5.66, 7.22), kicker="Ruang", text="Ruang Tamu", pos=(72, 300)),
    dict(kind="label", src=(14.76, 18.00), kicker="Bilik utama", text="Master Bedroom", pos=(72, 300)),
    dict(kind="chip", src=(16.55, 18.02), text="Bilik air sendiri", pos=(72, 1300)),
    dict(kind="chip", src=(19.45, 20.86), text="Masih baru, belum dipakai", pos=(72, 1300)),
    dict(kind="chip", src=(23.80, 25.62), text="Hanya barang owner disimpan", pos=(72, 1300)),
    dict(kind="label", src=(25.70, 27.30), kicker="Bilik", text="Bilik Keempat", pos=(72, 300)),
    dict(kind="label", src=(28.28, 31.50), kicker="Ruang", text="Ruang Dapur", pos=(72, 300)),
    dict(kind="chip", src=(30.06, 31.50), text="Kondisi baru", pos=(72, 1300)),
    dict(kind="label", src=(34.50, 39.50), kicker="Bilik", text="Bilik Kedua", pos=(72, 300)),
    dict(kind="chip", src=(35.80, 39.50), text="Siling tinggi · sesuai buat loteng", pos=(72, 1300)),
    dict(kind="label", src=(39.96, 41.02), kicker="Bilik", text="Bilik Ketiga", pos=(72, 300)),
    dict(kind="label", src=(43.50, 45.25), kicker="Bilik air", text="Toilet Kedua", pos=(72, 300)),
    dict(kind="label", src=(47.78, 52.25), kicker="Luar rumah", text="Tanah Belakang", pos=(72, 300)),
    dict(kind="chip", src=(48.90, 52.25), text="Siap bertile", pos=(72, 1230)),
    dict(kind="chip", src=(50.46, 52.25), text="+ lebihan ±5 kaki", pos=(72, 1320)),
    # Size stat
    dict(kind="stat", src=(53.10, 55.30), kicker="Keluasan rumah", num="1,600", unit="kaki persegi"),
    # Financing
    dict(kind="list", src=(55.42, 59.95), kicker="Pembiayaan", items=[("LPPSA", 56.82), ("Loan bank", 57.76)]),
    # Recap photos (overlay stills from the tour)
    dict(kind="photo", src=(60.78, 66.20), img="assets/photos/ruang-tamu.jpg", box=(92, 340, 270, 400), rot=-3),
    dict(kind="photo", src=(61.20, 66.20), img="assets/photos/master.jpg", box=(362, 312, 270, 400), rot=1.5),
    dict(kind="photo", src=(61.60, 66.20), img="assets/photos/dapur.jpg", box=(630, 352, 250, 370), rot=3),
    dict(kind="label", src=(62.48, 66.20), kicker="Kanvas kosong", text="Reno ikut idea sendiri", pos=(72, 1120)),
    # CTA
    dict(kind="cta", src=(67.56, 70.25), kicker="Berminat?", text="Isi borang di bawah"),
]

# ---------------------------------------------------------------------------
esc = html.escape


def overlay_html(i, o):
    s, e = out_t(o["src"][0]), out_t(o["src"][1])
    d = round(e - s, 3)
    oid = f"ov{i}"
    attrs = f'id="{oid}" class="ov clip {o["kind"]}" data-start="{s}" data-duration="{d}" data-track-index="{2 + i % 6}"'
    k = o["kind"]
    if k == "label":
        x, y = o["pos"]
        return (f'<div {attrs} style="left:{x}px;top:{y}px">'
                f'<div class="glow"></div><div class="kicker">{esc(o["kicker"])}</div>'
                f'<div class="script write">{esc(o["text"])}</div>'
                f'<svg class="swash" viewBox="0 0 400 24" width="400" height="24"><path d="M4 16 C 90 6, 200 22, 396 8" /></svg>'
                f'</div>'), (s, e)
    if k == "hook":
        return (f'<div {attrs}>'
                f'<div class="glow"></div><div class="kicker">{esc(o["kicker"])}</div>'
                + "".join(f'<div class="script big write">{esc(t)}</div>' for t in o["text"].split("|")) +
                f'<svg class="swash" viewBox="0 0 400 24" width="560" height="32"><path d="M4 16 C 90 6, 200 22, 396 8" /></svg>'
                f'</div>'), (s, e)
    if k == "chip":
        x, y = o["pos"]
        return (f'<div {attrs} style="left:{x}px;top:{y}px"><span class="dot"></span><span class="t">{esc(o["text"])}</span></div>'), (s, e)
    if k == "photo":
        x, y, w, h = o["box"]
        return (f'<div {attrs} style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--rot:{o["rot"]}deg">'
                f'<img src="{o["img"]}" alt="" /></div>'), (s, e)
    if k == "stat":
        return (f'<div {attrs}><div class="kicker">{esc(o["kicker"])}</div>'
                f'<div class="num write">{esc(o["num"])}</div>'
                f'<div class="script unit write">{esc(o["unit"])}</div></div>'), (s, e)
    if k == "list":
        items = "".join(f'<div class="item" data-at="{out_t(t)}"><span class="tick"><svg viewBox="0 0 24 24"><path d="M4 12.5 L10 18 L20 6"/></svg></span><span class="script write">{esc(n)}</span></div>' for n, t in o["items"])
        return (f'<div {attrs}><div class="glow"></div><div class="kicker">{esc(o["kicker"])}</div>{items}'
                f'<div class="sub">pun boleh</div></div>'), (s, e)
    if k == "cta":
        return (f'<div {attrs}><div class="glow"></div><div class="kicker">{esc(o["kicker"])}</div>'
                f'<div class="script big write">{esc(o["text"])}</div>'
                f'<svg class="arrow" viewBox="0 0 60 120" width="48" height="96"><path d="M30 4 C 26 40, 34 70, 30 110 M14 92 L30 112 L46 92"/></svg>'
                f'</div>'), (s, e)
    raise ValueError(k)


def build():
    vids = []
    for i, (a, b, sc) in enumerate(SEGMENTS):
        s, e = seg_bounds(i)
        vids.append(
            f'<div id="seg{i}" class="seg">'
            f'<div class="punch" style="transform:scale({sc})">'
            f'<video id="v{i}" class="clip" src="assets/tour.mp4" playsinline data-start="{s}" data-duration="{round(e - s, 3)}" '
            f'data-media-start="{a}" data-has-audio="true" data-fade-in="0.03" data-fade-out="0.04" data-track-index="1"></video>'
            f'</div></div>')

    ovs, js = [], []
    for i, o in enumerate(OVERLAYS):
        h_, (s, e) = overlay_html(i, o)
        ovs.append(h_)
        js.append({"id": f"ov{i}", "kind": o["kind"], "s": s, "e": e})

    hook_end = seg_bounds(0)[1]
    guides = ""
    if GUIDES:
        guides = (f'<div id="guides" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="9">'
                  f'<div class="g-top"><span>TikTok / IG UI (atas)</span></div>'
                  f'<div class="g-bottom"><span>Caption + butang (bawah)</span></div>'
                  f'<div class="g-right"><span>Ikon</span></div>'
                  f'<div class="g-safe"></div></div>')

    fonts = open("fonts-local.css").read()
    page = TEMPLATE
    for k, v in {
        "__FONTS__": fonts, "__TOTAL__": str(TOTAL), "__VIDEOS__": "\n      ".join(vids),
        "__OVERLAYS__": "\n      ".join(ovs), "__GUIDES__": guides, "__OVJSON__": json.dumps(js),
        "__HOOKEND__": str(hook_end), "__SAFE_TOP__": str(SAFE["top"]), "__SAFE_BOTTOM__": str(SAFE["bottom"]),
        "__SAFE_LEFT__": str(SAFE["left"]), "__SAFE_RIGHT__": str(SAFE["right"]),
    }.items():
        page = page.replace(k, v)
    open("index.html", "w").write(page)
    print(f"index.html written: {len(SEGMENTS)} segments, {len(OVERLAYS)} overlays, total {TOTAL}s, guides={GUIDES}")


TEMPLATE = r"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      __FONTS__
      :root {
        --ink: #34241a;          /* walnut ink, matches the door frames */
        --ink-soft: rgba(52, 36, 26, 0.72);
        --paper: rgba(250, 247, 241, 0.92);
        --wood: #8a5232;
        --script: 'Allura', cursive;
        --serif: 'Cormorant Garamond', serif;
        --sans: 'Manrope', sans-serif;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #111; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
      .seg { position: absolute; inset: 0; overflow: hidden; }
      .punch { position: absolute; inset: 0; transform-origin: 50% 45%; }
      .punch video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }

      .ov { position: absolute; z-index: 10; }
      .kicker {
        font-family: var(--sans); font-weight: 700; font-size: 24px; letter-spacing: 0.32em;
        text-transform: uppercase; color: var(--ink-soft);
        text-shadow: 0 0 14px rgba(255,255,255,0.9), 0 0 2px rgba(255,255,255,0.9);
      }
      .script {
        font-family: var(--script); font-size: 118px; line-height: 1.05; color: var(--ink);
        white-space: nowrap; padding: 0 18px 0 4px; margin-left: -4px;
        text-shadow: 0 0 22px rgba(255,255,255,0.85), 0 0 3px rgba(255,255,255,0.95);
      }
      .write {
        -webkit-mask-image: linear-gradient(90deg, #000 0%, #000 47%, transparent 53%, transparent 100%);
        mask-image: linear-gradient(90deg, #000 0%, #000 47%, transparent 53%, transparent 100%);
        -webkit-mask-size: 250% 100%; mask-size: 250% 100%;
        -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
        -webkit-mask-position: 100% 0; mask-position: 100% 0;
      }
      .swash { display: block; margin-top: -6px; overflow: visible; }
      .swash path, .arrow path, .tick path {
        fill: none; stroke: var(--wood); stroke-width: 3; stroke-linecap: round; stroke-linejoin: round;
        filter: drop-shadow(0 0 4px rgba(255,255,255,0.9));
      }

      .label .script { margin-top: 2px; }
      .ov .script, .ov .num { width: max-content; }
      .stat .script, .stat .num, .cta .script { margin-left: auto; margin-right: auto; }
      .glow { position: absolute; left: -110px; right: -90px; top: -70px; bottom: -60px; z-index: -1; pointer-events: none;
        background: radial-gradient(closest-side, rgba(255,251,244,0.60) 0%, rgba(255,251,244,0.34) 45%, rgba(255,251,244,0) 100%); }
      .hook .glow, .cta .glow, .list .glow { left: -140px; right: -140px; top: -90px; bottom: -80px; }

      .hook { left: __SAFE_LEFT__px; top: 330px; }
      .hook .kicker { font-size: 26px; }
      .script.big { font-size: 150px; line-height: 1.0; }
      .hook .script.big + .script.big { padding-left: 90px; }

      .chip {
        display: inline-flex; align-items: center; gap: 16px; padding: 18px 30px 18px 24px;
        background: var(--paper); border-radius: 999px; color: var(--ink);
        font-family: var(--sans); font-weight: 500; font-size: 32px; letter-spacing: 0.01em;
        box-shadow: 0 10px 30px rgba(40, 28, 18, 0.18); white-space: nowrap;
      }
      .chip .dot { width: 12px; height: 12px; border-radius: 50%; background: var(--wood); flex: none; }

      .photo {
        border-radius: 16px; overflow: hidden;
        box-shadow: 0 18px 40px rgba(30, 20, 12, 0.30);
      }
      .photo img { width: 100%; height: 100%; object-fit: cover; display: block; }

      .stat { left: 132px; width: 728px; top: 600px; text-align: center; padding: 48px 20px 54px;
        background: rgba(250, 246, 239, 0.9); border-radius: 28px; box-shadow: 0 24px 60px rgba(30,20,12,0.28); }
      .stat .num {
        font-family: var(--serif); font-weight: 600; font-size: 250px; line-height: 0.95; color: var(--ink);
        text-shadow: 0 0 30px rgba(255,255,255,0.9), 0 0 4px rgba(255,255,255,0.9); padding: 0 20px;
      }
      .stat .unit { font-size: 104px; margin-top: -10px; padding: 0 20px; }
      .stat .kicker { margin-bottom: 10px; }

      .list { left: __SAFE_LEFT__px; top: 330px; }
      .list .item { display: flex; align-items: center; gap: 22px; margin-top: 12px; }
      .list .tick {
        width: 64px; height: 64px; border-radius: 50%; background: var(--paper); flex: none;
        display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 22px rgba(40,28,18,0.18);
      }
      .list .tick svg { width: 34px; height: 34px; overflow: visible; }
      .list .tick path { stroke-width: 3.4; filter: none; }
      .list .script { font-size: 112px; }
      .list .sub {
        font-family: var(--serif); font-style: italic; font-weight: 500; font-size: 52px; color: var(--ink);
        margin: 6px 0 0 86px; text-shadow: 0 0 16px rgba(255,255,255,0.9);
      }

      .cta { left: __SAFE_LEFT__px; width: 848px; top: 900px; text-align: center; }
      .cta .script.big { font-size: 120px; }
      .cta .arrow { display: block; margin: 14px auto 0; overflow: visible; width: 64px; height: 128px; }

      #flash { position: absolute; inset: 0; background: #fffdf8; opacity: 0; z-index: 20; pointer-events: none; }

      /* safe-zone guides (preview only) */
      #guides { position: absolute; inset: 0; z-index: 50; pointer-events: none; font-family: var(--sans); }
      #guides > div { position: absolute; background: rgba(255, 40, 80, 0.10); }
      #guides span { position: absolute; left: 16px; bottom: 10px; font-size: 22px; font-weight: 700; color: rgba(255,40,80,0.95); letter-spacing: .05em; }
      .g-top { left: 0; right: 0; top: 0; height: __SAFE_TOP__px; }
      .g-bottom { left: 0; right: 0; top: __SAFE_BOTTOM__px; bottom: 0; }
      .g-bottom span { top: 14px; bottom: auto !important; }
      .g-right { left: __SAFE_RIGHT__px; right: 0; top: __SAFE_TOP__px; height: calc(__SAFE_BOTTOM__px - __SAFE_TOP__px); }
      .g-right span { left: 10px !important; top: 14px; bottom: auto !important; }
      #guides .g-safe { left: __SAFE_LEFT__px; top: __SAFE_TOP__px; width: calc(__SAFE_RIGHT__px - __SAFE_LEFT__px); height: calc(__SAFE_BOTTOM__px - __SAFE_TOP__px);
        background: none; border: 3px dashed rgba(255,40,80,0.85); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="__TOTAL__" data-width="1080" data-height="1920" data-fps="30">
      __VIDEOS__
      __OVERLAYS__
      <div id="flash" class="clip" data-start="0" data-duration="__TOTAL__" data-track-index="8"></div>
      __GUIDES__
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const OV = __OVJSON__;
      const OUT = 0.35;

      function writeIn(el, at, dur) {
        tl.fromTo(el, { webkitMaskPosition: "100% 0", maskPosition: "100% 0" },
          { webkitMaskPosition: "0% 0", maskPosition: "0% 0", duration: dur, ease: "power1.inOut" }, at);
      }
      function drawIn(path, at, dur) {
        const L = path.getTotalLength();
        tl.fromTo(path, { strokeDasharray: L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur, ease: "power2.inOut" }, at);
      }
      // shrink any written line that would leave the safe zone (max 848px wide)
      document.querySelectorAll(".ov .script, .ov .num").forEach(el => {
        let fs = parseFloat(getComputedStyle(el).fontSize), guard = 0, r = el.getBoundingClientRect();
        while ((r.right > __SAFE_RIGHT__ || r.left < __SAFE_LEFT__ - 8) && guard++ < 40) {
          fs -= 4; el.style.fontSize = fs + "px"; r = el.getBoundingClientRect();
        }
      });
      function writeDur(el) { return Math.min(1.25, 0.35 + 0.045 * el.textContent.length); }
      function fadeOut(el, e) {
        tl.to(el, { opacity: 0, y: -8, filter: "blur(4px)", duration: OUT, ease: "power2.in" }, e - OUT);
      }

      OV.forEach(o => {
        const el = document.getElementById(o.id);
        const s = o.s, e = o.e;
        if (o.kind === "label" || o.kind === "hook" || o.kind === "cta") {
          const kick = el.querySelector(".kicker");
          const glow = el.querySelector(".glow");
          if (glow) tl.fromTo(glow, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: "power1.out" }, s);
          tl.fromTo(kick, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, s);
          let t0 = s + 0.12, wd = 0;
          el.querySelectorAll(".script").forEach(scr => { wd = writeDur(scr); writeIn(scr, t0, wd); t0 += wd * 0.92; });
          wd = t0 - s - 0.12;
          const sw = el.querySelector(".swash path, .arrow path");
          if (sw) drawIn(sw, s + 0.12 + wd * 0.75, 0.55);
          if (o.kind === "cta") {
            tl.to(el.querySelector(".arrow"), { y: 10, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: 3 }, s + wd + 0.6);
          }
          fadeOut(el, e);
        } else if (o.kind === "chip") {
          tl.fromTo(el, { opacity: 0, x: -14, clipPath: "inset(0 100% 0 0 round 999px)" },
            { opacity: 1, x: 0, clipPath: "inset(0 0% 0 0 round 999px)", duration: 0.55, ease: "power3.out" }, s);
          fadeOut(el, e);
        } else if (o.kind === "photo") {
          tl.fromTo(el, { opacity: 0, y: 26, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "power3.out" }, s);
          tl.to(el, { y: -14, duration: Math.max(0.1, e - s - 0.6 - OUT), ease: "none" }, s + 0.6);
          fadeOut(el, e);
        } else if (o.kind === "stat") {
          const kick = el.querySelector(".kicker"), num = el.querySelector(".num"), unit = el.querySelector(".unit");
          tl.fromTo(el, { opacity: 0, y: 24, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }, s - 0.05);
          tl.fromTo(kick, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, s);
          writeIn(num, s + 0.1, 0.7);
          writeIn(unit, s + 0.75, 0.75);
          fadeOut(el, e);
        } else if (o.kind === "list") {
          const kick = el.querySelector(".kicker");
          tl.fromTo(el.querySelector(".glow"), { opacity: 0 }, { opacity: 1, duration: 0.45 }, s);
          tl.fromTo(kick, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, s);
          let last = s;
          el.querySelectorAll(".item").forEach(it => {
            const at = parseFloat(it.dataset.at);
            tl.fromTo(it.querySelector(".tick"), { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }, at - 0.1);
            drawIn(it.querySelector(".tick path"), at, 0.35);
            const sc = it.querySelector(".script");
            writeIn(sc, at + 0.05, writeDur(sc));
            last = at + writeDur(sc);
          });
          tl.fromTo(el.querySelector(".sub"), { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.45, ease: "power2.out" }, last);
          fadeOut(el, e);
        }
      });

      // dip-to-white after the hook
      const H = __HOOKEND__;
      tl.fromTo("#flash", { opacity: 0 }, { opacity: 0.85, duration: 0.1, ease: "power1.in" }, H - 0.1);
      tl.to("#flash", { opacity: 0, duration: 0.28, ease: "power2.out" }, H);
      // slow push-in on the hook
      tl.fromTo("#seg0 .punch", { scale: 1.0 }, { scale: 1.07, duration: H, ease: "none" }, 0);

      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    build()
