"""Build the Taman Keriang Permai "Bauhaus" edit (index.html + compositions/*.html).

Edit copy and timings in SCENES / SFX below, then run:  python3 build.py
Times are seconds on the cut timeline (assets/footage.mp4 + assets/voice.wav).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
TOTAL = 25.60          # root duration (voice ends ~24.6, CTA holds on the last shot)

R, Y, B, K, C = "#E1301E", "#F4B400", "#1D4FA0", "#141414", "#F3ECDD"

FONT = """
    @font-face { font-family: 'Jost'; src: url('assets/fonts/Jost.woff2') format('woff2'); font-weight: 400 900; }
"""

CSS = f"""
    #root {{ position: absolute; inset: 0; pointer-events: none; font-family: 'Jost', sans-serif; color: {K}; }}
    .a {{ position: absolute; }}
    .card {{ position: absolute; background: {C}; box-shadow: 12px 12px 0 {K}; }}
    .pill {{ position: absolute; padding: 14px 34px 18px; font-weight: 800; white-space: nowrap; box-shadow: 10px 10px 0 {K}; }}
    .circ {{ position: absolute; border-radius: 50%; }}
    .tri {{ position: absolute; clip-path: polygon(50% 0, 100% 100%, 0 100%); }}
    .t {{ position: absolute; white-space: nowrap; line-height: 0.9; letter-spacing: -0.02em; }}
    .w {{ display: inline-block; }}
"""


def scene(sid, dur, body, js):
    return f"""<template>
  <style>{FONT}{CSS}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}" data-layout-allow-overlap>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const S = (q) => document.querySelector(q);
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


# exit helper: everything in the scene lifts and fades
def exit_all(sel, t):
    return f'    tl.to("{sel}", {{ y: "-=46", opacity: 0, duration: 0.22, ease: "power3.in", stagger: 0.03 }}, {t});\n'


SCENES = []

# 1. HOOK 0.00-2.40  "Ok untuk geng-geng berniaga yang mana nak beli rumah"
SCENES.append(("hook", 0.0, 2.40, f"""
    <div id="hk-sq" class="a" style="left:96px; top:258px; width:150px; height:150px; background:{B};"></div>
    <div id="hk-card" class="card" style="left:150px; top:320px; width:690px; height:300px;"></div>
    <div id="hk-ci" class="circ" style="left:712px; top:236px; width:200px; height:200px; background:{R};"></div>
    <div id="hk-l1" class="t" style="left:196px; top:362px; font-size:58px; font-weight:600;">untuk geng</div>
    <div id="hk-l2" class="t" style="left:186px; top:434px; font-size:160px; font-weight:900;">peniaga</div>
    <div id="hk-tr" class="tri" style="left:708px; top:560px; width:170px; height:150px; background:{Y};"></div>
    <div id="hk-pill" class="pill" style="left:150px; top:672px; background:{R}; color:{C}; font-size:66px;">nak beli rumah?</div>
""", f"""
    tl.fromTo("#hk-ci", {{ scale: 0.55 }}, {{ scale: 1, duration: 0.5, ease: "back.out(1.6)" }}, 0);
    tl.fromTo("#hk-sq", {{ rotation: -45 }}, {{ rotation: 0, duration: 0.55, ease: "expo.out" }}, 0);
    tl.fromTo("#hk-tr", {{ scale: 0, rotation: -120, transformOrigin: "50% 66%" }}, {{ scale: 1, rotation: 0, duration: 0.5, ease: "back.out(1.5)" }}, 0.18);
    tl.fromTo("#hk-pill", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.42, ease: "expo.out" }}, 1.30);
{exit_all("#hk-pill, #hk-l2, #hk-l1, #hk-card, #hk-ci, #hk-sq, #hk-tr", 2.12)}"""))

