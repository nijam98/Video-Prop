"""TikTok cover (1080x1920) in the same scrapbook paper-cutout style as the video.
usage: python3 thumbnail/build_thumb.py   (from rumah-changlun/), then
       npx hyperframes snapshot thumbnail --at 0 --no-end
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "edit"))
from build_comp import SHARED_CSS, torn, cut, burst, piece, NOISE  # noqa: E402

def tiles(word, x, y, seed, sizes=(118, 124, 130), fsmul=1.0):
    fonts = ["f-arch", "f-play", "f-goth", "f-mono", "f-arch", "f-play", "f-goth", "f-arch"]
    cols = ["tomato", "cream", "mustard", "ink", "teal", "cream", "tomato", "mustard"]
    r = random.Random(seed); out = []; k = 0
    for ch in word:
        if ch == " ":
            x += 40; continue
        f = fonts[k % 8]; size = r.choice(sizes)
        w = size * (0.74 if f == "f-goth" else 0.86)
        fs = {"f-goth": 1.17, "f-mono": 0.8, "f-play": 0.87, "f-arch": 0.8}[f] * size * fsmul
        out.append(f'<div class="abs" style="left:{x:.0f}px;top:{y + r.uniform(-16, 16):.0f}px;width:{w:.0f}px;height:{size}px">'
                   f'<div class="shad" style="width:100%;height:100%"><div class="face bg-{cols[k % 8]} {f}" style="clip-path:{cut(100 + k + seed)};width:100%;height:100%;'
                   f'display:flex;align-items:center;justify-content:center;font-size:{fs:.0f}px;line-height:1;transform:rotate({r.uniform(-9, 9):.1f}deg)">{ch}</div></div></div>')
        x += w + 7; k += 1
    return "".join(out), x

def photo(src, x, y, w, h, rot, seed, pos="50% 50%", tape="pink"):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg)">'
            f'<div class="shad" style="width:100%;height:100%;display:block"><div class="face" style="width:100%;height:100%;display:block;background:#FFF9EE;padding:14px 14px 14px;clip-path:{torn(seed, 7)}">'
            f'<img src="{src}" style="width:100%;height:100%;object-fit:cover;object-position:{pos};display:block"></div></div>'
            f'<div class="tape {tape}" style="left:{w/2-60:.0f}px;top:-18px;transform:rotate({-rot*1.5:.0f}deg)"></div></div>')

full, xe = tiles("FULL RENO", 0, 0, 0)
shift = (1080 - xe) / 2  # centre the word
full, _ = tiles("FULL RENO", shift, 300, 0)
body = [full]
body.append('<div class="abs" style="left:0;width:1080px;top:478px;text-align:center">'
            + piece('DARI DEPAN <span style="color:#E4502F">&#10140;</span> SAMPAI BELAKANG', "cream", 21, pad="16px 30px", fs=44, font="f-arch", tape=(-26, -14, -22, "")).replace('class="boil"', 'class="boil" style="transform:rotate(-1.5deg)"')
            + '</div>')
tag_poly = "polygon(14% 0,100% 0,100% 100%,14% 100%,0 50%)"
body.append('<div class="abs" style="left:46px;top:630px;transform:rotate(-8deg)"><div class="shad">'
            f'<div class="face bg-kraft f-arch" style="clip-path:{tag_poly};padding:24px 46px 24px 100px;font-size:58px;line-height:1.02">'
            '<div style="position:absolute;left:40px;top:50%;width:28px;height:28px;margin-top:-14px;border-radius:50%;background:#3B2A1C"></div>'
            'RUMAH<br>DIJUAL<div class="f-mark" style="font-size:44px;color:#E4502F;margin-top:6px">habis murah!</div></div></div></div>')
body.append(photo("assets/kitchen.jpg", 4, 1000, 420, 520, -6, 31, pos="55% 60%", tape="pink"))
body.append(photo("assets/bedroom.jpg", 300, 1110, 330, 400, 5, 32, pos="50% 50%", tape="teal"))
body.append('<div class="abs" style="left:612px;top:960px;width:430px;height:430px"><div class="shad" style="width:100%;height:100%">'
            f'<div class="core" style="inset:-10px;clip-path:{burst(77, 24, 41)}"></div>'
            f'<div class="face bg-tomato f-arch" style="clip-path:{burst(78, 24, 42)};width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:48px;line-height:1.0;text-align:center;transform:rotate(-6deg)">'
            '<div class="f-mark" style="font-size:32px;color:#F4B33A;transform:rotate(-4deg)">harga</div>BAWAH<br>MARKET<br>VALUE</div></div></div>')
body.append('<div class="abs" style="left:0;width:1080px;top:1556px;text-align:center">'
            + piece('&#128205; TAMAN JELUTONG FASA 1, CHANGLUN', "ink", 1602, pad="14px 30px", fs=40, font="f-arch") + '</div>')
html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #C99D6E; }}
      {SHARED_CSS}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #bg {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      #shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(20,14,8,.42) 0%, rgba(20,14,8,0) 30%, rgba(20,14,8,0) 52%, rgba(20,14,8,.5) 100%); }}
      .boil {{ position: relative; display: inline-block; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="thumb" data-start="0" data-width="1080" data-height="1920" data-no-timeline>
      <img id="bg" src="assets/bg.jpg" alt="">
      <div id="shade"></div>
      {''.join(body)}
    </div>
  </body>
</html>
"""
html = html.replace("#root { position: absolute; inset: 0; overflow: visible; pointer-events: none; }", "")
html = html.replace(".mv { position: relative; display: inline-block; opacity: 0; }", "")
open(os.path.join(HERE, "index.html"), "w").write(html)
print("wrote thumbnail/index.html")
