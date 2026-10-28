# Video-Prop

Overlay pipeline for listing **REN51072** (Rumah | Tanah Untuk Dijual).
The source is an iPhone 4K HDR (HLG) clip, cut into two parts, each delivered as
4K (2160x3840) 60 fps SDR H.264.

| Part | Time in source | Overlay |
|------|----------------|---------|
| 1 | 0:00 – 1:40.38 | Y2K chrome CTA, bottom of the frame (`tools/part1_y2k.py`) |
| 2 | 1:40.38 – end  | Isometric 3D CTA card + button with CTA zoom, top of the frame (`tools/part2_iso.py`) |

## Build

```bash
cd tools
python3 render_frames.py part1 OV1      # 2 s intro + 4 s seamless loop as PNGs
python3 render_frames.py part2 OV2
./encode.sh SRC.mov 0        100.3833 OV1 part1.mp4
./encode.sh SRC.mov 100.3833 100.3834 OV2 part2.mp4
```

- HDR -> SDR uses ffmpeg's `colorspace` filter (fast, close to a zscale/hable tonemap).
  `make_lut.py` bakes the slower zscale tonemap into a .cube if a LUT is ever preferred.
- Overlay loops are checked with `render_frames.py partN DIR --check` (frame t == t + 4 s).
- Fonts in `tools/fonts` are Google Fonts (OFL): Rubik Mono One, Bungee, Orbitron, Montserrat.