# 2. RUMAH NI UNTUK HAMPA 2.55-4.30
SCENES.append(("hampa", 2.55, 1.75, f"""
    <div id="hp-b1" class="pill" style="left:150px; top:330px; background:{Y}; font-size:96px;">rumah ni</div>
    <div id="hp-b2" class="pill" style="left:290px; top:478px; background:{B}; color:{C}; font-size:96px;">untuk hampa</div>
    <div id="hp-arrow" class="a" style="left:180px; top:600px; width:90px; height:200px;">
      <div class="a" style="left:30px; top:0; width:30px; height:120px; background:{R};"></div>
      <div class="tri" style="left:0; top:110px; width:90px; height:80px; background:{R}; transform: rotate(180deg);"></div>
    </div>
""", f"""
    tl.fromTo("#hp-b1", {{ x: -700 }}, {{ x: 0, duration: 0.45, ease: "expo.out" }}, 0.02);
    tl.fromTo("#hp-b2", {{ x: 760 }}, {{ x: 0, duration: 0.45, ease: "expo.out" }}, 0.62);
    tl.fromTo("#hp-arrow", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power4.out" }}, 0.9);
{exit_all("#hp-b1, #hp-b2, #hp-arrow", 1.52)}"""))

# 3. SEBAB APA? 4.28-5.05
SCENES.append(("sebab", 4.28, 0.80, f"""
    <div id="sb-ci" class="circ" style="left:400px; top:330px; width:280px; height:280px; background:{Y}; box-shadow: 12px 12px 0 {K};"></div>
    <div id="sb-q" class="t" style="left:400px; top:356px; width:280px; text-align:center; font-size:250px; font-weight:900;">?</div>
    <div id="sb-pill" class="pill" style="left:360px; top:640px; background:{K}; color:{C}; font-size:58px;">sebab apa</div>
""", f"""
    tl.fromTo("#sb-ci", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(1.8)" }}, 0);
    tl.fromTo("#sb-q", {{ scale: 0, rotation: -30 }}, {{ scale: 1, rotation: 0, duration: 0.32, ease: "back.out(2)" }}, 0.06);
    tl.fromTo("#sb-pill", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.25, ease: "expo.out" }}, 0.1);
    tl.to("#sb-ci, #sb-q, #sb-pill", {{ scale: 0.6, opacity: 0, duration: 0.14, ease: "power3.in" }}, 0.64);
"""))

# 4. SYARAT + LAYAK 5.05-9.55
SCENES.append(("syarat", 5.05, 4.50, f"""
    <div id="sy-tag" class="pill" style="left:110px; top:270px; background:{K}; color:{C}; font-size:44px; padding:10px 26px 14px;">perlu</div>
    <div id="sy-r1" class="a" style="left:110px; top:370px; width:800px; height:170px;">
      <div class="a" style="left:0; top:0; width:170px; height:170px; background:{R}; box-shadow: 10px 10px 0 {K};"></div>
      <div class="t" style="left:0; top:44px; width:170px; text-align:center; font-size:86px; font-weight:800; color:{C};">01</div>
      <div class="card" style="left:200px; top:0; width:420px; height:170px;"></div>
      <div class="t" style="left:236px; top:34px; font-size:120px; font-weight:900;">SSM</div>
    </div>
    <div id="sy-r2" class="a" style="left:110px; top:580px; width:850px; height:170px;">
      <div class="circ" style="left:0; top:0; width:170px; height:170px; background:{B}; box-shadow: 10px 10px 0 {K};"></div>
      <div class="t" style="left:0; top:44px; width:170px; text-align:center; font-size:86px; font-weight:800; color:{C};">02</div>
      <div class="card" style="left:200px; top:0; width:600px; height:170px;"></div>
      <div class="t" style="left:232px; top:24px; font-size:64px; font-weight:800;">penyata bank</div>
      <div class="t" style="left:232px; top:96px; font-size:56px; font-weight:600;"><span style="background:{Y}; padding:0 10px;">6 bulan</span></div>
    </div>
    <div id="sy-st" class="a" style="left:300px; top:300px; width:480px; height:480px;">
      <div class="circ" style="left:0; top:0; width:480px; height:480px; background:{Y}; box-shadow: 14px 14px 0 {K};"></div>
      <div class="circ" style="left:34px; top:34px; width:412px; height:412px; border: 6px solid {K};"></div>
      <div class="t" style="left:0; top:104px; width:480px; text-align:center; font-size:62px; font-weight:600;">hampa</div>
      <div class="t" style="left:0; top:178px; width:480px; text-align:center; font-size:150px; font-weight:900;">layak</div>
      <svg class="a" style="left:190px; top:330px;" width="100" height="80" viewBox="0 0 100 80"><path d="M8 40 L38 68 L92 10" fill="none" stroke="{R}" stroke-width="16" stroke-linecap="square"/></svg>
    </div>
    <div id="sy-pill" class="pill" style="left:290px; top:830px; background:{B}; color:{C}; font-size:72px;">beli teres</div>
""", f"""
    tl.fromTo("#sy-tag", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.3, ease: "expo.out" }}, 0.0);
    tl.fromTo("#sy-r1", {{ x: -900 }}, {{ x: 0, duration: 0.5, ease: "expo.out" }}, 0.5);
    tl.fromTo("#sy-r2", {{ x: -900 }}, {{ x: 0, duration: 0.5, ease: "expo.out" }}, 1.15);
    tl.to("#sy-tag, #sy-r1, #sy-r2", {{ x: -1000, duration: 0.32, ease: "power3.in", stagger: 0.04 }}, 1.88);
    tl.fromTo("#sy-st", {{ scale: 0, rotation: -200 }}, {{ scale: 1, rotation: -8, duration: 0.6, ease: "back.out(1.4)" }}, 2.12);
    tl.fromTo("#sy-pill", {{ y: 80, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4, ease: "power4.out" }}, 2.9);
{exit_all("#sy-pill, #sy-st", 4.22)}"""))

