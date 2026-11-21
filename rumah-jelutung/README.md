# Rumah Taman Jelutong Fasa 2, Changlun — HyperFrames edit

Vertical (1080×1920) house-tour edit for TikTok / Instagram Reels, built with HyperFrames.

## Files
- `build.py` — edit decision list (cuts) + overlays → generates `index.html`
- `index.html` — HyperFrames composition (generated, do not hand-edit)
- `transcript.json` — Whisper large-v3 word-level transcript of the original clip
- `assets/photos/` — stills pulled from the footage, used as photo overlays
- `assets/fonts/` — Allura (writing), Cormorant Garamond (numbers), Manrope (labels)
- `assets/tour.mp4` — **not committed** (127 MB). Regenerate from the original `IMG_0722.MOV`:

```bash
ffmpeg -i IMG_0722.MOV -map 0:v:0 -map 0:a:0 \
 -vf "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1080:1920:flags=lanczos,fps=30,eq=saturation=1.05:contrast=1.03,colorbalance=rm=0.02:gm=-0.015:bm=-0.02" \
 -c:v libx264 -preset medium -crf 17 -g 15 -c:a aac -b:a 192k -ar 48000 -movflags +faststart assets/tour.mp4
```
(The iPhone source is HLG HDR; this tone-maps it to SDR Rec.709.)

## Build & render
```bash
python3 build.py --guides   # preview with TikTok/IG safe-zone guides
python3 build.py            # final, no guides
npx hyperframes@0.9.74 lint
npx hyperframes@0.9.74 render -q high -o renders/final.mp4
```

## Safe zone
Combined TikTok + IG Reels: all text/graphics kept inside x 72–920, y 260–1420.
