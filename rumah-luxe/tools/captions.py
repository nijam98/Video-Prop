"""Write compositions/captions.html from the hand-checked caption groups below (times are in the cut).
*word* marks the keyword set in Cormorant italic. usage: python3 tools/captions.py"""
import html, os, re
G = [
 ("Cantik tak *cantik?*", 0.10, 1.12), ("Sila *komen.*", 1.12, 2.35),
 ("Ruang tamu yang", 2.50, 3.55), ("sangat-sangat *cantik.*", 3.55, 4.68),
 ("And then sini ada *ruang makan,*", 4.70, 5.66), ("bawah ni ada satu bilik.", 5.66, 6.66),
 ("Bilik *keempat,*", 6.70, 7.62), ("bilik ni sesuai kalau nak buat", 7.64, 8.86), ("*bilik tetamu* pun boleh.", 8.86, 10.10),
 ("Built-in satu *toilet,*", 10.13, 11.55), ("*fully tiled* sampai kat atas.", 11.58, 13.35),
 ("Yang ni *ruang dapur.*", 13.38, 14.22), ("Yang ni boleh buat *dapur kering.*", 14.24, 15.45),
 ("Lebih kurang dalam *sembilan kaki,*", 15.48, 16.40), ("*extend* buat dapur besar.", 16.40, 17.90), ("Mesti *cantik.*", 17.93, 18.52),
 ("Kita tengok *ruang atas* pula.", 18.56, 20.60),
 ("Ruangan atas ni ada satu lagi", 20.64, 21.95), ("*ruang keluarga.*", 21.95, 23.08),
 ("Atas memiliki *tiga bilik*", 23.10, 24.80), ("dan *dua tandas.*", 24.80, 25.88),
 ("Sini *master bedroom.*", 25.90, 27.22), ("Master bedroom dia *luas,*", 27.25, 28.75),
 ("and then ada *tingkap.*", 28.78, 29.62), ("Nanti ke depan,", 29.64, 30.48),
 ("*extend* sahaja buat", 30.50, 31.60), ("*balkoni* depan ni.", 31.60, 32.80),
 ("Yang ni toilet", 32.85, 33.55), ("*master bedroom.*", 33.55, 34.50),
 ("Yang ni kita masuk ke", 34.55, 35.45), ("*bilik yang kedua.*", 35.45, 36.48),
 ("And then *toilet sharing.*", 36.50, 37.50),
 ("Sebelah sini", 37.55, 38.40), ("*bilik yang ketiga.*", 38.40, 40.14),
 ("Yang mana berminat,", 40.18, 41.45), ("yang bekerja di *Kulim*", 41.50, 43.20), ("ataupun belah *Penang.*", 43.25, 46.05),
 ("Nak cari rumah *teres*", 46.10, 47.20), ("*mampu beli,* mampu milik lagi,", 47.20, 49.62),
 ("promosinya sangat-sangat *menarik,*", 49.67, 50.90), ("boleh tekan *link di bio.*", 50.92, 52.18),
 ("Unit sangat-sangat *terhad.*", 52.20, 53.55),
]
def words(txt):
    out, em = [], False
    for tok in re.findall(r"\*|[^\s*]+", txt):
        if tok == "*": em = not em; continue
        out.append((tok, em))
    return out
groups_html, js = [], []
for i, (txt, s, e) in enumerate(G):
    spans = " ".join(f'<span class="cw{" em" if em else ""}">{html.escape(w)}</span>' for w, em in words(txt))
    groups_html.append(f'      <div id="cg{i}" class="cg"><p>{spans}</p></div>')
    js.append(f'    cap("#cg{i}", {s:.2f}, {e:.2f});')
doc = f'''<template>
  <style>
    @font-face {{ font-family: "Cormorant"; src: url("assets/fonts/cormorant-italic.woff2") format("woff2"); font-weight: 300 700; font-style: italic; }}
    @font-face {{ font-family: "Manrope"; src: url("assets/fonts/manrope.woff2") format("woff2"); font-weight: 200 800; font-style: normal; }}
    #root {{ position: absolute; inset: 0; }}
    #cap-band {{ position: absolute; left: 120px; top: 1102px; width: 660px; height: 140px; }}
    .cg {{ position: absolute; left: 0; bottom: 0; width: 660px; text-align: center; opacity: 0; visibility: hidden; }}
    .cg p {{ font: 600 40px/1.22 "Manrope", sans-serif; color: #f5f0e8; letter-spacing: 0.005em;
      text-shadow: 0 2px 6px rgba(14, 10, 8, 0.55), 0 6px 26px rgba(14, 10, 8, 0.5); }}
    .cw {{ display: inline-block; }}
    .cw.em {{ font: italic 500 54px/1 "Cormorant", serif; color: #f6e9d4; letter-spacing: 0; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    <div id="cap-band">
{chr(10).join(groups_html)}
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    function cap(sel, s, e) {{
      tl.set(sel, {{ opacity: 1, visibility: "visible" }}, s);
      tl.fromTo(sel + " .cw", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power2.out", stagger: 0.05 }}, s);
      tl.to(sel, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, e - 0.1);
      tl.set(sel, {{ opacity: 0, visibility: "hidden" }}, e);
    }}
{chr(10).join(js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
'''
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "compositions/captions.html"), "w").write(doc)
print(len(G), "groups")