# 5. HARGA 9.70-12.10  "Bulanan lebih kurang dalam RM1,200 sahaja"
SCENES.append(("harga", 9.70, 2.42, f"""
    <div id="hg-ci" class="circ" style="left:690px; top:250px; width:230px; height:230px; background:{R};"></div>
    <div id="hg-card" class="card" style="left:130px; top:330px; width:760px; height:360px;"></div>
    <div id="hg-l1" class="t" style="left:180px; top:372px; font-size:60px; font-weight:600;">bulanan &plusmn;</div>
    <div id="hg-num" class="t" style="left:170px; top:456px; font-size:176px; font-weight:900;">RM<span id="hg-val">1,200</span></div>
    <div id="hg-bar" class="a" style="left:180px; top:640px; width:640px; height:22px; background:{Y};"></div>
    <div id="hg-pill" class="pill" style="left:560px; top:700px; background:{B}; color:{C}; font-size:64px;">sahaja</div>
""", f"""
    tl.fromTo("#hg-card", {{ clipPath: "inset(0 0 100% 0)" }}, {{ clipPath: "inset(0 0 0% 0)", duration: 0.45, ease: "expo.out" }}, 0.05);
    tl.fromTo("#hg-ci", {{ scale: 0 }}, {{ scale: 1, duration: 0.5, ease: "back.out(1.6)" }}, 0.15);
    tl.fromTo("#hg-l1", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2 }}, 0.2);
    tl.fromTo("#hg-num", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, 0.95);
    const cnt = {{ v: 800 }};
    tl.fromTo(cnt, {{ v: 800 }}, {{ v: 1200, duration: 0.55, ease: "expo.out",
      onUpdate: () => {{ S("#hg-val").textContent = Math.round(cnt.v / 10) * 10 >= 1000 ? (Math.floor(Math.round(cnt.v/10)*10/1000) + "," + String(Math.round(cnt.v/10)*10 % 1000).padStart(3, "0")) : String(Math.round(cnt.v/10)*10); }} }}, 0.95);
    tl.fromTo("#hg-bar", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.5, ease: "expo.out" }}, 1.25);
    tl.fromTo("#hg-pill", {{ x: 500 }}, {{ x: 0, duration: 0.45, ease: "expo.out" }}, 1.72);
{exit_all("#hg-pill, #hg-num, #hg-l1, #hg-bar, #hg-card, #hg-ci", 2.18)}"""))

