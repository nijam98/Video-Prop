"""Generate the holographic "Laporan Terkini" HyperFrames project (index.html + compositions/*.html).

Edit cuts, copy and timings here, then re-run:  python3 build.py
Output is plain HyperFrames HTML that Studio can still edit.

Look: holographic news HUD floating in the top band (wall + empty room above the presenter's head),
clear of the face, the TikTok/IG top bar and the right-hand action rail.
Dark cyan glass panels, scanlines, a sweep band, an iridescent rim, chromatic-split type,
text that decodes in on the spoken word, and a glitch-out on "hilang".
"""
import json, os

P = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FOOTAGE = os.environ.get("FOOTAGE", "assets/footage.mp4")

# ------------------------------------------------------------------ edit (source seconds)
CUTS = [
    (0.42, 7.70),    # Laporan terkini, jerebu sudah hilang. Penonton-penonton dinasihatkan ... dengan kadar yang segera.
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
S_NAS = (3.0, starts[1])
S_AMR = (starts[1], starts[2])
S_RMH = (starts[2], round(starts[4] + 0.6, 3))   # holds through "Jadi," so the checklist reads
S_CTA = (S_RMH[1], TOTAL)

CYAN = "#7FF3FF"
INK = "#EAFDFF"
MAG = "#FF5AD9"
LOCATION = os.environ.get("LOCATION", "TAMAN SERI PAGI FASA 2")

PX, PW, PY = 90, 900, 262          # panel x / width / top: the band above the presenter's head

# ------------------------------------------------------------------ shared look + engine
COMMON_CSS = f"""
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .wrap {{ position: absolute; inset: 0; }}
    .holo {{ position: absolute; border-radius: 16px; overflow: hidden;
      background: linear-gradient(180deg, rgba(8,34,56,0.86) 0%, rgba(4,16,32,0.9) 100%);
      box-shadow: 0 0 0 2px rgba(127,243,255,0.7), 0 0 34px rgba(60,220,255,0.45), inset 0 0 48px rgba(60,200,255,0.22); }}
    .scan {{ position: absolute; left: 0; top: -10px; width: 100%; height: calc(100% + 20px);
      background: repeating-linear-gradient(0deg, rgba(150,245,255,0.09) 0 2px, rgba(0,0,0,0) 2px 5px); }}
    .sweep {{ position: absolute; left: 0; top: 0; width: 100%; height: 140px;
      background: linear-gradient(180deg, rgba(127,243,255,0) 0%, rgba(127,243,255,0.16) 50%, rgba(127,243,255,0) 100%); }}
    .rim {{ position: absolute; left: 0; top: 0; width: 100%; height: 5px;
      background: linear-gradient(90deg, #7FF3FF 0%, #9C8CFF 25%, #FF5AD9 50%, #9C8CFF 75%, #7FF3FF 100%);
      background-size: 300% 100%; }}
    .mline {{ position: absolute; height: 4px; background: #E9FFFF; border-radius: 4px;
      box-shadow: 0 0 18px #7FF3FF, 0 0 40px rgba(127,243,255,0.8); }}
    .brk {{ position: absolute; width: 34px; height: 34px; border: 0 solid {CYAN}; filter: drop-shadow(0 0 6px rgba(127,243,255,0.9)); }}
    .brk.tl {{ border-top-width: 4px; border-left-width: 4px; border-radius: 8px 0 0 0; }}
    .brk.tr {{ border-top-width: 4px; border-right-width: 4px; border-radius: 0 8px 0 0; }}
    .brk.bl {{ border-bottom-width: 4px; border-left-width: 4px; border-radius: 0 0 0 8px; }}
    .brk.br {{ border-bottom-width: 4px; border-right-width: 4px; border-radius: 0 0 8px 0; }}
    .lbl {{ position: absolute; font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 30px;
      letter-spacing: 0.14em; color: {CYAN}; white-space: pre; text-shadow: 0 0 12px rgba(127,243,255,0.8); }}
    .ttl {{ position: absolute; font-family: 'Oswald', sans-serif; font-weight: 700; color: {INK}; white-space: pre;
      letter-spacing: 0.035em; line-height: 1;
      text-shadow: -3px 0 rgba(255,90,217,0.6), 3px 0 rgba(0,235,255,0.75), 0 0 22px rgba(90,230,255,0.75); }}
    .mag {{ color: #FFE4F8; text-shadow: -3px 0 rgba(0,235,255,0.6), 3px 0 rgba(255,90,217,0.85), 0 0 24px rgba(255,90,217,0.85); }}
    .chip {{ position: absolute; border-radius: 10px; border: 2px solid rgba(127,243,255,0.75);
      background: rgba(127,243,255,0.12); box-shadow: 0 0 16px rgba(127,243,255,0.35); }}
    .chip.m {{ border-color: rgba(255,90,217,0.85); background: rgba(255,90,217,0.14); box-shadow: 0 0 18px rgba(255,90,217,0.45); }}
"""

ENGINE = r"""
      // Decode engine: each .dc element types in from scrambled glyphs over [t0, t0 + d].
      // paint(t) is a pure function of scene time, so any seek lands on the same frame.
      function Decoder(rootSel) {
        var G = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+<>/";
        var host = document.querySelector(rootSel), items = [];
        host.querySelectorAll(".dc").forEach(function (el) {
          items.push({ el: el, txt: el.textContent, t0: parseFloat(el.getAttribute("data-t0")), d: parseFloat(el.getAttribute("data-d") || "0.35") });
        });
        function paint(t) {
          var f = Math.floor(t * 40);
          items.forEach(function (it, k) {
            if (t < it.t0) { it.el.style.opacity = "0"; return; }
            it.el.style.opacity = "1";
            var p = Math.min(1, (t - it.t0) / it.d), n = it.txt.length, shown = Math.floor(p * n), s = "";
            if (p >= 1) { if (it.el.textContent !== it.txt) it.el.textContent = it.txt; return; }
            for (var i = 0; i < n; i++) {
              var ch = it.txt.charAt(i);
              s += (i < shown || ch === " " || ch === "·") ? ch : (i < shown + 4 ? G.charAt((i * 7 + f * 13 + k * 5) % G.length) : " ");
            }
            it.el.textContent = s;
          });
        }
        var time = 0, drv = {};
        Object.defineProperty(drv, "t", { get: function () { return time; }, set: function (v) { time = v; paint(v); } });
        paint(0);
        return drv;
      }
"""


def panel(pid, x, y, w, h, inner):
    """A holographic glass panel with scanlines, sweep, rim and corner brackets."""
    return f'''      <div id="{pid}" class="wrap" data-layout-allow-overlap>
        <div id="{pid}-glass" class="holo" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">
          <div id="{pid}-scan" class="scan"></div>
          <div id="{pid}-sweep" class="sweep"></div>
          <div id="{pid}-rim" class="rim"></div>
        </div>
        <div class="brk tl" style="left:{x - 12}px;top:{y - 12}px"></div>
        <div class="brk tr" style="left:{x + w - 22}px;top:{y - 12}px"></div>
        <div class="brk bl" style="left:{x - 12}px;top:{y + h - 22}px"></div>
        <div class="brk br" style="left:{x + w - 22}px;top:{y + h - 22}px"></div>
        <div id="{pid}-line" class="mline" style="left:{x}px;top:{y + h // 2 - 2}px;width:{w}px;opacity:0"></div>
        <div id="{pid}-body" style="position:absolute;inset:0">
{inner}
        </div>
      </div>'''


def panel_fx(pid, h, dur, appear=True, at=0.0):
    """Materialize (projection line -> panel -> flicker), idle motion, and a glitch-out at the end."""
    s = []
    if appear:
        s.append(f'tl.fromTo("#{pid}-line", {{ opacity: 0, scaleX: 0.1 }}, {{ opacity: 1, scaleX: 1, duration: 0.14, ease: "power3.out" }}, {at});')
        s.append(f'tl.to("#{pid}-line", {{ opacity: 0, duration: 0.16, ease: "power2.in" }}, {at + 0.2:.3f});')
        s.append(f'tl.fromTo("#{pid}", {{ scaleY: 0.03, opacity: 0, transformOrigin: "50% {PY + h / 2:.0f}px" }}, {{ scaleY: 1, opacity: 1, duration: 0.26, ease: "power3.out" }}, {at + 0.1:.3f});')
        for k, (dt, o) in enumerate([(0.38, 0.45), (0.42, 1), (0.47, 0.7), (0.5, 1)]):
            s.append(f'tl.set("#{pid}-glass", {{ opacity: {o} }}, {at + dt:.3f});')
    # idle: scanlines drift, a sweep band passes every 1.6 s, the rim colours travel
    s.append(f'tl.fromTo("#{pid}-scan", {{ y: 0 }}, {{ y: {5 * int(dur * 8)}, duration: {dur:.3f}, ease: "none" }}, 0);')
    reps = max(0, int(dur / 1.6) - 1)
    s.append(f'tl.fromTo("#{pid}-sweep", {{ y: -140 }}, {{ y: {h + 10}, duration: 1.6, ease: "none", repeat: {reps} }}, 0);')
    s.append(f'tl.fromTo("#{pid}-rim", {{ backgroundPosition: "0% 0%" }}, {{ backgroundPosition: "300% 0%", duration: {dur:.3f}, ease: "none" }}, 0);')
    # glitch-out: horizontal jitter + flicker, then gone
    g0 = dur - 0.2
    for k, (dt, x, sk, o) in enumerate([(0, -14, 8, 0.8), (0.04, 10, -6, 0.4), (0.08, -6, 4, 0.9), (0.12, 18, 0, 0.25), (0.16, 0, 0, 0)]):
        s.append(f'tl.set("#{pid}", {{ x: {x}, skewX: {sk}, opacity: {o} }}, {g0 + dt:.3f});')
    return s


def scene(cid, body, script, dur):
    return f'''<template>
  <style>{COMMON_CSS}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    (function () {{
{ENGINE}
      const tl = gsap.timeline({{ paused: true }});
      const drv = Decoder('[data-composition-id="{cid}"]');
      tl.to(drv, {{ t: {dur}, duration: {dur}, ease: "none" }}, 0);
{chr(10).join("      " + l for l in script)}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
'''


def dc(eid, cls, x, y, size, text, t0, d=0.35, extra=""):
    return (f'          <div id="{eid}" class="{cls} dc" data-t0="{t0:.3f}" data-d="{d}" data-layout-ignore '
            f'style="left:{x}px;top:{y}px;font-size:{size}px;{extra}">{text}</div>')


def static(eid, cls, x, y, size, text, extra=""):
    return f'          <div id="{eid}" class="{cls}" style="left:{x}px;top:{y}px;font-size:{size}px;{extra}">{text}</div>'


def pop(sel, at, s):
    s.append(f'tl.fromTo("{sel}", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.4)" }}, {at:.3f});')


IX = PX + 44   # inner left

# ------------------------------------------------------------------ 0. SIARAN (news bug, whole film)
sr_body = f'''      <div id="sr" class="wrap">
        <div id="sr-live" class="chip m" style="left:{PX}px;top:178px;width:150px;height:56px;background:rgba(40,6,34,0.88)"></div>
        <div id="sr-dot" style="position:absolute;left:{PX + 20}px;top:197px;width:18px;height:18px;border-radius:50%;background:#FF4D6D;box-shadow:0 0 14px #FF4D6D"></div>
        <div class="lbl" style="left:{PX + 50}px;top:186px;color:#FFE4F8;text-shadow:0 0 12px rgba(255,90,217,0.9)">LIVE</div>
        <div id="sr-chan" class="chip" style="left:{PX + 166}px;top:178px;width:{PW - 166}px;height:56px;background:rgba(4,22,40,0.88)"></div>
        <div class="lbl" style="left:{PX + 190}px;top:186px">BERITA HARTANAH</div>
        <div class="lbl" style="left:{PX + PW - 230}px;top:186px;color:{INK}">ALOR SETAR</div>
      </div>'''
sr_script = [
    f'tl.fromTo("#sr-dot", {{ opacity: 1 }}, {{ opacity: 0.25, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: {int(TOTAL / 0.5) - 1} }}, 0);',
    f'tl.fromTo("#sr-chan", {{ boxShadow: "0 0 10px rgba(127,243,255,0.25)" }}, {{ boxShadow: "0 0 22px rgba(127,243,255,0.55)", duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: {int(TOTAL / 1.2) - 1} }}, 0);',
]

# ------------------------------------------------------------------ 1. HOOK  (frame 0 is the thumbnail: the panel is already up)
HK_H = 330
L = lambda src, s0: out(src) - s0
hk_inner = "\n".join([
    static("hk-lbl", "lbl", IX, PY + 34, 30, "◆ LAPORAN TERKINI · 01"),
    static("hk-ttl", "ttl", IX, PY + 84, 104, "LAPORAN TERKINI"),
    dc("hk-k1", "lbl", IX, PY + 236, 40, "JEREBU", L(1.53, 0), 0.3, f"color:{INK}"),
    dc("hk-k2", "ttl mag", IX + 190, PY + 222, 66, "SUDAH HILANG", L(2.10, 0), 0.4),
    static("hk-ok", "chip", IX + 630, PY + 224, 1, "", "width:70px;height:66px;opacity:0"),
    static("hk-okm", "ttl", IX + 646, PY + 228, 56, "✓", "opacity:0"),
])
hk_body = panel("hk", PX, PY, PW, HK_H, hk_inner)
hk_dur = S_HOOK[1] - S_HOOK[0]
hk_script = panel_fx("hk", HK_H, hk_dur, appear=False)
pop("#hk-ok", L(2.59, 0), hk_script)
pop("#hk-okm", L(2.59, 0) + 0.04, hk_script)

# ------------------------------------------------------------------ 2. NASIHAT
N0 = S_NAS[0]
NS_H = 380
ns_inner = "\n".join([
    dc("ns-lbl", "lbl", IX, PY + 34, 30, "◆ NASIHAT KEPADA PENONTON", 0.32, 0.45),
    dc("ns-ttl", "ttl", IX, PY + 88, 112, "BELI RUMAH INI", L(5.20, N0), 0.45),
    dc("ns-k", "lbl", IX, PY + 268, 34, "KADAR", L(6.68, N0) - 0.05, 0.25, f"color:{INK}"),
    static("ns-bar", "chip", IX + 150, PY + 270, 1, "", "width:330px;height:40px;opacity:0"),
    static("ns-fill", "", IX + 156, PY + 276, 1, "", f"position:absolute;width:318px;height:28px;border-radius:6px;background:linear-gradient(90deg,{CYAN},{MAG});box-shadow:0 0 18px rgba(255,90,217,0.7)"),
    dc("ns-seg", "ttl mag", IX + 512, PY + 252, 76, "SEGERA!", L(7.28, N0) - 0.06, 0.25),
])
ns_body = panel("ns", PX, PY, PW, NS_H, ns_inner)
ns_dur = round(S_NAS[1] - N0, 3)
ns_script = panel_fx("ns", NS_H, ns_dur)
ns_script.append(f'tl.fromTo("#ns-bar", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, {L(6.68, N0) - 0.05:.3f});')
ns_script.append(f'tl.fromTo("#ns-fill", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: {L(7.28, N0) - L(6.70, N0):.3f}, ease: "power2.in" }}, {L(6.70, N0):.3f});')
ns_script.append(f'tl.fromTo("#ns-seg", {{ scale: 1.35 }}, {{ scale: 1, duration: 0.25, ease: "back.out(2.5)" }}, {L(7.28, N0) - 0.06:.3f});')

# ------------------------------------------------------------------ 3. AMARAN  (the "hilang" line glitches away)
A0 = S_AMR[0]
AM_H = 360
am_inner = "\n".join([
    dc("am-lbl", "lbl", IX, PY + 34, 30, "⚠ AMARAN", 0.3, 0.3, f"color:#FFE4F8;text-shadow:0 0 12px rgba(255,90,217,0.9)"),
    dc("am-ttl", "ttl", IX, PY + 86, 100, "JANGAN JADI SI DIA", 0.42, 0.55),
    dc("am-k1", "ttl", IX, PY + 222, 78, "DATANG...", L(10.38, A0), 0.3),
    f'          <div id="am-gone" style="position:absolute;left:{IX + 372}px;top:{PY + 222}px">',
    dc("am-k2", "ttl mag", 0, 0, 78, "TAPI HILANG", L(10.90, A0), 0.35, "position:relative"),
    "          </div>",
])
am_body = panel("am", PX, PY, PW, AM_H, am_inner)
am_dur = round(S_AMR[1] - A0, 3)
am_script = panel_fx("am", AM_H, am_dur)
g = L(11.40, A0)
for k, (dt, x, o) in enumerate([(0, 12, 0.6), (0.05, -16, 1), (0.1, 8, 0.3), (0.16, -22, 0.8), (0.22, 30, 0.15), (0.3, -8, 0.5), (0.38, 0, 0)]):
    am_script.append(f'tl.set("#am-gone", {{ x: {x}, opacity: {o}, skewX: {(-1) ** k * 10} }}, {g + dt:.3f});')

# ------------------------------------------------------------------ 4. RUMAH INI  (tidak hilang, ada geran, ada kunci)
R0 = S_RMH[0]
RM_H = 430
rm_inner = "\n".join([
    dc("rm-lbl", "lbl", IX, PY + 34, 30, "◆ STATUS RUMAH", 0.3, 0.3),
    dc("rm-ttl", "ttl", IX, PY + 86, 100, "RUMAH INI", 0.36, 0.35),
    static("rm-chip", "chip m", IX, PY + 196, 1, "", "width:812px;height:90px;opacity:0"),
    dc("rm-st", "ttl mag", IX + 24, PY + 206, 66, "TIDAK HILANG \u2713", L(12.56, R0), 0.35),
    static("rm-c1", "chip", IX, PY + 310, 1, "", "width:390px;height:96px;opacity:0"),
    static("rm-c1m", "ttl", IX + 22, PY + 320, 72, "✓", f"color:{CYAN};opacity:0"),
    dc("rm-c1t", "ttl", IX + 100, PY + 320, 68, "ADA GERAN", L(14.56, R0) - 0.06, 0.3),
    static("rm-c2", "chip m", IX + 422, PY + 310, 1, "", "width:390px;height:96px;opacity:0"),
    static("rm-c2m", "ttl mag", IX + 444, PY + 320, 72, "✓", "opacity:0"),
    dc("rm-c2t", "ttl", IX + 522, PY + 320, 68, "ADA KUNCI", L(15.39, R0) - 0.1, 0.3),
])
rm_body = panel("rm", PX, PY, PW, RM_H, rm_inner)
rm_dur = round(S_RMH[1] - R0, 3)
rm_script = panel_fx("rm", RM_H, rm_dur)
rm_script.append(f'tl.fromTo("#rm-chip", {{ opacity: 0, scaleX: 0.2 }}, {{ opacity: 1, scaleX: 1, duration: 0.22, ease: "power3.out" }}, {L(12.56, R0) - 0.04:.3f});')
for c, src in (("rm-c1", 14.56), ("rm-c2", 15.39)):
    rm_script.append(f'tl.fromTo("#{c}", {{ opacity: 0, scaleX: 0.2 }}, {{ opacity: 1, scaleX: 1, duration: 0.22, ease: "power3.out" }}, {L(src, R0) - 0.1:.3f});')
    pop(f"#{c}m", L(src, R0) - 0.02, rm_script)

# ------------------------------------------------------------------ 5. CTA  (holo tab + the real profile screenshot)
C0 = S_CTA[0]
TAB_H = 168
CW = 660
CX = (W - CW) // 2
SC = CW / 1206
IMG_H = round(822 * SC)
IMG_Y = PY + TAB_H + 26
ct_inner = "\n".join([
    f'          <div id="ct-qw" style="position:absolute;left:{IX}px;top:{PY + 26}px">',
    dc("ct-q", "ttl", 0, 0, 72, "YANG MANA BERMINAT?", 0.1, 0.45, "position:relative"),
    "          </div>",
    dc("ct-loc", "lbl", IX, PY + 118, 30, f"◉ {LOCATION} · ALOR SETAR", L(19.24, C0), 0.6, f"color:{INK}"),
])
tab = panel("ct", PX, PY, PW, TAB_H, ct_inner)
# the link line in the screenshot (source px) -> frame px
lk_x0, lk_x1, lk_y0, lk_y1 = 30, 780, 664, 720
HX, HY = CX + round(lk_x0 * SC), IMG_Y + round(lk_y0 * SC)
HW, HH = round((lk_x1 - lk_x0) * SC), round((lk_y1 - lk_y0) * SC)
ct_body = f'''{tab}
      <div id="ct-cta" style="position:absolute;left:{IX}px;top:{PY + 26}px;opacity:0">
        <div id="ct-cta-t" class="ttl mag" style="left:0;top:0;font-size:72px">TEKAN LINK DI BIO ▸</div>
      </div>
      <div id="ct-card" style="position:absolute;left:{CX}px;top:{IMG_Y}px;width:{CW}px;height:{IMG_H}px;border-radius:20px;overflow:hidden;background:#000;box-shadow:0 0 0 2px rgba(127,243,255,0.8), 0 0 36px rgba(60,220,255,0.5)">
        <img id="ct-shot" src="assets/cta-profile.jpg" alt="Profil TikTok NAZProperty" style="position:absolute;left:0;top:0;width:{CW}px;height:{IMG_H}px" />
        <div id="ct-cscan" class="scan" style="opacity:0.55"></div>
        <div id="ct-csweep" class="sweep"></div>
      </div>
      <div id="ct-hl" style="position:absolute;left:{HX - 8}px;top:{HY - 6}px;width:{HW + 16}px;height:{HH + 12}px;border:4px solid {MAG};border-radius:12px;box-shadow:0 0 20px rgba(255,90,217,0.6);opacity:0"></div>'''
ct_dur = round(TOTAL - C0, 3)
ct_script = panel_fx("ct", TAB_H, ct_dur + 0.4)   # no glitch-out: the CTA holds to the last frame
ct_script = [l for l in ct_script if "skewX" not in l]
t_tekan = L(17.67, C0)
ct_script += [
    f'tl.to("#ct-qw", {{ opacity: 0, duration: 0.08 }}, {t_tekan - 0.1:.3f});',
    f'tl.set("#ct-cta", {{ opacity: 1 }}, {t_tekan - 0.02:.3f});',
    f'tl.fromTo("#ct-cta-t", {{ x: -18, skewX: -12, opacity: 0.4 }}, {{ x: 0, skewX: 0, opacity: 1, duration: 0.24, ease: "power3.out" }}, {t_tekan - 0.02:.3f});',
    f'tl.fromTo("#ct-card", {{ opacity: 0, scaleY: 0.04, transformOrigin: "50% 50%" }}, {{ opacity: 1, scaleY: 1, duration: 0.32, ease: "power3.out" }}, 0.3);',
    f'tl.set("#ct-card", {{ opacity: 0.5 }}, 0.66);',
    f'tl.set("#ct-card", {{ opacity: 1 }}, 0.7);',
    f'tl.fromTo("#ct-cscan", {{ y: 0 }}, {{ y: {5 * int(ct_dur * 8)}, duration: {ct_dur:.3f}, ease: "none" }}, 0);',
    f'tl.fromTo("#ct-csweep", {{ y: -140 }}, {{ y: {IMG_H + 10}, duration: 1.8, ease: "none", repeat: {int(ct_dur / 1.8) - 1} }}, 0);',
    f'tl.fromTo("#ct-hl", {{ opacity: 0, scale: 1.1 }}, {{ opacity: 1, scale: 1, duration: 0.28, ease: "back.out(2)" }}, {L(18.09, C0):.3f});',
    f'tl.fromTo("#ct-hl", {{ boxShadow: "0 0 18px rgba(255,90,217,0.45)" }}, {{ boxShadow: "0 0 34px rgba(255,90,217,0.95)", duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: 5 }}, {L(18.09, C0) + 0.3:.3f});',
]

# ------------------------------------------------------------------ write scenes
os.makedirs(os.path.join(P, "compositions"), exist_ok=True)
SCENES = [
    ("siaran", sr_body, sr_script, (0.0, TOTAL), 9),
    ("hook", hk_body, hk_script, S_HOOK, 3),
    ("nasihat", ns_body, ns_script, S_NAS, 4),
    ("amaran", am_body, am_script, S_AMR, 3),
    ("rumah", rm_body, rm_script, S_RMH, 4),
    ("cta", ct_body, ct_script, S_CTA, 3),
]
for cid, body, script, win, _ in SCENES:
    with open(os.path.join(P, "compositions", f"{cid}.html"), "w") as f:
        f.write(scene(cid, body, script, round(win[1] - win[0], 3)))

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
for z, (cid, _, _, (a, b), tr) in enumerate(SCENES):
    hosts.append(f'''      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html"
        data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="{tr}" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index:{20 + z}"></div>''')


def sfx(id_, f, s, d, v, tr):
    return (f'      <audio id="{id_}" class="clip" src="assets/sfx/{f}" data-start="{max(0, s):.3f}" data-duration="{d}" '
            f'data-track-index="{tr}" data-volume="{v}" data-fade-out="0.12"></audio>')


audio = [
    sfx("sfx-ok", "ping.mp3", out(2.59), 0.8, 0.22, 6),
    sfx("sfx-glitch-1", "glitch-1.mp3", S_HOOK[1] - 0.2, 0.35, 0.16, 7),
    sfx("sfx-in-2", "whoosh-short.mp3", S_NAS[0] + 0.06, 0.5, 0.14, 6),
    sfx("sfx-type-1", "typing.mp3", out(5.20), 0.5, 0.16, 8),
    sfx("sfx-segera", "impact-bass-1.mp3", out(7.28) - 0.06, 1.0, 0.26, 6),
    sfx("sfx-glitch-2", "glitch-3.mp3", S_NAS[1] - 0.2, 0.3, 0.14, 7),
    sfx("sfx-in-3", "whoosh-short.mp3", S_AMR[0] + 0.06, 0.5, 0.12, 9),
    sfx("sfx-type-2", "typing.mp3", S_AMR[0] + 0.42, 0.6, 0.14, 8),
    sfx("sfx-hilang", "glitch-2.mp3", out(11.40), 0.6, 0.24, 7),
    sfx("sfx-in-4", "whoosh-short.mp3", S_RMH[0] + 0.06, 0.5, 0.12, 6),
    sfx("sfx-tick-1", "pop.mp3", out(14.56) - 0.02, 0.5, 0.2, 8),
    sfx("sfx-tick-2", "pop.mp3", out(15.39) - 0.02, 0.5, 0.2, 6),
    sfx("sfx-glitch-3", "glitch-1.mp3", S_RMH[1] - 0.2, 0.3, 0.14, 7),
    sfx("sfx-cta", "whoosh-cinematic.mp3", S_CTA[0] + 0.1, 1.2, 0.14, 8),
    sfx("sfx-link", "chime.mp3", out(18.09), 1.2, 0.18, 6),
    sfx("sfx-lokasi", "sparkle.mp3", out(19.24), 1.0, 0.14, 7),
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
print("total", TOTAL, "starts", starts, "speech_end", SPEECH_END)
print("scenes", S_HOOK, S_NAS, S_AMR, S_RMH, S_CTA, "card y", IMG_Y, "to", IMG_Y + IMG_H)
