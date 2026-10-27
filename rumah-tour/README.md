# rumah-tour

TikTok / Reels edit (1080×1920, 30 fps) of a house walkthrough, built with HyperFrames.

- `tools/edl.py` — cut list: which source seconds are kept (pauses and repeats removed, hook moved to the front), snapped to quiet points; writes `edl.json` with word timings.
- `tools/build.py` — writes `index.html` and `compositions/*.html` (graphics, captions, sound) from `edl.json`. Change CTA text at the top of this file.
- `assets/footage.mp4` is not in git: it is the source `.MOV` tonemapped from HDR (HLG) to SDR 1080×1920 — see the ffmpeg line below.

```bash
ffmpeg -i source.mov -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv:w=1080:h=1920,format=yuv420p,eq=saturation=1.08:contrast=1.03,fps=30" -c:v libx264 -crf 16 -g 30 -c:a aac -b:a 256k assets/footage.mp4
python3 tools/build.py && npx hyperframes check && npx hyperframes render -q delivery -o out.mp4
```