# 6. LOKASI 12.10-13.90  "Dekat Taman Keriang Permai"
SCENES.append(("lokasi", 12.10, 1.80, f"""
    <div id="lk-pin" class="a" style="left:120px; top:300px; width:170px; height:250px;">
      <div class="circ" style="left:0; top:0; width:170px; height:170px; background:{R}; box-shadow: 8px 8px 0 {K};"></div>
      <div class="circ" style="left:55px; top:55px; width:60px; height:60px; background:{C};"></div>
      <div class="tri" style="left:35px; top:150px; width:100px; height:100px; background:{R}; transform: rotate(180deg);"></div>
    </div>
    <div id="lk-card" class="card" style="left:310px; top:320px; width:660px; height:240px;"></div>
    <div id="lk-t1" class="t" style="left:340px; top:350px; font-size:82px; font-weight:900;"><span class="w">taman</span> <span class="w">keriang</span></div>
    <div id="lk-t2" class="t" style="left:340px; top:446px; font-size:82px; font-weight:900;"><span class="w">permai</span></div>
    <div id="lk-pill" class="pill" style="left:320px; top:610px; background:{B}; color:{C}; font-size:52px;">changlun, kedah</div>
""", f"""
    tl.fromTo("#lk-pin", {{ y: -420 }}, {{ y: 0, duration: 0.5, ease: "back.out(1.3)" }}, 0.0);
    tl.fromTo("#lk-card", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.4, ease: "expo.out" }}, 0.12);
    tl.fromTo("#lk-t1 .w, #lk-t2 .w", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.14, stagger: 0.12 }}, 0.42);
    tl.fromTo("#lk-pill", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.35, ease: "expo.out" }}, 0.85);
{exit_all("#lk-pill, #lk-t2, #lk-t1, #lk-card, #lk-pin", 1.56)}"""))

# 7. SIAP + DUDUK TAHUN DEPAN 13.85-17.70
SCENES.append(("siap", 13.85, 3.85, f"""
    <div id="sp-a" class="a" style="left:150px; top:320px; width:760px; height:300px;">
      <div class="a" style="left:0; top:0; width:560px; height:250px; background:{Y}; box-shadow: 12px 12px 0 {K};"></div>
      <div class="t" style="left:40px; top:30px; font-size:60px; font-weight:600;">rumah</div>
      <div class="t" style="left:34px; top:96px; font-size:150px; font-weight:900;">siap</div>
      <div id="sp-ok" class="circ" style="left:470px; top:20px; width:230px; height:230px; background:{R}; box-shadow: 10px 10px 0 {K};">
        <svg class="a" style="left:45px; top:58px;" width="140" height="110" viewBox="0 0 140 110"><path d="M12 56 L54 96 L128 14" fill="none" stroke="{C}" stroke-width="22" stroke-linecap="square"/></svg>
      </div>
    </div>
    <div id="sp-b" class="a" style="left:120px; top:290px; width:840px; height:520px;">
      <div id="sp-tag" class="pill" style="left:0; top:0; background:{K}; color:{C}; font-size:48px; padding:10px 26px 14px;">yang penting</div>
      <div id="sp-cal" class="a" style="left:640px; top:70px; width:180px; height:180px; background:{R}; box-shadow: 10px 10px 0 {K};">
        <div class="circ" style="left:40px; top:40px; width:100px; height:100px; background:{Y};"></div>
      </div>
      <div id="sp-b1" class="pill" style="left:0; top:110px; background:{C}; font-size:100px;">boleh duduk</div>
      <div id="sp-b2" class="pill" style="left:90px; top:270px; background:{B}; color:{C}; font-size:100px;">tahun depan</div>
    </div>
""", f"""
    tl.fromTo("#sp-a", {{ x: -900 }}, {{ x: 0, duration: 0.5, ease: "expo.out" }}, 0.06);
    tl.fromTo("#sp-ok", {{ scale: 0, rotation: -90 }}, {{ scale: 1, rotation: 0, duration: 0.45, ease: "back.out(1.8)" }}, 0.5);
    tl.to("#sp-a", {{ x: 1000, duration: 0.3, ease: "power3.in" }}, 1.0);
    tl.fromTo("#sp-tag", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.3, ease: "expo.out" }}, 1.12);
    tl.fromTo("#sp-b1", {{ x: -900 }}, {{ x: 0, duration: 0.5, ease: "expo.out" }}, 2.0);
    tl.fromTo("#sp-cal", {{ scale: 0, rotation: 90 }}, {{ scale: 1, rotation: 0, duration: 0.5, ease: "back.out(1.5)" }}, 2.2);
    tl.fromTo("#sp-b2", {{ x: 900 }}, {{ x: 0, duration: 0.5, ease: "expo.out" }}, 3.0);
{exit_all("#sp-b2, #sp-b1, #sp-cal, #sp-tag", 3.6)}"""))

