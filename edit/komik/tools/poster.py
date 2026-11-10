"""TikTok / IG cover poster in the same pop-art comic style as the edit.

usage: python3 tools/poster.py SOURCE.mov [frame_time]
writes poster/ (a one-frame HyperFrames project) and renders/Kulim_Komik_poster.png + .jpg
Key text sits inside y 240-1300 so it survives TikTok's 3:4 profile-grid crop and the feed UI.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from build import FONT, CSS, burst, speedlines, check, pin, C, M, Y, K, P, WHT, RED, W, H  # noqa: E402

OUT = os.path.join(HERE, "poster")
HF = "hyperframes@0.8.210"

BODY = f"""
    <img id="bg" class="clip" src="assets/bg.jpg" data-start="0" data-duration="2" style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;object-fit:cover;">
    <div id="frame" class="a" style="left:0;top:0;width:{W}px;height:{H}px;border:22px solid {P};box-shadow: inset 0 0 0 10px {K};"></div>

    <div class="box" style="left:84px;top:256px;font-size:44px;transform:rotate(-2deg);">misi hari ini:</div>
    <div class="bang" style="left:84px;top:340px;font-size:124px;transform:rotate(-2deg);">NAK CARI RUMAH</div>
    <div class="bang y" style="left:80px;top:470px;font-size:130px;transform:rotate(-2deg);">FULLY RENOVATED?</div>

    <div class="a" style="left:380px;top:640px;width:560px;height:340px;transform:rotate(5deg);">
      {burst("pk", 560, 340, M, points=13, inner=0.7, seed=2)}
      <div class="lbl" style="left:0;top:78px;width:560px;text-align:center;font-size:46px;color:{WHT};-webkit-text-stroke:8px {K};paint-order:stroke fill;">KAWASAN</div>
      <div class="bang" style="left:0;top:122px;width:560px;text-align:center;font-size:140px;">KULIM!</div>
    </div>
    <div class="a" style="left:300px;top:650px;width:120px;height:156px;transform:rotate(-10deg);">{pin(120)}</div>

    <div class="a" style="left:10px;top:820px;width:620px;height:440px;">{speedlines(620, 460, n=26)}</div>
    <div class="a" style="left:80px;top:850px;width:500px;height:360px;transform:rotate(-4deg);">
      {burst("pp", 500, 360, Y, points=15, inner=0.72, seed=13)}
      <div class="bang m" style="left:0;top:74px;width:500px;text-align:center;font-size:70px;">RM</div>
      <div class="bang m" style="left:0;top:138px;width:500px;text-align:center;font-size:160px;">370K</div>
    </div>

    <div class="a" style="left:590px;top:960px;width:330px;height:220px;transform:rotate(7deg);">
      <div class="a" style="left:0;top:0;width:300px;height:96px;border:9px solid {RED};background:rgba(255,246,222,0.94);box-shadow:8px 8px 0 {K};"></div>
      <div class="lbl" style="left:0;top:18px;width:300px;text-align:center;font-size:66px;color:{RED};">FREEHOLD</div>
      <div class="a" style="left:0;top:116px;width:300px;height:96px;border:9px solid {RED};background:rgba(255,246,222,0.94);box-shadow:8px 8px 0 {K};"></div>
      <div class="lbl" style="left:0;top:136px;width:300px;text-align:center;font-size:60px;color:{RED};">NON-BUMI</div>
    </div>

    <div class="a" style="left:84px;top:1240px;width:830px;height:90px;">
      <div class="box" style="left:0;top:0;font-size:50px;background:{WHT};">3 bilik</div>
      <div class="box" style="left:228px;top:0;font-size:50px;background:{C};">2 tandas</div>
      <div class="box" style="left:500px;top:0;font-size:50px;background:{WHT};">1,194 sqft</div>
    </div>
"""


def page():
    return f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
{FONT}{CSS.replace("#root {", "#poster {")}
    </style>
  </head>
  <body>
    <div id="poster" data-composition-id="main" data-start="0" data-duration="2" data-width="{W}" data-height="{H}"
         data-layout-allow-overlap data-layout-allow-overflow style="position:absolute;inset:0;overflow:hidden;">
{BODY}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def main(src, t):
    os.makedirs(os.path.join(OUT, "assets/fonts"), exist_ok=True)
    for f in ("Bangers.woff2", "ComicNeue-700.woff2"):
        shutil.copy(os.path.join(HERE, "assets/fonts", f), os.path.join(OUT, "assets/fonts", f))
    # background: the glossy hallway through the gate, same grade as the edit
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf",
                    "scale=1080:1920:flags=lanczos,eq=contrast=1.06:saturation=1.14:gamma=0.98,unsharp=5:5:0.35",
                    "-q:v", "2", os.path.join(OUT, "assets/bg.jpg")], check=True)
    for name, body in (("hyperframes.json", '{\n  "paths": { "assets": "assets" }\n}\n'),
                       ("meta.json", '{\n  "id": "komik-poster",\n  "name": "komik-poster"\n}\n'),
                       ("package.json", '{\n  "name": "komik-poster",\n  "private": true,\n  "type": "module"\n}\n')):
        with open(os.path.join(OUT, name), "w") as fh:
            fh.write(body)
    with open(os.path.join(OUT, "index.html"), "w") as fh:
        fh.write(page())
    snap = os.path.join(HERE, "build/poster_snap")
    shutil.rmtree(snap, ignore_errors=True)
    subprocess.run(["npx", "--yes", HF, "snapshot", OUT, "--at", "1", "--no-end", "-o", snap], check=True,
                   stdout=subprocess.DEVNULL)
    png = [f for f in os.listdir(snap) if f.startswith("frame-")][0]
    os.makedirs(os.path.join(HERE, "renders"), exist_ok=True)
    shutil.copy(os.path.join(snap, png), os.path.join(HERE, "renders/Kulim_Komik_poster.png"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "renders/Kulim_Komik_poster.png"),
                    "-q:v", "2", os.path.join(HERE, "renders/Kulim_Komik_poster.jpg")], check=True)
    print("renders/Kulim_Komik_poster.png")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 6.3)
