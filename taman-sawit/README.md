# Teres Taman Impian Mesra, Gurun — reel (HyperFrames)

Vertical 1080×1920 reel (22.3 s), edited from a 32.6 s hand-held site walk (iPhone, 4K HLG HEVC 60fps) plus the drone photo.

- **Look: "Berus Dakwat & Cop"** (ink brush & chop seal): dry-brush ink strokes with bristle streaks, vermilion chop seals
  that slam in with ink speckle and splatter, hand-drawn ensō circles and arrows, rice-paper caption strips,
  ink-swipe transitions and a rice-paper grain over the whole frame.
  Type: Knewave (brush lettering) + Mansalva (hand notes) + Barlow Condensed 800 (captions, seals).
  Palette: ink #17130F, vermilion #D8321F, rice paper #F4ECDD.
- **Drone photo** (`assets/photo.jpg`) is painted in by a brush mask: in the hook (ensō round the terrace rows),
  on "semi-D" (zoom + ensō on the semi-D units) and on the end card.
- **Edit:** hook = "Teres paling murah, harga bermula RM228K" moved to the front, then "bulanan sangat murah" and
  the location. Cut: "ok nampak depan tu, depan ni ada satu lagi", "ok", the 2nd "harga RM228", the unclear
  "macam biasa … isi sahaja" (repeat of the CTA), "bye bye" and every pause. The half second the camera passes the
  house columns is a freeze frame (`assets/columns.jpg`) under "projek tengah berjalan".
- **Safe zone:** passes `hyperframes check --safe-zone tiktok` and `--safe-zone reels` with no warnings
  (graphics y 290–1010, captions x 116–780, bottom ≤ 1170, nothing right of x 780 below y 840).
- **Audio:** voice -15 LUFS with fades on every cut; SFX pre-normalised to -20 LUFS, placed at 0.14–0.5 gain;
  hip-hop bed ducked under the voice and lifted for the end card. Mix ≈ -15.5 LUFS.

## Rebuild

```bash
tools/prepare-footage.sh /path/to/original.MOV   # HLG HDR -> SDR 1080x1920 60fps footage + cleaned voice (not in git)
python3 tools/build.py                           # regenerates index.html + compositions/*
npx hyperframes check --safe-zone tiktok && npx hyperframes check --safe-zone reels
npx hyperframes render -q draft -f 30 -o renders/preview-draft.mp4    # preview
npx hyperframes render -q high -f 60 -o renders/teres-impian-mesra.mp4  # final
```

All timings (cuts, captions, SFX, camera) live in the tables at the top of `tools/build.py`.
`assets/columns.jpg` is frame 7.0 s of the original, tone-mapped the same way as the footage.

Previous looks to avoid next time: Bauhaus, kinetic type, Y2K, art deco, holographic, split-flap, paper cut-out,
stick-figure comic, pop-art halftone comic, architect's sketchbook, crayon & oil pastel, and now ink brush & chop seal.