# 8. HAMPIR SEPARUH 17.90-19.30
SCENES.append(("separuh", 17.90, 1.40, f"""
    <svg id="sr-ring" class="a" style="left:120px; top:300px;" width="330" height="330" viewBox="0 0 330 330">
      <circle cx="165" cy="165" r="130" fill="{C}" stroke="{K}" stroke-width="8"/>
      <circle id="sr-arc" cx="165" cy="165" r="65" fill="none" stroke="{R}" stroke-width="130" stroke-dasharray="408.4" stroke-dashoffset="408.4" transform="rotate(-90 165 165)"/>
      <circle cx="165" cy="165" r="130" fill="none" stroke="{K}" stroke-width="8"/>
      <line x1="165" y1="35" x2="165" y2="295" stroke="{K}" stroke-width="8"/>
    </svg>
    <div id="sr-t1" class="pill" style="left:480px; top:316px; background:{C}; font-size:56px; padding:8px 24px 12px;">hampir</div>
    <div id="sr-t2" class="pill" style="left:480px; top:440px; background:{Y}; font-size:100px;">separuh</div>
    <div id="sr-t3" class="pill" style="left:560px; top:580px; background:{K}; color:{C}; font-size:60px;">dah!</div>
""", f"""
    tl.fromTo("#sr-ring", {{ scale: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, 0.0);
    tl.fromTo("#sr-arc", {{ attr: {{ "stroke-dashoffset": 408.4 }} }}, {{ attr: {{ "stroke-dashoffset": 222 }}, duration: 0.7, ease: "power2.out" }}, 0.25);
    tl.fromTo("#sr-t1", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.15 }}, 0.2);
    tl.fromTo("#sr-t2", {{ x: 560 }}, {{ x: 0, duration: 0.42, ease: "expo.out" }}, 0.5);
    tl.fromTo("#sr-t3", {{ scale: 0 }}, {{ scale: 1, duration: 0.3, ease: "back.out(2)" }}, 0.95);
{exit_all("#sr-t3, #sr-t2, #sr-t1, #sr-ring", 1.18)}"""))

# 9. 2 JENIS - TYPE A / TYPE B 19.35-22.40
SCENES.append(("jenis", 19.35, 3.05, f"""
    <div id="jn-2" class="circ" style="left:120px; top:280px; width:200px; height:200px; background:{Y}; box-shadow: 10px 10px 0 {K};"></div>
    <div id="jn-2t" class="t" style="left:120px; top:290px; width:200px; text-align:center; font-size:180px; font-weight:900;">2</div>
    <div id="jn-tt" class="pill" style="left:350px; top:310px; background:{C}; font-size:84px;">jenis teres</div>
    <div id="jn-a" class="a" style="left:140px; top:540px; width:330px; height:330px; background:{R}; box-shadow: 12px 12px 0 {K};">
      <div class="t" style="left:30px; top:28px; font-size:58px; font-weight:600; color:{C};">type</div>
      <div class="t" style="left:0; top:80px; width:330px; text-align:center; font-size:230px; font-weight:900; color:{C};">A</div>
    </div>
    <div id="jn-b" class="circ" style="left:560px; top:540px; width:330px; height:330px; background:{B}; box-shadow: 12px 12px 0 {K};">
      <div class="t" style="left:0; top:40px; width:330px; text-align:center; font-size:58px; font-weight:600; color:{C};">type</div>
      <div class="t" style="left:0; top:92px; width:330px; text-align:center; font-size:210px; font-weight:900; color:{C};">B</div>
    </div>
""", f"""
    tl.fromTo("#jn-2, #jn-2t", {{ scale: 0 }}, {{ scale: 1, duration: 0.4, ease: "back.out(1.8)" }}, 0.12);
    tl.fromTo("#jn-tt", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.4, ease: "expo.out" }}, 0.4);
    tl.fromTo("#jn-a", {{ y: 700, rotation: -20 }}, {{ y: 0, rotation: 0, duration: 0.5, ease: "back.out(1.2)" }}, 1.62);
    tl.fromTo("#jn-b", {{ y: 700, rotation: 20 }}, {{ y: 0, rotation: 0, duration: 0.5, ease: "back.out(1.2)" }}, 2.32);
{exit_all("#jn-b, #jn-a, #jn-tt, #jn-2t, #jn-2", 2.86)}"""))

# 10. CTA 22.55-25.60  "Nak tahu detail tekan link dekat bio"
SCENES.append(("cta", 22.55, TOTAL - 22.55, f"""
    <div id="ct-sq" class="a" style="left:110px; top:300px; width:140px; height:140px; background:{B};"></div>
    <div id="ct-ci" class="circ" style="left:760px; top:620px; width:170px; height:170px; background:{Y};"></div>
    <div id="ct-q" class="pill" style="left:170px; top:360px; background:{C}; font-size:66px;">nak tahu detail?</div>
    <div id="ct-btn" class="a" style="left:150px; top:500px; width:700px; height:190px; background:{R}; box-shadow: 14px 14px 0 {K};">
      <div class="t" style="left:0; top:24px; width:700px; text-align:center; font-size:62px; font-weight:600; color:{C};">klik</div>
      <div class="t" style="left:0; top:84px; width:700px; text-align:center; font-size:96px; font-weight:900; color:{C};">link di bio</div>
    </div>
    <div id="ct-h" class="pill" style="left:150px; top:740px; background:{K}; color:{C}; font-size:46px; padding:10px 26px 14px;">@nazpropertyy</div>
""", f"""
    tl.fromTo("#ct-sq", {{ rotation: -90, scale: 0 }}, {{ rotation: 0, scale: 1, duration: 0.5, ease: "back.out(1.5)" }}, 0.0);
    tl.fromTo("#ct-q", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.4, ease: "expo.out" }}, 0.3);
    tl.fromTo("#ct-btn", {{ y: 260, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "expo.out" }}, 0.95);
    tl.fromTo("#ct-ci", {{ scale: 0 }}, {{ scale: 1, duration: 0.45, ease: "back.out(1.8)" }}, 1.1);
    tl.fromTo("#ct-h", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.35, ease: "expo.out" }}, 1.3);
    tl.to("#ct-btn", {{ scale: 0.93, boxShadow: "4px 4px 0 {K}", x: 8, y: 8, duration: 0.08, ease: "power2.in" }}, 1.43);
    tl.to("#ct-btn", {{ scale: 1, boxShadow: "14px 14px 0 {K}", x: 0, y: 0, duration: 0.3, ease: "back.out(2)" }}, 1.52);
"""))

# Bauhaus shape wipes over the big jump cuts (cover peaks on the cut)
WIPES = [8.72, 13.94, 19.06, 22.44]

# punch-in settle on smaller jump cuts
PUNCH = [2.32, 5.14, 12.12, 16.0]

# sound effects: (time the hit should land, file, volume)
SFX = [
    (0.06, "pop", 0.45),
    (2.58, "whoosh-short", 0.35), (3.18, "whoosh-short", 0.30),
    (4.30, "pop", 0.45),
    (5.56, "click-soft", 0.55), (6.21, "click-soft", 0.55),
    (7.20, "ping", 0.35),
    (8.72, "whoosh", 0.45),
    (10.70, "impact-bass-1", 0.45),
    (12.30, "pop", 0.40),
    (13.94, "whoosh-short", 0.40),
    (14.40, "sparkle", 0.30),
    (18.20, "pop", 0.40),
    (19.06, "whoosh", 0.40),
    (21.00, "pop", 0.45), (21.70, "click", 0.40),
    (22.44, "whoosh-short", 0.40),
    (24.00, "click", 0.55),
]


def wipes_scene():
    body, js = [], []
    for i, t in enumerate(WIPES):
        body.append(f'    <div class="a" style="left:-420px; top:-360px; width:1920px; height:2640px; transform: rotate(-14deg);">')
        for j, col in enumerate([R, Y, B]):
            body.append(f'      <div id="wp{i}{j}" class="a" style="left:0; top:{j*880}px; width:1920px; height:900px; background:{col};"></div>')
            js.append(f'    tl.set("#wp{i}{j}", {{ x: -2100 }}, 0);')
            js.append(f'    tl.fromTo("#wp{i}{j}", {{ x: -2100 }}, {{ x: 0, duration: 0.2, ease: "power3.in", immediateRender: false }}, {t - 0.27 + j*0.03:.3f});')
            js.append(f'    tl.to("#wp{i}{j}", {{ x: 2200, duration: 0.26, ease: "power3.out" }}, {t + 0.03 + j*0.03:.3f});')
        body.append('    </div>')
    return scene("wipes", TOTAL, "\n".join(body), "\n".join(js))


def index():
    hosts = []
    for i, (sid, st, du, _, _) in enumerate(SCENES):
        hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st}" data-duration="{du:.2f}" data-track-index="{2 + i % 2}" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:{10 + i};"></div>')
    sfx, lanes = [], []
    for i, (t, f, v) in enumerate(SFX):
        start = max(0.0, t - SFX_PEAK.get(f, 0.0) + 1 / 60)
        dur = min(SFX_DUR[f], TOTAL - start)
        lane = next((k for k, end in enumerate(lanes) if end <= start), None)
        if lane is None:
            lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = start + dur
        sfx.append(f'      <audio id="sfx{i}" src="assets/sfx/{f}.mp3" data-start="{start:.3f}" data-duration="{dur:.3f}" data-volume="{v}" data-track-index="{8 + lane}"></audio>')
    punch = '      tl.set("#footwrap", { scale: 1 }, 0);\n' + "\n".join(
        f'      tl.fromTo("#footwrap", {{ scale: 1.08 }}, {{ scale: 1, duration: 0.45, ease: "expo.out", immediateRender: false }}, {t});' for t in PUNCH)
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
      <div id="wipes" data-composition-id="wipes" data-composition-src="compositions/wipes.html" data-start="0" data-duration="{TOTAL}" data-track-index="4" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:50;"></div>
      <audio id="voice" src="assets/voice.wav" data-start="0" data-volume="1" data-track-index="6"></audio>
      <audio id="music" src="assets/music.mp3" data-start="0" data-duration="{TOTAL}" data-volume="1" data-fade-out="1.2" data-track-index="7"
        data-automation='{{"version":1,"lanes":[{{"target":"volume","points":[{{"t":0,"v":0.13}},{{"t":24.5,"v":0.13}},{{"t":24.9,"v":0.32}},{{"t":{TOTAL},"v":0.32}}]}}]}}'></audio>
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

os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
for sid, st, du, body, js in SCENES:
    open(os.path.join(HERE, "compositions", f"{sid}.html"), "w").write(scene(sid, du, body, js))
open(os.path.join(HERE, "compositions", "wipes.html"), "w").write(wipes_scene())
open(os.path.join(HERE, "index.html"), "w").write(index())
print("built", len(SCENES) + 1, "scenes")
